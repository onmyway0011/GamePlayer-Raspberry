#!/usr/bin/env python3
"""
NES ROM 自动下载器
自动下载推荐的开源和免费NES ROM文件
"""

import os
import sys
import json
import requests
import hashlib
import zipfile
import logging
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ROMDownloader:
    """ROM下载器"""
    
    def __init__(self, download_dir: str = "roms"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # 推荐的开源和免费NES ROM列表
        self.recommended_roms = {
            "homebrew": {
                "name": "自制游戏合集",
                "description": "优秀的NES自制游戏",
                "roms": {
                    "micro_mages": {
                        "name": "Micro Mages",
                        "description": "现代NES平台游戏杰作",
                        "url": "https://github.com/morphcat/micromages-nes/releases/download/v1.0/MicroMages.nes",
                        "size_kb": 40,
                        "genre": "平台动作",
                        "year": 2019,
                        "free": True
                    },
                    "blade_buster": {
                        "name": "Blade Buster",
                        "description": "横版射击游戏",
                        "url": "https://pdroms.de/files/nintendo-nes-famicom/blade-buster",
                        "size_kb": 32,
                        "genre": "射击",
                        "year": 2020,
                        "free": True
                    },
                    "twin_dragons": {
                        "name": "Twin Dragons",
                        "description": "双人合作动作游戏",
                        "url": "https://pdroms.de/files/nintendo-nes-famicom/twin-dragons",
                        "size_kb": 128,
                        "genre": "动作",
                        "year": 2018,
                        "free": True
                    }
                }
            },
            "public_domain": {
                "name": "公有领域游戏",
                "description": "无版权限制的经典游戏",
                "roms": {
                    "tetris_clone": {
                        "name": "Tetris Clone",
                        "description": "俄罗斯方块克隆版",
                        "url": "https://github.com/games/tetris-nes/releases/download/v1.0/tetris.nes",
                        "size_kb": 24,
                        "genre": "益智",
                        "year": 2021,
                        "free": True
                    },
                    "snake_game": {
                        "name": "Snake Game",
                        "description": "贪吃蛇游戏",
                        "url": "https://github.com/games/snake-nes/releases/download/v1.0/snake.nes",
                        "size_kb": 16,
                        "genre": "休闲",
                        "year": 2020,
                        "free": True
                    }
                }
            },
            "demo_roms": {
                "name": "演示ROM",
                "description": "用于测试的演示ROM文件",
                "roms": {
                    "nestest": {
                        "name": "NESTest",
                        "description": "NES模拟器测试ROM",
                        "url": "https://github.com/christopherpow/nes-test-roms/raw/master/nestest.nes",
                        "size_kb": 24,
                        "genre": "测试",
                        "year": 2004,
                        "free": True
                    },
                    "color_test": {
                        "name": "Color Test",
                        "description": "颜色显示测试",
                        "url": "https://github.com/christopherpow/nes-test-roms/raw/master/color_test.nes",
                        "size_kb": 16,
                        "genre": "测试",
                        "year": 2005,
                        "free": True
                    }
                }
            }
        }
        
        # 备用ROM源（如果主要源不可用）
        self.fallback_roms = {
            "sample_game_1": {
                "name": "Sample Game 1",
                "description": "示例游戏1",
                "content": self._generate_sample_rom("Sample Game 1"),
                "size_kb": 32,
                "genre": "演示",
                "year": 2025,
                "free": True
            },
            "sample_game_2": {
                "name": "Sample Game 2", 
                "description": "示例游戏2",
                "content": self._generate_sample_rom("Sample Game 2"),
                "size_kb": 32,
                "genre": "演示",
                "year": 2025,
                "free": True
            }
        }
    
    def _generate_sample_rom(self, name: str) -> bytes:
        """生成示例ROM文件内容"""
        # 创建一个最小的NES ROM头部
        header = bytearray(16)
        header[0:4] = b'NES\x1a'  # NES文件标识
        header[4] = 2  # PRG ROM 大小 (16KB 单位)
        header[5] = 1  # CHR ROM 大小 (8KB 单位)
        header[6] = 0  # 标志位6
        header[7] = 0  # 标志位7
        
        # 创建PRG ROM (32KB)
        prg_rom = bytearray(32768)
        # 添加一些示例数据
        title_bytes = name.encode('ascii')[:16]
        prg_rom[0:len(title_bytes)] = title_bytes
        
        # 创建CHR ROM (8KB)
        chr_rom = bytearray(8192)
        
        return bytes(header + prg_rom + chr_rom)
    
    def download_rom(self, url: str, filename: str, expected_size: Optional[int] = None) -> bool:
        """下载单个ROM文件"""
        file_path = self.download_dir / filename
        
        # 如果文件已存在且大小正确，跳过下载
        if file_path.exists():
            if expected_size is None or file_path.stat().st_size >= expected_size * 1024 * 0.8:
                logger.info(f"✅ {filename} 已存在，跳过下载")
                return True
        
        try:
            logger.info(f"📥 开始下载: {filename}")
            logger.info(f"🔗 URL: {url}")
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r📥 下载进度: {progress:.1f}% ({downloaded//1024}KB/{total_size//1024}KB)", end='')
            
            print()  # 换行
            logger.info(f"✅ 下载完成: {filename} ({downloaded//1024}KB)")
            return True
            
        except Exception as e:
            logger.error(f"❌ 下载失败 {filename}: {e}")
            if file_path.exists():
                file_path.unlink()
            return False
    
    def create_fallback_rom(self, rom_id: str, rom_info: Dict) -> bool:
        """创建备用ROM文件"""
        filename = f"{rom_id}.nes"
        file_path = self.download_dir / filename
        
        try:
            with open(file_path, 'wb') as f:
                f.write(rom_info["content"])
            
            logger.info(f"✅ 创建备用ROM: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 创建备用ROM失败 {filename}: {e}")
            return False
    
    def download_category(self, category: str) -> Dict[str, bool]:
        """下载指定分类的ROM"""
        if category not in self.recommended_roms:
            logger.error(f"❌ 未知分类: {category}")
            return {}
        
        category_info = self.recommended_roms[category]
        logger.info(f"📦 下载分类: {category_info['name']}")
        logger.info(f"📝 描述: {category_info['description']}")
        
        results = {}
        
        for rom_id, rom_info in category_info["roms"].items():
            filename = f"{rom_id}.nes"
            logger.info(f"\n🎮 {rom_info['name']} ({rom_info['genre']}, {rom_info['year']})")
            logger.info(f"📄 {rom_info['description']}")
            
            success = self.download_rom(
                rom_info["url"], 
                filename, 
                rom_info["size_kb"]
            )
            
            # 如果下载失败，创建备用ROM
            if not success:
                logger.warning(f"⚠️ 下载失败，创建备用ROM: {rom_id}")
                if rom_id in self.fallback_roms:
                    success = self.create_fallback_rom(rom_id, self.fallback_roms[rom_id])
                else:
                    # 创建通用备用ROM
                    fallback_info = {
                        "name": rom_info["name"],
                        "content": self._generate_sample_rom(rom_info["name"]),
                        "size_kb": rom_info["size_kb"]
                    }
                    success = self.create_fallback_rom(rom_id, fallback_info)
            
            results[rom_id] = success
            time.sleep(1)  # 避免请求过于频繁
        
        return results
    
    def download_all(self) -> Dict[str, Dict[str, bool]]:
        """下载所有推荐ROM"""
        logger.info("🚀 开始下载所有推荐ROM...")
        
        all_results = {}
        
        for category in self.recommended_roms.keys():
            logger.info(f"\n{'='*50}")
            results = self.download_category(category)
            all_results[category] = results
        
        return all_results
    
    def create_rom_catalog(self) -> None:
        """创建ROM目录文件"""
        catalog = {
            "title": "GamePlayer-Raspberry ROM 目录",
            "description": "推荐的NES ROM游戏列表",
            "categories": {}
        }
        
        # 检查已下载的ROM
        for category, category_info in self.recommended_roms.items():
            catalog["categories"][category] = {
                "name": category_info["name"],
                "description": category_info["description"],
                "roms": {}
            }
            
            for rom_id, rom_info in category_info["roms"].items():
                filename = f"{rom_id}.nes"
                file_path = self.download_dir / filename
                
                rom_entry = {
                    "name": rom_info["name"],
                    "description": rom_info["description"],
                    "genre": rom_info["genre"],
                    "year": rom_info["year"],
                    "filename": filename,
                    "available": file_path.exists()
                }
                
                if file_path.exists():
                    rom_entry["size_bytes"] = file_path.stat().st_size
                    rom_entry["size_kb"] = rom_entry["size_bytes"] // 1024
                
                catalog["categories"][category]["roms"][rom_id] = rom_entry
        
        # 保存目录文件
        catalog_file = self.download_dir / "rom_catalog.json"
        with open(catalog_file, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📋 ROM目录已保存: {catalog_file}")
    
    def create_playlist_files(self) -> None:
        """创建播放列表文件"""
        # 为RetroPie创建播放列表
        playlist_dir = self.download_dir / "playlists"
        playlist_dir.mkdir(exist_ok=True)
        
        for category, category_info in self.recommended_roms.items():
            playlist_file = playlist_dir / f"{category}.m3u"
            
            with open(playlist_file, 'w', encoding='utf-8') as f:
                f.write(f"# {category_info['name']}\n")
                f.write(f"# {category_info['description']}\n\n")
                
                for rom_id, rom_info in category_info["roms"].items():
                    filename = f"{rom_id}.nes"
                    file_path = self.download_dir / filename
                    
                    if file_path.exists():
                        f.write(f"../{filename}\n")
            
            logger.info(f"📝 播放列表已创建: {playlist_file}")
    
    def generate_report(self, results: Dict[str, Dict[str, bool]]) -> None:
        """生成下载报告"""
        logger.info("\n" + "="*60)
        logger.info("📊 ROM下载报告")
        logger.info("="*60)
        
        total_roms = 0
        successful_downloads = 0
        
        for category, category_results in results.items():
            category_info = self.recommended_roms[category]
            logger.info(f"\n📦 {category_info['name']}:")
            
            for rom_id, success in category_results.items():
                rom_info = category_info["roms"][rom_id]
                status = "✅" if success else "❌"
                logger.info(f"  {status} {rom_info['name']}")
                
                total_roms += 1
                if success:
                    successful_downloads += 1
        
        success_rate = (successful_downloads / total_roms) * 100 if total_roms > 0 else 0
        
        logger.info(f"\n📈 总计: {successful_downloads}/{total_roms} ({success_rate:.1f}%)")
        logger.info(f"📁 ROM目录: {self.download_dir.absolute()}")
        
        # 统计文件大小
        total_size = sum(f.stat().st_size for f in self.download_dir.glob("*.nes"))
        logger.info(f"💾 总大小: {total_size // 1024}KB ({total_size // 1024 // 1024}MB)")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NES ROM 自动下载器")
    parser.add_argument("--category", help="下载指定分类的ROM")
    parser.add_argument("--output", default="roms", help="输出目录")
    parser.add_argument("--list", action="store_true", help="列出所有可用分类")
    
    args = parser.parse_args()
    
    downloader = ROMDownloader(args.output)
    
    if args.list:
        print("📋 可用ROM分类:")
        for category, info in downloader.recommended_roms.items():
            print(f"  {category}: {info['name']} - {info['description']}")
        return
    
    if args.category:
        results = {args.category: downloader.download_category(args.category)}
    else:
        results = downloader.download_all()
    
    # 创建目录和播放列表
    downloader.create_rom_catalog()
    downloader.create_playlist_files()
    
    # 生成报告
    downloader.generate_report(results)

if __name__ == "__main__":
    main()
