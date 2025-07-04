#!/usr/bin/env python3
"""
配置管理器 - 负责加载和管理所有配置文件
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass

class GeneralSettings:
    """通用设置"""
    max_retries: int = 3
    timeout_seconds: int = 300
    parallel_workers: int = 4
    enable_cache: bool = True
    cache_duration_hours: int = 24
    enable_transaction: bool = True
    backup_before_fix: bool = True

@dataclass

class RomSettings:
    """ROM设置"""
    min_size_bytes: int = 1024
    max_size_bytes: int = 104857600
    supported_extensions: List[str] = field(default_factory=lambda: [".nes", ".smc", ".sfc", ".gb", ".gbc", ".gba", ".md", ".gen"])
    create_missing: bool = True
    fix_corrupted: bool = True
    verify_headers: bool = True

@dataclass

class EmulatorSettings:
    """模拟器设置"""
    test_timeout_seconds: int = 5
    install_timeout_seconds: int = 600
    auto_install: bool = True
    prefer_gui: bool = True
    fallback_to_cli: bool = True

@dataclass

class LoggingSettings:
    """日志设置"""
    level: str = "INFO"
    file: str = "logs/emulator_fix.log"
    max_size_mb: int = 10
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

@dataclass

class SecuritySettings:
    """安全设置"""
    validate_paths: bool = True
    restrict_commands: bool = True
    check_permissions: bool = True
    safe_mode: bool = True

@dataclass

class UISettings:
    """用户界面设置"""
    show_progress: bool = True
    interactive_mode: bool = False
    generate_html_report: bool = True
    report_path: str = "reports/fix_report.html"


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: Optional[Path] = None):
        """初始化配置管理器"""
        if config_dir is None:
            # 获取项目根目录
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent
            config_dir = project_root / "config" / "emulator_fix"

        self.config_dir = Path(config_dir)
        self._standard_roms: Optional[Dict[str, Dict[str, str]]] = None
        self._emulator_commands: Optional[Dict[str, Any]] = None
        self._settings: Optional[Dict[str, Any]] = None

        # 设置对象
        self.general: Optional[GeneralSettings] = None
        self.rom: Optional[RomSettings] = None
        self.emulator: Optional[EmulatorSettings] = None
        self.logging: Optional[LoggingSettings] = None
        self.security: Optional[SecuritySettings] = None
        self.ui: Optional[UISettings] = None

        self._load_all_configs()

    def _load_all_configs(self) -> None:
        """加载所有配置文件"""
        try:
            self._load_standard_roms()
            self._load_emulator_commands()
            self._load_settings()
            logger.info("✅ 所有配置文件加载成功")
        except Exception as e:
            logger.error(f"❌ 配置文件加载失败: {e}")
            raise

    def _load_standard_roms(self) -> None:
        """加载标准ROM配置"""
        config_file = self.config_dir / "standard_roms.json"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self._standard_roms = json.load(f)
            logger.debug(f"✅ 标准ROM配置加载成功: {config_file}")
        except FileNotFoundError:
            logger.error(f"❌ 标准ROM配置文件不存在: {config_file}")
            self._standard_roms = {}
        except json.JSONDecodeError as e:
            logger.error(f"❌ 标准ROM配置文件格式错误: {e}")
            self._standard_roms = {}

    def _load_emulator_commands(self) -> None:
        """加载模拟器命令配置"""
        config_file = self.config_dir / "emulator_commands.json"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self._emulator_commands = json.load(f)
            logger.debug(f"✅ 模拟器命令配置加载成功: {config_file}")
        except FileNotFoundError:
            logger.error(f"❌ 模拟器命令配置文件不存在: {config_file}")
            self._emulator_commands = {}
        except json.JSONDecodeError as e:
            logger.error(f"❌ 模拟器命令配置文件格式错误: {e}")
            self._emulator_commands = {}

    def _load_settings(self) -> None:
        """加载修复设置"""
        config_file = self.config_dir / "fix_settings.json"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self._settings = json.load(f)

            # 创建设置对象
            self.general = GeneralSettings(**self._settings.get("general", {}))
            self.rom = RomSettings(**self._settings.get("rom_settings", {}))
            self.emulator = EmulatorSettings(**self._settings.get("emulator_settings", {}))
            self.logging = LoggingSettings(**self._settings.get("logging", {}))
            self.security = SecuritySettings(**self._settings.get("security", {}))
            self.ui = UISettings(**self._settings.get("ui", {}))

            logger.debug(f"✅ 修复设置加载成功: {config_file}")
        except FileNotFoundError:
            logger.error(f"❌ 修复设置文件不存在: {config_file}")
            self._create_default_settings()
        except json.JSONDecodeError as e:
            logger.error(f"❌ 修复设置文件格式错误: {e}")
            self._create_default_settings()

    def _create_default_settings(self) -> None:
        """创建默认设置"""
        self.general = GeneralSettings()
        self.rom = RomSettings()
        self.emulator = EmulatorSettings()
        self.logging = LoggingSettings()
        self.security = SecuritySettings()
        self.ui = UISettings()

    @property
    def standard_roms(self) -> Dict[str, Dict[str, str]]:
        """获取标准ROM配置"""
        return self._standard_roms or {}

    @property
    def emulator_commands(self) -> Dict[str, Any]:
        """获取模拟器命令配置"""
        return self._emulator_commands or {}

    def get_emulator_info(self, emulator_name: str) -> Optional[Dict[str, Any]]:
        """获取特定模拟器信息"""
        emulators = self.emulator_commands.get("emulators", {})
        return emulators.get(emulator_name)

    def get_install_command(self, package_manager: str, emulator_name: str) -> Optional[str]:
        """获取安装命令"""
        install_commands = self.emulator_commands.get("install_commands", {})
        pm_commands = install_commands.get(package_manager, {})
        return pm_commands.get(emulator_name)

    def get_emulator_description(self, emulator_name: str) -> str:
        """获取模拟器描述"""
        descriptions = self.emulator_commands.get("descriptions", {})
        return descriptions.get(emulator_name, f"{emulator_name} 模拟器")

    def reload_configs(self) -> None:
        """重新加载所有配置"""
        logger.info("🔄 重新加载配置文件...")
        self._load_all_configs()

    def validate_config(self) -> List[str]:
        """验证配置完整性"""
        issues = []

        if not self._standard_roms:
            issues.append("标准ROM配置为空")

        if not self._emulator_commands:
            issues.append("模拟器命令配置为空")

        if not self.general:
            issues.append("通用设置未加载")

        # 验证路径
        if self.logging and self.logging.file:
            log_dir = Path(self.logging.file).parent
            if not log_dir.exists():
                try:
                    log_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    issues.append(f"无法创建日志目录: {e}")

        if self.ui and self.ui.report_path:
            report_dir = Path(self.ui.report_path).parent
            if not report_dir.exists():
                try:
                    report_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    issues.append(f"无法创建报告目录: {e}")

        return issues


def get_config_manager() -> ConfigManager:
    """获取配置管理器单例"""
    if not hasattr(get_config_manager, '_instance'):
        get_config_manager._instance = ConfigManager()
    return get_config_manager._instance

if __name__ == "__main__":
    # 测试配置管理器
    import sys
    logging.basicConfig(level=logging.DEBUG)

    try:
        config = ConfigManager()
        issues = config.validate_config()

        if issues:
            print("❌ 配置验证失败:")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)
        else:
            print("✅ 配置验证通过")
            print(f"📊 标准ROM系统: {list(config.standard_roms.keys())}")
            print(f"🎮 支持的模拟器: {list(config.emulator_commands.get('emulators', {}).keys())}")
    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        sys.exit(1)
