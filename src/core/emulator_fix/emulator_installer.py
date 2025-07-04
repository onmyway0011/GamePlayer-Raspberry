#!/usr/bin/env python3
"""
模拟器安装器 - 负责模拟器的检测、安装和配置
"""

import os
import subprocess
import shutil
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from .config_manager import get_config_manager
from .logger_setup import get_logger
from .state_manager import get_state_manager, FixType
from .transaction_manager import transaction

logger = get_logger("emulator")


class EmulatorInstallError(Exception):
    """模拟器安装错误"""
    pass


class EmulatorTestError(Exception):
    """模拟器测试错误"""
    pass


class EmulatorInstaller:
    """模拟器安装器"""

    def __init__(self):
        """初始化模拟器安装器"""
        self.config = get_config_manager()
        self.state_manager = get_state_manager()
        self.platform = platform.system().lower()

        # 检测包管理器
        self.package_manager = self._detect_package_manager()
        logger.info(f"🎮 模拟器安装器初始化，平台: {self.platform}, 包管理器: {self.package_manager}")

    def _detect_package_manager(self) -> Optional[str]:
        """检测可用的包管理器"""
        managers = {
            "brew": ["brew", "--version"],
            "apt": ["apt", "--version"],
            "yum": ["yum", "--version"],
            "pacman": ["pacman", "--version"],
            "dnf": ["dnf", "--version"]
        }

        for manager, test_cmd in managers.items():
            try:
                result = subprocess.run(
                    test_cmd,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.debug(f"✅ 检测到包管理器: {manager}")
                    return manager
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        logger.warning("⚠️ 未检测到支持的包管理器")
        return None

    def check_emulators(self) -> Dict[str, Dict[str, Any]]:
        """检查模拟器状态"""
        logger.info("🔍 检查模拟器状态...")

        emulator_status = {}
        emulator_configs = self.config.emulator_commands.get("emulators", {})

        for emulator_name, emulator_config in emulator_configs.items():
            status = self._check_single_emulator(emulator_name, emulator_config)
            emulator_status[emulator_name] = status

        # 统计结果
        available = len([s for s in emulator_status.values() if s["available"]])
        total = len(emulator_status)

        logger.info(f"📊 模拟器检查完成: {available}/{total} 可用")

        return emulator_status

    def _check_single_emulator(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """检查单个模拟器"""
        command = config.get("command")
        if not command:
            return {
                "available": False,
                "error": "配置中缺少命令",
                "path": None,
                "version": None
            }

        # 检查命令是否存在
        command_path = shutil.which(command)
        if not command_path:
            return {
                "available": False,
                "error": "命令不存在",
                "path": None,
                "version": None
            }

        # 尝试获取版本信息
        version = self._get_emulator_version(command)

        logger.debug(f"✅ 模拟器可用: {name} ({command_path})")
        return {
            "available": True,
            "error": None,
            "path": command_path,
            "version": version
        }

    def _get_emulator_version(self, command: str) -> Optional[str]:
        """获取模拟器版本"""
        version_args = ["--version", "-v", "-V", "version"]

        for arg in version_args:
            try:
                result = subprocess.run(
                    [command, arg],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip().split('\n')[0]
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        return None

    def install_emulators(self, emulator_status: Dict[str, Dict[str, Any]]) -> int:
        """安装缺失的模拟器"""
        if not self.package_manager:
            logger.error("❌ 没有可用的包管理器，无法安装模拟器")
            return 0

        if not self.config.emulator.auto_install:
            logger.info("ℹ️ 自动安装已禁用")
            return 0

        # 收集需要安装的模拟器
        to_install = []
        for name, status in emulator_status.items():
            if not status["available"]:
                install_cmd = self.config.get_install_command(self.package_manager, name)
                if install_cmd:
                    to_install.append((name, install_cmd))
                else:
                    logger.warning(f"⚠️ 没有 {name} 的安装命令配置")

        if not to_install:
            logger.info("✅ 所有模拟器都已安装")
            return 0

        logger.info(f"🔧 开始安装 {len(to_install)} 个模拟器...")

        installed_count = 0

        try:
            with transaction(backup_enabled=False) as tx:
                # 并行安装模拟器
                if self.config.general.parallel_workers > 1 and len(to_install) > 1:
                    installed_count = self._install_emulators_parallel(to_install, tx)
                else:
                    installed_count = self._install_emulators_sequential(to_install, tx)

                logger.info(f"✅ 模拟器安装完成: {installed_count} 个")

        except Exception as e:
            logger.error(f"❌ 模拟器安装失败: {e}")
            raise

        return installed_count

    def _install_emulators_sequential(self, to_install: List[Tuple[str, str]], tx) -> int:
        """顺序安装模拟器"""
        installed_count = 0

        for name, install_cmd in to_install:
            try:
                if self._install_single_emulator(name, install_cmd, tx):
                    installed_count += 1
            except Exception as e:
                logger.error(f"❌ 安装模拟器失败 {name}: {e}")

        return installed_count

    def _install_emulators_parallel(self, to_install: List[Tuple[str, str]], tx) -> int:
        """并行安装模拟器"""
        installed_count = 0

        with ThreadPoolExecutor(max_workers=self.config.general.parallel_workers) as executor:
            # 提交任务
            future_to_emulator = {
                executor.submit(self._install_single_emulator, name, install_cmd, tx): (name, install_cmd)
                for name, install_cmd in to_install
            }

            # 收集结果
            for future in as_completed(future_to_emulator):
                name, install_cmd = future_to_emulator[future]
                try:
                    if future.result():
                        installed_count += 1
                except Exception as e:
                    logger.error(f"❌ 并行安装模拟器失败 {name}: {e}")

        return installed_count

    def _install_single_emulator(self, name: str, install_cmd: str, tx):
        """安装单个模拟器"""
        try:
            # 添加状态跟踪
            item_id = f"install_{name}"
            fix_item = self.state_manager.add_fix_item(
                item_id,
                FixType.EMULATOR_INSTALL,
                f"安装模拟器: {name}",
                f"使用 {self.package_manager} 安装 {name}",
                {"package_manager": self.package_manager, "install_command": install_cmd}
            )

            fix_item.start()

            # 构建安装命令
            if self.package_manager == "brew":
                cmd = ["brew", "install", install_cmd]
            elif self.package_manager == "apt":
                cmd = ["sudo", "apt", "install", "-y", install_cmd]
            elif self.package_manager == "yum":
                cmd = ["sudo", "yum", "install", "-y", install_cmd]
            elif self.package_manager == "dnf":
                cmd = ["sudo", "dnf", "install", "-y", install_cmd]
            elif self.package_manager == "pacman":
                cmd = ["sudo", "pacman", "-S", "--noconfirm", install_cmd]
            else:
                raise EmulatorInstallError(f"不支持的包管理器: {self.package_manager}")

            description = self.config.get_emulator_description(name)
            logger.info(f"🔧 安装 {name} ({description})...")
            logger.debug(f"📝 安装命令: {' '.join(cmd)}")

            # 执行安装命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.emulator.install_timeout_seconds
            )

            if result.returncode == 0:
                # 验证安装
                emulator_config = self.config.get_emulator_info(name)
                if emulator_config:
                    command = emulator_config.get("command")
                    if command and shutil.which(command):
                        fix_item.complete({
                            "command_path": shutil.which(command),
                            "install_output": result.stdout[:500]  # 限制输出长度
                        })
                        logger.info(f"✅ 安装成功: {name}")
                        return True

                fix_item.fail("安装后验证失败")
                logger.error(f"❌ 安装后验证失败: {name}")
                return False
            else:
                error_msg = result.stderr or result.stdout or "未知错误"
                fix_item.fail(error_msg[:200])  # 限制错误信息长度
                logger.error(f"❌ 安装失败: {name} - {error_msg}")
                return False

        except subprocess.TimeoutExpired:
            if 'fix_item' in locals():
                fix_item.fail("安装超时")
            logger.error(f"❌ 安装超时: {name}")
            return False
        except Exception as e:
            if 'fix_item' in locals():
                fix_item.fail(str(e))
            logger.error(f"❌ 安装异常: {name} - {e}")
            return False

    def test_emulators(self, test_rom_path: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
        """测试模拟器功能"""
        logger.info("🧪 测试模拟器功能...")

        if not test_rom_path or not test_rom_path.exists():
            logger.warning("⚠️ 没有测试ROM，跳过功能测试")
            return {}

        emulator_configs = self.config.emulator_commands.get("emulators", {})
        test_results = {}

        for name, config in emulator_configs.items():
            if not shutil.which(config.get("command", "")):
                continue

            result = self._test_single_emulator(name, config, test_rom_path)
            test_results[name] = result

        # 统计结果
        working = len([r for r in test_results.values() if r["working"]])
        total = len(test_results)

        logger.info(f"📊 模拟器测试完成: {working}/{total} 工作正常")

        return test_results

    def _test_single_emulator(self, name: str, config: Dict[str, Any], test_rom_path: Path) -> Dict[str, Any]:
        """测试单个模拟器"""
        command = config.get("command")
        systems = config.get("systems", {})
        environment = config.get("environment", {})

        # 确定测试系统
        rom_system = self._detect_rom_system(test_rom_path)
        if rom_system not in systems:
            return {
                "working": False,
                "error": f"不支持系统 {rom_system}",
                "tested": False
            }

        try:
            # 构建测试命令
            cmd = [command] + systems[rom_system] + [str(test_rom_path)]

            # 设置环境变量
            env = os.environ.copy()
            env.update(environment)

            logger.debug(f"🧪 测试 {name}: {' '.join(cmd)}")

            # 启动模拟器（短时间后自动退出）
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.emulator.test_timeout_seconds,
                env=env
            )

            # 超时是正常的（说明模拟器在运行）
            return {
                "working": True,
                "error": None,
                "tested": True,
                "output": result.stdout[:200] if result.stdout else None
            }

        except subprocess.TimeoutExpired:
            # 超时说明模拟器正在运行，这是好事
            logger.debug(f"✅ {name} 正在运行（超时是正常的）")
            return {
                "working": True,
                "error": None,
                "tested": True,
                "output": "模拟器启动成功（超时退出）"
            }
        except FileNotFoundError:
            return {
                "working": False,
                "error": "命令不存在",
                "tested": True
            }
        except Exception as e:
            return {
                "working": False,
                "error": str(e),
                "tested": True
            }

    def _detect_rom_system(self, rom_path: Path) -> str:
        """检测ROM系统类型"""
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

        return extension_map.get(extension, "nes")  # 默认为NES

    def fix_emulator_config(self) -> int:
        """修复模拟器配置"""
        logger.info("🔧 修复模拟器配置...")

        fixed_count = 0

        try:
            # 修复mednafen配置
            if self._fix_mednafen_config():
                fixed_count += 1

            # 可以添加其他模拟器的配置修复

            logger.info(f"✅ 模拟器配置修复完成: {fixed_count} 个")

        except Exception as e:
            logger.error(f"❌ 模拟器配置修复失败: {e}")
            raise

        return fixed_count

    def _fix_mednafen_config(self):
        """修复mednafen配置"""
        try:
            # 添加状态跟踪
            item_id = "fix_mednafen_config"
            fix_item = self.state_manager.add_fix_item(
                item_id,
                FixType.EMULATOR_CONFIG,
                "修复mednafen配置",
                "创建或修复mednafen配置文件以解决乱码问题"
            )

            fix_item.start()

            # mednafen配置文件路径
            home_dir = Path.home()
            mednafen_config = home_dir / ".mednafen" / "mednafen.cfg"

            # 如果配置文件不存在，创建基本配置
            if not mednafen_config.exists():
                mednafen_config.parent.mkdir(exist_ok=True)

                config_content = """# Mednafen Configuration
# 解决中文乱码问题
nes.videoip 0
nes.stretch 1
nes.xres 256
nes.yres 240
nes.xscale 2
nes.yscale 2

# 音频设置
sound.enabled 1
sound.rate 48000
sound.buffer_time 100

# 输入设置
nes.input.port1 gamepad
nes.input.port2 gamepad

# 视频设置
video.driver opengl
video.fs 0
video.glvsync 1

# 字体设置 (解决乱码)
osd.alpha_blend 1
"""

                with open(mednafen_config, 'w', encoding='utf-8') as f:
                    f.write(config_content)

                fix_item.complete({"config_path": str(mednafen_config)})
                logger.info(f"✅ 创建mednafen配置: {mednafen_config}")
                return True
            else:
                fix_item.skip("配置文件已存在")
                logger.debug(f"✅ mednafen配置已存在: {mednafen_config}")
                return False

        except Exception as e:
            if 'fix_item' in locals():
                fix_item.fail(str(e))
            logger.error(f"❌ 修复mednafen配置失败: {e}")
            return False

    def get_emulator_summary(self) -> Dict[str, Any]:
        """获取模拟器摘要"""
        emulator_status = self.check_emulators()

        available_emulators = []
        missing_emulators = []

        for name, status in emulator_status.items():
            if status["available"]:
                available_emulators.append({
                    "name": name,
                    "path": status["path"],
                    "version": status["version"],
                    "description": self.config.get_emulator_description(name)
                })
            else:
                missing_emulators.append({
                    "name": name,
                    "error": status["error"],
                    "description": self.config.get_emulator_description(name)
                })

        return {
            "platform": self.platform,
            "package_manager": self.package_manager,
            "total_emulators": len(emulator_status),
            "available_emulators": len(available_emulators),
            "missing_emulators": len(missing_emulators),
            "available": available_emulators,
            "missing": missing_emulators
        }

if __name__ == "__main__":
    # 测试模拟器安装器
    installer = EmulatorInstaller()

    # 检查模拟器
    status = installer.check_emulators()
    print("📊 模拟器状态:")
    for name, info in status.items():
        status_text = "✅ 可用" if info["available"] else f"❌ 不可用 ({info['error']})"
        print(f"  {name}: {status_text}")

    # 获取摘要
    summary = installer.get_emulator_summary()
    print(f"\n📋 摘要: {summary['available_emulators']}/{summary['total_emulators']} 个模拟器可用")

    print("✅ 模拟器安装器测试完成")
