#!/usr/bin/env python3
"""
ROM管理器 - 负责ROM文件的检查、创建和修复
"""

import hashlib
import struct
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from .config_manager import get_config_manager
from .logger_setup import get_logger
from .state_manager import get_state_manager, FixType
from .transaction_manager import transaction

logger = get_logger("rom")


class RomValidationError(Exception):
    """ROM验证错误"""
    pass


class RomCreationError(Exception):
    """ROM创建错误"""
    pass


class RomManager:
    """ROM管理器"""

    def __init__(self, project_root: Optional[Path] = None):
        """初始化ROM管理器"""
        if project_root is None:
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent

        self.project_root = Path(project_root)
        self.roms_dir = self.project_root / "data" / "roms"
        self.config = get_config_manager()
        self.state_manager = get_state_manager()

        # 创建ROM目录
        self.roms_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"📁 ROM管理器初始化，ROM目录: {self.roms_dir}")

    def check_rom_files(self) -> Dict[str, List[str]]:
        """检查ROM文件状态"""
        logger.info("🔍 检查ROM文件状态...")

        issues = {
            "missing": [],
            "empty": [],
            "corrupted": [],
            "invalid_header": []
        }

        standard_roms = self.config.standard_roms

        for system, roms in standard_roms.items():
            system_dir = self.roms_dir / system

            if not system_dir.exists():
                system_dir.mkdir(parents=True, exist_ok=True)
                logger.debug(f"📁 创建系统目录: {system_dir}")

            for rom_file, rom_name in roms.items():
                rom_path = system_dir / rom_file

                try:
                    self._check_single_rom(rom_path, system, issues)
                except Exception as e:
                    logger.error(f"❌ 检查ROM失败 {rom_file}: {e}")
                    issues["corrupted"].append(str(rom_path))

        # 统计结果
        total_issues = sum(len(issue_list) for issue_list in issues.values())
        logger.info(f"📊 ROM检查完成，发现 {total_issues} 个问题")

        for issue_type, issue_list in issues.items():
            if issue_list:
                logger.info(f"  {issue_type}: {len(issue_list)} 个")

        return issues

    def _check_single_rom(self, rom_path: Path, system: str, issues: Dict[str, List[str]]) -> None:
        """检查单个ROM文件"""
        if not rom_path.exists():
            issues["missing"].append(str(rom_path))
            logger.debug(f"❌ 缺失ROM: {rom_path.name}")
            return

        # 检查文件大小
        file_size = rom_path.stat().st_size

        if file_size == 0:
            issues["empty"].append(str(rom_path))
            logger.debug(f"📄 空ROM文件: {rom_path.name}")
            return

        if file_size < self.config.rom.min_size_bytes:
            issues["corrupted"].append(str(rom_path))
            logger.debug(f"🔧 ROM文件过小: {rom_path.name} ({file_size} bytes)")
            return

        if file_size > self.config.rom.max_size_bytes:
            issues["corrupted"].append(str(rom_path))
            logger.debug(f"🔧 ROM文件过大: {rom_path.name} ({file_size} bytes)")
            return

        # 验证ROM头部
        if self.config.rom.verify_headers:
            try:
                if not self._validate_rom_header(rom_path, system):
                    issues["invalid_header"].append(str(rom_path))
                    logger.debug(f"🔧 ROM头部无效: {rom_path.name}")
                    return
            except Exception as e:
                logger.warning(f"⚠️ 头部验证失败 {rom_path.name}: {e}")

        logger.debug(f"✅ ROM正常: {rom_path.name}")

    def _validate_rom_header(self, rom_path: Path, system: str):
        """验证ROM头部"""
        try:
            with open(rom_path, 'rb') as f:
                header = f.read(16)

            if system == "nes":
                # 验证iNES头部
                return len(header) >= 4 and header[:4] == b'NES\x1a'
            elif system == "snes":
                # SNES ROM通常没有固定头部，检查文件大小
                return len(header) >= 16
            elif system in ["gameboy", "gba"]:
                # Game Boy ROM头部验证
                return len(header) >= 16
            else:
                # 其他系统暂时只检查长度
                return len(header) >= 16

        except Exception as e:
            logger.warning(f"⚠️ 读取ROM头部失败: {e}")
            return False

    def fix_rom_files(self, issues: Dict[str, List[str]]) -> int:
        """修复ROM文件"""
        logger.info("🔧 开始修复ROM文件...")

        fixed_count = 0

        # 收集需要修复的ROM
        roms_to_fix = []
        for issue_type in ["missing", "empty", "corrupted", "invalid_header"]:
            for rom_path_str in issues.get(issue_type, []):
                roms_to_fix.append((Path(rom_path_str), issue_type))

        if not roms_to_fix:
            logger.info("✅ 没有需要修复的ROM文件")
            return 0

        # 使用事务确保原子性
        try:
            with transaction(backup_enabled=self.config.general.backup_before_fix) as tx:

                # 并行修复ROM
                if self.config.general.parallel_workers > 1:
                    fixed_count = self._fix_roms_parallel(roms_to_fix, tx)
                else:
                    fixed_count = self._fix_roms_sequential(roms_to_fix, tx)

                logger.info(f"✅ ROM修复完成: {fixed_count} 个文件")

        except Exception as e:
            logger.error(f"❌ ROM修复失败: {e}")
            raise

        return fixed_count

    def _fix_roms_sequential(self, roms_to_fix: List[Tuple[Path, str]], tx) -> int:
        """顺序修复ROM"""
        fixed_count = 0

        for rom_path, issue_type in roms_to_fix:
            try:
                if self._fix_single_rom(rom_path, issue_type, tx):
                    fixed_count += 1
            except Exception as e:
                logger.error(f"❌ 修复ROM失败 {rom_path.name}: {e}")

        return fixed_count

    def _fix_roms_parallel(self, roms_to_fix: List[Tuple[Path, str]], tx) -> int:
        """并行修复ROM"""
        fixed_count = 0

        with ThreadPoolExecutor(max_workers=self.config.general.parallel_workers) as executor:
            # 提交任务
            future_to_rom = {
                executor.submit(self._fix_single_rom, rom_path, issue_type, tx): (rom_path, issue_type)
                for rom_path, issue_type in roms_to_fix
            }

            # 收集结果
            for future in as_completed(future_to_rom):
                rom_path, issue_type = future_to_rom[future]
                try:
                    if future.result():
                        fixed_count += 1
                except Exception as e:
                    logger.error(f"❌ 并行修复ROM失败 {rom_path.name}: {e}")

        return fixed_count

    def _fix_single_rom(self, rom_path: Path, issue_type: str, tx):
        """修复单个ROM文件"""
        try:
            # 确定系统类型
            system = self._detect_system_from_path(rom_path)
            if not system:
                logger.error(f"❌ 无法确定系统类型: {rom_path}")
                return False

            # 添加状态跟踪
            item_id = f"fix_rom_{rom_path.stem}"
            fix_item = self.state_manager.add_fix_item(
                item_id,
                FixType.ROM_REPAIR if issue_type != "missing" else FixType.ROM_CREATION,
                f"修复ROM: {rom_path.name}",
                f"修复 {issue_type} 问题: {rom_path}",
                {"system": system, "issue_type": issue_type}
            )

            fix_item.start()

            # 创建ROM内容
            rom_content = self._create_rom_content(system, rom_path.name)

            # 添加到事务
            tx.add_file_operation(
                f"fix_rom_{rom_path.stem}",
                "rom_fix",
                f"修复ROM文件: {rom_path.name}",
                rom_path,
                content=rom_content
            )

            fix_item.complete({
                "size": len(rom_content),
                "system": system
            })

            logger.info(f"✅ 修复ROM: {rom_path.name}")
            return True

        except Exception as e:
            if 'fix_item' in locals():
                fix_item.fail(str(e))
            logger.error(f"❌ 修复ROM失败 {rom_path.name}: {e}")
            return False

    def _detect_system_from_path(self, rom_path: Path) -> Optional[str]:
        """从路径检测系统类型"""
        path_parts = rom_path.parts

        # 检查路径中的系统目录
        for part in path_parts:
            if part in self.config.standard_roms:
                return part

        # 根据扩展名推测
        extension = rom_path.suffix.lower()
        extension_map = {
            ".nes": "nes",
            ".fds": "nes",
            ".smc": "snes",
            ".sfc": "snes",
            ".gb": "gameboy",
            ".gbc": "gameboy",
            ".gba": "gba",
            ".md": "genesis",
            ".gen": "genesis"
        }

        return extension_map.get(extension)

    def _create_rom_content(self, system: str, filename: str) -> bytes:
        """创建ROM内容"""
        if system == "nes":
            return self._create_nes_rom()
        elif system == "snes":
            return self._create_snes_rom()
        elif system == "gameboy":
            return self._create_gameboy_rom()
        elif system == "gba":
            return self._create_gba_rom()
        else:
            # 默认创建简单的ROM
            return self._create_generic_rom()

    def _create_nes_rom(self) -> bytes:
        """创建NES ROM"""
        # iNES头部 (16字节)
        ines_header = bytearray([
            0x4E, 0x45, 0x53, 0x1A,  # "NES" + MS-DOS EOF
            0x01,  # PRG ROM size (16KB units)
            0x01,  # CHR ROM size (8KB units)
            0x00,  # Flags 6: Mapper 0, Vertical mirroring
            0x00,  # Flags 7: Mapper 0
            0x00,  # PRG RAM size
            0x00,  # Flags 9: NTSC
            0x00,  # Flags 10
            0x00, 0x00, 0x00, 0x00, 0x00  # Padding
        ])

        # PRG ROM (16KB) - 程序代码
        prg_rom = bytearray(16384)

        # 添加基本的6502汇编代码
        # 重置向量指向$8000 (在PRG ROM的最后4字节)
        prg_rom[0x3FFC] = 0x00  # Reset vector low (16KB - 4)
        prg_rom[0x3FFD] = 0x80  # Reset vector high

        # 在$8000处放置简单的程序
        prg_rom[0x0000] = 0x78  # SEI (禁用中断)
        prg_rom[0x0001] = 0xD8  # CLD (清除十进制模式)
        prg_rom[0x0002] = 0xA9  # LDA #$00
        prg_rom[0x0003] = 0x00
        prg_rom[0x0004] = 0x8D  # STA $2000
        prg_rom[0x0005] = 0x00
        prg_rom[0x0006] = 0x20
        prg_rom[0x0007] = 0x4C  # JMP $8007 (无限循环)
        prg_rom[0x0008] = 0x07
        prg_rom[0x0009] = 0x80

        # CHR ROM (8KB) - 图形数据
        chr_rom = bytearray(8192)

        # 添加基本的图形数据
        for i in range(0, 256, 16):  # 16个图块
            # 创建简单的图案
            chr_rom[i:i+8] = [0xFF, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0xFF]
            chr_rom[i+8:i+16] = [0x00, 0x7E, 0x7E, 0x7E, 0x7E, 0x7E, 0x7E, 0x00]

        # 组合完整的ROM
        return bytes(ines_header + prg_rom + chr_rom)

    def _create_snes_rom(self) -> bytes:
        """创建SNES ROM"""
        # 创建32KB的SNES ROM
        rom_size = 32 * 1024
        rom_data = bytearray(rom_size)

        # 添加SNES头部信息（在ROM末尾）
        header_offset = rom_size - 64

        # 游戏标题 (21字节)
        title = b"DEMO GAME           "[:21]
        rom_data[header_offset:header_offset+21] = title

        # ROM配置
        rom_data[header_offset + 21] = 0x00  # ROM速度
        rom_data[header_offset + 22] = 0x00  # 芯片类型
        rom_data[header_offset + 23] = 0x05  # ROM大小 (32KB)
        rom_data[header_offset + 24] = 0x00  # RAM大小

        # 重置向量
        rom_data[rom_size - 4:rom_size - 2] = struct.pack('<H', 0x8000)

        return bytes(rom_data)

    def _create_gameboy_rom(self) -> bytes:
        """创建Game Boy ROM"""
        # 创建32KB的Game Boy ROM
        rom_size = 32 * 1024
        rom_data = bytearray(rom_size)

        # Game Boy头部 (从0x100开始)
        # 入口点
        rom_data[0x100:0x104] = [0x00, 0xC3, 0x50, 0x01]  # NOP; JP $0150

        # Nintendo logo (必须正确才能启动)
        nintendo_logo = bytes([
            0xCE, 0xED, 0x66, 0x66, 0xCC, 0x0D, 0x00, 0x0B,
            0x03, 0x73, 0x00, 0x83, 0x00, 0x0C, 0x00, 0x0D,
            0x00, 0x08, 0x11, 0x1F, 0x88, 0x89, 0x00, 0x0E,
            0xDC, 0xCC, 0x6E, 0xE6, 0xDD, 0xDD, 0xD9, 0x99,
            0xBB, 0xBB, 0x67, 0x63, 0x6E, 0x0E, 0xEC, 0xCC,
            0xDD, 0xDC, 0x99, 0x9F, 0xBB, 0xB9, 0x33, 0x3E
        ])
        rom_data[0x104:0x134] = nintendo_logo

        # 游戏标题
        title = b"DEMO GAME\x00\x00\x00\x00\x00\x00\x00"[:16]
        rom_data[0x134:0x144] = title

        # 头部校验和
        checksum = 0
        for i in range(0x134, 0x14D):
            checksum = (checksum - rom_data[i] - 1) & 0xFF
        rom_data[0x14D] = checksum

        return bytes(rom_data)

    def _create_gba_rom(self) -> bytes:
        """创建GBA ROM"""
        # 创建256KB的GBA ROM
        rom_size = 256 * 1024
        rom_data = bytearray(rom_size)

        # GBA头部
        # 入口点 (ARM代码)
        rom_data[0x00:0x04] = [0x00, 0x00, 0xA0, 0xE1]  # NOP

        # Nintendo logo (必须正确)
        nintendo_logo = bytes([
            0x24, 0xFF, 0xAE, 0x51, 0x69, 0x9A, 0xA2, 0x21,
            0x3D, 0x84, 0x82, 0x0A, 0x84, 0xE4, 0x09, 0xAD,
            0x11, 0x24, 0x8B, 0x98, 0xC0, 0x81, 0x7F, 0x21,
            0xA3, 0x52, 0xBE, 0x19, 0x93, 0x09, 0xCE, 0x20,
            0x10, 0x46, 0x4A, 0x4A, 0xF8, 0x27, 0x31, 0xEC,
            0x58, 0xC7, 0xE8, 0x33, 0x82, 0xE3, 0xCE, 0xBF,
            0x85, 0xF4, 0xDF, 0x94, 0xCE, 0x4B, 0x09, 0xC1,
            0x94, 0x56, 0x8A, 0xC0, 0x13, 0x72, 0xA7, 0xFC,
            0x9F, 0x84, 0x4D, 0x73, 0xA3, 0xCA, 0x9A, 0x61,
            0x58, 0x97, 0xA3, 0x27, 0xFC, 0x03, 0x98, 0x76,
            0x23, 0x1D, 0xC7, 0x61, 0x03, 0x04, 0xAE, 0x56,
            0xBF, 0x38, 0x84, 0x00, 0x40, 0xA7, 0x0E, 0xFD,
            0xFF, 0x52, 0xFE, 0x03, 0x6F, 0x95, 0x30, 0xF1,
            0x97, 0xFB, 0xC0, 0x85, 0x60, 0xD6, 0x80, 0x25,
            0xA9, 0x63, 0xBE, 0x03, 0x01, 0x4E, 0x38, 0xE2,
            0xF9, 0xA2, 0x34, 0xFF, 0xBB, 0x3E, 0x03, 0x44,
            0x78, 0x00, 0x90, 0xCB, 0x88, 0x11, 0x3A, 0x94,
            0x65, 0xC0, 0x7C, 0x63, 0x87, 0xF0, 0x3C, 0xAF,
            0xD6, 0x25, 0xE4, 0x8B, 0x38, 0x0A, 0xAC, 0x72,
            0x21, 0xD4, 0xF8, 0x07
        ])
        rom_data[0x04:0xA0] = nintendo_logo

        # 游戏标题
        title = b"DEMO GAME\x00\x00\x00"[:12]
        rom_data[0xA0:0xAC] = title

        return bytes(rom_data)

    def _create_generic_rom(self) -> bytes:
        """创建通用ROM"""
        # 创建64KB的通用ROM
        rom_size = 64 * 1024
        rom_data = bytearray(rom_size)

        # 填充一些模式数据
        for i in range(0, rom_size, 4):
            rom_data[i:i+4] = struct.pack('<I', i)

        return bytes(rom_data)

    def get_rom_info(self, rom_path: Path) -> Dict[str, Any]:
        """获取ROM信息"""
        if not rom_path.exists():
            return {"exists": False}

        info = {
            "exists": True,
            "size": rom_path.stat().st_size,
            "system": self._detect_system_from_path(rom_path),
            "valid_header": False
        }

        # 计算MD5
        try:
            with open(rom_path, 'rb') as f:
                content = f.read()
                info["md5"] = hashlib.md5(content, usedforsecurity=False).hexdigest()
        except Exception as e:
            logger.warning(f"⚠️ 计算MD5失败: {e}")

        # 验证头部
        if info["system"]:
            try:
                info["valid_header"] = self._validate_rom_header(rom_path, info["system"])
            except Exception as e:
                logger.warning(f"⚠️ 验证头部失败: {e}")

        return info

if __name__ == "__main__":
    # 测试ROM管理器
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试配置
        test_config_dir = Path(temp_dir) / "config"
        test_config_dir.mkdir()

        # 创建测试ROM配置
        test_roms = {
            "nes": {
                "test_game.nes": "测试游戏"
            }
        }

        with open(test_config_dir / "standard_roms.json", 'w') as f:
            import json
            json.dump(test_roms, f)

        # 测试ROM管理器
        rom_manager = RomManager(Path(temp_dir))

        # 检查ROM
        issues = rom_manager.check_rom_files()
        print(f"📊 发现问题: {issues}")

        # 修复ROM
        fixed = rom_manager.fix_rom_files(issues)
        print(f"✅ 修复了 {fixed} 个ROM文件")

        # 再次检查
        issues_after = rom_manager.check_rom_files()
        print(f"📊 修复后问题: {issues_after}")

        print("✅ ROM管理器测试完成")
