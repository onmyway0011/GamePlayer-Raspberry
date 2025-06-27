#!/usr/bin/env python3
"""
增强版NES游戏启动器
支持自动启动、存档管理、游戏切换、Web界面等功能
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
import threading
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.core.save_manager import SaveManager
    from src.core.cheat_manager import CheatManager
    from src.core.device_manager import DeviceManager
    from src.core.config_manager import ConfigManager
    from src.core.audio_manager import AudioManager
except (ImportError, Exception) as e:
    # 如果核心模块不存在或初始化失败，创建简单的替代类
    print(f"⚠️ 核心模块加载失败: {e}")
    print("🔄 使用简化模式运行...")
    class SaveManager:
        def __init__(self, *args, **kwargs):
            """TODO: Add docstring"""
            pass
        def load_game(self, *args, **kwargs):
            """TODO: Add docstring"""
            return None
        def save_game(self, *args, **kwargs):
            """TODO: Add docstring"""
            return True

    class CheatManager:
        def __init__(self, *args, **kwargs):
            """TODO: Add docstring"""
            pass
        def enable_cheats(self, *args, **kwargs):
            """TODO: Add docstring"""
            return True

    class DeviceManager:
        def __init__(self, *args, **kwargs):
            """TODO: Add docstring"""
            pass
        def detect_devices(self):
            """TODO: Add docstring"""
            return []

    class ConfigManager:
        def __init__(self, *args, **kwargs):
            """TODO: Add docstring"""
            pass
        def get(self, key, default=None):
            """TODO: Add docstring"""
            return default

    class AudioManager:
        def __init__(self, *args, **kwargs):
            """TODO: Add docstring"""
            pass
        def load_audio_config(self):
            """TODO: Add docstring"""
            pass
        def create_default_sounds(self):
            """TODO: Add docstring"""
            pass
        def play_sound(self, *args, **kwargs):
            """TODO: Add docstring"""
            return True
        def play_music(self, *args, **kwargs):
            """TODO: Add docstring"""
            return True
        def stop_music(self):
            """TODO: Add docstring"""
            pass
        def set_master_volume(self, volume):
            """TODO: Add docstring"""
            pass

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/gameplayer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnhancedGameLauncher:
    """增强版游戏启动器"""

    def __init__(self, roms_dir: str = None, autostart: bool = False):
        """TODO: Add docstring"""
        self.project_root = Path(__file__).parent.parent.parent
        self.roms_dir = Path(roms_dir) if roms_dir else self.project_root / "data" / "roms" / "nes"
        self.saves_dir = self.project_root / "data" / "saves"
        self.web_dir = self.project_root / "data" / "web"
        self.autostart = autostart

        # 创建必要目录
        self.roms_dir.mkdir(parents=True, exist_ok=True)
        self.saves_dir.mkdir(parents=True, exist_ok=True)
        self.web_dir.mkdir(parents=True, exist_ok=True)

        # 初始化管理器
        self.save_manager = SaveManager(str(self.saves_dir))
        self.cheat_manager = CheatManager()
        self.device_manager = DeviceManager()
        self.config_manager = ConfigManager()
        self.audio_manager = AudioManager(str(self.project_root / "data" / "audio"))

        # 游戏列表
        self.games = []
        self.current_game = None
        self.web_server = None

        logger.info("🎮 增强版游戏启动器初始化完成")

        # 显示自动启用的金手指
        self.show_auto_cheats_info()

    def show_auto_cheats_info(self):
        """显示自动启用的金手指信息"""
        try:
            logger.info("🎯 金手指自动启用配置:")

            # 显示各系统的自动金手指
            systems = ["nes", "snes", "gb", "gba", "genesis"]
            for system in systems:
                auto_cheats = self.cheat_manager.get_auto_enable_cheats(system)
                if auto_cheats:
                    system_info = self.cheat_manager.get_system_cheats(system)
                    system_name = system_info.get("system_name", system.upper()) if system_info else system.upper()
                    logger.info(f"  📱 {system_name}:")
                    for cheat in auto_cheats:
                        logger.info(f"    ✅ {cheat}")
                else:
                    logger.info(f"  📱 {system.upper()}: 无自动金手指")

            logger.info("💡 这些金手指将在游戏启动时自动启用")

        except Exception as e:
            logger.error(f"❌ 显示金手指信息失败: {e}")

    def scan_games(self) -> List[Dict]:
        """扫描游戏ROM文件"""
        logger.info(f"🔍 扫描游戏目录: {self.roms_dir}")

        games = []
        rom_files = list(self.roms_dir.glob("*.nes"))

        for rom_file in rom_files:
            game_info = {
                "id": rom_file.stem,
                "title": rom_file.stem.replace("_", " ").title(),
                "path": str(rom_file),
                "size": rom_file.stat().st_size,
                "has_save": self.has_save_file(rom_file.stem),
                "last_played": self.get_last_played(rom_file.stem)
            }
            games.append(game_info)

        # 按最后游玩时间排序
        games.sort(key=lambda x: x.get("last_played", 0), reverse=True)

        logger.info(f"✅ 找到 {len(games)} 个游戏")
        return games

    def has_save_file(self, game_id: str):
        """检查是否有存档文件"""
        save_files = list(self.saves_dir.glob(f"{game_id}_*.sav"))
        return len(save_files) > 0

    def get_last_played(self, game_id: str) -> float:
        """获取最后游玩时间"""
        try:
            info_file = self.saves_dir / f"{game_id}_info.json"
            if info_file.exists():
                with open(info_file, 'r') as f:
                    info = json.load(f)
                    return info.get("last_played", 0)
        except:
            pass
        return 0

    def update_last_played(self, game_id: str):
        """更新最后游玩时间"""
        try:
            info_file = self.saves_dir / f"{game_id}_info.json"
            info = {}
            if info_file.exists():
                with open(info_file, 'r') as f:
                    info = json.load(f)

            info["last_played"] = time.time()
            info["play_count"] = info.get("play_count", 0) + 1

            with open(info_file, 'w') as f:
                json.dump(info, f, indent=2)
        except Exception as e:
            logger.error(f"❌ 更新游玩时间失败: {e}")

    def start_game(self, game_id: str, load_save: bool = True):
        """启动游戏"""
        logger.info(f"🎮 启动游戏: {game_id}")

        # 查找游戏文件
        game = None
        for g in self.games:
            if g["id"] == game_id:
                game = g
                break

        if not game:
            logger.error(f"❌ 找不到游戏: {game_id}")
            return False

        try:
            # 更新最后游玩时间
            self.update_last_played(game_id)

            # 自动启用金手指
            logger.info("🎯 正在自动启用金手指...")
            enabled_count = self.cheat_manager.auto_enable_cheats_for_game("nes", game_id)
            if enabled_count > 0:
                logger.info(f"✅ 已自动启用 {enabled_count} 个金手指")
            else:
                logger.info("ℹ️ 没有需要自动启用的金手指")

            # 加载存档（如果存在且要求加载）
            if load_save and game["has_save"]:
                save_data = self.save_manager.load_game(game["path"])
                if save_data:
                    logger.info("💾 已加载游戏存档")

            # 启动游戏
            self.current_game = game_id

            # 使用不同的模拟器启动游戏
            success = self._launch_with_emulator(game["path"])

            if success:
                logger.info(f"✅ 游戏 {game_id} 启动成功")
                return True
            else:
                logger.error(f"❌ 游戏 {game_id} 启动失败")
                return False

        except Exception as e:
            logger.error(f"❌ 启动游戏失败: {e}")
            return False

    def _launch_with_emulator(self, rom_path: str):
        """使用模拟器启动游戏"""
        emulators = [
            # RetroArch
            ["retroarch", "-L", "/opt/retropie/libretrocores/lr-nestopia/nestopia_libretro.so", rom_path],
            # Nestopia
            ["nestopia", rom_path],
            # FCEUX
            ["fceux", rom_path],
            # 简单的Python游戏（如果其他都不可用）
            ["python3", str(self.project_root / "src" / "scripts" / "run_nes_game.py"), rom_path]
        ]

        for emulator_cmd in emulators:
            try:
                logger.info(f"🎯 尝试启动器: {emulator_cmd[0]}")

                # 检查命令是否存在
                if subprocess.run(["which", emulator_cmd[0]], capture_output=True).returncode != 0:
                    continue

                # 启动游戏
                process = subprocess.Popen(
                    emulator_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                # 等待一下看是否成功启动
                time.sleep(2)
                if process.poll() is None:  # 进程还在运行
                    logger.info(f"✅ 使用 {emulator_cmd[0]} 启动成功")

                    # 等待游戏结束
                    process.wait()

                    # 游戏结束后自动保存
                    self._auto_save_game()

                    return True

            except Exception as e:
                logger.warning(f"⚠️ 启动器 {emulator_cmd[0]} 失败: {e}")
                continue

        logger.error("❌ 所有启动器都失败了")
        return False

    def _auto_save_game(self):
        """自动保存游戏"""
        if self.current_game:
            try:
                # 这里应该从模拟器获取游戏状态
                # 简化版本：只记录游戏时间
                game_state = {
                    "game_time": time.time(),
                    "auto_save": True
                }

                game_path = None
                for game in self.games:
                    if game["id"] == self.current_game:
                        game_path = game["path"]
                        break

                if game_path:
                    self.save_manager.save_game(game_path, game_state)
                    logger.info("💾 游戏自动保存完成")

            except Exception as e:
                logger.error(f"❌ 自动保存失败: {e}")

    def start_web_server(self, port: int = 8080):
        """启动Web服务器"""
        try:
            # 创建Web界面文件
            self._create_web_interface()

            # 启动HTTP服务器，直接服务data/web目录
            web_dir = Path("data/web")
            web_dir.mkdir(parents=True, exist_ok=True)

            class CustomHandler(SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    """TODO: Add docstring"""
                    super().__init__(*args, directory=str(web_dir), **kwargs)

            self.web_server = socketserver.TCPServer(("", port), CustomHandler)
            logger.info(f"🌐 Web服务器启动: http://localhost:{port}")

            # 在新线程中运行服务器
            server_thread = threading.Thread(target=self.web_server.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            return True

        except Exception as e:
            logger.error(f"❌ Web服务器启动失败: {e}")
            return False

    def _create_web_interface(self):
        """创建Web界面文件"""
        # 确保Web目录存在
        web_dir = Path("data/web")
        web_dir.mkdir(parents=True, exist_ok=True)

        # 生成游戏数据JSON
        games_json = json.dumps(self.games, indent=2)

        with open(web_dir / "games.json", "w") as f:
            f.write(games_json)

        logger.info("🌐 Web界面文件已创建")

        logger.info("🌐 Web界面文件已创建")

    def run_autostart(self):
        """自动启动模式"""
        logger.info("🚀 自动启动模式")

        # 扫描游戏
        self.games = self.scan_games()

        if not self.games:
            logger.warning("⚠️ 没有找到游戏文件")
            return

        # 启动Web服务器
        self.start_web_server()

        # 检测设备
        devices = self.device_manager.detect_devices()
        logger.info(f"🎮 检测到设备: {len(devices)} 个")

        # 如果有游戏，自动启动最近玩的游戏
        if self.games:
            recent_game = self.games[0]  # 已按最后游玩时间排序

            if recent_game["has_save"]:
                logger.info(f"🎯 自动继续游戏: {recent_game['title']}")
                self.start_game(recent_game["id"], load_save=True)
            else:
                logger.info(f"🎯 自动开始新游戏: {recent_game['title']}")
                self.start_game(recent_game["id"], load_save=False)
        else:
            logger.info("⚠️ 没有找到游戏，只启动Web界面")

        # 保持Web服务器运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("👋 自动启动模式退出")

    def run_interactive(self):
        """交互模式"""
        logger.info("🎮 交互模式")

        # 扫描游戏
        self.games = self.scan_games()

        if not self.games:
            print("❌ 没有找到游戏文件")
            return

        # 启动Web服务器
        self.start_web_server()

        # 显示游戏列表
        print("\n🎮 可用游戏:")
        for i, game in enumerate(self.games):
            save_indicator = "💾" if game["has_save"] else "🆕"
            print(f"  {i+1}. {save_indicator} {game['title']}")

        print(f"\n🌐 Web界面: http://localhost:8080/game_switcher/")

        # 用户选择
        while True:
            try:
                choice = input("\n请选择游戏编号 (或输入 'q' 退出): ").strip()

                if choice.lower() == 'q':
                    break

                game_index = int(choice) - 1
                if 0 <= game_index < len(self.games):
                    game = self.games[game_index]

                    # 询问是否加载存档
                    load_save = False
                    if game["has_save"]:
                        load_choice = input("是否加载存档? (y/n): ").strip().lower()
                        load_save = load_choice == 'y'

                    self.start_game(game["id"], load_save)
                else:
                    print("❌ 无效的选择")

            except (ValueError, KeyboardInterrupt):
                break

        print("👋 再见！")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="增强版NES游戏启动器")
    parser.add_argument("--roms-dir", help="ROM文件目录")
    parser.add_argument("--autostart", action="store_true", help="自动启动模式")
    parser.add_argument("--web-only", action="store_true", help="只启动Web服务器")
    parser.add_argument("--port", type=int, default=8080, help="Web服务器端口")

    args = parser.parse_args()

    # 创建启动器
    launcher = EnhancedGameLauncher(
        roms_dir=args.roms_dir,
        autostart=args.autostart
    )

    try:
        if args.web_only:
            # 只启动Web服务器
            launcher.games = launcher.scan_games()
            launcher.start_web_server(args.port)
            print(f"🌐 Web服务器运行在: http://localhost:{args.port}/game_switcher/")
            print("按 Ctrl+C 停止服务器")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 服务器已停止")

        elif args.autostart:
            # 自动启动模式
            launcher.run_autostart()
        else:
            # 交互模式
            launcher.run_interactive()

    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        logger.error(f"❌ 程序运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
