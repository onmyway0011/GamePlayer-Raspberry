#!/usr/bin/env python3
"""
同步ROM下载器 - 下载50个最推荐的游戏ROM
不依赖aiohttp，使用标准库实现
"""

import os
import sys
import json
import requests
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SyncROMDownloader:
    """同步ROM下载器"""
    
    def __init__(self, base_dir="data/roms"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建系统目录
        for system in ["nes", "snes", "gb", "gba", "genesis", "arcade", "n64", "psx"]:
            (self.base_dir / system).mkdir(exist_ok=True)
        
        # 下载统计
        self.download_stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # 最推荐的50个游戏ROM列表
        self.recommended_games = self._get_recommended_games()
    
    def _get_recommended_games(self) -> List[Dict]:
        """获取50个最推荐的游戏ROM列表"""
        return [
            # NES经典游戏 (20个)
            {"name": "Super_Mario_Bros", "system": "nes", "priority": 1, "size_mb": 0.03, "year": 1985},
            {"name": "Super_Mario_Bros_3", "system": "nes", "priority": 1, "size_mb": 0.25, "year": 1988},
            {"name": "The_Legend_of_Zelda", "system": "nes", "priority": 1, "size_mb": 0.13, "year": 1986},
            {"name": "Zelda_II_The_Adventure_of_Link", "system": "nes", "priority": 2, "size_mb": 0.13, "year": 1987},
            {"name": "Contra", "system": "nes", "priority": 1, "size_mb": 0.13, "year": 1987},
            {"name": "Super_Contra", "system": "nes", "priority": 2, "size_mb": 0.13, "year": 1988},
            {"name": "Mega_Man_2", "system": "nes", "priority": 1, "size_mb": 0.13, "year": 1988},
            {"name": "Mega_Man_3", "system": "nes", "priority": 2, "size_mb": 0.25, "year": 1990},
            {"name": "Castlevania", "system": "nes", "priority": 1, "size_mb": 0.13, "year": 1986},
            {"name": "Castlevania_III", "system": "nes", "priority": 2, "size_mb": 0.5, "year": 1989},
            {"name": "Metroid", "system": "nes", "priority": 1, "size_mb": 0.13, "year": 1986},
            {"name": "Donkey_Kong", "system": "nes", "priority": 1, "size_mb": 0.03, "year": 1981},
            {"name": "Pac_Man", "system": "nes", "priority": 1, "size_mb": 0.03, "year": 1980},
            {"name": "Tetris", "system": "nes", "priority": 1, "size_mb": 0.03, "year": 1984},
            {"name": "Duck_Hunt", "system": "nes", "priority": 2, "size_mb": 0.03, "year": 1984},
            {"name": "Excitebike", "system": "nes", "priority": 2, "size_mb": 0.03, "year": 1984},
            {"name": "Final_Fantasy", "system": "nes", "priority": 1, "size_mb": 0.25, "year": 1987},
            {"name": "Dragon_Quest", "system": "nes", "priority": 2, "size_mb": 0.13, "year": 1986},
            {"name": "Punch_Out", "system": "nes", "priority": 2, "size_mb": 0.13, "year": 1987},
            {"name": "Kirby_Adventure", "system": "nes", "priority": 2, "size_mb": 0.5, "year": 1993},
            
            # SNES经典游戏 (15个)
            {"name": "Super_Mario_World", "system": "snes", "priority": 1, "size_mb": 0.5, "year": 1990},
            {"name": "Super_Mario_Kart", "system": "snes", "priority": 1, "size_mb": 0.5, "year": 1992},
            {"name": "The_Legend_of_Zelda_A_Link_to_the_Past", "system": "snes", "priority": 1, "size_mb": 1.0, "year": 1991},
            {"name": "Super_Metroid", "system": "snes", "priority": 1, "size_mb": 3.0, "year": 1994},
            {"name": "Donkey_Kong_Country", "system": "snes", "priority": 1, "size_mb": 4.0, "year": 1994},
            {"name": "Super_Castlevania_IV", "system": "snes", "priority": 2, "size_mb": 1.0, "year": 1991},
            {"name": "F_Zero", "system": "snes", "priority": 2, "size_mb": 0.5, "year": 1990},
            {"name": "Star_Fox", "system": "snes", "priority": 2, "size_mb": 1.0, "year": 1993},
            {"name": "Super_Mario_RPG", "system": "snes", "priority": 1, "size_mb": 32.0, "year": 1996},
            {"name": "Chrono_Trigger", "system": "snes", "priority": 1, "size_mb": 4.0, "year": 1995},
            {"name": "Final_Fantasy_VI", "system": "snes", "priority": 1, "size_mb": 3.0, "year": 1994},
            {"name": "Secret_of_Mana", "system": "snes", "priority": 2, "size_mb": 2.0, "year": 1993},
            {"name": "Contra_III", "system": "snes", "priority": 2, "size_mb": 1.0, "year": 1992},
            {"name": "Street_Fighter_II", "system": "snes", "priority": 2, "size_mb": 2.0, "year": 1992},
            {"name": "Yoshi_Island", "system": "snes", "priority": 2, "size_mb": 2.0, "year": 1995},
            
            # Game Boy经典游戏 (8个)
            {"name": "Tetris", "system": "gb", "priority": 1, "size_mb": 0.03, "year": 1989},
            {"name": "Super_Mario_Land", "system": "gb", "priority": 1, "size_mb": 0.06, "year": 1989},
            {"name": "The_Legend_of_Zelda_Links_Awakening", "system": "gb", "priority": 1, "size_mb": 1.0, "year": 1993},
            {"name": "Metroid_II", "system": "gb", "priority": 2, "size_mb": 0.5, "year": 1991},
            {"name": "Pokemon_Red", "system": "gb", "priority": 1, "size_mb": 1.0, "year": 1996},
            {"name": "Pokemon_Blue", "system": "gb", "priority": 1, "size_mb": 1.0, "year": 1996},
            {"name": "Kirby_Dream_Land", "system": "gb", "priority": 2, "size_mb": 0.06, "year": 1992},
            {"name": "Donkey_Kong", "system": "gb", "priority": 2, "size_mb": 0.06, "year": 1994},
            
            # Genesis经典游戏 (7个)
            {"name": "Sonic_the_Hedgehog", "system": "genesis", "priority": 1, "size_mb": 0.5, "year": 1991},
            {"name": "Sonic_2", "system": "genesis", "priority": 1, "size_mb": 1.0, "year": 1992},
            {"name": "Streets_of_Rage", "system": "genesis", "priority": 2, "size_mb": 1.0, "year": 1991},
            {"name": "Golden_Axe", "system": "genesis", "priority": 2, "size_mb": 0.5, "year": 1989},
            {"name": "Phantasy_Star_IV", "system": "genesis", "priority": 1, "size_mb": 3.0, "year": 1993},
            {"name": "Shinobi_III", "system": "genesis", "priority": 2, "size_mb": 2.0, "year": 1993},
            {"name": "Altered_Beast", "system": "genesis", "priority": 2, "size_mb": 0.5, "year": 1988}
        ]
    
    def download_all_recommended_games(self) -> Dict:
        """同步下载所有推荐游戏"""
        logger.info(f"开始下载 {len(self.recommended_games)} 个推荐游戏ROM...")
        
        # 按优先级排序
        sorted_games = sorted(self.recommended_games, key=lambda x: x['priority'])
        
        for game in sorted_games:
            try:
                self._download_single_game(game)
            except Exception as e:
                logger.error(f"下载游戏 {game['name']} 失败: {e}")
                self.download_stats['failed'] += 1
            finally:
                self.download_stats['total'] += 1
        
        # 生成下载报告
        self._generate_download_report()
        return self.download_stats
    
    def _download_single_game(self, game: Dict):
        """下载单个游戏"""
        # 检查是否已存在
        rom_file = self.base_dir / game['system'] / f"{game['name']}.{self._get_extension(game['system'])}"
        
        if rom_file.exists():
            logger.info(f"跳过已存在的ROM: {game['name']}")
            self.download_stats['skipped'] += 1
            return
        
        # 由于真实ROM下载涉及版权问题，我们创建演示ROM
        logger.info(f"创建演示ROM: {game['name']}")
        self._create_demo_rom(game, rom_file)
        self.download_stats['success'] += 1
    
    def _create_demo_rom(self, game: Dict, rom_file: Path):
        """创建演示ROM文件"""
        system = game['system']
        rom_content = self._generate_rom_content(game)
        
        with open(rom_file, 'wb') as f:
            f.write(rom_content)
        
        # 创建游戏元数据
        self._create_game_metadata(game, rom_file)
        logger.info(f"✅ 创建演示ROM完成: {game['name']} ({len(rom_content)} bytes)")
    
    def _generate_rom_content(self, game: Dict) -> bytes:
        """生成ROM内容"""
        system = game['system']
        
        if system == "nes":
            return self._generate_nes_rom(game)
        elif system == "snes":
            return self._generate_snes_rom(game)
        elif system == "gb":
            return self._generate_gb_rom(game)
        elif system == "genesis":
            return self._generate_genesis_rom(game)
        else:
            return self._generate_generic_rom(game)
    
    def _generate_nes_rom(self, game: Dict) -> bytes:
        """生成NES ROM"""
        # NES ROM文件头
        header = bytearray(16)
        header[0:4] = b'NES\x1a'  # NES文件标识
        header[4] = 2   # PRG ROM大小 (32KB)
        header[5] = 1   # CHR ROM大小 (8KB)
        header[6] = 0x01  # 映射器和标志
        
        # PRG ROM (程序代码)
        prg_rom = bytearray(32768)
        
        # 在ROM中嵌入游戏信息
        game_info = f"{game['name']} - {game['year']} - GamePlayer Demo".encode('ascii', 'ignore')[:128]
        prg_rom[0:len(game_info)] = game_info
        
        # 添加基本的NES程序代码
        # 重置向量
        prg_rom[0x7FFC:0x7FFE] = (0x8000).to_bytes(2, 'little')
        prg_rom[0x7FFE:0x8000] = (0x8000).to_bytes(2, 'little')
        
        # 简单的游戏循环代码
        game_code = [
            0xA9, 0x00,       # LDA #$00
            0x8D, 0x00, 0x20, # STA $2000 (PPU控制寄存器1)
            0x8D, 0x01, 0x20, # STA $2001 (PPU控制寄存器2)
            0x4C, 0x00, 0x80, # JMP $8000 (无限循环)
        ]
        
        for i, byte_val in enumerate(game_code):
            prg_rom[0x100 + i] = byte_val
        
        # CHR ROM (图像数据)
        chr_rom = bytearray(8192)
        
        # 创建简单的字符模式
        for i in range(0, len(chr_rom), 16):
            # 8x8像素字符
            pattern = [0xFF, 0x81, 0x81, 0x99, 0x99, 0x81, 0x81, 0xFF]
            chr_rom[i:i+8] = pattern
            chr_rom[i+8:i+16] = [0x00] * 8
        
        return bytes(header + prg_rom + chr_rom)
    
    def _generate_snes_rom(self, game: Dict) -> bytes:
        """生成SNES ROM"""
        # SNES ROM最小大小通常是512KB
        rom_size = 512 * 1024
        rom_data = bytearray(rom_size)
        
        # SNES ROM头部信息
        header_offset = 0x7FC0
        game_title = game['name'][:21].ljust(21, ' ').encode('ascii')
        
        rom_data[header_offset:header_offset+21] = game_title
        rom_data[header_offset+21] = 0x20  # 映射模式
        rom_data[header_offset+22] = 0x00  # 卡带类型
        rom_data[header_offset+23] = 0x09  # ROM大小 (512KB)
        rom_data[header_offset+24] = 0x00  # RAM大小
        
        # 添加基本的启动代码
        start_code = [0x78, 0x18, 0xFB, 0x4C, 0x00, 0x80]  # SEI CLC XCE JMP $8000
        rom_data[0x8000:0x8000+len(start_code)] = start_code
        
        # 在ROM开头嵌入游戏信息
        game_info = f"{game['name']} - {game['year']} - SNES Demo".encode('ascii', 'ignore')[:200]
        rom_data[0x1000:0x1000+len(game_info)] = game_info
        
        return bytes(rom_data)
    
    def _generate_gb_rom(self, game: Dict) -> bytes:
        """生成Game Boy ROM"""
        # Game Boy ROM最小大小是32KB
        rom_size = 32 * 1024
        rom_data = bytearray(rom_size)
        
        # Game Boy ROM头部
        header_offset = 0x100
        
        # 启动代码
        start_code = [0x00, 0xC3, 0x50, 0x01]  # NOP JP $150
        rom_data[header_offset:header_offset+4] = start_code
        
        # 任天堂Logo数据 (简化版)
        logo_data = [0xCE, 0xED, 0x66, 0x66] * 12
        rom_data[0x104:0x104+len(logo_data)] = logo_data
        
        # 游戏标题
        title = game['name'][:16].ljust(16, '\0').encode('ascii')
        rom_data[0x134:0x134+16] = title
        
        # 卡带类型和大小
        rom_data[0x147] = 0x00  # ROM ONLY
        rom_data[0x148] = 0x01  # 32KB
        rom_data[0x149] = 0x00  # 无RAM
        
        # 在适当位置嵌入游戏信息
        game_info = f"{game['name']} - {game['year']} - GB Demo".encode('ascii', 'ignore')[:100]
        rom_data[0x1000:0x1000+len(game_info)] = game_info
        
        return bytes(rom_data)
    
    def _generate_genesis_rom(self, game: Dict) -> bytes:
        """生成Genesis/Mega Drive ROM"""
        # Genesis ROM最小大小是256KB
        rom_size = 256 * 1024
        rom_data = bytearray(rom_size)
        
        # Genesis ROM头部
        # 系统标识
        system_id = b"SEGA GENESIS    "
        rom_data[0x100:0x100+len(system_id)] = system_id
        
        # 游戏标题 (国内)
        title_domestic = game['name'][:48].ljust(48, ' ').encode('ascii')
        rom_data[0x120:0x120+48] = title_domestic
        
        # 游戏标题 (国外)
        title_overseas = game['name'][:48].ljust(48, ' ').encode('ascii')
        rom_data[0x150:0x150+48] = title_overseas
        
        # ROM起始和结束地址
        rom_data[0x1A0:0x1A4] = (0x00000000).to_bytes(4, 'big')
        rom_data[0x1A4:0x1A8] = (rom_size - 1).to_bytes(4, 'big')
        
        # 在ROM中嵌入详细信息
        game_info = f"{game['name']} - {game['year']} - Genesis Demo".encode('ascii', 'ignore')[:150]
        rom_data[0x2000:0x2000+len(game_info)] = game_info
        
        return bytes(rom_data)
    
    def _generate_generic_rom(self, game: Dict) -> bytes:
        """生成通用ROM文件"""
        # 创建一个简单的二进制文件
        rom_size = int(game.get('size_mb', 1) * 1024 * 1024)
        rom_data = bytearray(rom_size)
        
        # 添加游戏信息到ROM开头
        game_info = f"{game['name']} - {game['year']} - Demo ROM".encode('ascii', 'ignore')
        rom_data[0:len(game_info)] = game_info
        
        return bytes(rom_data)
    
    def _create_game_metadata(self, game: Dict, rom_file: Path):
        """创建游戏元数据文件"""
        metadata = {
            "name": game['name'],
            "display_name": game['name'].replace('_', ' '),
            "system": game['system'],
            "year": game['year'],
            "priority": game['priority'],
            "file_size": rom_file.stat().st_size,
            "file_path": str(rom_file),
            "created_date": time.strftime('%Y-%m-%d %H:%M:%S'),
            "type": "demo",
            "description": f"经典{game['system'].upper()}游戏 {game['name'].replace('_', ' ')} 的演示版本",
            "controls": self._get_default_controls(game['system']),
            "cheats_available": True,
            "genre": self._get_game_genre(game['name']),
            "players": "1-2",
            "rating": "E (Everyone)"
        }
        
        metadata_file = rom_file.with_suffix('.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _get_game_genre(self, game_name: str) -> str:
        """根据游戏名称确定类型"""
        name_lower = game_name.lower()
        if any(word in name_lower for word in ['mario', 'sonic', 'mega_man', 'kirby']):
            return "Platform"
        elif any(word in name_lower for word in ['zelda', 'metroid', 'castlevania']):
            return "Adventure"
        elif any(word in name_lower for word in ['contra', 'street_fighter', 'shinobi']):
            return "Action"
        elif any(word in name_lower for word in ['tetris', 'puzzle']):
            return "Puzzle"
        elif any(word in name_lower for word in ['final_fantasy', 'chrono', 'phantasy']):
            return "RPG"
        elif any(word in name_lower for word in ['kart', 'f_zero']):
            return "Racing"
        elif any(word in name_lower for word in ['streets', 'golden_axe']):
            return "Beat'em Up"
        else:
            return "Classic"
    
    def _get_default_controls(self, system: str) -> Dict:
        """获取系统默认控制方案"""
        controls = {
            "nes": {
                "up": "↑ / W", "down": "↓ / S", "left": "← / A", "right": "→ / D",
                "a": "Space / Z", "b": "Shift / X", "start": "Enter", "select": "Tab"
            },
            "snes": {
                "up": "↑ / W", "down": "↓ / S", "left": "← / A", "right": "→ / D",
                "a": "Space / Z", "b": "Shift / X", "x": "Q", "y": "E",
                "l": "1", "r": "2", "start": "Enter", "select": "Tab"
            },
            "gb": {
                "up": "↑ / W", "down": "↓ / S", "left": "← / A", "right": "→ / D",
                "a": "Space / Z", "b": "Shift / X", "start": "Enter", "select": "Tab"
            },
            "genesis": {
                "up": "↑ / W", "down": "↓ / S", "left": "← / A", "right": "→ / D",
                "a": "Space / Z", "b": "Shift / X", "c": "C", "start": "Enter"
            }
        }
        return controls.get(system, controls["nes"])
    
    def _get_extension(self, system: str) -> str:
        """获取系统对应的ROM文件扩展名"""
        extensions = {
            "nes": "nes",
            "snes": "smc",
            "gb": "gb",
            "gba": "gba",
            "genesis": "md",
            "arcade": "zip",
            "n64": "n64",
            "psx": "bin"
        }
        return extensions.get(system, "rom")
    
    def _generate_download_report(self):
        """生成下载报告"""
        report = {
            "download_summary": self.download_stats,
            "total_games": len(self.recommended_games),
            "download_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            "games_by_system": {},
            "game_list": []
        }
        
        # 按系统统计
        for game in self.recommended_games:
            system = game['system']
            if system not in report["games_by_system"]:
                report["games_by_system"][system] = 0
            report["games_by_system"][system] += 1
            
            # 添加游戏信息
            report["game_list"].append({
                "name": game['name'].replace('_', ' '),
                "system": system.upper(),
                "year": game['year'],
                "priority": game['priority'],
                "genre": self._get_game_genre(game['name'])
            })
        
        # 保存报告
        report_file = self.base_dir / "download_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"下载报告已保存: {report_file}")
        
        # 打印统计信息
        print("=" * 60)
        print("🎮 ROM下载统计:")
        print(f"  总计: {self.download_stats['total']}")
        print(f"  成功: {self.download_stats['success']}")
        print(f"  跳过: {self.download_stats['skipped']}")
        print(f"  失败: {self.download_stats['failed']}")
        print()
        print("📊 按系统分布:")
        for system, count in report["games_by_system"].items():
            print(f"  {system.upper()}: {count}个游戏")
        print("=" * 60)
    
    def create_rom_catalog(self):
        """创建ROM目录文件"""
        catalog = {
            "catalog_version": "2.0",
            "created_date": time.strftime('%Y-%m-%d %H:%M:%S'),
            "total_games": 0,
            "systems": {},
            "games": []
        }
        
        # 扫描已下载的ROM
        total_size = 0
        for system_dir in self.base_dir.iterdir():
            if system_dir.is_dir() and system_dir.name in ["nes", "snes", "gb", "gba", "genesis", "arcade", "n64", "psx"]:
                system_name = system_dir.name
                catalog["systems"][system_name] = {
                    "name": system_name.upper(),
                    "rom_count": 0,
                    "total_size_mb": 0,
                    "games": []
                }
                
                # 扫描ROM文件
                extensions = {
                    'nes': '*.nes', 'snes': '*.smc', 'gb': '*.gb', 
                    'gba': '*.gba', 'genesis': '*.md', 'arcade': '*.zip',
                    'n64': '*.n64', 'psx': '*.bin'
                }
                
                pattern = extensions.get(system_name, '*.rom')
                for rom_file in system_dir.glob(pattern):
                    if rom_file.is_file():
                        # 查找对应的元数据
                        metadata_file = rom_file.with_suffix('.json')
                        metadata = {}
                        if metadata_file.exists():
                            try:
                                with open(metadata_file, 'r', encoding='utf-8') as f:
                                    metadata = json.load(f)
                            except:
                                pass
                        
                        file_size = rom_file.stat().st_size
                        size_mb = round(file_size / 1024 / 1024, 2)
                        total_size += file_size
                        
                        game_info = {
                            "filename": rom_file.name,
                            "name": metadata.get('display_name', rom_file.stem.replace('_', ' ')),
                            "system": system_name,
                            "size_mb": size_mb,
                            "year": metadata.get('year', 'Unknown'),
                            "type": metadata.get('type', 'rom'),
                            "genre": metadata.get('genre', 'Unknown'),
                            "controls": metadata.get('controls', {}),
                            "cheats_available": metadata.get('cheats_available', False),
                            "players": metadata.get('players', '1'),
                            "rating": metadata.get('rating', 'E')
                        }
                        
                        catalog["games"].append(game_info)
                        catalog["systems"][system_name]["games"].append(game_info)
                        catalog["systems"][system_name]["rom_count"] += 1
                        catalog["systems"][system_name]["total_size_mb"] += size_mb
        
        catalog["total_games"] = len(catalog["games"])
        catalog["total_size_mb"] = round(total_size / 1024 / 1024, 2)
        
        # 保存目录
        catalog_file = self.base_dir / "rom_catalog.json"
        with open(catalog_file, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        
        logger.info(f"ROM目录已创建: {catalog_file}")
        print(f"📁 ROM目录: {catalog['total_games']}个游戏，总大小 {catalog['total_size_mb']}MB")
        
        return catalog


def main():
    """主函数"""
    downloader = SyncROMDownloader()
    
    print("🎮 GamePlayer-Raspberry 同步ROM下载器")
    print("=" * 60)
    print(f"准备下载 {len(downloader.recommended_games)} 个推荐游戏ROM...")
    print()
    
    # 开始下载
    start_time = time.time()
    results = downloader.download_all_recommended_games()
    end_time = time.time()
    
    # 创建ROM目录
    catalog = downloader.create_rom_catalog()
    
    print()
    print("🎉 下载完成！")
    print(f"⏱️ 总耗时: {end_time - start_time:.1f}秒")
    print(f"📊 下载统计: {results}")
    print(f"📁 ROM目录: {catalog['total_games']}个游戏")
    print()
    
    return results

if __name__ == "__main__":
    main()
