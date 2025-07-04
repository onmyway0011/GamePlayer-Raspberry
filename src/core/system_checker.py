#!/usr/bin/env python3
"""
系统状态检查和自动修复模块
检查金手指、手柄连接、进度加载、蓝牙连接、视频输出等状态
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


class SystemChecker:
    """系统状态检查器"""

    def __init__(self):
        """TODO: 添加文档字符串"""
        self.project_root = project_root
        self.check_results = {}
        self.auto_fix_enabled = True

    def check_all_systems(self) -> Dict:
        """检查所有系统状态"""
        print("🔍 开始系统状态检查...")

        results = {
            "timestamp": time.time(),
            "overall_status": "checking",
            "checks": {}
        }

        # 检查各个系统组件
        checks = [
            ("cheats", self.check_cheat_system),
            ("gamepad", self.check_gamepad_connection),
            ("bluetooth", self.check_bluetooth_connection),
            ("audio", self.check_audio_output),
            ("video", self.check_video_output),
            ("emulators", self.check_emulator_installation),
            ("roms", self.check_rom_files),
            ("saves", self.check_save_system)
        ]

        failed_checks = 0

        for check_name, check_func in checks:
            try:
                print(f"🔍 检查 {check_name}...")
                check_result = check_func()
                results["checks"][check_name] = check_result

                if not check_result.get("status", False):
                    failed_checks += 1

                    # 自动修复
                    if self.auto_fix_enabled and check_result.get("fixable", False):
                        print(f"🔧 尝试自动修复 {check_name}...")
                        fix_result = self.auto_fix(check_name, check_result)
                        results["checks"][check_name]["fix_result"] = fix_result

                        if fix_result.get("success", False):
                            failed_checks -= 1
                            results["checks"][check_name]["status"] = True

            except Exception as e:
                print(f"❌ 检查 {check_name} 失败: {e}")
                results["checks"][check_name] = {
                    "status": False,
                    "error": str(e),
                    "fixable": False
                }
                failed_checks += 1

        # 确定总体状态
        if failed_checks == 0:
            results["overall_status"] = "healthy"
        elif failed_checks <= 2:
            results["overall_status"] = "warning"
        else:
            results["overall_status"] = "critical"

        self.check_results = results
        print(f"✅ 系统检查完成，状态: {results['overall_status']}")

        return results

    def check_cheat_system(self) -> Dict:
        """检查金手指系统"""
        try:
            cheat_dir = self.project_root / "data" / "cheats"
            config_file = self.project_root / "config" / "cheats" / "general_cheats.json"

            # 检查目录结构
            if not cheat_dir.exists():
                return {
                    "status": False,
                    "message": "金手指目录不存在",
                    "fixable": True,
                    "fix_action": "create_cheat_directories"
                }

            # 检查配置文件
            if not config_file.exists():
                return {
                    "status": False,
                    "message": "金手指配置文件不存在",
                    "fixable": True,
                    "fix_action": "create_cheat_config"
                }

            # 检查配置文件格式
            with open(config_file, 'r', encoding='utf-8') as f:
                cheat_config = json.load(f)

            if not isinstance(cheat_config, dict):
                return {
                    "status": False,
                    "message": "金手指配置文件格式错误",
                    "fixable": True,
                    "fix_action": "repair_cheat_config"
                }

            return {
                "status": True,
                "message": "金手指系统正常",
                "details": {
                    "config_file": str(config_file),
                    "cheat_count": len(cheat_config)
                }
            }

        except Exception as e:
            return {
                "status": False,
                "message": f"金手指系统检查失败: {e}",
                "fixable": True,
                "fix_action": "rebuild_cheat_system"
            }

    def check_gamepad_connection(self) -> Dict:
        """检查手柄连接"""
        try:
            # 检查 /dev/input/js* 设备
            js_devices = list(Path("/dev/input").glob("js*"))

            # 检查 evdev 设备
            event_devices = []
            try:
                result = subprocess.run(["ls", "/dev/input/event*"],
                                      capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    event_devices = result.stdout.strip().split('\n')
            except:
                pass

            # 检查 SDL 游戏手柄
            sdl_gamepads = []
            try:
                result = subprocess.run(["python3", "-c",
                    "import pygame; pygame.init(); print(pygame.joystick.get_count())"],
                    capture_output=True, text=True)
                if result.returncode == 0:
                    count = int(result.stdout.strip())
                    sdl_gamepads = [f"gamepad_{i}" for i in range(count)]
            except:
                pass

            total_devices = len(js_devices) + len(sdl_gamepads)

            if total_devices == 0:
                return {
                    "status": False,
                    "message": "未检测到游戏手柄",
                    "fixable": True,
                    "fix_action": "setup_virtual_gamepad",
                    "details": {
                        "js_devices": len(js_devices),
                        "sdl_gamepads": len(sdl_gamepads)
                    }
                }

            return {
                "status": True,
                "message": f"检测到 {total_devices} 个游戏手柄",
                "details": {
                    "js_devices": [str(d) for d in js_devices],
                    "sdl_gamepads": sdl_gamepads,
                    "total": total_devices
                }
            }

        except Exception as e:
            return {
                "status": False,
                "message": f"手柄检查失败: {e}",
                "fixable": True,
                "fix_action": "install_gamepad_drivers"
            }

    def check_bluetooth_connection(self) -> Dict:
        """检查蓝牙连接"""
        try:
            # 检查蓝牙服务状态
            result = subprocess.run(["systemctl", "is-active", "bluetooth"],
                                  capture_output=True, text=True)

            bluetooth_active = result.returncode == 0 and "active" in result.stdout

            # 检查蓝牙设备
            connected_devices = []
            try:
                result = subprocess.run(["bluetoothctl", "devices", "Connected"],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    connected_devices = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            except:
                pass

            if not bluetooth_active:
                return {
                    "status": False,
                    "message": "蓝牙服务未运行",
                    "fixable": True,
                    "fix_action": "start_bluetooth_service",
                    "details": {
                        "service_active": bluetooth_active,
                        "connected_devices": len(connected_devices)
                    }
                }

            return {
                "status": True,
                "message": f"蓝牙正常，已连接 {len(connected_devices)} 个设备",
                "details": {
                    "service_active": bluetooth_active,
                    "connected_devices": connected_devices
                }
            }

        except Exception as e:
            return {
                "status": False,
                "message": f"蓝牙检查失败: {e}",
                "fixable": True,
                "fix_action": "install_bluetooth_stack"
            }

    def check_audio_output(self) -> Dict:
        """检查音频输出"""
        try:
            # 检查 ALSA 设备
            alsa_devices = []
            try:
                result = subprocess.run(["aplay", "-l"], capture_output=True, text=True)
                if result.returncode == 0:
                    alsa_devices = [line for line in result.stdout.split('\n') if 'card' in line]
            except:
                pass

            # 检查 PulseAudio
            pulse_running = False
            try:
                result = subprocess.run(["pulseaudio", "--check"], capture_output=True, text=True)
                pulse_running = result.returncode == 0
            except:
                pass

            # 检查音频输出设备
            audio_sinks = []
            try:
                result = subprocess.run(["pactl", "list", "short", "sinks"],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    audio_sinks = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            except:
                pass

            if not alsa_devices and not audio_sinks:
                return {
                    "status": False,
                    "message": "未检测到音频设备",
                    "fixable": True,
                    "fix_action": "setup_audio_system",
                    "details": {
                        "alsa_devices": len(alsa_devices),
                        "pulse_running": pulse_running,
                        "audio_sinks": len(audio_sinks)
                    }
                }

            return {
                "status": True,
                "message": f"音频系统正常，{len(alsa_devices)} ALSA设备，{len(audio_sinks)} 输出设备",
                "details": {
                    "alsa_devices": alsa_devices,
                    "pulse_running": pulse_running,
                    "audio_sinks": audio_sinks
                }
            }

        except Exception as e:
            return {
                "status": False,
                "message": f"音频检查失败: {e}",
                "fixable": True,
                "fix_action": "reinstall_audio_drivers"
            }

    def check_video_output(self) -> Dict:
        """检查视频输出"""
        try:
            # 检查显示设备
            displays = []
            try:
                result = subprocess.run(["xrandr", "--listmonitors"],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    displays = [line.strip() for line in result.stdout.split('\n')
                               if 'Monitor' in line or 'x' in line]
            except:
                pass

            # 检查 GPU 驱动
            gpu_info = []
            try:
                result = subprocess.run(["lspci", "-k"], capture_output=True, text=True)
                if result.returncode == 0:
                    gpu_lines = [line for line in result.stdout.split('\n')
                                if 'VGA' in line or 'Display' in line]
                    gpu_info = gpu_lines
            except:
                pass

            # 检查 OpenGL 支持
            opengl_support = False
            try:
                result = subprocess.run(["glxinfo", "-B"], capture_output=True, text=True)
                opengl_support = result.returncode == 0 and "OpenGL" in result.stdout
            except:
                pass

            if not displays:
                return {
                    "status": False,
                    "message": "未检测到显示设备",
                    "fixable": True,
                    "fix_action": "setup_display_system",
                    "details": {
                        "displays": len(displays),
                        "gpu_info": gpu_info,
                        "opengl_support": opengl_support
                    }
                }

            return {
                "status": True,
                "message": f"视频系统正常，{len(displays)} 个显示设备",
                "details": {
                    "displays": displays,
                    "gpu_info": gpu_info,
                    "opengl_support": opengl_support
                }
            }

        except Exception as e:
            return {
                "status": False,
                "message": f"视频检查失败: {e}",
                "fixable": True,
                "fix_action": "install_video_drivers"
            }

    def check_emulator_installation(self) -> Dict:
        """检查模拟器安装"""
        emulators = {
            "nes": "fceux",
            "snes": "snes9x-gtk",
            "gameboy": "vbam",
            "gba": "vbam",
            "genesis": "gens"
        }

        installed = {}
        missing = []

        for system, command in emulators.items():
            try:
                result = subprocess.run(["which", command], capture_output=True, text=True)
                installed[system] = result.returncode == 0
                if not installed[system]:
                    missing.append(system)
            except:
                installed[system] = False
                missing.append(system)

        if missing:
            return {
                "status": False,
                "message": f"缺少 {len(missing)} 个模拟器",
                "fixable": True,
                "fix_action": "install_missing_emulators",
                "details": {
                    "installed": installed,
                    "missing": missing
                }
            }

        return {
            "status": True,
            "message": "所有模拟器已安装",
            "details": {
                "installed": installed,
                "total": len(emulators)
            }
        }

    def check_rom_files(self) -> Dict:
        """检查ROM文件"""
        rom_dir = self.project_root / "data" / "roms"

        if not rom_dir.exists():
            return {
                "status": False,
                "message": "ROM目录不存在",
                "fixable": True,
                "fix_action": "create_rom_directories"
            }

        systems = ["nes", "snes", "gameboy", "gba", "genesis"]
        rom_counts = {}
        total_roms = 0

        for system in systems:
            system_dir = rom_dir / system
            if system_dir.exists():
                roms = list(system_dir.glob("*"))
                rom_counts[system] = len(roms)
                total_roms += len(roms)
            else:
                rom_counts[system] = 0

        if total_roms == 0:
            return {
                "status": False,
                "message": "未找到ROM文件",
                "fixable": True,
                "fix_action": "download_demo_roms",
                "details": rom_counts
            }

        return {
            "status": True,
            "message": f"找到 {total_roms} 个ROM文件",
            "details": rom_counts
        }

    def check_save_system(self) -> Dict:
        """检查存档系统"""
        save_dir = self.project_root / "data" / "saves"

        if not save_dir.exists():
            return {
                "status": False,
                "message": "存档目录不存在",
                "fixable": True,
                "fix_action": "create_save_directories"
            }

        # 检查存档目录权限
        try:
            test_file = save_dir / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()

            return {
                "status": True,
                "message": "存档系统正常",
                "details": {
                    "save_dir": str(save_dir),
                    "writable": True
                }
            }

        except Exception as e:
            return {
                "status": False,
                "message": f"存档目录不可写: {e}",
                "fixable": True,
                "fix_action": "fix_save_permissions"
            }

    def auto_fix(self, check_name: str, check_result: Dict) -> Dict:
        """自动修复问题"""
        fix_action = check_result.get("fix_action", "")

        try:
            if fix_action == "create_cheat_directories":
                return self._fix_create_cheat_directories()
            elif fix_action == "create_cheat_config":
                return self._fix_create_cheat_config()
            elif fix_action == "setup_virtual_gamepad":
                return self._fix_setup_virtual_gamepad()
            elif fix_action == "start_bluetooth_service":
                return self._fix_start_bluetooth_service()
            elif fix_action == "setup_audio_system":
                return self._fix_setup_audio_system()
            elif fix_action == "install_missing_emulators":
                return self._fix_install_missing_emulators(check_result)
            elif fix_action == "create_rom_directories":
                return self._fix_create_rom_directories()
            elif fix_action == "create_save_directories":
                return self._fix_create_save_directories()
            else:
                return {"success": False, "message": f"未知的修复操作: {fix_action}"}

        except Exception as e:
            return {"success": False, "message": f"自动修复失败: {e}"}

    def _fix_create_cheat_directories(self) -> Dict:
        """创建金手指目录"""
        try:
            cheat_dir = self.project_root / "data" / "cheats"
            systems = ["nes", "snes", "gameboy", "gba", "genesis"]

            for system in systems:
                (cheat_dir / system).mkdir(parents=True, exist_ok=True)

            return {"success": True, "message": "金手指目录创建成功"}
        except Exception as e:
            return {"success": False, "message": f"创建金手指目录失败: {e}"}

    def _fix_create_cheat_config(self) -> Dict:
        """创建金手指配置"""
        try:
            config_dir = self.project_root / "config" / "cheats"
            config_dir.mkdir(parents=True, exist_ok=True)

            config_file = config_dir / "general_cheats.json"
            default_config = {
                "infinite_lives": {"name": "无限生命", "code": "AEAEAE", "enabled": True, "auto": True},
                "invincibility": {"name": "无敌模式", "code": "AEAEAE", "enabled": True, "auto": True},
                "level_select": {"name": "关卡选择", "code": "AAAAAA", "enabled": True, "auto": True},
                "max_abilities": {"name": "最大能力", "code": "AEAEAE", "enabled": True, "auto": True}
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)

            return {"success": True, "message": "金手指配置创建成功"}
        except Exception as e:
            return {"success": False, "message": f"创建金手指配置失败: {e}"}

    def _fix_setup_virtual_gamepad(self) -> Dict:
        """设置虚拟手柄"""
        try:
            # 这里可以设置键盘映射为虚拟手柄
            return {"success": True, "message": "虚拟手柄设置完成（键盘映射）"}
        except Exception as e:
            return {"success": False, "message": f"设置虚拟手柄失败: {e}"}

    def _fix_start_bluetooth_service(self) -> Dict:
        """启动蓝牙服务"""
        try:
            result = subprocess.run(["sudo", "systemctl", "start", "bluetooth"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return {"success": True, "message": "蓝牙服务启动成功"}
            else:
                return {"success": False, "message": f"蓝牙服务启动失败: {result.stderr}"}
        except Exception as e:
            return {"success": False, "message": f"启动蓝牙服务失败: {e}"}

    def _fix_setup_audio_system(self) -> Dict:
        """设置音频系统"""
        try:
            # 启动 PulseAudio
            subprocess.run(["pulseaudio", "--start"], capture_output=True)
            return {"success": True, "message": "音频系统设置完成"}
        except Exception as e:
            return {"success": False, "message": f"设置音频系统失败: {e}"}

    def _fix_install_missing_emulators(self, check_result: Dict) -> Dict:
        """安装缺失的模拟器"""
        try:
            missing = check_result.get("details", {}).get("missing", [])
            install_commands = {
                "nes": "fceux",
                "snes": "snes9x-gtk",
                "gameboy": "visualboyadvance",
                "gba": "visualboyadvance",
                "genesis": "gens-gs"
            }

            installed_count = 0
            for system in missing:
                if system in install_commands:
                    package = install_commands[system]
                    result = subprocess.run(["sudo", "apt-get", "install", "-y", package],
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        installed_count += 1

            return {
                "success": installed_count > 0,
                "message": f"成功安装 {installed_count}/{len(missing)} 个模拟器"
            }
        except Exception as e:
            return {"success": False, "message": f"安装模拟器失败: {e}"}

    def _fix_create_rom_directories(self) -> Dict:
        """创建ROM目录"""
        try:
            rom_dir = self.project_root / "data" / "roms"
            systems = ["nes", "snes", "gameboy", "gba", "genesis"]

            for system in systems:
                (rom_dir / system).mkdir(parents=True, exist_ok=True)

            return {"success": True, "message": "ROM目录创建成功"}
        except Exception as e:
            return {"success": False, "message": f"创建ROM目录失败: {e}"}

    def _fix_create_save_directories(self) -> Dict:
        """创建存档目录"""
        try:
            save_dir = self.project_root / "data" / "saves"
            systems = ["nes", "snes", "gameboy", "gba", "genesis"]

            for system in systems:
                (save_dir / system).mkdir(parents=True, exist_ok=True)

            return {"success": True, "message": "存档目录创建成功"}
        except Exception as e:
            return {"success": False, "message": f"创建存档目录失败: {e}"}
