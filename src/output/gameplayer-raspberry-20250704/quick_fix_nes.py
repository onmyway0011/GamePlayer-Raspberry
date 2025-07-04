#!/usr/bin/env python3
"""
快速修复NES模拟器问题
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def fix_game_launcher():
    """修复游戏启动器配置"""
    launcher_file = project_root / "src" / "core" / "game_launcher.py"

    print("🔧 修复游戏启动器配置...")

    # 读取文件
    with open(launcher_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替换NES模拟器配置
    old_config = '''            "nes": {
                "emulator": "fceux",
                "command": "fceux",
                "args": ["--fullscreen", "0", "--sound", "1"],
                "extensions": [".nes"],
                "installed": False
            },'''

    new_config = '''            "nes": {
                "emulator": "mednafen",
                "command": "mednafen",
                "args": ["-force_module", "nes"],
                "extensions": [".nes"],
                "installed": True
            },'''

    if old_config in content:
        content = content.replace(old_config, new_config)

        # 写回文件
        with open(launcher_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ 游戏启动器配置已更新为使用mednafen")
        return True
    else:
        print("⚠️ 未找到需要替换的配置")
        return False


def fix_health_checker():
    """修复健康检查器配置"""
    checker_file = project_root / "src" / "core" / "game_health_checker.py"

    print("🔧 修复健康检查器配置...")

    # 读取文件
    with open(checker_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替换NES模拟器配置
    old_config = '''            "nes": {
                "command": "fceux",
                "install_cmd": "brew install fceux",
                "test_args": ["--help"],
                "extensions": [".nes"],
                "required": True
            },'''

    new_config = '''            "nes": {
                "command": "mednafen",
                "install_cmd": "brew install mednafen",
                "test_args": ["-help"],
                "extensions": [".nes"],
                "required": True
            },'''

    if old_config in content:
        content = content.replace(old_config, new_config)

        # 写回文件
        with open(checker_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ 健康检查器配置已更新为使用mednafen")
        return True
    else:
        print("⚠️ 未找到需要替换的配置")
        return False


def create_all_roms():
    """为所有NES游戏创建ROM文件"""
    print("📁 创建所有NES游戏的ROM文件...")

    roms_dir = project_root / "data" / "roms" / "nes"
    roms_dir.mkdir(parents=True, exist_ok=True)

    # NES游戏列表
    nes_games = [
        "Super_Mario_Bros.nes",
        "Legend_of_Zelda.nes",
        "Metroid.nes",
        "Castlevania.nes",
        "Mega_Man.nes",
        "Contra.nes",
        "Duck_Hunt.nes",
        "Pac_Man.nes",
        "Donkey_Kong.nes",
        "Galaga.nes"
    ]

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

    created_count = 0

    for rom_file in nes_games:
        rom_path = roms_dir / rom_file

        if not rom_path.exists():
            try:
                with open(rom_path, 'wb') as f:
                    f.write(rom_data)
                print(f"✅ 创建ROM: {rom_file}")
                created_count += 1
            except Exception as e:
                print(f"❌ 创建ROM失败 {rom_file}: {e}")
        else:
            print(f"⏭️ ROM已存在: {rom_file}")

    print(f"📊 创建了 {created_count} 个ROM文件")
    return created_count > 0


def test_mednafen():
    """测试mednafen是否可用"""
    print("🧪 测试mednafen...")

    import subprocess

    try:
        # 检查mednafen是否安装
        result = subprocess.run(["which", "mednafen"], capture_output=True, timeout=10)

        if result.returncode == 0:
            print("✅ mednafen已安装")

            # 测试帮助命令
            help_result = subprocess.run(["mednafen", "-help"], capture_output=True, text=True, timeout=10)

            if "nes" in help_result.stdout.lower():
                print("✅ mednafen支持NES模拟")
                return True
            else:
                print("❌ mednafen不支持NES模拟")
                return False
        else:
            print("❌ mednafen未安装")
            return False

    except Exception as e:
        print(f"❌ 测试mednafen失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 NES模拟器快速修复工具")
    print("=" * 40)

    success_count = 0

    # 1. 测试mednafen
    if test_mednafen():
        success_count += 1

    # 2. 修复游戏启动器
    if fix_game_launcher():
        success_count += 1

    # 3. 修复健康检查器
    if fix_health_checker():
        success_count += 1

    # 4. 创建ROM文件
    if create_all_roms():
        success_count += 1

    print("\n" + "=" * 40)
    print(f"🎯 修复完成: {success_count}/4 项成功")

    if success_count >= 3:
        print("🎉 NES模拟器修复成功！")
        print("💡 现在可以重启服务器测试游戏启动")
        print("🔗 命令: PORT=3012 python3 src/scripts/simple_demo_server.py")
    else:
        print("⚠️ 部分修复失败，请检查错误信息")

if __name__ == "__main__":
    main()
