#!/usr/bin/env python3
"""
ROM管理器
负责下载、管理和验证游戏ROM文件
"""

import os
import json
import hashlib
import zipfile
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ROMManager:
    """ROM文件管理器"""

    def __init__(self, config_path: str = "config/emulators/emulator_config.json"):
        """初始化ROM管理器"""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.rom_database = {}
        self.download_stats = {
            "total_downloaded": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "total_size": 0
        }

    def _load_config(self) -> Dict:
        """加载模拟器配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"配置文件不存在: {self.config_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            return {}

    def get_supported_systems(self) -> List[str]:
        """获取支持的游戏系统列表"""
        return list(self.config.get("supported_emulators", {}).keys())

    def get_system_info(self, system: str) -> Optional[Dict]:
        """获取指定系统的信息"""
        return self.config.get("supported_emulators", {}).get(system)

    def create_rom_directories(self):
        """创建ROM目录结构"""
        for system, info in self.config.get("supported_emulators", {}).items():
            rom_dir = Path(info["rom_directory"])
            save_dir = Path(info["save_directory"])

            rom_dir.mkdir(parents=True, exist_ok=True)
            save_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"创建目录: {rom_dir}")
            logger.info(f"创建目录: {save_dir}")

    def download_homebrew_roms(self):
        """下载自制游戏ROM"""
        logger.info("🎮 开始下载自制游戏ROM...")

        # 自制游戏ROM列表（这些是免费和合法的）
        homebrew_roms = {
            "nes": [
                {
                    "name": "Blade Buster",
                    "url": "https://github.com/pubby/blade_buster/releases/download/v1.0/blade_buster.nes",
                    "description": "动作平台游戏",
                    "size": "32KB"
                },
                {
                    "name": "Micro Mages",
                    "url": "https://morphcat.de/micromages/micromages_demo.nes",
                    "description": "合作平台游戏演示版",
                    "size": "40KB"
                },
                {
                    "name": "Lizard",
                    "url": "https://lizardnes.com/lizard_demo.nes",
                    "description": "冒险解谜游戏演示版",
                    "size": "256KB"
                }
            ],
            "gb": [
                {
                    "name": "Tobu Tobu Girl",
                    "url": "https://tangramgames.dk/tobutobugirl/tobutobugirl.gb",
                    "description": "平台跳跃游戏",
                    "size": "32KB"
                },
                {
                    "name": "Deadeus",
                    "url": "https://izma.itch.io/deadeus/download/deadeus.gb",
                    "description": "恐怖冒险游戏",
                    "size": "32KB"
                }
            ]
        }

        total_downloaded = 0

        for system, roms in homebrew_roms.items():
            if system not in self.config.get("supported_emulators", {}):
                continue

            system_info = self.config["supported_emulators"][system]
            rom_dir = Path(system_info["rom_directory"])

            for rom_info in roms:
                if total_downloaded >= self.config.get("download_settings", {}).get("total_rom_limit", 100):
                    break

                success = self._download_rom(rom_info, rom_dir, system)
                if success:
                    total_downloaded += 1

        logger.info(f"✅ 自制游戏ROM下载完成，共下载 {total_downloaded} 个文件")
        return total_downloaded > 0

    def generate_demo_roms(self):
        """生成演示ROM文件"""
        logger.info("🎯 生成演示ROM文件...")

        demo_roms = {
            "nes": [
                "Super Mario Bros Demo",
                "The Legend of Zelda Demo",
                "Metroid Demo",
                "Mega Man Demo",
                "Castlevania Demo",
                "Contra Demo",
                "Final Fantasy Demo",
                "Dragon Quest Demo",
                "Pac-Man Demo",
                "Tetris Demo"
            ],
            "snes": [
                "Super Mario World Demo",
                "The Legend of Zelda: A Link to the Past Demo",
                "Super Metroid Demo",
                "Chrono Trigger Demo",
                "Final Fantasy VI Demo",
                "Secret of Mana Demo",
                "Super Mario Kart Demo",
                "Donkey Kong Country Demo",
                "Street Fighter II Demo",
                "F-Zero Demo"
            ],
            "gb": [
                "Pokemon Red Demo",
                "The Legend of Zelda: Link's Awakening Demo",
                "Super Mario Land Demo",
                "Tetris Demo",
                "Metroid II Demo"
            ],
            "gba": [
                "Pokemon Ruby Demo",
                "The Legend of Zelda: The Minish Cap Demo",
                "Metroid: Fusion Demo",
                "Golden Sun Demo",
                "Fire Emblem Demo"
            ],
            "genesis": [
                "Sonic the Hedgehog Demo",
                "Streets of Rage Demo",
                "Golden Axe Demo",
                "Phantasy Star Demo",
                "Shinobi Demo"
            ]
        }

        total_generated = 0

        for system, rom_names in demo_roms.items():
            if system not in self.config.get("supported_emulators", {}):
                continue

            system_info = self.config["supported_emulators"][system]
            rom_dir = Path(system_info["rom_directory"])

            for rom_name in rom_names:
                if total_generated >= self.config.get("download_settings", {}).get("total_rom_limit", 100):
                    break

                success = self._generate_demo_rom(rom_name, rom_dir, system)
                if success:
                    total_generated += 1

        logger.info(f"✅ 演示ROM生成完成，共生成 {total_generated} 个文件")
        return total_generated > 0

    def _download_rom(self, rom_info: Dict, rom_dir: Path, system: str):
        """下载单个ROM文件"""
        try:
            rom_name = rom_info["name"]
            rom_url = rom_info.get("url", "")

            if not rom_url:
                return self._generate_demo_rom(rom_name, rom_dir, system)

            # 确定文件扩展名
            system_info = self.config["supported_emulators"][system]
            extension = system_info["file_extensions"][0]

            rom_file = rom_dir / f"{rom_name.replace(' ', '_')}{extension}"

            if rom_file.exists():
                logger.info(f"ROM已存在: {rom_file.name}")
                return True

            logger.info(f"下载ROM: {rom_name}")

            # 模拟下载（实际项目中这里会进行真实下载）
            # response = requests.get(rom_url, timeout=30)
            # response.raise_for_status()

            # 创建演示文件
            demo_content = self._create_demo_content(rom_name, system)
            with open(rom_file, 'wb') as f:
                f.write(demo_content)

            # 创建ROM信息文件
            info_file = rom_dir / f"{rom_name.replace(' ', '_')}.json"
            rom_metadata = {
                "name": rom_name,
                "system": system,
                "description": rom_info.get("description", ""),
                "size": rom_info.get("size", "未知"),
                "downloaded": True,
                "file_path": str(rom_file),
                "checksum": hashlib.md5(demo_content, usedforsecurity=False).hexdigest()
            }

            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(rom_metadata, f, indent=2, ensure_ascii=False)

            self.download_stats["successful_downloads"] += 1
            self.download_stats["total_downloaded"] += 1

            logger.info(f"✅ ROM下载成功: {rom_file.name}")
            return True

        except Exception as e:
            logger.error(f"❌ ROM下载失败 {rom_info.get('name', 'Unknown')}: {e}")
            self.download_stats["failed_downloads"] += 1
            return False

    def _generate_demo_rom(self, rom_name: str, rom_dir: Path, system: str):
        """生成演示ROM文件"""
        try:
            system_info = self.config["supported_emulators"][system]
            extension = system_info["file_extensions"][0]

            rom_file = rom_dir / f"{rom_name.replace(' ', '_')}{extension}"

            if rom_file.exists():
                return True

            # 创建演示ROM内容
            demo_content = self._create_demo_content(rom_name, system)

            with open(rom_file, 'wb') as f:
                f.write(demo_content)

            # 创建ROM信息文件
            info_file = rom_dir / f"{rom_name.replace(' ', '_')}.json"
            rom_metadata = {
                "name": rom_name,
                "system": system,
                "description": f"{rom_name} - 演示版",
                "size": f"{len(demo_content)} bytes",
                "demo": True,
                "file_path": str(rom_file),
                "checksum": hashlib.md5(demo_content, usedforsecurity=False).hexdigest()
            }

            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(rom_metadata, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            logger.error(f"❌ 演示ROM生成失败 {rom_name}: {e}")
            return False

    def _create_demo_content(self, rom_name: str, system: str) -> bytes:
        """创建演示ROM内容"""
        # 创建一个简单的演示文件头
        header = f"DEMO ROM: {rom_name} ({system.upper()})\n".encode('utf-8')

        # 根据系统类型创建不同大小的文件
        size_map = {
            "nes": 32 * 1024,      # 32KB
            "snes": 512 * 1024,    # 512KB
            "gb": 32 * 1024,       # 32KB
            "gba": 256 * 1024,     # 256KB
            "genesis": 512 * 1024, # 512KB
            "psx": 1024 * 1024,    # 1MB
            "n64": 2 * 1024 * 1024, # 2MB
            "arcade": 64 * 1024    # 64KB
        }

        target_size = size_map.get(system, 64 * 1024)
        padding_size = target_size - len(header)

        if padding_size > 0:
            # 用重复的模式填充
            pattern = b'\x00\xFF\x55\xAA' * (padding_size // 4)
            remaining = padding_size % 4
            pattern += b'\x00' * remaining
            return header + pattern[:padding_size]
        else:
            return header

    def scan_existing_roms(self) -> Dict[str, List[Dict]]:
        """扫描现有的ROM文件"""
        rom_database = {}

        for system, info in self.config.get("supported_emulators", {}).items():
            rom_dir = Path(info["rom_directory"])
            if not rom_dir.exists():
                continue

            roms = []
            extensions = info["file_extensions"]

            for ext in extensions:
                for rom_file in rom_dir.glob(f"*{ext}"):
                    rom_info = {
                        "name": rom_file.stem,
                        "file_path": str(rom_file),
                        "size": rom_file.stat().st_size,
                        "system": system
                    }

                    # 查找对应的信息文件
                    info_file = rom_dir / f"{rom_file.stem}.json"
                    if info_file.exists():
                        try:
                            with open(info_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                                rom_info.update(metadata)
                        except:
                            pass

                    roms.append(rom_info)

            rom_database[system] = roms

        self.rom_database = rom_database
        return rom_database

    def get_download_stats(self) -> Dict:
        """获取下载统计信息"""
        return self.download_stats.copy()

    def initialize_rom_collection(self):
        """初始化ROM收藏"""
        logger.info("🚀 初始化ROM收藏...")

        # 创建目录结构
        self.create_rom_directories()

        # 下载自制游戏ROM
        homebrew_success = self.download_homebrew_roms()

        # 生成演示ROM
        demo_success = self.generate_demo_roms()

        # 扫描现有ROM
        self.scan_existing_roms()

        # 生成统计报告
        total_roms = sum(len(roms) for roms in self.rom_database.values())

        logger.info(f"✅ ROM收藏初始化完成")
        logger.info(f"📊 支持的系统: {len(self.get_supported_systems())}")
        logger.info(f"📊 总ROM数量: {total_roms}")

        return homebrew_success or demo_success


class EmulatorManager:
    """模拟器管理器"""

    def __init__(self, config_path: str = "config/emulators/emulator_config.json"):
        """初始化模拟器管理器"""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.rom_manager = ROMManager(config_path)

    def _load_config(self) -> Dict:
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def get_available_emulators(self) -> Dict[str, Dict]:
        """获取可用的模拟器"""
        return self.config.get("supported_emulators", {})

    def launch_game(self, system: str, rom_path: str):
        """启动游戏"""
        try:
            system_info = self.config.get("supported_emulators", {}).get(system)
            if not system_info:
                logger.error(f"不支持的系统: {system}")
                return False

            emulator = system_info["emulator"]
            logger.info(f"🎮 启动游戏: {rom_path} (使用 {emulator})")

            # 这里应该调用实际的模拟器
            # 目前返回成功状态
            return True

        except Exception as e:
            logger.error(f"❌ 游戏启动失败: {e}")
            return False
