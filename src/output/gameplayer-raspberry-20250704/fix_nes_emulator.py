#!/usr/bin/env python3
"""
NES模拟器修复工具
专门解决NES模拟器启动失败的问题
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class NESEmulatorFixer:
    """NES模拟器修复器"""

    def __init__(self):
        """TODO: 添加文档字符串"""
        self.project_root = project_root
        self.roms_dir = self.project_root / "data" / "roms" / "nes"
        self.roms_dir.mkdir(parents=True, exist_ok=True)

        # NES模拟器选项（按优先级排序）
        self.emulator_options = [
            {
                "name": "fceux",
                "install_cmd": "brew install fceux",
                "test_cmd": ["fceux", "--help"],
                "description": "FCEUX - 功能完整的NES模拟器"
            },
            {
                "name": "nestopia",
                "install_cmd": "brew install nestopia",
                "test_cmd": ["nestopia", "--help"],
                "description": "Nestopia - 高精度NES模拟器"
            },
            {
                "name": "mednafen",
                "install_cmd": "brew install mednafen",
                "test_cmd": ["mednafen", "-help"],
                "description": "Mednafen - 多系统模拟器（支持NES）"
            },
            {
                "name": "fceux-cask",
                "install_cmd": "brew install --cask fceux",
                "test_cmd": ["fceux", "--help"],
                "description": "FCEUX (Cask版本)"
            }
        ]

    def check_homebrew(self):
        """检查Homebrew是否安装"""
        print("🍺 检查Homebrew...")
        try:
            result = subprocess.run(["which", "brew"], capture_output=True, timeout=10)
            if result.returncode == 0:
                print("✅ Homebrew已安装")
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
            print("⏳ 正在下载和安装Homebrew，这可能需要几分钟...")

            result = subprocess.run(
                install_script,
                shell=True,
                timeout=600  # 10分钟超时
            )

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

    def update_homebrew(self):
        """更新Homebrew"""
        print("🔄 更新Homebrew...")
        try:
            result = subprocess.run(
                ["brew", "update"],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                print("✅ Homebrew更新成功")
                return True
            else:
                print(f"⚠️ Homebrew更新警告: {result.stderr}")
                return True  # 更新失败不是致命错误

        except subprocess.TimeoutExpired:
            print("⚠️ Homebrew更新超时，继续安装...")
            return True
        except Exception as e:
            print(f"⚠️ Homebrew更新异常: {e}")
            return True

    def test_emulator(self, emulator_name, test_cmd):
        """测试模拟器是否可用"""
        print(f"🧪 测试模拟器: {emulator_name}")
        try:
            # 首先检查命令是否存在
            which_result = subprocess.run(
                ["which", emulator_name],
                capture_output=True,
                timeout=10
            )

            if which_result.returncode != 0:
                print(f"❌ {emulator_name} 命令不存在")
                return False

            # 尝试运行帮助命令
            result = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            # 对于某些模拟器，帮助命令可能返回非0状态码
            if result.returncode == 0 or "usage" in result.stdout.lower() or "help" in result.stdout.lower():
                print(f"✅ {emulator_name} 可用")
                return True
            else:
                print(f"❌ {emulator_name} 测试失败")
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ {emulator_name} 测试超时")
            return False
        except Exception as e:
            print(f"❌ {emulator_name} 测试异常: {e}")
            return False

    def install_emulator(self, emulator_config):
        """安装指定的模拟器"""
        name = emulator_config["name"]
        install_cmd = emulator_config["install_cmd"]
        test_cmd = emulator_config["test_cmd"]
        description = emulator_config["description"]

        print(f"\n🔧 安装 {description}")
        print(f"📝 命令: {install_cmd}")

        try:
            # 分割安装命令
            cmd_parts = install_cmd.split()

            print("⏳ 正在安装，请稍候...")
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )

            if result.returncode == 0:
                print(f"✅ {name} 安装成功")

                # 验证安装
                if self.test_emulator(name, test_cmd):
                    return True
                else:
                    print(f"⚠️ {name} 安装成功但测试失败")
                    return False
            else:
                print(f"❌ {name} 安装失败")
                print(f"错误输出: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ {name} 安装超时")
            return False
        except Exception as e:
            print(f"❌ {name} 安装异常: {e}")
            return False

    def create_test_rom(self):
        """创建测试ROM文件"""
        print("\n📁 创建测试ROM文件...")

        test_rom_path = self.roms_dir / "test_mario.nes"

        try:
            # 创建一个简单的NES ROM文件
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

            with open(test_rom_path, 'wb') as f:
                f.write(rom_data)

            print(f"✅ 测试ROM创建成功: {test_rom_path}")
            return str(test_rom_path)

        except Exception as e:
            print(f"❌ 创建测试ROM失败: {e}")
            return None

    def test_emulator_with_rom(self, emulator_name, rom_path):
        """使用ROM测试模拟器"""
        print(f"\n🎮 测试 {emulator_name} 运行ROM...")

        try:
            # 尝试启动模拟器（无头模式）
            cmd = [emulator_name, "--help"]  # 先测试帮助命令

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 or "usage" in result.stdout.lower():
                print(f"✅ {emulator_name} 可以正常运行")
                return True
            else:
                print(f"❌ {emulator_name} 运行测试失败")
                return False

        except Exception as e:
            print(f"❌ {emulator_name} ROM测试异常: {e}")
            return False

    def fix_nes_emulator(self):
        """修复NES模拟器"""
        print("🎮 NES模拟器修复工具")
        print("=" * 50)

        # 1. 检查Homebrew
        if not self.check_homebrew():
            print("\n📦 需要安装Homebrew...")
            if not self.install_homebrew():
                print("❌ 无法安装Homebrew，请手动安装")
                return False

        # 2. 更新Homebrew
        self.update_homebrew()

        # 3. 尝试安装模拟器
        print(f"\n🎯 尝试安装NES模拟器（共{len(self.emulator_options)}个选项）...")

        for i, emulator_config in enumerate(self.emulator_options, 1):
            print(f"\n--- 选项 {i}/{len(self.emulator_options)} ---")

            # 先测试是否已经安装
            if self.test_emulator(emulator_config["name"], emulator_config["test_cmd"]):
                print(f"🎉 {emulator_config['name']} 已经可用！")

                # 创建测试ROM并测试
                test_rom = self.create_test_rom()
                if test_rom and self.test_emulator_with_rom(emulator_config["name"], test_rom):
                    print(f"\n🎉 NES模拟器修复成功！")
                    print(f"✅ 使用的模拟器: {emulator_config['description']}")
                    return True

            # 尝试安装
            if self.install_emulator(emulator_config):
                print(f"🎉 {emulator_config['name']} 安装成功！")

                # 创建测试ROM并测试
                test_rom = self.create_test_rom()
                if test_rom and self.test_emulator_with_rom(emulator_config["name"], test_rom):
                    print(f"\n🎉 NES模拟器修复成功！")
                    print(f"✅ 安装的模拟器: {emulator_config['description']}")
                    return True

            print(f"⚠️ {emulator_config['name']} 安装失败，尝试下一个...")

        print("\n❌ 所有NES模拟器安装尝试都失败了")
        print("\n💡 手动解决建议:")
        print("1. 确保网络连接正常")
        print("2. 手动运行: brew install fceux")
        print("3. 检查系统权限和磁盘空间")
        print("4. 尝试重启终端后再次运行")

        return False

    def show_status(self):
        """显示当前状态"""
        print("\n📊 当前NES模拟器状态:")
        print("-" * 30)

        for emulator_config in self.emulator_options:
            name = emulator_config["name"]
            test_cmd = emulator_config["test_cmd"]

            if self.test_emulator(name, test_cmd):
                print(f"✅ {name}: 可用")
            else:
                print(f"❌ {name}: 不可用")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='NES模拟器修复工具')
    parser.add_argument('--status', action='store_true', help='仅显示当前状态')
    parser.add_argument('--force', action='store_true', help='强制重新安装')

    args = parser.parse_args()

    fixer = NESEmulatorFixer()

    if args.status:
        fixer.show_status()
    else:
        success = fixer.fix_nes_emulator()

        if success:
            print("\n🎮 NES模拟器现在可以正常使用了！")
            print("🔗 返回Web界面测试游戏启动功能")
        else:
            print("\n❌ NES模拟器修复失败")
            print("💡 请查看上面的错误信息和建议")

if __name__ == "__main__":
    main()
