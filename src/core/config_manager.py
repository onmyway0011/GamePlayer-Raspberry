#!/usr/bin/env python3
"""
配置管理器
统一管理所有配置文件和设置
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: str = "config"):
        """TODO: 添加文档字符串"""
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 主配置文件
        self.main_config_file = self.config_dir / "gameplayer_config.json"
        self.config = self.load_config()

        print(f"⚙️ 配置管理器初始化完成")
        print(f"📁 配置目录: {self.config_dir}")

    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.main_config_file.exists():
            try:
                with open(self.main_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"📂 配置文件已加载: {self.main_config_file}")
                return config
            except Exception as e:
                print(f"⚠️ 加载配置文件失败: {e}")

        # 返回默认配置
        return self.get_default_config()

    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "project": {
                "name": "GamePlayer-Raspberry",
                "version": "3.0.0",
                "description": "Enhanced NES Game Player"
            },
            "emulator": {
                "default_scale": 3,
                "fullscreen": False,
                "fps_limit": 60
            },
            "save_system": {
                "auto_save_enabled": True,
                "auto_save_interval": 30,
                "max_save_slots": 10
            },
            "cheat_system": {
                "auto_enable": True,
                "universal_cheats": {
                    "infinite_lives": True,
                    "infinite_health": True
                }
            },
            "device_management": {
                "auto_connect_controllers": True,
                "auto_connect_audio": True
            }
        }

    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.main_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"💾 配置文件已保存: {self.main_config_file}")
            return True
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """获取配置值（支持点号路径）"""
        keys = key_path.split('.')
        value = self.config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any):
        """设置配置值（支持点号路径）"""
        keys = key_path.split('.')
        config = self.config

        try:
            # 导航到最后一级
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]

            # 设置值
            config[keys[-1]] = value
            return True
        except Exception as e:
            print(f"❌ 设置配置值失败: {e}")
            return False

    def get_save_config(self) -> Dict[str, Any]:
        """获取存档系统配置"""
        return {
            "saves_dir": self.get("save_system.saves_directory", "saves"),
            "auto_save_enabled": self.get("save_system.auto_save_enabled", True),
            "auto_save_interval": self.get("save_system.auto_save_interval", 30),
            "max_save_slots": self.get("save_system.max_save_slots", 10),
            "cloud_config": self.get("save_system.cloud_sync", {})
        }

    def get_cheat_config(self) -> Dict[str, Any]:
        """获取作弊系统配置"""
        return {
            "cheats_dir": self.get("cheat_system.cheats_directory", "cheats"),
            "auto_enable": self.get("cheat_system.auto_enable", True),
            "universal_cheats": self.get("cheat_system.universal_cheats", {}),
            "game_specific_cheats": self.get("cheat_system.game_specific_cheats", True)
        }

    def get_device_config(self) -> Dict[str, Any]:
        """获取设备管理配置"""
        return {
            "auto_connect_controllers": self.get("device_management.auto_connect_controllers", True),
            "auto_connect_audio": self.get("device_management.auto_connect_audio", True),
            "controller_deadzone": self.get("device_management.controller_deadzone", 0.3),
            "monitor_devices": self.get("device_management.monitor_devices", True)
        }

    def get_emulator_config(self) -> Dict[str, Any]:
        """获取模拟器配置"""
        return {
            "scale": self.get("emulator.default_scale", 3),
            "fullscreen": self.get("emulator.fullscreen", False),
            "vsync": self.get("emulator.vsync", True),
            "fps_limit": self.get("emulator.fps_limit", 60),
            "audio_enabled": self.get("emulator.audio_enabled", True)
        }

    def get_rom_config(self) -> Dict[str, Any]:
        """获取ROM管理配置"""
        return {
            "roms_dir": self.get("rom_management.roms_directory", "roms"),
            "auto_download": self.get("rom_management.auto_download", True),
            "download_categories": self.get("rom_management.download_categories", []),
            "backup_enabled": self.get("rom_management.backup_enabled", True),
            "verify_integrity": self.get("rom_management.verify_integrity", True)
        }

    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI配置"""
        return {
            "theme": self.get("ui.theme", "dark"),
            "language": self.get("ui.language", "zh-CN"),
            "show_fps": self.get("ui.show_fps", False),
            "show_debug_info": self.get("ui.show_debug_info", False),
            "control_hints_duration": self.get("ui.control_hints_duration", 5),
            "status_display": self.get("ui.status_display", True)
        }

    def update_config(self, updates: Dict[str, Any]):
        """批量更新配置"""
        try:
            for key_path, value in updates.items():
                self.set(key_path, value)
            return self.save_config()
        except Exception as e:
            print(f"❌ 批量更新配置失败: {e}")
            return False

    def reset_to_defaults(self):
        """重置为默认配置"""
        try:
            self.config = self.get_default_config()
            return self.save_config()
        except Exception as e:
            print(f"❌ 重置配置失败: {e}")
            return False

    def export_config(self, export_path: str):
        """导出配置文件"""
        try:
            export_file = Path(export_path)
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"📤 配置已导出: {export_file}")
            return True
        except Exception as e:
            print(f"❌ 导出配置失败: {e}")
            return False

    def import_config(self, import_path: str):
        """导入配置文件"""
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                print(f"❌ 配置文件不存在: {import_file}")
                return False

            with open(import_file, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)

            self.config = imported_config
            success = self.save_config()
            if success:
                print(f"📥 配置已导入: {import_file}")
            return success
        except Exception as e:
            print(f"❌ 导入配置失败: {e}")
            return False

    def validate_config(self):
        """验证配置文件完整性"""
        required_sections = [
            "project",
            "emulator",
            "save_system",
            "cheat_system",
            "device_management"
        ]

        for section in required_sections:
            if section not in self.config:
                print(f"⚠️ 缺少配置节: {section}")
                return False

        print(f"✅ 配置文件验证通过")
        return True

    def get_config_info(self) -> Dict[str, Any]:
        """获取配置信息"""
        return {
            "config_file": str(self.main_config_file),
            "config_dir": str(self.config_dir),
            "project_name": self.get("project.name", "Unknown"),
            "project_version": self.get("project.version", "Unknown"),
            "sections": list(self.config.keys()),
            "file_exists": self.main_config_file.exists(),
            "is_valid": self.validate_config()
        }
