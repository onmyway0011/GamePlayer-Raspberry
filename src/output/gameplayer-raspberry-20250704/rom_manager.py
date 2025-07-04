#!/usr/bin/env python3
"""
ROM 管理器
管理NES ROM文件的下载、安装和组织
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional
import argparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ROMManager:
    """ROM管理器"""

    def __init__(self, roms_dir: str = "/home/pi/RetroPie/roms/nes"):
        """TODO: 添加文档字符串"""
        self.roms_dir = Path(roms_dir)
        self.roms_dir.mkdir(parents=True, exist_ok=True)

        self.catalog_file = self.roms_dir / "rom_catalog.json"
        self.playlists_dir = self.roms_dir / "playlists"
        self.playlists_dir.mkdir(exist_ok=True)

    def list_roms(self) -> None:
        """列出所有ROM文件"""
        logger.info("📋 ROM文件列表:")

        rom_files = list(self.roms_dir.glob("*.nes"))

        if not rom_files:
            logger.info("❌ 没有找到ROM文件")
            return

        # 加载目录信息
        catalog = self._load_catalog()

        for rom_file in sorted(rom_files):
            size_kb = rom_file.stat().st_size // 1024

            # 从目录中查找ROM信息
            rom_info = self._find_rom_in_catalog(rom_file.name, catalog)

            if rom_info:
                print(f"🎮 {rom_info['name']}")
                print(f"   📁 文件: {rom_file.name}")
                print(f"   📊 大小: {size_kb}KB")
                print(f"   🎯 类型: {rom_info['genre']}")
                print(f"   📅 年份: {rom_info['year']}")
                print(f"   📝 描述: {rom_info['description']}")
            else:
                print(f"🎮 {rom_file.stem}")
                print(f"   📁 文件: {rom_file.name}")
                print(f"   📊 大小: {size_kb}KB")

            print()

    def _load_catalog(self) -> Dict:
        """加载ROM目录"""
        if not self.catalog_file.exists():
            return {}

        try:
            with open(self.catalog_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ 加载目录失败: {e}")
            return {}

    def _find_rom_in_catalog(self, filename: str, catalog: Dict) -> Optional[Dict]:
        """在目录中查找ROM信息"""
        for category_info in catalog.get("categories", {}).values():
            for rom_info in category_info.get("roms", {}).values():
                if rom_info.get("filename") == filename:
                    return rom_info
        return None

    def download_roms(self, category: Optional[str] = None) -> None:
        """下载ROM文件"""
        logger.info("📥 开始下载ROM文件...")

        try:
            # 导入ROM下载器
            from rom_downloader import ROMDownloader

            downloader = ROMDownloader(str(self.roms_dir))

            if category:
                results = {category: downloader.download_category(category)}
            else:
                results = downloader.download_all()

            # 创建目录和播放列表
            downloader.create_rom_catalog()
            downloader.create_playlist_files()

            # 生成报告
            downloader.generate_report(results)

        except ImportError:
            logger.error("❌ 无法导入ROM下载器")
        except Exception as e:
            logger.error(f"❌ 下载失败: {e}")

    def create_playlist(self, name: str, rom_files: List[str]) -> None:
        """创建播放列表"""
        playlist_file = self.playlists_dir / f"{name}.m3u"

        try:
            with open(playlist_file, 'w', encoding='utf-8') as f:
                f.write(f"# {name} 播放列表\n\n")

                for rom_file in rom_files:
                    rom_path = self.roms_dir / rom_file
                    if rom_path.exists():
                        f.write(f"../{rom_file}\n")
                    else:
                        logger.warning(f"⚠️ ROM文件不存在: {rom_file}")

            logger.info(f"✅ 播放列表已创建: {playlist_file}")

        except Exception as e:
            logger.error(f"❌ 创建播放列表失败: {e}")

    def list_playlists(self) -> None:
        """列出所有播放列表"""
        logger.info("📋 播放列表:")

        playlist_files = list(self.playlists_dir.glob("*.m3u"))

        if not playlist_files:
            logger.info("❌ 没有找到播放列表")
            return

        for playlist_file in sorted(playlist_files):
            print(f"📝 {playlist_file.stem}")

            try:
                with open(playlist_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                rom_count = sum(1 for line in lines if line.strip() and not line.startswith('#'))
                print(f"   🎮 包含 {rom_count} 个ROM")

                # 显示前几行注释
                for line in lines[:3]:
                    if line.startswith('#'):
                        print(f"   💬 {line.strip()[1:].strip()}")

            except Exception as e:
                print(f"   ❌ 读取失败: {e}")

            print()

    def verify_roms(self) -> None:
        """验证ROM文件完整性"""
        logger.info("🔍 验证ROM文件...")

        rom_files = list(self.roms_dir.glob("*.nes"))

        if not rom_files:
            logger.info("❌ 没有找到ROM文件")
            return

        valid_count = 0
        invalid_count = 0

        for rom_file in rom_files:
            try:
                with open(rom_file, 'rb') as f:
                    header = f.read(16)

                # 检查NES文件头
                if len(header) >= 4 and header[0:4] == b'NES\x1a':
                    print(f"✅ {rom_file.name} - 有效的NES ROM")
                    valid_count += 1
                else:
                    print(f"❌ {rom_file.name} - 无效的文件格式")
                    invalid_count += 1

            except Exception as e:
                print(f"❌ {rom_file.name} - 读取失败: {e}")
                invalid_count += 1

        print(f"\n📊 验证结果: {valid_count} 个有效, {invalid_count} 个无效")

    def clean_roms(self) -> None:
        """清理无效的ROM文件"""
        logger.info("🧹 清理无效ROM文件...")

        rom_files = list(self.roms_dir.glob("*.nes"))
        removed_count = 0

        for rom_file in rom_files:
            try:
                with open(rom_file, 'rb') as f:
                    header = f.read(16)

                # 检查文件大小和格式
                if rom_file.stat().st_size < 1024:  # 小于1KB
                    logger.info(f"🗑️ 删除过小文件: {rom_file.name}")
                    rom_file.unlink()
                    removed_count += 1
                elif len(header) < 4 or header[0:4] != b'NES\x1a':
                    logger.info(f"🗑️ 删除无效格式: {rom_file.name}")
                    rom_file.unlink()
                    removed_count += 1

            except Exception as e:
                logger.error(f"❌ 处理文件失败 {rom_file.name}: {e}")

        logger.info(f"✅ 清理完成，删除了 {removed_count} 个文件")

    def backup_roms(self, backup_dir: str) -> None:
        """备份ROM文件"""
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"💾 备份ROM到: {backup_path}")

        try:
            # 复制ROM文件
            rom_files = list(self.roms_dir.glob("*.nes"))
            for rom_file in rom_files:
                shutil.copy2(rom_file, backup_path)

            # 复制目录和播放列表
            if self.catalog_file.exists():
                shutil.copy2(self.catalog_file, backup_path)

            if self.playlists_dir.exists():
                shutil.copytree(self.playlists_dir, backup_path / "playlists", dirs_exist_ok=True)

            logger.info(f"✅ 备份完成，共 {len(rom_files)} 个文件")

        except Exception as e:
            logger.error(f"❌ 备份失败: {e}")

    def restore_roms(self, backup_dir: str) -> None:
        """从备份恢复ROM文件"""
        backup_path = Path(backup_dir)

        if not backup_path.exists():
            logger.error(f"❌ 备份目录不存在: {backup_dir}")
            return

        logger.info(f"📥 从备份恢复: {backup_path}")

        try:
            # 恢复ROM文件
            rom_files = list(backup_path.glob("*.nes"))
            for rom_file in rom_files:
                shutil.copy2(rom_file, self.roms_dir)

            # 恢复目录文件
            backup_catalog = backup_path / "rom_catalog.json"
            if backup_catalog.exists():
                shutil.copy2(backup_catalog, self.catalog_file)

            # 恢复播放列表
            backup_playlists = backup_path / "playlists"
            if backup_playlists.exists():
                shutil.copytree(backup_playlists, self.playlists_dir, dirs_exist_ok=True)

            logger.info(f"✅ 恢复完成，共 {len(rom_files)} 个文件")

        except Exception as e:
            logger.error(f"❌ 恢复失败: {e}")


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description="ROM管理器")
    parser.add_argument("--roms-dir", default="/home/pi/RetroPie/roms/nes", help="ROM目录路径")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 列出ROM
    subparsers.add_parser("list", help="列出所有ROM文件")

    # 下载ROM
    download_parser = subparsers.add_parser("download", help="下载ROM文件")
    download_parser.add_argument("--category", help="下载指定分类")

    # 创建播放列表
    playlist_parser = subparsers.add_parser("playlist", help="创建播放列表")
    playlist_parser.add_argument("name", help="播放列表名称")
    playlist_parser.add_argument("roms", nargs="+", help="ROM文件列表")

    # 列出播放列表
    subparsers.add_parser("playlists", help="列出所有播放列表")

    # 验证ROM
    subparsers.add_parser("verify", help="验证ROM文件完整性")

    # 清理ROM
    subparsers.add_parser("clean", help="清理无效ROM文件")

    # 备份ROM
    backup_parser = subparsers.add_parser("backup", help="备份ROM文件")
    backup_parser.add_argument("backup_dir", help="备份目录")

    # 恢复ROM
    restore_parser = subparsers.add_parser("restore", help="恢复ROM文件")
    restore_parser.add_argument("backup_dir", help="备份目录")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = ROMManager(args.roms_dir)

    if args.command == "list":
        manager.list_roms()
    elif args.command == "download":
        manager.download_roms(args.category)
    elif args.command == "playlist":
        manager.create_playlist(args.name, args.roms)
    elif args.command == "playlists":
        manager.list_playlists()
    elif args.command == "verify":
        manager.verify_roms()
    elif args.command == "clean":
        manager.clean_roms()
    elif args.command == "backup":
        manager.backup_roms(args.backup_dir)
    elif args.command == "restore":
        manager.restore_roms(args.backup_dir)

if __name__ == "__main__":
    main()
