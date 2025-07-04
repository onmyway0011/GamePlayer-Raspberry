#!/usr/bin/env python3
"""
改进的游戏启动器
解决乱码和加载失败问题，支持GUI模拟器
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class ImprovedGameLauncher:
    """改进的游戏启动器"""

    def __init__(self):
        """TODO: Add docstring"""
        self.project_root = project_root
        self.roms_dir = self.project_root / "data" / "roms"

        # 模拟器配置 - 优先使用GUI版本解决乱码问题
        self.emulators = {
            "nes": [
                {
                    "name": "Nestopia",
                    "type": "gui",
                    "command": "open",
                    "args": ["-a", "Nestopia"],
                    "description": "最佳NES模拟器，完美支持中文"
                },
                {
                    "name": "mednafen",
                    "type": "cli",
                    "command": "mednafen",
                    "args": ["-force_module", "nes"],
                    "description": "命令行NES模拟器"
                }
            ],
            "snes": [
                {
                    "name": "Snes9x",
                    "type": "gui",
                    "command": "open",
                    "args": ["-a", "Snes9x"],
                    "description": "最佳SNES模拟器"
                },
                {
                    "name": "mednafen",
                    "type": "cli",
                    "command": "mednafen",
                    "args": ["-force_module", "snes"],
                    "description": "命令行SNES模拟器"
                }
            ],
            "gameboy": [
                {
                    "name": "Visual Boy Advance-M",
                    "type": "gui",
                    "command": "open",
                    "args": ["-a", "Visual Boy Advance-M"],
                    "description": "Game Boy模拟器"
                },
                {
                    "name": "mednafen",
                    "type": "cli",
                    "command": "mednafen",
                    "args": ["-force_module", "gb"],
                    "description": "命令行Game Boy模拟器"
                }
            ]
        }

    def check_emulator_availability(self, system: str) -> List[Dict]:
        """检查模拟器可用性"""
        print(f"🔍 检查 {system.upper()} 模拟器...")

        available_emulators = []

        if system not in self.emulators:
            print(f"  ❌ 不支持的系统: {system}")
            return available_emulators

        for emulator in self.emulators[system]:
            name = emulator["name"]
            emulator_type = emulator["type"]
            command = emulator["command"]

            try:
                if emulator_type == "gui":
                    # 检查GUI应用是否存在
                    app_name = emulator["args"][1]  # -a 后面的应用名
                    app_path = f"/Applications/{app_name}.app"

                    if Path(app_path).exists():
                        print(f"  ✅ {name} (GUI) - 可用")
                        available_emulators.append(emulator)
                    else:
                        print(f"  ❌ {name} (GUI) - 未安装")

                elif emulator_type == "cli":
                    # 检查命令行工具
                    result = subprocess.run(
                        ["which", command],
                        capture_output=True,
                        timeout=5
                    )

                    if result.returncode == 0:
                        print(f"  ✅ {name} (CLI) - 可用")
                        available_emulators.append(emulator)
                    else:
                        print(f"  ❌ {name} (CLI) - 未安装")

            except Exception as e:
                print(f"  ❌ {name} - 检查失败: {e}")

        return available_emulators

    def launch_game_with_emulator(self, emulator: Dict, rom_path: str) -> Tuple[bool, str, Optional[int]]:
        """使用指定模拟器启动游戏"""
        name = emulator["name"]
        emulator_type = emulator["type"]
        command = emulator["command"]
        args = emulator["args"].copy()

        print(f"🎮 使用 {name} 启动游戏...")
        print(f"📁 ROM文件: {rom_path}")

        try:
            if emulator_type == "gui":
                # GUI模拟器启动方式
                full_command = [command] + args + [rom_path]

                print(f"🚀 启动命令: {' '.join(full_command)}")

                # 启动GUI应用
                process = subprocess.Popen(
                    full_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                # 等待一下确保启动
                time.sleep(2)

                # 检查进程状态
                if process.poll() is None:
                    print(f"  ✅ {name} 启动成功 (PID: {process.pid})")
                    return True, f"游戏启动成功 (PID: {process.pid})", process.pid
                else:
                    stdout, stderr = process.communicate()
                    error_msg = stderr.decode('utf-8') if stderr else stdout.decode('utf-8') if stdout else "进程立即退出"
                    print(f"  ❌ {name} 启动失败: {error_msg}")
                    print(f"  📊 返回码: {process.returncode}")
                    return False, f"启动失败: {error_msg} (返回码: {process.returncode})", None

            elif emulator_type == "cli":
                # 命令行模拟器启动方式
                full_command = [command] + args + [rom_path]

                print(f"🚀 启动命令: {' '.join(full_command)}")

                # 设置环境变量（特别是mednafen）
                env = os.environ.copy()
                env['MEDNAFEN_ALLOWMULTI'] = '1'

                # 启动命令行应用
                process = subprocess.Popen(
                    full_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env
                )

                # 等待一下确保启动
                time.sleep(1)

                # 检查进程状态
                if process.poll() is None:
                    print(f"  ✅ {name} 启动成功 (PID: {process.pid})")
                    return True, f"游戏启动成功 (PID: {process.pid})", process.pid
                else:
                    stdout, stderr = process.communicate()
                    error_msg = stderr.decode('utf-8') if stderr else stdout.decode('utf-8') if stdout else "进程立即退出"
                    print(f"  ❌ {name} 启动失败: {error_msg}")
                    print(f"  📊 返回码: {process.returncode}")
                    return False, f"启动失败: {error_msg} (返回码: {process.returncode})", None

        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ {name} 启动异常: {error_msg}")
            return False, f"启动异常: {error_msg}", None

        return False, "未知错误", None

    def launch_game(self, system: str, game_id: str) -> Tuple[bool, str, Optional[int]]:
        """启动游戏"""
        print(f"🎮 启动游戏: {system}/{game_id}")

        # 查找ROM文件
        rom_extensions = [".nes", ".smc", ".gb", ".gba", ".md", ".bin"]
        rom_path = None

        for ext in rom_extensions:
            potential_path = self.roms_dir / system / f"{game_id}{ext}"
            if potential_path.exists():
                rom_path = str(potential_path)
                break

        if not rom_path:
            error_msg = f"ROM文件不存在: {game_id}"
            print(f"❌ {error_msg}")
            return False, error_msg, None

        # 检查ROM文件大小
        rom_size = Path(rom_path).stat().st_size
        if rom_size == 0:
            error_msg = f"ROM文件为空: {game_id}"
            print(f"❌ {error_msg}")
            return False, error_msg, None

        print(f"📊 ROM文件大小: {rom_size} bytes")

        # 获取可用模拟器
        available_emulators = self.check_emulator_availability(system)

        if not available_emulators:
            error_msg = f"没有可用的 {system.upper()} 模拟器"
            print(f"❌ {error_msg}")
            return False, error_msg, None

        # 尝试使用每个可用模拟器
        for emulator in available_emulators:
            success, message, pid = self.launch_game_with_emulator(emulator, rom_path)

            if success:
                return True, message, pid
            else:
                print(f"  ⚠️ {emulator['name']} 失败，尝试下一个...")

        # 所有模拟器都失败
        error_msg = "所有模拟器都启动失败"
        print(f"❌ {error_msg}")
        return False, error_msg, None

    def test_all_systems(self):
        """测试所有系统的模拟器"""
        print("🧪 测试所有系统的模拟器...")
        print("=" * 50)

        results = {}

        for system in self.emulators.keys():
            print(f"\n🎮 测试 {system.upper()} 系统:")

            available_emulators = self.check_emulator_availability(system)

            results[system] = {
                "available_emulators": len(available_emulators),
                "emulators": [e["name"] for e in available_emulators]
            }

            if available_emulators:
                print(f"  ✅ 可用模拟器: {', '.join(results[system]['emulators'])}")
            else:
                print(f"  ❌ 没有可用模拟器")

        print(f"\n{'='*50}")
        print("📊 测试结果总结:")

        total_systems = len(self.emulators)
        working_systems = sum(1 for r in results.values() if r["available_emulators"] > 0)

        for system, result in results.items():
            count = result["available_emulators"]
            emulators = ", ".join(result["emulators"])
            print(f"  {system.upper()}: {count} 个模拟器 ({emulators})")

        print(f"\n🎯 总体状态: {working_systems}/{total_systems} 个系统可用")

        if working_systems == total_systems:
            print("🎉 所有系统都有可用模拟器！")
        else:
            print("⚠️ 部分系统缺少模拟器")

        return results

    def create_launch_script(self):
        """创建游戏启动脚本"""
        script_content = '''#!/bin/bash
# 游戏启动脚本
# 使用方法: ./launch_game.sh <system> <game_id>

if [ $# -ne 2 ]; then
    echo "使用方法: $0 <system> <game_id>"
    echo "示例: $0 nes Super_Mario_Bros"
    exit 1
fi

SYSTEM=$1
GAME_ID=$2

echo "🎮 启动游戏: $SYSTEM/$GAME_ID"

# 调用Python启动器
python3 src/scripts/improved_game_launcher.py --launch "$SYSTEM" "$GAME_ID"
'''

        script_path = self.project_root / "launch_game.sh"

        with open(script_path, 'w') as f:
            f.write(script_content)

        # 设置执行权限
        os.chmod(script_path, 0o755)

        print(f"✅ 创建启动脚本: {script_path}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='改进的游戏启动器')
    parser.add_argument('--test', action='store_true', help='测试所有模拟器')
    parser.add_argument('--launch', nargs=2, metavar=('SYSTEM', 'GAME_ID'), help='启动游戏')
    parser.add_argument('--create-script', action='store_true', help='创建启动脚本')

    args = parser.parse_args()

    launcher = ImprovedGameLauncher()

    if args.test:
        launcher.test_all_systems()
    elif args.launch:
        system, game_id = args.launch
        success, message, pid = launcher.launch_game(system, game_id)

        if success:
            print(f"🎉 {message}")
        else:
            print(f"❌ {message}")
            sys.exit(1)
    elif args.create_script:
        launcher.create_launch_script()
    else:
        print("🎮 改进的游戏启动器")
        print("使用 --help 查看帮助")
        launcher.test_all_systems()

if __name__ == "__main__":
    main()
