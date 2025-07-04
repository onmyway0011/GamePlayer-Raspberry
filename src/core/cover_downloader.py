#!/usr/bin/env python3
"""
游戏封面下载器
从网上下载游戏封面图片
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

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class CoverDownloader:
    """游戏封面下载器"""

    def __init__(self):
        """TODO: 添加文档字符串"""
        self.project_root = project_root
        self.covers_dir = self.project_root / "data" / "web" / "images" / "covers"
        self.covers_dir.mkdir(parents=True, exist_ok=True)

        # 创建系统子目录
        for system in ["nes", "snes", "gameboy", "gba", "genesis", "psx", "n64", "arcade"]:
            (self.covers_dir / system).mkdir(exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # 游戏封面URL映射
        self.cover_urls = {
            "nes": {
                "super_mario_bros": "https://upload.wikimedia.org/wikipedia/en/5/50/NES_Super_Mario_Bros.png",
                "zelda": "https://upload.wikimedia.org/wikipedia/en/4/41/Legend_of_zelda_cover_%28with_cartridge%29_gold.png",
                "metroid": "https://upload.wikimedia.org/wikipedia/en/3/3d/Metroid_boxart.jpg",
                "castlevania": "https://upload.wikimedia.org/wikipedia/en/5/51/Castlevania_1_box.jpg",
                "mega_man": "https://upload.wikimedia.org/wikipedia/en/d/d3/Mega_Man_1_box_artwork.jpg",
                "contra": "https://upload.wikimedia.org/wikipedia/en/7/75/Contra_cover.jpg",
                "duck_hunt": "https://upload.wikimedia.org/wikipedia/en/6/6a/Duck_Hunt_cover.jpg",
                "pac_man": "https://upload.wikimedia.org/wikipedia/en/5/59/Pac-Man_Plus_Flyer.png",
                "donkey_kong": "https://upload.wikimedia.org/wikipedia/en/8/8a/Donkey_Kong_arcade_flyer.jpg",
                "galaga": "https://upload.wikimedia.org/wikipedia/en/2/2a/Galaga_flyer.jpg"
            },
            "snes": {
                "super_mario_world": "https://upload.wikimedia.org/wikipedia/en/3/32/Super_Mario_World_Coverart.png",
                "chrono_trigger": "https://upload.wikimedia.org/wikipedia/en/a/a7/Chrono_Trigger.jpg",
                "super_metroid": "https://upload.wikimedia.org/wikipedia/en/e/e4/Super_Metroid_box_art.jpg",
                "final_fantasy_vi": "https://upload.wikimedia.org/wikipedia/en/8/8a/FF6_US_boxart.jpg",
                "zelda_link_to_past": "https://upload.wikimedia.org/wikipedia/en/2/21/The_Legend_of_Zelda_A_Link_to_the_Past_SNES_Game_Cover.jpg",
                "super_mario_kart": "https://upload.wikimedia.org/wikipedia/en/3/38/SuperMarioKart_box.jpg",
                "donkey_kong_country": "https://upload.wikimedia.org/wikipedia/en/c/c9/Donkey_Kong_Country_SNES_cover.jpg",
                "street_fighter_ii": "https://upload.wikimedia.org/wikipedia/en/2/2a/Street_Fighter_II_SNES_cover.jpg"
            },
            "gameboy": {
                "tetris": "https://upload.wikimedia.org/wikipedia/en/4/4a/Tetris_Boxshot.jpg",
                "pokemon_red": "https://upload.wikimedia.org/wikipedia/en/a/a6/Pok%C3%A9mon_Red_Version_box_art.jpg",
                "pokemon_blue": "https://upload.wikimedia.org/wikipedia/en/f/f4/Pok%C3%A9mon_Blue_Version_box_art.jpg",
                "zelda_links_awakening": "https://upload.wikimedia.org/wikipedia/en/6/6a/The_Legend_of_Zelda_Link%27s_Awakening_box_art.jpg",
                "super_mario_land": "https://upload.wikimedia.org/wikipedia/en/b/b8/Super_Mario_Land_box_art.jpg",
                "metroid_ii": "https://upload.wikimedia.org/wikipedia/en/9/93/Metroid_II_box_art.jpg"
            },
            "gba": {
                "pokemon_ruby": "https://upload.wikimedia.org/wikipedia/en/b/b2/Pok%C3%A9mon_Ruby_Version_box_art.jpg",
                "pokemon_sapphire": "https://upload.wikimedia.org/wikipedia/en/f/f7/Pok%C3%A9mon_Sapphire_Version_box_art.jpg",
                "fire_emblem": "https://upload.wikimedia.org/wikipedia/en/9/9d/Fire_Emblem_GBA_cover.jpg",
                "golden_sun": "https://upload.wikimedia.org/wikipedia/en/4/40/Golden_Sun_box.jpg",
                "advance_wars": "https://upload.wikimedia.org/wikipedia/en/5/5a/Advance_Wars_Coverart.png",
                "mario_kart_super_circuit": "https://upload.wikimedia.org/wikipedia/en/c/c1/Mario_Kart_Super_Circuit_box_art.jpg"
            },
            "genesis": {
                "sonic": "https://upload.wikimedia.org/wikipedia/en/b/ba/Sonic_the_Hedgehog_1_Genesis_box_art.jpg",
                "sonic_2": "https://upload.wikimedia.org/wikipedia/en/0/03/Sonic_the_Hedgehog_2_US_Genesis_box_art.jpg",
                "streets_of_rage": "https://upload.wikimedia.org/wikipedia/en/6/6d/Streets_of_Rage_cover.jpg",
                "golden_axe": "https://upload.wikimedia.org/wikipedia/en/4/48/Golden_Axe_cover.jpg",
                "phantasy_star_iv": "https://upload.wikimedia.org/wikipedia/en/c/c3/Phantasy_Star_IV_cover.jpg"
            }
        }

    def download_cover(self, system: str, game_id: str, url: str):
        """下载单个游戏封面"""
        try:
            cover_path = self.covers_dir / system / f"{game_id}.jpg"

            # 如果文件已存在，跳过下载
            if cover_path.exists():
                print(f"✅ 封面已存在: {system}/{game_id}")
                return True

            print(f"📥 下载封面: {system}/{game_id}")

            # 下载图片
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # 保存图片
            with open(cover_path, 'wb') as f:
                f.write(response.content)

            print(f"✅ 封面下载成功: {cover_path}")
            return True

        except Exception as e:
            print(f"❌ 下载封面失败 {system}/{game_id}: {e}")
            return False

    def download_all_covers(self) -> Dict[str, int]:
        """下载所有游戏封面"""
        print("🖼️ 开始下载游戏封面...")

        results = {}

        for system, games in self.cover_urls.items():
            print(f"\n📂 下载 {system.upper()} 游戏封面...")

            success_count = 0
            total_count = len(games)

            for game_id, url in games.items():
                if self.download_cover(system, game_id, url):
                    success_count += 1

                # 避免请求过于频繁
                time.sleep(0.5)

            results[system] = {
                "success": success_count,
                "total": total_count,
                "rate": f"{success_count/total_count*100:.1f}%"
            }

            print(f"📊 {system.upper()} 完成: {success_count}/{total_count} ({results[system]['rate']})")

        return results

    def get_cover_path(self, system: str, game_id: str) -> Optional[str]:
        """获取游戏封面路径"""
        cover_path = self.covers_dir / system / f"{game_id}.jpg"

        if cover_path.exists():
            # 返回相对于web根目录的路径
            return f"/static/images/covers/{system}/{game_id}.jpg"

        return None

    def create_placeholder_cover(self, system: str, game_id: str, game_name: str) -> str:
        """创建占位符封面"""
        try:
            from PIL import Image, ImageDraw, ImageFont

            # 创建占位符图片
            img = Image.new('RGB', (300, 400), color='#667eea')
            draw = ImageDraw.Draw(img)

            # 尝试使用系统字体
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
                small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()

            # 绘制游戏名称
            text_lines = self._wrap_text(game_name, 20)
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
            placeholder_path = self.covers_dir / system / f"{game_id}.jpg"
            img.save(placeholder_path, 'JPEG', quality=85)

            return f"/static/images/covers/{system}/{game_id}.jpg"

        except Exception as e:
            print(f"⚠️ 创建占位符失败: {e}")
            return "/static/images/placeholder.jpg"

    def _wrap_text(self, text: str, max_length: int) -> List[str]:
        """文本换行"""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(f"{current_line} " + word) <= max_length:
                current_line += " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def search_cover_online(self, game_name: str, system: str) -> Optional[str]:
        """在线搜索游戏封面"""
        try:
            # 使用多个搜索源
            search_engines = [
                f"https://www.mobygames.com/search/quick?q={quote(game_name)}",
                f"https://www.igdb.com/search?type=1&q={quote(game_name)}",
                f"https://thegamesdb.net/search.php?name={quote(game_name)}"
            ]

            # 这里可以实现更复杂的搜索逻辑
            # 目前返回None，使用预定义的URL
            return None

        except Exception as e:
            print(f"⚠️ 在线搜索封面失败: {e}")
            return None

    def generate_cover_report(self) -> Dict:
        """生成封面下载报告"""
        report = {
            "timestamp": time.time(),
            "systems": {},
            "total_covers": 0,
            "total_games": 0
        }

        for system in ["nes", "snes", "gameboy", "gba", "genesis"]:
            system_dir = self.covers_dir / system

            if system_dir.exists():
                covers = list(system_dir.glob("*.jpg"))
                games_with_urls = len(self.cover_urls.get(system, {}))

                report["systems"][system] = {
                    "downloaded_covers": len(covers),
                    "available_urls": games_with_urls,
                    "coverage": f"{len(covers)/max(games_with_urls, 1)*100:.1f}%"
                }

                report["total_covers"] += len(covers)
                report["total_games"] += games_with_urls

        report["overall_coverage"] = f"{report['total_covers']/max(report['total_games'], 1)*100:.1f}%"

        return report


def main():
    """主函数"""
    downloader = CoverDownloader()

    print("🖼️ GamePlayer-Raspberry 游戏封面下载器")
    print("=" * 50)

    # 下载所有封面
    results = downloader.download_all_covers()

    # 生成报告
    report = downloader.generate_cover_report()

    print(f"\n📊 下载完成报告:")
    print(f"总封面数: {report['total_covers']}")
    print(f"总游戏数: {report['total_games']}")
    print(f"覆盖率: {report['overall_coverage']}")

    for system, stats in report["systems"].items():
        print(f"  {system.upper()}: {stats['downloaded_covers']}/{stats['available_urls']} ({stats['coverage']})")

if __name__ == "__main__":
    main()
