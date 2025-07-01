#!/usr/bin/env python3
"""
NES游戏运行器
自动选择最佳模拟器运行NES游戏
"""

import os
import sys
import subprocess
import time
import signal
import locale
from pathlib import Path
from typing import Optional, List
import shutil

# 设置编码
if sys.platform.startswith('win'):
    # Windows系统
    os.environ['PYTHONIOENCODING'] = 'utf-8'
else:
    # Unix/Linux/macOS系统
    locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 模拟器检测和安装提示


def check_emulator_availability():
    """检查模拟器可用性并提供安装建议"""
    emulators = {
        'fceux': {
            'name': 'FCEUX',
            'install_command': 'sudo apt-get install fceux',
            'description': '经典的NES模拟器'
        },
        'retroarch': {
            'name': 'RetroArch',
            'install_command': 'sudo apt-get install retroarch',
            'description': '多平台模拟器前端'
        },
        'mednafen': {
            'name': 'Mednafen',
            'install_command': 'sudo apt-get install mednafen',
            'description': '多系统模拟器'
        }
    }

    available_emulators = []
    missing_emulators = []

    for emulator, info in emulators.items():
        if subprocess.run(['which', emulator], capture_output=True).returncode == 0:
            available_emulators.append(emulator)
        else:
            missing_emulators.append((emulator, info))

    if not available_emulators:
        print("⚠️ 未检测到可用的NES模拟器")
        print("💡 建议安装以下模拟器之一:")
        for emulator, info in missing_emulators:
            print(f"  • {info['name']}: {info['description']}")
            print(f"    安装命令: {info['install_command']}")
        print("🔧 或者使用内置的Python模拟器")

    return available_emulators


