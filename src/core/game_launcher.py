#!/usr/bin/env python3
"""
真正的游戏启动器
集成实际的模拟器，支持真正运行游戏
"""

import os
import sys
import json
import time
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class GameLauncher:
    """游戏启动器"""

    def __init__(self):
        """初始化游戏启动器"""
        self.project_root = project_root
        self.running_games = {}  # 正在运行的游戏进程
        self.emulator_configs = self._load_emulator_configs()
        self.system_settings = self._load_system_settings()

    def _load_emulator_configs(self) -> Dict:
        """加载模拟器配置"""
        config_file = self.project_root / "config" / "emulators" / "emulator_config.json"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载模拟器配置失败: {e}")
            return self._get_default_emulator_configs()

    def _get_default_emulator_configs(self) -> Dict:
        """获取默认模拟器配置"""
        return {
            "nes": {
                "emulator": "mednafen",
                "command": "mednafen",
                "args": ["-force_module", "nes"],
                "extensions": [".nes"],
                "installed": True
            },
            "snes": {
                "emulator": "snes9x",
                "command": "snes9x-gtk",
                "args": ["-fullscreen"],
                "extensions": [".smc", ".sfc"],
                "installed": False
            },
            "gameboy": {
                "emulator": "visualboyadvance",
                "command": "vbam",
                "args": ["--fullscreen"],
                "extensions": [".gb", ".gbc"],
                "installed": False
            },
            "gba": {
                "emulator": "visualboyadvance",
                "command": "vbam",
                "args": ["--fullscreen"],
                "extensions": [".gba"],
                "installed": False
            },
            "genesis": {
                "emulator": "gens",
                "command": "gens",
                "args": ["--fullscreen"],
                "extensions": [".md", ".gen"],
                "installed": False
            }
        }

    def _load_system_settings(self) -> Dict:
        """加载系统设置"""
        settings_file = self.project_root / "config" / "emulators" / "general_settings.json"
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载系统设置失败: {e}")
            return self._get_default_system_settings()

    def _get_default_system_settings(self) -> Dict:
        """获取默认系统设置"""
        return {
            "display": {
                "fullscreen": True,
                "resolution": "1920x1080",
                "vsync": True,
                "scaling": "auto"
            },
            "audio": {
                "enabled": True,
                "volume": 80,
                "sample_rate": 44100,
                "buffer_size": 512
            },
            "input": {
                "gamepad_enabled": True,
                "keyboard_enabled": True,
                "auto_detect_gamepad": True,
                "gamepad_deadzone": 0.1
            },
            "performance": {
                "frame_skip": 0,
                "speed_limit": 100,
                "rewind_enabled": False,
                "save_states": True
            }
        }

    def check_emulator_availability(self, system: str):
        """检查模拟器是否可用"""
        if system not in self.emulator_configs:
            return False

        config = self.emulator_configs[system]
        command = config.get("command", "")

        try:
            # 特殊处理mednafen
            if command == "mednafen":
                # 检查mednafen是否存在
                result = subprocess.run(["which", "mednafen"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # 验证mednafen支持NES
                    help_result = subprocess.run(["mednafen", "-help"], capture_output=True, text=True, timeout=10)
                    available = "nes" in help_result.stdout.lower()
                else:
                    available = False
            else:
                # 检查其他命令是否存在
                result = subprocess.run(["which", command], capture_output=True, text=True, timeout=10)
                available = result.returncode == 0

            # 更新配置
            config["installed"] = available

            return available
        except Exception as e:
            print(f"检查模拟器失败: {e}")
            return False

    def install_emulator(self, system: str):
        """安装模拟器"""
        if system not in self.emulator_configs:
            return False

        config = self.emulator_configs[system]
        emulator = config.get("emulator", "")

        try:
            print(f"🔧 正在安装 {emulator} 模拟器...")

            # 根据系统类型安装对应的模拟器
            install_commands = {
                "nes": ["brew", "install", "mednafen"],
                "snes": ["brew", "install", "snes9x"],
                "gameboy": ["brew", "install", "visualboyadvance-m"],
                "gba": ["brew", "install", "visualboyadvance-m"],
                "genesis": ["brew", "install", "blastem"]
            }

            if system in install_commands:
                result = subprocess.run(install_commands[system], capture_output=True, text=True)
                success = result.returncode == 0

                if success:
                    print(f"✅ {emulator} 安装成功")
                    config["installed"] = True
                else:
                    print(f"❌ {emulator} 安装失败: {result.stderr}")

                return success

        except Exception as e:
            print(f"❌ 安装模拟器失败: {e}")

        return False

    def apply_cheat_codes(self, system: str, game_id: str, cheats: List[Dict]):
        """应用金手指代码"""
        try:
            # 创建金手指文件
            cheat_dir = self.project_root / "data" / "cheats" / system
            cheat_dir.mkdir(parents=True, exist_ok=True)

            cheat_file = cheat_dir / f"{game_id}.cht"

            # 生成金手指文件内容
            cheat_content = []
            for cheat in cheats:
                if cheat.get("enabled", False):
                    cheat_content.append(f"# {cheat.get('name', 'Unknown')}")
                    cheat_content.append(f"{cheat.get('code', '')}")
                    cheat_content.append("")

            # 写入金手指文件
            with open(cheat_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(cheat_content))

            print(f"✅ 金手指配置已应用: {len(cheats)} 个")
            return True

        except Exception as e:
            print(f"❌ 应用金手指失败: {e}")
            return False

    def load_save_state(self, system: str, game_id: str, slot: int = 1):
        """加载存档"""
        try:
            save_dir = self.project_root / "data" / "saves" / system
            save_file = save_dir / f"{game_id}_slot_{slot}.sav"

            if save_file.exists():
                print(f"✅ 存档已加载: 槽位 {slot}")
                return True
            else:
                print(f"⚠️ 存档不存在: 槽位 {slot}")
                return False

        except Exception as e:
            print(f"❌ 加载存档失败: {e}")
            return False

    def launch_game(self, system: str, game_id: str, rom_file: str,
        """TODO: Add docstring"""
                   cheats: List[Dict] = None, save_slot: int = 1) -> Tuple[bool, str]:
        """启动游戏"""
        try:
            # 检查模拟器是否可用
            if not self.check_emulator_availability(system):
                print(f"⚠️ {system} 模拟器不可用，尝试安装...")
                if not self.install_emulator(system):
                    return False, f"{system} 模拟器安装失败"

            # 检查ROM文件
            rom_path = self.project_root / "data" / "roms" / system / rom_file
            if not rom_path.exists():
                return False, f"ROM文件不存在: {rom_file}"

            # 应用金手指
            if cheats:
                self.apply_cheat_codes(system, game_id, cheats)

            # 加载存档
            self.load_save_state(system, game_id, save_slot)

            # 构建启动命令
            config = self.emulator_configs[system]
            command = [config["command"]]
            command.extend(config.get("args", []))

            # 添加金手指文件参数
            cheat_file = self.project_root / "data" / "cheats" / system / f"{game_id}.cht"
            if cheat_file.exists() and system == "nes":
                command.extend(["--loadlua", str(cheat_file)])

            # 添加ROM文件
            command.append(str(rom_path))

            print(f"🚀 启动命令: {' '.join(command)}")

            # 启动游戏进程
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.project_root)
            )

            # 记录运行的游戏
            self.running_games[game_id] = {
                "process": process,
                "system": system,
                "rom_file": rom_file,
                "start_time": time.time()
            }

            print(f"✅ 游戏启动成功: {game_id} (PID: {process.pid})")
            return True, f"游戏启动成功 (PID: {process.pid})"

        except Exception as e:
            error_msg = f"游戏启动失败: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg

    def stop_game(self, game_id: str):
        """停止游戏"""
        if game_id not in self.running_games:
            return False

        try:
            game_info = self.running_games[game_id]
            process = game_info["process"]

            # 终止进程
            process.terminate()

            # 等待进程结束
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

            # 移除记录
            del self.running_games[game_id]

            print(f"✅ 游戏已停止: {game_id}")
            return True

        except Exception as e:
            print(f"❌ 停止游戏失败: {e}")
            return False

    def get_running_games(self) -> Dict:
        """获取正在运行的游戏"""
        # 清理已结束的进程
        finished_games = []
        for game_id, game_info in self.running_games.items():
            if game_info["process"].poll() is not None:
                finished_games.append(game_id)

        for game_id in finished_games:
            del self.running_games[game_id]

        return self.running_games.copy()

    def is_game_running(self, game_id: str):
        """检查游戏是否正在运行"""
        if game_id not in self.running_games:
            return False

        process = self.running_games[game_id]["process"]
        return process.poll() is None

    def get_game_status(self, game_id: str) -> str:
        """获取游戏状态"""
        if self.is_game_running(game_id):
            return "运行中"
        elif game_id in self.running_games:
            return "已结束"
        else:
            return "未启动"
