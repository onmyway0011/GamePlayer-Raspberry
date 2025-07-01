#!/usr/bin/env python3
"""
ROM集成测试
测试ROM下载、管理和集成功能
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import sys
import os

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scripts.rom_downloader import ROMDownloader
from src.scripts.rom_manager import ROMManager


class TestROMIntegration(unittest.TestCase):
    """ROM集成测试"""

    def setUp(self):
        """设置测试环境"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.roms_dir = self.test_dir / "roms"
        self.roms_dir.mkdir()

        self.downloader = ROMDownloader(str(self.roms_dir))
        self.manager = ROMManager(str(self.roms_dir))

    def tearDown(self):
        """清理测试环境"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_rom_downloader_initialization(self):
        """测试ROM下载器初始化"""
        self.assertTrue(self.roms_dir.exists())
        self.assertIsInstance(self.downloader.recommended_roms, dict)
        # self.assertIn("public_domain", self.downloader.recommended_roms)
        # self.assertIn("demo_roms", self.downloader.recommended_roms)
        self.assertIn("homebrew_games", self.downloader.recommended_roms)

    def test_sample_rom_generation(self):
        """测试示例ROM生成"""
        rom_content = self.downloader._generate_sample_rom("Test Game")

        # 检查ROM文件头
        self.assertEqual(rom_content[0:4], b'NES\x1a')
        self.assertEqual(len(rom_content), 16 + 32768 + 8192)  # 头部 + PRG + CHR

        # 检查标题
        title_start = 16  # 跳过头部
        title_bytes = rom_content[title_start:title_start+9]
        self.assertEqual(title_bytes, b'Test Game')

    def test_fallback_rom_creation(self):
        """测试备用ROM创建"""
        rom_info = {
            "name": "Test ROM",
            "content": self.downloader._generate_sample_rom("Test ROM"),
            "size_kb": 32
        }

        success = self.downloader.create_fallback_rom("test_rom", rom_info)
        self.assertTrue(success)

        rom_file = self.roms_dir / "test_rom.nes"
        self.assertTrue(rom_file.exists())
        self.assertGreater(rom_file.stat().st_size, 1024)  # 至少1KB

    def test_rom_catalog_creation(self):
        """测试ROM目录创建"""
        # 创建一些示例ROM
        self.downloader.create_fallback_rom("game1", {
            "name": "Game 1",
            "content": self.downloader._generate_sample_rom("Game 1"),
            "size_kb": 32
        })

        self.downloader.create_rom_catalog()

        catalog_file = self.roms_dir / "rom_catalog.json"
        self.assertTrue(catalog_file.exists())

        with open(catalog_file, 'r', encoding='utf-8') as f:
            catalog = json.load(f)

        self.assertIn("title", catalog)
        self.assertIn("categories", catalog)

    def test_playlist_creation(self):
        """测试播放列表创建"""
        # 创建一些示例ROM
        self.downloader.create_fallback_rom("game1", {
            "name": "Game 1",
            "content": self.downloader._generate_sample_rom("Game 1"),
            "size_kb": 32
        })

        self.downloader.create_playlist_files()

        playlists_dir = self.roms_dir / "playlists"
        self.assertTrue(playlists_dir.exists())

        # 检查播放列表文件
        for category in self.downloader.recommended_roms.keys():
            playlist_file = playlists_dir / f"{category}.m3u"
            self.assertTrue(playlist_file.exists())

    def test_rom_manager_list_roms(self):
        """测试ROM管理器列出ROM"""
        # 创建示例ROM
        rom_file = self.roms_dir / "test_game.nes"
        rom_content = self.downloader._generate_sample_rom("Test Game")

        with open(rom_file, 'wb') as f:
            f.write(rom_content)

        # 测试列出ROM（不会有输出，但不应该出错）
        try:
            self.manager.list_roms()
        except Exception as e:
            self.fail(f"list_roms() 抛出异常: {e}")

    def test_rom_manager_verify_roms(self):
        """测试ROM验证"""
        # 创建有效的ROM文件
        valid_rom = self.roms_dir / "valid.nes"
        valid_content = self.downloader._generate_sample_rom("Valid ROM")
        with open(valid_rom, 'wb') as f:
            f.write(valid_content)

        # 创建无效的ROM文件
        invalid_rom = self.roms_dir / "invalid.nes"
        with open(invalid_rom, 'wb') as f:
            f.write(b"invalid content")

        # 验证不会抛出异常
        try:
            self.manager.verify_roms()
        except Exception as e:
            self.fail(f"verify_roms() 抛出异常: {e}")

    def test_rom_manager_clean_roms(self):
        """测试ROM清理"""
        # 创建有效的ROM文件
        valid_rom = self.roms_dir / "valid.nes"
        valid_content = self.downloader._generate_sample_rom("Valid ROM")
        with open(valid_rom, 'wb') as f:
            f.write(valid_content)

        # 创建过小的文件
        small_rom = self.roms_dir / "small.nes"
        with open(small_rom, 'wb') as f:
            f.write(b"small")

        # 创建无效格式的文件
        invalid_rom = self.roms_dir / "invalid.nes"
        with open(invalid_rom, 'wb') as f:
            f.write(b"invalid content" * 100)  # 足够大但格式无效

        # 执行清理
        self.manager.clean_roms()

        # 检查结果
        self.assertTrue(valid_rom.exists())  # 有效文件应该保留
        self.assertFalse(small_rom.exists())  # 过小文件应该被删除
        self.assertFalse(invalid_rom.exists())  # 无效文件应该被删除

    def test_rom_manager_backup_restore(self):
        """测试ROM备份和恢复"""
        # 创建示例ROM
        rom_file = self.roms_dir / "test_game.nes"
        rom_content = self.downloader._generate_sample_rom("Test Game")

        with open(rom_file, 'wb') as f:
            f.write(rom_content)

        # 创建目录文件
        self.downloader.create_rom_catalog()

        # 备份
        backup_dir = self.test_dir / "backup"
        self.manager.backup_roms(str(backup_dir))

        # 检查备份文件
        self.assertTrue((backup_dir / "test_game.nes").exists())
        self.assertTrue((backup_dir / "rom_catalog.json").exists())

        # 删除原文件
        rom_file.unlink()
        (self.roms_dir / "rom_catalog.json").unlink()

        # 恢复
        self.manager.restore_roms(str(backup_dir))

        # 检查恢复结果
        self.assertTrue(rom_file.exists())
        self.assertTrue((self.roms_dir / "rom_catalog.json").exists())

    def test_rom_manager_create_playlist(self):
        """测试创建自定义播放列表"""
        # 创建示例ROM文件
        rom_files = ["game1.nes", "game2.nes", "game3.nes"]
        for rom_name in rom_files:
            rom_file = self.roms_dir / rom_name
            rom_content = self.downloader._generate_sample_rom(rom_name)
            with open(rom_file, 'wb') as f:
                f.write(rom_content)

        # 创建播放列表
        self.manager.create_playlist("my_favorites", rom_files)

        # 检查播放列表文件
        playlist_file = self.roms_dir / "playlists" / "my_favorites.m3u"
        self.assertTrue(playlist_file.exists())

        # 检查播放列表内容
        with open(playlist_file, 'r', encoding='utf-8') as f:
            content = f.read()

        for rom_name in rom_files:
            self.assertIn(f"../{rom_name}", content)

    def test_download_category_with_fallback(self):
        """测试分类下载（使用备用ROM）"""
        # 下载演示ROM分类（会使用备用ROM）
        results = self.downloader.download_category("homebrew_games")

        # 检查结果
        self.assertIsInstance(results, dict)

        # 检查是否创建了ROM文件
        rom_files = list(self.roms_dir.glob("*.nes"))
        self.assertGreater(len(rom_files), 0)

        # 验证ROM文件格式
        for rom_file in rom_files:
            with open(rom_file, 'rb') as f:
                header = f.read(4)
            self.assertEqual(header, b'NES\x1a')


class TestROMConfiguration(unittest.TestCase):
    """ROM配置测试"""

    def test_packages_config_has_rom_section(self):
        """测试包配置包含ROM部分"""
        config_file = project_root / "config" / "packages.json"

        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 检查ROM配置部分
            if "rom_configuration" in config:
                rom_config = config["rom_configuration"]
                self.assertIn("download_enabled", rom_config)
                self.assertIn("rom_directory", rom_config)
                self.assertIn("categories", rom_config)

if __name__ == '__main__':
    unittest.main()