class NESGameRunner:
    """NES游戏运行器"""

    def __init__(self):
        """初始化游戏运行器"""
        self.project_root = project_root
        self.running_process = None

        # 检查模拟器可用性
        check_emulator_availability()

        # 可用的模拟器列表（按优先级排序）
        self.emulators = [
            {
                'name': 'Simple NES Player',
                'command': ['python3', str(self.project_root / 'scripts' / 'simple_nes_player.py')],
                'description': '简单NES播放器（推荐）'
            },
            {
                'name': 'NES Emulator (Python)',
                'command': ['python3', str(self.project_root / 'core' / 'nes_emulator.py')],
                'description': '内置Python NES模拟器'
            },
            {
                'name': 'RetroArch (if available)',
                'command': ['retroarch', '-L'],
                'description': 'RetroArch模拟器'
            },
            {
                'name': 'FCEUX (if available)',
                'command': ['fceux'],
                'description': 'FCEUX模拟器'
            }
        ]

    def check_emulator_availability(self, emulator: dict):
        """检查模拟器是否可用"""
        try:
            if emulator['name'] == 'RetroArch (if available)':
                # 检查RetroArch是否安装
                result = subprocess.run(['which', 'retroarch'],
                                      capture_output=True, text=True)
                return result.returncode == 0

            elif emulator['name'] == 'FCEUX (if available)':
                # 检查FCEUX是否安装
                result = subprocess.run(['which', 'fceux'],
                                      capture_output=True, text=True)
                return result.returncode == 0

            else:
                # 检查Python脚本是否存在
                script_path = Path(emulator['command'][1])
                if script_path.exists():
                    # 额外检查脚本是否可执行
                    try:
                        # 测试脚本是否能正常导入
                        test_cmd = ['python3', '-c', f'import sys; sys.path.insert(0, "{script_path.parent.parent}"); exec(open("{script_path}").read())']
                        result = subprocess.run(test_cmd, capture_output=True, timeout=5)
                        return True  # 如果能导入就认为可用
                    except:
                        return True  # 如果测试失败，仍然认为可用
                return False

        except Exception:
            return False

    def get_available_emulators(self):
        """自动检测系统中可用的NES模拟器"""
        emulator_candidates = [
            {"name": "Nestopia", "command": [shutil.which("nestopia")], "priority": 1},
            {"name": "FCEUX", "command": [shutil.which("fceux")], "priority": 2},
            {"name": "Mesen", "command": [shutil.which("mesen")], "priority": 3},
            {"name": "VirtuaNES", "command": [shutil.which("virtuanes")], "priority": 4},
            {"name": "Mednafen", "command": [shutil.which("mednafen"), "-nes.input.port1", "gamepad"], "priority": 5},
            {"name": "RetroArch (if available)", "command": [shutil.which("retroarch"), "-L"], "priority": 6},
        ]
        available = []
        for emu in emulator_candidates:
            if emu["command"][0]:
                available.append(emu)

        # 如果没有检测到外部模拟器，添加内置Python模拟器
        if not available:
            available.append({
                "name": "内置Python模拟器",
                "command": [sys.executable, "src/scripts/simple_nes_player.py"],
                "priority": 999
            })

        # 按优先级排序
        available.sort(key=lambda x: x["priority"])
        return available

    def validate_rom(self, rom_path: str):
        """验证ROM文件"""
        try:
            rom_file = Path(rom_path)

            if not rom_file.exists():
                print(f"❌ ROM文件不存在: {rom_path}")
                return False

            if rom_file.suffix.lower() not in ['.nes']:
                print(f"❌ 不支持的文件格式: {rom_file.suffix}")
                return False

            # 检查文件大小
            file_size = rom_file.stat().st_size
            if file_size < 16:  # 至少需要16字节的头部
                print(f"❌ ROM文件太小: {file_size} bytes")
                return False

            # 检查NES头部
            with open(rom_file, 'rb') as f:
                header = f.read(16)
                if len(header) < 16:
                    print(f"❌ ROM文件头部不完整")
                    return False

                if header[:4] != b'NES\x1a':
                    print(f"❌ 不是有效的NES ROM文件（缺少NES头部标识）")
                    print(f"   期望: NES\\x1a")
                    print(f"   实际: {header[:4]}")
                    return False

            print(f"✅ ROM文件验证通过: {rom_file.name}")
            print(f"   文件大小: {file_size} bytes")
            return True

        except Exception as e:
            print(f"❌ ROM验证失败: {e}")
            return False

    def run_with_emulator(self, emulator: dict, rom_path: str):
        """使用指定模拟器运行游戏"""
        try:
            print(f"🎮 使用 {emulator['name']} 启动游戏...")

            # 构建命令
            cmd = emulator['command'].copy()

            if emulator['name'] == 'RetroArch (if available)':
                # RetroArch需要指定核心
                cmd.extend(['/usr/lib/libretro/nestopia_libretro.so', rom_path])
            else:
                cmd.append(rom_path)

            print(f"执行命令: {' '.join(cmd)}")

            # 设置环境变量
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUNBUFFERED'] = '1'

            # 启动进程
            self.running_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None  # 创建新的进程组
            )

            # 等待一小段时间检查是否成功启动
            time.sleep(2)

            if self.running_process.poll() is None:
                print(f"✅ 游戏启动成功！")
                print(f"📋 控制说明:")
                print(f"   - WASD/方向键: 移动")
                print(f"   - 空格/Z: A按钮")
                print(f"   - Shift/X: B按钮")
                print(f"   - Enter: Start")
                print(f"   - Tab: Select")
                print(f"   - P: 暂停")
                print(f"   - ESC: 退出")
                print(f"")
                print(f"🎮 正在运行游戏，按Ctrl+C退出...")

                # 等待游戏进程结束
                try:
                    self.running_process.wait()
                    print(f"👋 游戏已退出")
                    return True
                except KeyboardInterrupt:
                    print(f"\n🛑 用户中断游戏")
                    self.stop_game()
                    return True
            else:
                # 获取错误信息
                stdout, stderr = self.running_process.communicate()
                error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "未知错误"
                print(f"❌ 游戏启动失败: {error_msg}")
                return False

        except FileNotFoundError:
            print(f"❌ 模拟器不存在: {emulator['command'][0]}")
            return False
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            return False

    def stop_game(self):
        """停止游戏"""
        if self.running_process:
            try:
                if hasattr(os, 'killpg'):
                    # Unix系统：发送SIGTERM信号给整个进程组
                    os.killpg(os.getpgid(self.running_process.pid), signal.SIGTERM)
                else:
                    # Windows系统：直接终止进程
                    self.running_process.terminate()

                # 等待进程结束
                self.running_process.wait(timeout=5)
                print("✅ 游戏进程已停止")
            except subprocess.TimeoutExpired:
                # 如果进程没有响应，强制杀死
                if hasattr(os, 'killpg'):
                    os.killpg(os.getpgid(self.running_process.pid), signal.SIGKILL)
                else:
                    self.running_process.kill()
                print("⚠️ 强制停止游戏进程")
            except Exception as e:
                print(f"⚠️ 停止游戏时出错: {e}")
            finally:
                self.running_process = None

    def run_game_with_fallback(self, rom_path: str, emulator_name: Optional[str] = None):
        """运行游戏，支持模拟器自动切换"""
        print(f"🚀 准备运行NES游戏: {Path(rom_path).name}")

        # 验证ROM文件
        if not self.validate_rom(rom_path):
            return False

        # 获取可用模拟器
        available_emulators = self.get_available_emulators()

        if not available_emulators:
            print("❌ 没有可用的模拟器")
            return False

        # 选择模拟器
        if emulator_name:
            # 使用指定的模拟器
            selected_emulator = None
            for emulator in available_emulators:
                if emulator_name.lower() in emulator['name'].lower():
                    selected_emulator = emulator
                    break

            if not selected_emulator:
                print(f"❌ 指定的模拟器不可用: {emulator_name}")
                print("可用的模拟器:")
                for i, emulator in enumerate(available_emulators):
                    print(f"  {i+1}. {emulator['name']}")
                return False
        else:
            # 使用第一个可用的模拟器
            selected_emulator = available_emulators[0]

        # 尝试运行游戏，如果失败则自动切换模拟器
        for i, emulator in enumerate(available_emulators):
            print(f"\n🎮 尝试使用模拟器 {i+1}/{len(available_emulators)}: {emulator['name']}")

            success = self.run_with_emulator(emulator, rom_path)
            if success:
                print(f"✅ 使用 {emulator['name']} 成功运行游戏")
                return True
            else:
                print(f"❌ {emulator['name']} 运行失败")
                if i < len(available_emulators) - 1:
                    print(f"🔄 自动切换到下一个模拟器...")
                    time.sleep(1)  # 短暂等待
                else:
                    print(f"❌ 所有模拟器都无法运行游戏")
                    return False

        return False

    def run_game(self, rom_path: str, emulator_name: Optional[str] = None):
        """运行游戏（保持向后兼容）"""
        return self.run_game_with_fallback(rom_path, emulator_name)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="NES游戏运行器")
    parser.add_argument("rom", nargs="?", help="ROM文件路径")
    parser.add_argument("--emulator", help="指定模拟器名称")
    parser.add_argument("--list-emulators", action="store_true", help="列出可用模拟器")

    args = parser.parse_args()

    runner = NESGameRunner()

    if args.list_emulators:
        print("🎮 可用的NES模拟器:")
        available = runner.get_available_emulators()
        if not available:
            print("❌ 没有可用的模拟器")
        return

    if not args.rom:
        print("❌ 请指定ROM文件路径")
        parser.print_help()
        sys.exit(1)

    # 设置信号处理
    def signal_handler(signum, frame):
        """信号处理函数"""
        print(f"\n🛑 收到信号 {signum}，正在停止游戏...")
        runner.stop_game()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        success = runner.run_game(args.rom, args.emulator)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
