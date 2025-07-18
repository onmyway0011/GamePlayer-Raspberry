#!/usr/bin/env python3
"""
GamePlayer-Raspberry 简单演示服务器
用于测试Web界面功能
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any
from aiohttp import web, web_static
from aiohttp.web import Response, json_response
import aiohttp_cors
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GamePlayerServer:
    """GamePlayer Web服务器"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.project_root = Path(__file__).parent
        self.web_dir = self.project_root / "src/web"
        self.rom_dir = self.project_root / "data/roms"
        self.config_dir = self.project_root / "config/emulators"
        
        # 确保目录存在
        self.web_dir.mkdir(parents=True, exist_ok=True)
        self.rom_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def create_app(self) -> web.Application:
        """创建Web应用"""
        app = web.Application()
        
        # 配置CORS
        cors = aiohttp_cors.setup(app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # API路由
        api_routes = [
            web.get('/api/status', self.get_status),
            web.get('/api/systems', self.get_systems),
            web.get('/api/games/{system}', self.get_games),
            web.post('/api/launch', self.launch_game),
            web.get('/api/settings', self.get_settings),
            web.post('/api/settings', self.save_settings),
            web.get('/api/stats', self.get_stats),
        ]
        
        for route in api_routes:
            cors.add(app.router.add_route(route.method, route.path, route.handler))
        
        # 静态文件服务
        if self.web_dir.exists():
            app.router.add_static('/', self.web_dir, name='static')
            # 添加根路径重定向到index.html
            app.router.add_get('/', self.serve_index)
        else:
            logger.warning(f"Web目录不存在: {self.web_dir}")
            app.router.add_get('/', self.serve_fallback)
        
        return app
    
    async def serve_index(self, request):
        """服务主页"""
        index_file = self.web_dir / "index.html"
        if index_file.exists():
            return web.FileResponse(index_file)
        else:
            return await self.serve_fallback(request)
    
    async def serve_fallback(self, request):
        """备用页面"""
        html_content = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>GamePlayer-Raspberry</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-align: center;
                    padding: 2rem;
                    min-height: 100vh;
                    margin: 0;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 3rem;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                }
                h1 {
                    font-size: 2.5rem;
                    margin-bottom: 1rem;
                }
                .icon {
                    font-size: 4rem;
                    margin-bottom: 2rem;
                }
                .status {
                    background: rgba(76, 175, 80, 0.2);
                    border: 1px solid rgba(76, 175, 80, 0.5);
                    border-radius: 10px;
                    padding: 1rem;
                    margin: 2rem 0;
                }
                .api-info {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 1.5rem;
                    margin-top: 2rem;
                    text-align: left;
                }
                .endpoint {
                    background: rgba(0, 0, 0, 0.2);
                    padding: 0.5rem 1rem;
                    border-radius: 5px;
                    margin: 0.5rem 0;
                    font-family: monospace;
                    font-size: 0.9rem;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">🎮</div>
                <h1>GamePlayer-Raspberry</h1>
                <p>游戏启动器后端服务正在运行</p>
                
                <div class="status">
                    ✅ 服务器状态: 运行中<br>
                    🕒 启动时间: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """<br>
                    🌐 端口: """ + str(self.port) + """
                </div>
                
                <div class="api-info">
                    <h3>🔗 可用API端点:</h3>
                    <div class="endpoint">GET /api/status - 系统状态</div>
                    <div class="endpoint">GET /api/systems - 游戏系统列表</div>
                    <div class="endpoint">GET /api/games/{system} - 游戏列表</div>
                    <div class="endpoint">POST /api/launch - 启动游戏</div>
                    <div class="endpoint">GET /api/settings - 获取设置</div>
                    <div class="endpoint">POST /api/settings - 保存设置</div>
                    <div class="endpoint">GET /api/stats - 统计信息</div>
                </div>
                
                <p style="margin-top: 2rem; font-size: 0.9rem; opacity: 0.8;">
                    请访问 <strong>/</strong> 查看游戏启动器界面<br>
                    (如果Web文件存在的话)
                </p>
            </div>
        </body>
        </html>
        """
        return web.Response(text=html_content, content_type='text/html')
    
    async def get_status(self, request):
        """获取系统状态"""
        return json_response({
            "online": True,
            "server_time": datetime.now().isoformat(),
            "uptime": "运行中",
            "version": "1.0.0",
            "systems_available": await self._count_available_systems()
        })
    
    async def get_systems(self, request):
        """获取游戏系统列表"""
        systems = {}
        
        # 扫描ROM目录
        systems_config = {
            "nes": {"name": "Nintendo Entertainment System", "extensions": [".nes"]},
            "snes": {"name": "Super Nintendo", "extensions": [".smc", ".sfc"]},
            "gameboy": {"name": "Game Boy", "extensions": [".gb", ".gbc"]},
            "gba": {"name": "Game Boy Advance", "extensions": [".gba"]},
            "genesis": {"name": "Sega Genesis", "extensions": [".md", ".gen"]}
        }
        
        for system, config in systems_config.items():
            system_dir = self.rom_dir / system
            games = []
            
            if system_dir.exists():
                for ext in config["extensions"]:
                    for rom_file in system_dir.glob(f"*{ext}"):
                        games.append({
                            "name": rom_file.stem.replace("_", " ").title(),
                            "filename": rom_file.name,
                            "system": system,
                            "size": self._format_file_size(rom_file.stat().st_size),
                            "path": str(rom_file.relative_to(self.project_root))
                        })
            
            systems[system] = games
        
        return json_response({
            "games": systems,
            "total_systems": len(systems_config),
            "total_games": sum(len(games) for games in systems.values())
        })
    
    async def get_games(self, request):
        """获取特定系统的游戏列表"""
        system = request.match_info['system']
        
        systems_data = await self.get_systems(request)
        systems_json = json.loads(systems_data.text)
        
        games = systems_json["games"].get(system, [])
        
        return json_response({
            "system": system,
            "games": games,
            "count": len(games)
        })
    async def launch_game(self, request):
        """启动游戏"""
        try:
            data = await request.json()
            system = data.get('system')
            game = data.get('game')
            save_slot = data.get('saveSlot', 1)
            cheats = data.get('cheats', False)
            
            logger.info(f"启动游戏请求: {system}/{game} (存档位置: {save_slot}, 金手指: {cheats})")
            
            # 这里应该调用实际的游戏启动逻辑
            # 目前只是模拟成功响应
            await asyncio.sleep(1)  # 模拟启动时间
            
            return json_response({
                "success": True,
                "message": f"游戏 {game} 已启动",
                "system": system,
                "game": game,
                "save_slot": save_slot,
                "cheats_enabled": cheats,
                "launch_time": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"启动游戏失败: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def get_settings(self, request):
        """获取设置"""
        settings_file = self.config_dir / "user_settings.json"
        
        default_settings = {
            "display": {
                "fullscreen": True,
                "resolution": "1920x1080",
                "vsync": True
            },
            "audio": {
                "enabled": True,
                "volume": 80,
                "sample_rate": 44100
            },
            "input": {
                "gamepad_enabled": True,
                "keyboard_enabled": True,
                "auto_detect_gamepad": True
            }
        }
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # 合并默认设置和保存的设置
                    for category, defaults in default_settings.items():
                        if category not in settings:
                            settings[category] = defaults
                        else:
                            for key, value in defaults.items():
                                if key not in settings[category]:
                                    settings[category][key] = value
                    return json_response(settings)
            except Exception as e:
                logger.error(f"读取设置文件失败: {e}")
        
        return json_response(default_settings)
    
    async def save_settings(self, request):
        """保存设置"""
        try:
            settings = await request.json()
            settings_file = self.config_dir / "user_settings.json"
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            logger.info("设置已保存")
            return json_response({
                "success": True,
                "message": "设置已保存",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def get_stats(self, request):
        """获取统计信息"""
        # 计算统计数据
        systems_data = await self.get_systems(request)
        systems_json = json.loads(systems_data.text)
        total_games = systems_json["total_games"]
        system_distribution = {}
        
        for system, games in systems_json["games"].items():
            if games:
                system_distribution[system] = len(games)
        
        return json_response({
            "total_games": total_games,
            "total_systems": len(system_distribution),
            "play_time": 0,  # 这里可以从持久化存储中获取
            "favorite_games": 0,
            "achievements": 0,
            "system_distribution": system_distribution,
            "last_updated": datetime.now().isoformat()
        })
    
    async def _count_available_systems(self) -> int:
        """计算可用的游戏系统数量"""
        count = 0
        systems = ["nes", "snes", "gameboy", "gba", "genesis"]
        
        for system in systems:
            system_dir = self.rom_dir / system
            if system_dir.exists() and any(system_dir.iterdir()):
                count += 1
        
        return count
    
    def _format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    async def start_server(self):
        """启动服务器"""
        app = self.create_app()
        
        logger.info(f"🎮 GamePlayer-Raspberry 服务器启动中...")
        logger.info(f"📁 项目根目录: {self.project_root}")
        logger.info(f"🌐 Web目录: {self.web_dir}")
        logger.info(f"💾 ROM目录: {self.rom_dir}")
        logger.info(f"⚙️ 配置目录: {self.config_dir}")
        logger.info(f"🚀 服务器将在端口 {self.port} 上启动")
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        logger.info(f"✅ 服务器已启动!")
        logger.info(f"🌐 访问地址: http://localhost:{self.port}")
        logger.info(f"📋 API状态: http://localhost:{self.port}/api/status")
        logger.info(f"🎯 按 Ctrl+C 停止服务器")
        
        try:
            # 保持服务器运行
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 正在停止服务器...")
            await runner.cleanup()
            logger.info("👋 服务器已停止")
async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GamePlayer-Raspberry Web服务器')
    parser.add_argument('--port', type=int, default=8080, help='服务器端口 (默认: 8080)')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        server = GamePlayerServer(port=args.port)
        await server.start_server()
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序异常: {e}")
        sys.exit(1)