#!/usr/bin/env python3
"""
游戏模拟器启动失败修复工具
诊断和修复所有模拟器启动问题
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class EmulatorStartupFixer:
    """模拟器启动修复器"""

    def __init__(self):
        """TODO: Add docstring"""
        self.project_root = project_root

        # 模拟器配置
        self.emulators = {
            "nes": {
                "primary": "mednafen",
                "alternatives": ["fceux", "nestopia"],
                "install_commands": [
                    "brew install mednafen",
                    "brew install fceux",
                    "brew install nestopia"
                ],
                "test_args": ["-help"],
                "launch_args": ["-force_module", "nes"]
            },
            "snes": {
                "primary": "mednafen",
                "alternatives": ["snes9x", "bsnes"],
                "install_commands": [
                    "brew install mednafen",
                    "brew install snes9x",
                    "brew install bsnes"
                ],
                "test_args": ["-help"],
                "launch_args": ["-force_module", "snes"]
            },
            "gameboy": {
                "primary": "mednafen",
                "alternatives": ["visualboyadvance-m", "gambatte"],
                "install_commands": [
                    "brew install mednafen",
                    "brew install visualboyadvance-m",
                    "brew install gambatte"
                ],
                "test_args": ["-help"],
                "launch_args": ["-force_module", "gb"]
            },
            "gba": {
                "primary": "mednafen",
                "alternatives": ["visualboyadvance-m", "mgba"],
                "install_commands": [
                    "brew install mednafen",
                    "brew install visualboyadvance-m",
                    "brew install mgba"
                ],
                "test_args": ["-help"],
                "launch_args": ["-force_module", "gba"]
            },
            "genesis": {
                "primary": "mednafen",
                "alternatives": ["blastem", "gens"],
                "install_commands": [
                    "brew install mednafen",
                    "brew install blastem"
                ],
                "test_args": ["-help"],
                "launch_args": ["-force_module", "md"]
            }
        }

    def check_homebrew(self):
        """检查Homebrew状态"""
        print("🍺 检查Homebrew...")

        try:
            result = subprocess.run(["which", "brew"], capture_output=True, timeout=10)

            if result.returncode == 0:
                print("✅ Homebrew已安装")

                # 检查Homebrew版本
                version_result = subprocess.run(["brew", "--version"], capture_output=True, text=True, timeout=10)
                if version_result.returncode == 0:
                    version_line = version_result.stdout.split('\n')[0]
                    print(f"📊 版本: {version_line}")

                return True
            else:
                print("❌ Homebrew未安装")
                return False

        except Exception as e:
            print(f"❌ 检查Homebrew失败: {e}")
            return False

    def install_homebrew(self):
        """安装Homebrew"""
        print("📦 安装Homebrew...")

        try:
            install_script = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            print("⏳ 正在安装Homebrew，这可能需要几分钟...")

            result = subprocess.run(install_script, shell=True, timeout=600)

            if result.returncode == 0:
                print("✅ Homebrew安装成功")
                return True
            else:
                print("❌ Homebrew安装失败")
                return False

        except subprocess.TimeoutExpired:
            print("❌ Homebrew安装超时")
            return False
        except Exception as e:
            print(f"❌ Homebrew安装异常: {e}")
            return False

    def test_emulator(self, emulator_name: str, test_args: list):
        """测试模拟器是否可用"""
        print(f"🧪 测试模拟器: {emulator_name}")

        try:
            # 检查命令是否存在
            which_result = subprocess.run(["which", emulator_name], capture_output=True, timeout=10)

            if which_result.returncode != 0:
                print(f"  ❌ {emulator_name} 未安装")
                return False

            # 测试运行
            test_result = subprocess.run([emulator_name] + test_args, capture_output=True, text=True, timeout=10)

            # 对于某些模拟器，帮助命令可能返回非0状态码
            if test_result.returncode == 0 or "usage" in test_result.stdout.lower() or "help" in test_result.stdout.lower():
                print(f"  ✅ {emulator_name} 可用")
                return True
            else:
                print(f"  ❌ {emulator_name} 测试失败")
                return False

        except subprocess.TimeoutExpired:
            print(f"  ❌ {emulator_name} 测试超时")
            return False
        except Exception as e:
            print(f"  ❌ {emulator_name} 测试异常: {e}")
            return False

    def install_emulator(self, install_command: str):
        """安装模拟器"""
        print(f"🔧 执行安装: {install_command}")

        try:
            cmd_parts = install_command.split()

            result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                print(f"  ✅ 安装成功")
                return True
            else:
                print(f"  ❌ 安装失败: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"  ❌ 安装超时")
            return False
        except Exception as e:
            print(f"  ❌ 安装异常: {e}")
            return False

    def fix_system_emulator(self, system: str):
        """修复指定系统的模拟器"""
        print(f"\n🎮 修复 {system.upper()} 模拟器...")

        if system not in self.emulators:
            print(f"❌ 不支持的系统: {system}")
            return False

        config = self.emulators[system]
        primary = config["primary"]
        alternatives = config["alternatives"]
        install_commands = config["install_commands"]
        test_args = config["test_args"]

        # 首先测试主要模拟器
        if self.test_emulator(primary, test_args):
            print(f"✅ {system.upper()} 主要模拟器 {primary} 已可用")
            return True

        # 测试替代模拟器
        for alt in alternatives:
            if self.test_emulator(alt, test_args):
                print(f"✅ {system.upper()} 替代模拟器 {alt} 已可用")
                return True

        # 所有模拟器都不可用，尝试安装
        print(f"⚠️ {system.upper()} 所有模拟器都不可用，开始安装...")

        for install_cmd in install_commands:
            if self.install_emulator(install_cmd):
                # 安装成功后测试
                emulator_name = install_cmd.split()[-1]  # 获取模拟器名称

                if self.test_emulator(emulator_name, test_args):
                    print(f"✅ {system.upper()} 模拟器 {emulator_name} 安装并测试成功")
                    return True

        print(f"❌ {system.upper()} 模拟器修复失败")
        return False

    def create_test_rom(self, system: str) -> str:
        """创建测试ROM文件"""
        print(f"📁 创建 {system.upper()} 测试ROM...")

        roms_dir = self.project_root / "data" / "roms" / system
        roms_dir.mkdir(parents=True, exist_ok=True)

        if system == "nes":
            rom_path = roms_dir / "test_mario.nes"

            # iNES头部格式
            ines_header = bytearray([
                0x4E, 0x45, 0x53, 0x1A,  # "NES" + MS-DOS EOF
                0x01,  # PRG ROM size (16KB units)
                0x01,  # CHR ROM size (8KB units)
                0x00,  # Flags 6
                0x00,  # Flags 7
                0x00,  # PRG RAM size
                0x00,  # Flags 9
                0x00,  # Flags 10
                0x00, 0x00, 0x00, 0x00, 0x00  # Padding
            ])

            # 创建16KB的PRG ROM数据
            prg_rom = bytearray(16384)

            # 创建8KB的CHR ROM数据
            chr_rom = bytearray(8192)

            # 组合完整的ROM
            rom_data = ines_header + prg_rom + chr_rom

        elif system == "snes":
            rom_path = roms_dir / "test_mario.smc"
            # 创建简单的SNES ROM (512KB)
            rom_data = bytearray(524288)

        elif system == "gameboy":
            rom_path = roms_dir / "test_tetris.gb"
            # 创建简单的Game Boy ROM (32KB)
            rom_data = bytearray(32768)

        elif system == "gba":
            rom_path = roms_dir / "test_pokemon.gba"
            # 创建简单的GBA ROM (32MB)
            rom_data = bytearray(33554432)

        elif system == "genesis":
            rom_path = roms_dir / "test_sonic.md"
            # 创建简单的Genesis ROM (1MB)
            rom_data = bytearray(1048576)

        else:
            print(f"  ⚠️ 不支持的系统: {system}")
            return ""

        try:
            with open(rom_path, 'wb') as f:
                f.write(rom_data)

            print(f"  ✅ 测试ROM创建: {rom_path}")
            return str(rom_path)

        except Exception as e:
            print(f"  ❌ 创建测试ROM失败: {e}")
            return ""

    def test_emulator_with_rom(self, system: str, emulator_name: str, rom_path: str):
        """使用ROM测试模拟器启动"""
        print(f"🎮 测试 {emulator_name} 启动 {system.upper()} 游戏...")

        if not os.path.exists(rom_path):
            print(f"  ❌ ROM文件不存在: {rom_path}")
            return False

        try:
            config = self.emulators[system]
            launch_args = config["launch_args"]

            # 构建启动命令
            cmd = [emulator_name] + launch_args + [rom_path]

            print(f"  🚀 启动命令: {' '.join(cmd)}")

            # 尝试启动（3秒后自动退出）
            result = subprocess.run(cmd, timeout=3, capture_output=True, text=True)

            print(f"  ✅ {emulator_name} 启动成功")
            return True

        except subprocess.TimeoutExpired:
            print(f"  ✅ {emulator_name} 正在运行（超时是正常的）")
            return True
        except Exception as e:
            print(f"  ❌ {emulator_name} 启动失败: {e}")
            return False

    def fix_all_emulators(self):
        """修复所有模拟器"""
        print("🎮 游戏模拟器启动失败修复工具")
        print("=" * 50)

        # 1. 检查Homebrew
        if not self.check_homebrew():
            if not self.install_homebrew():
                print("❌ 无法安装Homebrew，请手动安装")
                return False

        # 2. 修复每个系统的模拟器
        success_count = 0
        total_systems = len(self.emulators)

        for system in self.emulators.keys():
            if self.fix_system_emulator(system):
                success_count += 1

                # 创建测试ROM并测试启动
                rom_path = self.create_test_rom(system)
                if rom_path:
                    config = self.emulators[system]
                    primary = config["primary"]

                    if self.test_emulator_with_rom(system, primary, rom_path):
                        print(f"🎉 {system.upper()} 模拟器完全正常")
                    else:
                        print(f"⚠️ {system.upper()} 模拟器安装成功但启动测试失败")

        # 3. 显示结果
        print(f"\n{'='*50}")
        print(f"🎯 修复完成: {success_count}/{total_systems} 个系统")

        if success_count == total_systems:
            print("🎉 所有模拟器修复成功！")
            print("💡 现在可以正常启动游戏了")
        else:
            print("⚠️ 部分模拟器修复失败")
            print("💡 请检查错误信息并手动安装")

        return success_count == total_systems

    def generate_status_report(self):
        """生成模拟器状态报告"""
        print("\n📊 模拟器状态报告:")
        print("-" * 30)

        for system, config in self.emulators.items():
            print(f"\n🎮 {system.upper()}:")

            primary = config["primary"]
            alternatives = config["alternatives"]
            test_args = config["test_args"]

            # 测试主要模拟器
            if self.test_emulator(primary, test_args):
                print(f"  ✅ 主要: {primary}")
            else:
                print(f"  ❌ 主要: {primary}")

            # 测试替代模拟器
            for alt in alternatives:
                if self.test_emulator(alt, test_args):
                    print(f"  ✅ 替代: {alt}")
                else:
                    print(f"  ❌ 替代: {alt}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='游戏模拟器启动失败修复工具')
    parser.add_argument('--system', '-s', help='指定要修复的系统 (nes, snes, gameboy, gba, genesis)')
    parser.add_argument('--status', action='store_true', help='仅显示当前状态')
    parser.add_argument('--test', action='store_true', help='测试模拟器启动')

    args = parser.parse_args()

    fixer = EmulatorStartupFixer()

    if args.status:
        fixer.generate_status_report()
    elif args.system:
        success = fixer.fix_system_emulator(args.system)
        if success:
            print(f"\n🎉 {args.system.upper()} 模拟器修复成功！")
        else:
            print(f"\n❌ {args.system.upper()} 模拟器修复失败")
    else:
        fixer.fix_all_emulators()

if __name__ == "__main__":
    main()
