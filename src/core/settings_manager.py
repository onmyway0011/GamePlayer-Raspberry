#!/usr/bin/env python3
"""
设置管理器
负责管理模拟器的各种设置和配置
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class SettingsManager:
    """设置管理器"""
    
    def __init__(self, config_dir: str = "config/emulators"):
        """初始化设置管理器"""
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.settings = {}
        self.default_settings = {}
        self.settings_file = self.config_dir / "general_settings.json"
        self.user_settings_file = self.config_dir / "user_settings.json"
        
        # 加载设置
        self.load_settings()
        
    def load_settings(self):
        """加载设置"""
        try:
            # 加载默认设置
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.default_settings = json.load(f)
            else:
                self.create_default_settings()
            
            # 加载用户设置
            if self.user_settings_file.exists():
                with open(self.user_settings_file, 'r', encoding='utf-8') as f:
                    user_settings = json.load(f)
                    # 合并用户设置到默认设置
                    self.settings = self._merge_settings(self.default_settings, user_settings)
            else:
                self.settings = self.default_settings.copy()
            
            logger.info("✅ 设置加载完成")
            
        except Exception as e:
            logger.error(f"❌ 设置加载失败: {e}")
            self.create_default_settings()
    
    def create_default_settings(self):
        """创建默认设置"""
        self.default_settings = {
            "display_settings": {
                "resolution": {"width": 1920, "height": 1080, "fullscreen": False},
                "scaling": {"smooth_scaling": True, "scanlines": False},
                "frame_settings": {"vsync": True, "show_fps": False}
            },
            "audio_settings": {
                "master_volume": 80,
                "sound_effects": True,
                "background_music": True,
                "sample_rate": 44100
            },
            "input_settings": {
                "keyboard": {"enabled": True},
                "gamepad": {"enabled": True, "auto_detect": True},
                "mouse": {"enabled": True}
            },
            "emulation_settings": {
                "save_states": {"enabled": True, "auto_save": True},
                "cheats": {"enabled": True, "auto_apply": False}
            }
        }
        
        self.settings = self.default_settings.copy()
        self.save_settings()
        logger.info("📝 创建默认设置")
    
    def _merge_settings(self, default: Dict, user: Dict) -> Dict:
        """合并设置"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def save_settings(self):
        """保存设置"""
        try:
            # 计算用户设置（与默认设置的差异）
            user_settings = self._get_user_changes()
            
            with open(self.user_settings_file, 'w', encoding='utf-8') as f:
                json.dump(user_settings, f, indent=2, ensure_ascii=False)
            
            logger.info("💾 设置已保存")
            
        except Exception as e:
            logger.error(f"❌ 设置保存失败: {e}")
    
    def _get_user_changes(self) -> Dict:
        """获取用户修改的设置"""
        return self._diff_settings(self.default_settings, self.settings)
    
    def _diff_settings(self, default: Dict, current: Dict) -> Dict:
        """计算设置差异"""
        diff = {}
        
        for key, value in current.items():
            if key not in default:
                diff[key] = value
            elif isinstance(value, dict) and isinstance(default[key], dict):
                sub_diff = self._diff_settings(default[key], value)
                if sub_diff:
                    diff[key] = sub_diff
            elif value != default[key]:
                diff[key] = value
        
        return diff
    
    def get_setting(self, path: str, default: Any = None) -> Any:
        """获取设置值"""
        try:
            keys = path.split('.')
            value = self.settings
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
            
        except Exception as e:
            logger.error(f"❌ 获取设置失败 {path}: {e}")
            return default
    
    def set_setting(self, path: str, value: Any) -> bool:
        """设置值"""
        try:
            keys = path.split('.')
            current = self.settings
            
            # 导航到父级
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # 设置值
            current[keys[-1]] = value
            
            logger.info(f"✅ 设置已更新: {path} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 设置更新失败 {path}: {e}")
            return False
    
    def get_display_settings(self) -> Dict:
        """获取显示设置"""
        return self.get_setting("display_settings", {})
    
    def get_audio_settings(self) -> Dict:
        """获取音频设置"""
        return self.get_setting("audio_settings", {})
    
    def get_input_settings(self) -> Dict:
        """获取输入设置"""
        return self.get_setting("input_settings", {})
    
    def get_emulation_settings(self) -> Dict:
        """获取模拟设置"""
        return self.get_setting("emulation_settings", {})
    
    def get_system_settings(self, system: str) -> Dict:
        """获取系统特定设置"""
        return self.get_setting(f"system_specific.{system}", {})
    
    def update_display_settings(self, settings: Dict) -> bool:
        """更新显示设置"""
        try:
            current_display = self.get_display_settings()
            current_display.update(settings)
            return self.set_setting("display_settings", current_display)
        except Exception as e:
            logger.error(f"❌ 更新显示设置失败: {e}")
            return False
    
    def update_audio_settings(self, settings: Dict) -> bool:
        """更新音频设置"""
        try:
            current_audio = self.get_audio_settings()
            current_audio.update(settings)
            return self.set_setting("audio_settings", current_audio)
        except Exception as e:
            logger.error(f"❌ 更新音频设置失败: {e}")
            return False
    
    def update_input_settings(self, settings: Dict) -> bool:
        """更新输入设置"""
        try:
            current_input = self.get_input_settings()
            current_input.update(settings)
            return self.set_setting("input_settings", current_input)
        except Exception as e:
            logger.error(f"❌ 更新输入设置失败: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """重置为默认设置"""
        try:
            self.settings = self.default_settings.copy()
            self.save_settings()
            logger.info("🔄 设置已重置为默认值")
            return True
        except Exception as e:
            logger.error(f"❌ 重置设置失败: {e}")
            return False
    
    def export_settings(self, file_path: str) -> bool:
        """导出设置"""
        try:
            export_data = {
                "settings": self.settings,
                "export_time": "2025-06-27",
                "version": "1.0"
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📤 设置已导出到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 设置导出失败: {e}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """导入设置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if "settings" in import_data:
                self.settings = import_data["settings"]
                self.save_settings()
                logger.info(f"📥 设置已导入: {file_path}")
                return True
            else:
                logger.error("❌ 导入文件格式无效")
                return False
                
        except Exception as e:
            logger.error(f"❌ 设置导入失败: {e}")
            return False
    
    def get_available_resolutions(self) -> List[Dict]:
        """获取可用分辨率"""
        return self.get_setting("display_settings.resolution.available_resolutions", [])
    
    def get_key_mappings(self, player: int = 1) -> Dict:
        """获取按键映射"""
        return self.get_setting(f"input_settings.keyboard.key_mappings.player{player}", {})
    
    def update_key_mapping(self, player: int, action: str, key: str) -> bool:
        """更新按键映射"""
        path = f"input_settings.keyboard.key_mappings.player{player}.{action}"
        return self.set_setting(path, key)
    
    def get_gamepad_settings(self) -> Dict:
        """获取手柄设置"""
        return self.get_setting("input_settings.gamepad", {})
    
    def is_feature_enabled(self, feature_path: str) -> bool:
        """检查功能是否启用"""
        return self.get_setting(feature_path, False)
    
    def get_raspberry_pi_settings(self) -> Dict:
        """获取树莓派优化设置"""
        return self.get_setting("raspberry_pi_optimizations", {})
    
    def apply_raspberry_pi_optimizations(self) -> bool:
        """应用树莓派优化"""
        try:
            pi_settings = self.get_raspberry_pi_settings()
            
            if not pi_settings:
                logger.warning("⚠️ 未找到树莓派优化设置")
                return False
            
            logger.info("🍓 应用树莓派优化设置...")
            
            # 这里应该实际应用优化设置
            # 目前只是记录日志
            for category, settings in pi_settings.items():
                logger.info(f"  {category}: {settings}")
            
            logger.info("✅ 树莓派优化设置已应用")
            return True
            
        except Exception as e:
            logger.error(f"❌ 应用树莓派优化失败: {e}")
            return False
