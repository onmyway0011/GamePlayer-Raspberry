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
from pathlib import Path
from typing import Optional, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class NESGameRunner:
    """NES游戏运行器"""

    def __init__(self):
        """TODO: Add docstring"""
        self.project_root = project_root
        self.running_process = None

        # 可用的模拟器列表（按优先级排序）
        self.emulators = [
            {
                'name': 'NES Emulator (Python)',
                'command': ['python3', str(self.project_root / 'core' / 'nes_emulator.py')],
                'description': '内置Python NES模拟器'
            },
            {
                'name': 'Simple NES Player',
                'command': ['python3', str(self.project_root / 'scripts' / 'simple_nes_player.py')],
                'description': '简单NES播放器'
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
                return script_path.exists()

        except Exception:
            return False

    def get_available_emulators(self) -> List[dict]:
        """获取可用的模拟器列表"""
        available = []

        for emulator in self.emulators:
            if self.check_emulator_availability(emulator):
                available.append(emulator)
                print(f"✅ {emulator['name']} - {emulator['description']}")
            else:
                print(f"❌ {emulator['name']} - 不可用")

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
                header = f.read(4)
                if header != b'NES\x1a':
                    print(f"❌ 不是有效的NES ROM文件")
                    return False

            print(f"✅ ROM文件验证通过: {rom_file.name}")
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

            # 启动进程
            self.running_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # 创建新的进程组
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
                error_msg = stderr.decode() if stderr else "未知错误"
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
                # 发送SIGTERM信号给整个进程组
                os.killpg(os.getpgid(self.running_process.pid), signal.SIGTERM)

                # 等待进程结束
                self.running_process.wait(timeout=5)
                print("✅ 游戏进程已停止")
            except subprocess.TimeoutExpired:
                # 如果进程没有响应，强制杀死
                os.killpg(os.getpgid(self.running_process.pid), signal.SIGKILL)
                print("⚠️ 强制停止游戏进程")
            except Exception as e:
                print(f"⚠️ 停止游戏时出错: {e}")
            finally:
                self.running_process = None

    def run_game(self, rom_path: str, emulator_name: Optional[str] = None):
        """运行游戏"""
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

        # 运行游戏
        return self.run_with_emulator(selected_emulator, rom_path)


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
        """TODO: Add docstring"""
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
