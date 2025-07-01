#!/usr/bin/env python3
"""
Bing图片搜索封面下载器
优先使用Bing搜索下载游戏封面
"""

import os
import sys
import json
import time
import requests
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote, urlencode
import re

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class BingCoverDownloader:
    """Bing图片搜索封面下载器"""

    def __init__(self):
        """TODO: Add docstring"""
        self.project_root = project_root
        self.covers_dir = self.project_root / "data" / "web" / "images" / "covers"
        self.covers_dir.mkdir(parents=True, exist_ok=True)

        # 创建系统子目录
        for system in ["nes", "snes", "gameboy", "gba", "genesis", "psx", "n64", "arcade"]:
            (self.covers_dir / system).mkdir(exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        # 游戏名称映射
        self.game_names = {
            "nes": {
                "super_mario_bros": "Super Mario Bros NES game cover",
                "zelda": "The Legend of Zelda NES game cover",
                "metroid": "Metroid NES game cover",
                "castlevania": "Castlevania NES game cover",
                "mega_man": "Mega Man NES game cover",
                "contra": "Contra NES game cover",
                "duck_hunt": "Duck Hunt NES game cover",
                "pac_man": "Pac-Man NES game cover",
                "donkey_kong": "Donkey Kong NES game cover",
                "galaga": "Galaga NES game cover"
            },
            "snes": {
                "super_mario_world": "Super Mario World SNES game cover",
                "chrono_trigger": "Chrono Trigger SNES game cover",
                "zelda_link_to_the_past": "The Legend of Zelda A Link to the Past SNES game cover",
                "super_metroid": "Super Metroid SNES game cover",
                "final_fantasy_vi": "Final Fantasy VI SNES game cover"
            },
            "gameboy": {
                "tetris": "Tetris Game Boy game cover",
                "pokemon_red": "Pokemon Red Version Game Boy game cover",
                "zelda_links_awakening": "The Legend of Zelda Link's Awakening Game Boy game cover",
                "metroid_ii": "Metroid II Return of Samus Game Boy game cover"
            },
            "gba": {
                "pokemon_ruby": "Pokemon Ruby Version GBA game cover",
                "zelda_minish_cap": "The Legend of Zelda The Minish Cap GBA game cover",
                "metroid_fusion": "Metroid Fusion GBA game cover",
                "mario_kart": "Mario Kart Super Circuit GBA game cover"
            },
            "genesis": {
                "sonic": "Sonic the Hedgehog Genesis game cover",
                "streets_of_rage": "Streets of Rage Genesis game cover",
                "phantasy_star": "Phantasy Star Genesis game cover"
            }
        }

        # 备用图片源
        self.fallback_sources = [
            "https://via.placeholder.com/300x400/667eea/ffffff?text={game_name}",
            "https://dummyimage.com/300x400/667eea/ffffff&text={game_name}"
        ]

    def search_bing_images(self, query: str, count: int = 10) -> List[str]:
        """使用Bing搜索图片"""
        print(f"🔍 Bing搜索: {query}")

        try:
            # Bing图片搜索URL
            search_url = "https://www.bing.com/images/search"
            params = {
                'q': query,
                'form': 'HDRSC2',
                'first': '1',
                'tsc': 'ImageBasicHover',
                'count': count
            }

            response = self.session.get(search_url, params=params, timeout=15)
            response.raise_for_status()

            # 解析图片URL
            image_urls = []

            # 使用正则表达式提取图片URL
            # Bing图片搜索结果中的图片URL模式
            patterns = [
                r'"murl":"([^"]+)"',  # 主要图片URL
                r'"turl":"([^"]+)"',  # 缩略图URL
                r'src="([^"]+\.(?:jpg|jpeg|png|gif|webp))"',  # 直接图片URL
            ]

            for pattern in patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    # 清理URL
                    url = match.replace('\\u002f', '/').replace('\\', '')

                    # 过滤有效的图片URL
                    if self.is_valid_image_url(url):
                        image_urls.append(url)

                        if len(image_urls) >= count:
                            break

                if len(image_urls) >= count:
                    break

            # 去重并限制数量
            unique_urls = list(dict.fromkeys(image_urls))[:count]

            print(f"  📊 找到 {len(unique_urls)} 个图片URL")
            return unique_urls

        except Exception as e:
            print(f"  ❌ Bing搜索失败: {e}")
            return []

    def is_valid_image_url(self, url: str):
        """验证是否为有效的图片URL"""
        if not url or len(url) < 10:
            return False

        # 检查URL格式
        if not url.startswith(('http://', 'https://')):
            return False

        # 检查图片扩展名
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        url_lower = url.lower()

        # 直接检查扩展名或包含图片相关参数
        if any(ext in url_lower for ext in image_extensions):
            return True

        # 检查是否包含图片相关关键词
        image_keywords = ['image', 'img', 'photo', 'picture', 'cover', 'box']
        if any(keyword in url_lower for keyword in image_keywords):
            return True

        return False

    def download_cover_from_bing(self, system: str, game_id: str, game_name: str):
        """从Bing搜索并下载游戏封面"""
        cover_path = self.covers_dir / system / f"{game_id}.jpg"

        # 如果文件已存在，跳过下载
        if cover_path.exists():
            print(f"✅ 封面已存在: {system}/{game_id}")
            return True

        print(f"📥 从Bing下载封面: {system}/{game_id}")

        # 搜索图片
        image_urls = self.search_bing_images(game_name, count=5)

        if not image_urls:
            print(f"  ⚠️ 未找到图片，使用备用方案")
            return self.create_placeholder_cover(system, game_id, game_name)

        # 尝试下载每个图片
        for i, url in enumerate(image_urls):
            try:
                print(f"  🔗 尝试下载 {i+1}/{len(image_urls)}: {url[:60]}...")

                response = self.session.get(url, timeout=15, stream=True)
                response.raise_for_status()

                # 检查内容类型
                content_type = response.headers.get('content-type', '').lower()
                if not any(img_type in content_type for img_type in ['image/', 'jpeg', 'jpg', 'png', 'gif']):
                    print(f"    ⚠️ 非图片内容: {content_type}")
                    continue

                # 读取内容
                content = response.content

                # 检查文件大小
                if len(content) < 1024:  # 小于1KB
                    print(f"    ⚠️ 文件太小: {len(content)} bytes")
                    continue

                if len(content) > 5242880:  # 大于5MB
                    print(f"    ⚠️ 文件太大: {len(content)} bytes")
                    continue

                # 保存图片
                with open(cover_path, 'wb') as f:
                    f.write(content)

                print(f"    ✅ 封面下载成功: {cover_path}")
                return True

            except Exception as e:
                print(f"    ❌ 下载失败: {e}")
                continue

        # 所有URL都失败，创建占位符
        print(f"  🎨 创建占位符封面...")
        return self.create_placeholder_cover(system, game_id, game_name)

    def create_placeholder_cover(self, system: str, game_id: str, game_name: str):
        """创建占位符封面"""
        try:
            # 确保系统目录存在
            system_dir = self.covers_dir / system
            system_dir.mkdir(parents=True, exist_ok=True)

            from PIL import Image, ImageDraw, ImageFont

            # 创建占位符图片
            img = Image.new('RGB', (300, 400), color='#667eea')
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
            text_lines = self._wrap_text(game_name.replace(' game cover', ''), 20)
            y_offset = 150

            for line in text_lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (300 - text_width) // 2
                draw.text((x, y_offset), line, fill='white', font=font)
                y_offset += 30

            # 绘制系统名称
            system_text = system.upper()
            bbox = draw.textbbox((0, 0), system_text, font=small_font)
            text_width = bbox[2] - bbox[0]
            x = (300 - text_width) // 2
            draw.text((x, 350), system_text, fill='#FFD700', font=small_font)

            # 保存占位符
            placeholder_path = system_dir / f"{game_id}.jpg"
            img.save(placeholder_path, 'JPEG', quality=85)

            print(f"    ✅ 占位符创建成功: {placeholder_path}")
            return True

        except Exception as e:
            print(f"    ❌ 创建占位符失败: {e}")
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
        print("🖼️ 开始从Bing下载游戏封面...")

        results = {}

        for system, games in self.game_names.items():
            print(f"\n📂 下载 {system.upper()} 游戏封面...")

            success_count = 0
            total_count = len(games)

            for game_id, game_name in games.items():
                if self.download_cover_from_bing(system, game_id, game_name):
                    success_count += 1

                # 避免请求过于频繁
                time.sleep(2)

            results[system] = {
                "success": success_count,
                "total": total_count,
                "rate": f"{success_count/total_count*100:.1f}%" if total_count > 0 else "0.0%"
            }

            print(f"📊 {system.upper()} 完成: {success_count}/{total_count} ({results[system]['rate']})")

        return results

    def download_single_cover(self, system: str, game_id: str):
        """下载单个游戏封面"""
        if system in self.game_names and game_id in self.game_names[system]:
            game_name = self.game_names[system][game_id]
            return self.download_cover_from_bing(system, game_id, game_name)
        else:
            # 生成默认搜索词
            game_name = f"{game_id.replace('_', ' ')} {system} game cover"
            return self.download_cover_from_bing(system, game_id, game_name)


def main():
    """主函数"""
    downloader = BingCoverDownloader()

    print("🖼️ Bing游戏封面下载器")
    print("=" * 50)

    # 下载所有封面
    results = downloader.download_all_covers()

    print(f"\n📊 下载完成报告:")
    total_success = 0
    total_games = 0

    for system, stats in results.items():
        success = stats["success"]
        total = stats["total"]
        rate = stats["rate"]

        total_success += success
        total_games += total

        print(f"  {system.upper()}: {success}/{total} ({rate})")

    overall_rate = f"{total_success/total_games*100:.1f}%" if total_games > 0 else "0.0%"
    print(f"\n🎯 总体成功率: {total_success}/{total_games} ({overall_rate})")

if __name__ == "__main__":
    main()
