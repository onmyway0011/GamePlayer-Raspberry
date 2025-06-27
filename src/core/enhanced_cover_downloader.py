#!/usr/bin/env python3
"""
增强的游戏封面下载器
使用多个可靠的图片源下载游戏封面
"""

import os
import sys
import json
import time
import requests
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote
import base64

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class EnhancedCoverDownloader:
    """增强的游戏封面下载器"""
    
    def __init__(self):
        self.project_root = project_root
        self.covers_dir = self.project_root / "data" / "web" / "images" / "covers"
        self.covers_dir.mkdir(parents=True, exist_ok=True)

        # 创建系统子目录
        for system in ["nes", "snes", "gameboy", "gba", "genesis", "psx", "n64", "arcade"]:
            (self.covers_dir / system).mkdir(exist_ok=True)

        # 加载配置
        self.config = self.load_config()

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.get('download_settings', {}).get('user_agent',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        })

        # 从配置加载封面源
        self.cover_sources = self.config.get('game_covers', {})

        # 备用图片源
        self.fallback_sources = [
            "https://via.placeholder.com/300x400/667eea/ffffff?text={game_name}",
            "https://dummyimage.com/300x400/667eea/ffffff&text={game_name}",
            "https://picsum.photos/300/400?random={game_id}"
        ]

    def load_config(self) -> Dict:
        """加载封面源配置"""
        config_file = self.project_root / "config" / "covers" / "cover_sources.json"

        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"✅ 封面配置加载成功: {config_file}")
                return config
            else:
                print(f"⚠️ 配置文件不存在: {config_file}")
                return self.get_default_config()
        except Exception as e:
            print(f"❌ 加载配置失败: {e}")
            return self.get_default_config()

    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "game_covers": {},
            "download_settings": {
                "timeout": 15,
                "max_retries": 3,
                "retry_delay": 2,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "max_file_size": 5242880,
                "min_file_size": 1024
            },
            "placeholder_settings": {
                "width": 300,
                "height": 400,
                "background_color": "#667eea",
                "text_color": "#ffffff",
                "accent_color": "#FFD700"
            }
        }
    
    def download_cover_from_sources(self, system: str, game_id: str, sources: List[str], game_name: str = "") -> bool:
        """从多个源尝试下载封面"""
        cover_path = self.covers_dir / system / f"{game_id}.jpg"

        # 如果文件已存在，跳过下载
        if cover_path.exists():
            print(f"✅ 封面已存在: {system}/{game_id}")
            return True

        print(f"📥 下载封面: {system}/{game_id}")

        # 获取下载设置
        download_settings = self.config.get('download_settings', {})
        timeout = download_settings.get('timeout', 15)
        max_file_size = download_settings.get('max_file_size', 5242880)
        min_file_size = download_settings.get('min_file_size', 1024)

        # 尝试每个源
        for i, url in enumerate(sources):
            try:
                print(f"  🔗 尝试源 {i+1}/{len(sources)}: {url[:50]}...")

                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()

                # 检查内容类型
                content_type = response.headers.get('content-type', '').lower()
                if not any(img_type in content_type for img_type in ['image/', 'jpeg', 'jpg', 'png', 'gif']):
                    print(f"  ⚠️ 非图片内容: {content_type}")
                    continue

                # 检查文件大小
                content_length = len(response.content)
                if content_length < min_file_size:
                    print(f"  ⚠️ 文件太小: {content_length} bytes")
                    continue

                if content_length > max_file_size:
                    print(f"  ⚠️ 文件太大: {content_length} bytes")
                    continue

                # 保存图片
                with open(cover_path, 'wb') as f:
                    f.write(response.content)

                print(f"  ✅ 封面下载成功: {cover_path}")
                return True

            except requests.exceptions.RequestException as e:
                print(f"  ❌ 下载失败: {e}")
                continue
            except Exception as e:
                print(f"  ❌ 处理失败: {e}")
                continue

        # 所有源都失败，尝试创建占位符
        print(f"  🎨 创建占位符封面...")
        return self.create_placeholder_cover(system, game_id, game_name or game_id.replace('_', ' ').title())
    
    def create_placeholder_cover(self, system: str, game_id: str, game_name: str) -> bool:
        """创建占位符封面"""
        try:
            # 确保系统目录存在
            system_dir = self.covers_dir / system
            system_dir.mkdir(parents=True, exist_ok=True)

            from PIL import Image, ImageDraw, ImageFont

            # 获取占位符设置
            placeholder_settings = self.config.get('placeholder_settings', {})
            width = placeholder_settings.get('width', 300)
            height = placeholder_settings.get('height', 400)
            bg_color = placeholder_settings.get('background_color', '#667eea')
            text_color = placeholder_settings.get('text_color', '#ffffff')
            accent_color = placeholder_settings.get('accent_color', '#FFD700')

            # 创建占位符图片
            img = Image.new('RGB', (width, height), color=bg_color)
            draw = ImageDraw.Draw(img)

            # 尝试使用系统字体
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
                small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", 24)
                    small_font = ImageFont.truetype("arial.ttf", 16)
                except:
                    font = ImageFont.load_default()
                    small_font = ImageFont.load_default()

            # 绘制游戏名称
            text_lines = self._wrap_text(game_name, 20)
            y_offset = height // 2 - 50

            for line in text_lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                draw.text((x, y_offset), line, fill=text_color, font=font)
                y_offset += 30

            # 绘制系统名称
            system_text = system.upper()
            bbox = draw.textbbox((0, 0), system_text, font=small_font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, height - 50), system_text, fill=accent_color, font=small_font)

            # 保存占位符
            placeholder_path = system_dir / f"{game_id}.jpg"
            img.save(placeholder_path, 'JPEG', quality=85)

            print(f"  ✅ 占位符创建成功: {placeholder_path}")
            return True

        except Exception as e:
            print(f"  ❌ 创建占位符失败: {e}")

            # 最后的备用方案：创建简单的文本文件
            try:
                system_dir = self.covers_dir / system
                system_dir.mkdir(parents=True, exist_ok=True)

                placeholder_path = system_dir / f"{game_id}.txt"
                with open(placeholder_path, 'w', encoding='utf-8') as f:
                    f.write(f"Game: {game_name}\nSystem: {system.upper()}\nCover not available")
                print(f"  📝 创建文本占位符: {placeholder_path}")
                return True
            except Exception as e2:
                print(f"  ❌ 创建文本占位符也失败: {e2}")
                return False
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """文本换行"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if len(' '.join(current_line + [word])) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def download_all_covers(self) -> Dict[str, Dict]:
        """下载所有游戏封面"""
        print("🖼️ 开始下载游戏封面（增强版）...")

        results = {}

        for system, games in self.cover_sources.items():
            print(f"\n📂 下载 {system.upper()} 游戏封面...")

            success_count = 0
            total_count = len(games)

            for game_id, game_data in games.items():
                # 处理新的配置结构
                if isinstance(game_data, dict):
                    game_name = game_data.get('name', game_id.replace('_', ' ').title())
                    sources = game_data.get('sources', [])
                else:
                    # 兼容旧格式
                    game_name = game_id.replace('_', ' ').title()
                    sources = game_data if isinstance(game_data, list) else []

                if sources and self.download_cover_from_sources(system, game_id, sources, game_name):
                    success_count += 1

                # 避免请求过于频繁
                time.sleep(1)

            results[system] = {
                "success": success_count,
                "total": total_count,
                "rate": f"{success_count/total_count*100:.1f}%" if total_count > 0 else "0.0%"
            }

            print(f"📊 {system.upper()} 完成: {success_count}/{total_count} ({results[system]['rate']})")

        return results
    
    def add_cover_source(self, system: str, game_id: str, urls: List[str]):
        """添加新的封面源"""
        if system not in self.cover_sources:
            self.cover_sources[system] = {}
        
        if game_id not in self.cover_sources[system]:
            self.cover_sources[system][game_id] = []
        
        self.cover_sources[system][game_id].extend(urls)
        print(f"✅ 为 {system}/{game_id} 添加了 {len(urls)} 个封面源")
    
    def get_cover_path(self, system: str, game_id: str) -> Optional[str]:
        """获取游戏封面路径"""
        cover_path = self.covers_dir / system / f"{game_id}.jpg"
        
        if cover_path.exists():
            return f"/static/images/covers/{system}/{game_id}.jpg"
        
        return None
    
    def generate_cover_report(self) -> Dict:
        """生成封面下载报告"""
        report = {
            "timestamp": time.time(),
            "systems": {},
            "total_covers": 0,
            "total_games": 0,
            "sources_used": len(self.cover_sources)
        }
        
        for system in ["nes", "snes", "gameboy", "gba", "genesis"]:
            system_dir = self.covers_dir / system
            
            if system_dir.exists():
                covers = list(system_dir.glob("*.jpg"))
                games_with_sources = len(self.cover_sources.get(system, {}))
                
                report["systems"][system] = {
                    "downloaded_covers": len(covers),
                    "available_sources": games_with_sources,
                    "coverage": f"{len(covers)/max(games_with_sources, 1)*100:.1f}%"
                }
                
                report["total_covers"] += len(covers)
                report["total_games"] += games_with_sources
        
        report["overall_coverage"] = f"{report['total_covers']/max(report['total_games'], 1)*100:.1f}%"
        
        return report

def main():
    """主函数"""
    downloader = EnhancedCoverDownloader()
    
    print("🖼️ GamePlayer-Raspberry 增强封面下载器")
    print("=" * 50)
    
    # 下载所有封面
    results = downloader.download_all_covers()
    
    # 生成报告
    report = downloader.generate_cover_report()
    
    print(f"\n📊 下载完成报告:")
    print(f"总封面数: {report['total_covers']}")
    print(f"总游戏数: {report['total_games']}")
    print(f"覆盖率: {report['overall_coverage']}")
    print(f"使用源数: {report['sources_used']}")
    
    for system, stats in report["systems"].items():
        print(f"  {system.upper()}: {stats['downloaded_covers']}/{stats['available_sources']} ({stats['coverage']})")

if __name__ == "__main__":
    main()
