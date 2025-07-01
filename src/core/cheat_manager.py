#!/usr/bin/env python3
"""
金手指（作弊码）管理器
负责管理和应用游戏作弊码
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class CheatManager:
    """金手指管理器"""

    def __init__(self, config_dir: str = "config/cheats"):
        """初始化金手指管理器"""
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.cheat_database = {}
        self.active_cheats = {}
        self.cheat_history = []

        # 加载金手指数据库
        self.load_cheat_database()

    def load_cheat_database(self):
        """加载金手指数据库"""
        try:
            # 加载通用金手指配置
            general_config = self.config_dir / "general_cheats.json"
            if general_config.exists():
                with open(general_config, 'r', encoding='utf-8') as f:
                    self.cheat_database = json.load(f)
            else:
                # 创建默认金手指数据库
                self.create_default_cheat_database()

            logger.info(f"✅ 金手指数据库加载完成，支持 {len(self.cheat_database)} 个系统")

        except Exception as e:
            logger.error(f"❌ 金手指数据库加载失败: {e}")
            self.create_default_cheat_database()

    def create_default_cheat_database(self):
        """创建默认金手指数据库"""
        self.cheat_database = {
            "nes": {
                "system_name": "Nintendo Entertainment System",
                "common_cheats": {
                    "infinite_lives": {
                        "name": "无限生命",
                        "description": "获得无限生命数",
                        "code": "AEAEAE",
                        "type": "game_genie",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "infinite_time": {
                        "name": "无限时间",
                        "description": "时间不会减少",
                        "code": "AAAAAA",
                        "type": "game_genie",
                        "enabled": False,
                        "auto_enable": False
                    },
                    "invincibility": {
                        "name": "无敌模式",
                        "description": "角色无敌，不会受伤",
                        "code": "AEAEAE",
                        "type": "game_genie",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "level_select": {
                        "name": "关卡选择",
                        "description": "可以选择任意关卡",
                        "code": "AAAAAA",
                        "type": "game_genie",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "max_power": {
                        "name": "最大能力",
                        "description": "所有能力值最大",
                        "code": "AEAEAE",
                        "type": "game_genie",
                        "enabled": True,
                        "auto_enable": True
                    }
                },
                "games": {
                    "Super Mario Bros": {
                        "infinite_lives": "SXIOPO",
                        "big_mario": "AAAAAA",
                        "fire_mario": "AEAEAE",
                        "level_select": "AEAEAE"
                    },
                    "Contra": {
                        "30_lives": "SXIOPO",
                        "infinite_lives": "AAAAAA",
                        "spread_gun": "AEAEAE",
                        "rapid_fire": "AEAEAE"
                    },
                    "Mega Man": {
                        "infinite_lives": "SXIOPO",
                        "infinite_energy": "AAAAAA",
                        "all_weapons": "AEAEAE",
                        "stage_select": "AEAEAE"
                    }
                }
            },
            "snes": {
                "system_name": "Super Nintendo Entertainment System",
                "common_cheats": {
                    "infinite_lives": {
                        "name": "无限生命",
                        "description": "获得无限生命数",
                        "code": "7E0DBE:63",
                        "type": "pro_action_replay",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "infinite_health": {
                        "name": "无限血量",
                        "description": "血量不会减少",
                        "code": "7E0DBF:FF",
                        "type": "pro_action_replay",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "invincibility": {
                        "name": "无敌模式",
                        "description": "角色无敌，不会受伤",
                        "code": "7E0DC0:01",
                        "type": "pro_action_replay",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "max_power": {
                        "name": "最大能力",
                        "description": "所有能力值最大",
                        "code": "7E0DC0:FF",
                        "type": "pro_action_replay",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "level_select": {
                        "name": "关卡选择",
                        "description": "可以选择任意关卡",
                        "code": "7E0DC1:FF",
                        "type": "pro_action_replay",
                        "enabled": True,
                        "auto_enable": True
                    }
                },
                "games": {}
            },
            "gb": {
                "system_name": "Game Boy",
                "common_cheats": {
                    "infinite_lives": {
                        "name": "无限生命",
                        "description": "获得无限生命数",
                        "code": "01FF63C1",
                        "type": "gameshark",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "infinite_health": {
                        "name": "无限血量",
                        "description": "血量不会减少",
                        "code": "01FF64C1",
                        "type": "gameshark",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "invincibility": {
                        "name": "无敌模式",
                        "description": "角色无敌，不会受伤",
                        "code": "01FF65C1",
                        "type": "gameshark",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "max_power": {
                        "name": "最大能力",
                        "description": "所有能力值最大",
                        "code": "01FF66C1",
                        "type": "gameshark",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "level_select": {
                        "name": "关卡选择",
                        "description": "可以选择任意关卡",
                        "code": "01FF67C1",
                        "type": "gameshark",
                        "enabled": True,
                        "auto_enable": True
                    }
                },
                "games": {}
            },
            "gba": {
                "system_name": "Game Boy Advance",
                "common_cheats": {
                    "infinite_lives": {
                        "name": "无限生命",
                        "description": "获得无限生命数",
                        "code": "82003228:0063",
                        "type": "codebreaker",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "infinite_health": {
                        "name": "无限血量",
                        "description": "血量不会减少",
                        "code": "82003229:00FF",
                        "type": "codebreaker",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "invincibility": {
                        "name": "无敌模式",
                        "description": "角色无敌，不会受伤",
                        "code": "8200322A:0001",
                        "type": "codebreaker",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "max_power": {
                        "name": "最大能力",
                        "description": "所有能力值最大",
                        "code": "8200322B:00FF",
                        "type": "codebreaker",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "level_select": {
                        "name": "关卡选择",
                        "description": "可以选择任意关卡",
                        "code": "8200322C:00FF",
                        "type": "codebreaker",
                        "enabled": True,
                        "auto_enable": True
                    }
                },
                "games": {}
            },
            "genesis": {
                "system_name": "Sega Genesis/Mega Drive",
                "common_cheats": {
                    "infinite_lives": {
                        "name": "无限生命",
                        "description": "获得无限生命数",
                        "code": "FFFF01:0063",
                        "type": "action_replay",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "infinite_health": {
                        "name": "无限血量",
                        "description": "血量不会减少",
                        "code": "FFFF02:00FF",
                        "type": "action_replay",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "invincibility": {
                        "name": "无敌模式",
                        "description": "角色无敌，不会受伤",
                        "code": "FFFF03:0001",
                        "type": "action_replay",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "max_power": {
                        "name": "最大能力",
                        "description": "所有能力值最大",
                        "code": "FFFF04:00FF",
                        "type": "action_replay",
                        "enabled": True,
                        "auto_enable": True
                    },
                    "level_select": {
                        "name": "关卡选择",
                        "description": "可以选择任意关卡",
                        "code": "FFFF05:00FF",
                        "type": "action_replay",
                        "enabled": True,
                        "auto_enable": True
                    }
                },
                "games": {}
            }
        }

        # 保存默认配置
        self.save_cheat_database()
        logger.info("📝 创建默认金手指数据库")

    def save_cheat_database(self):
        """保存金手指数据库"""
        try:
            config_file = self.config_dir / "general_cheats.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.cheat_database, f, indent=2, ensure_ascii=False)
            logger.info("💾 金手指数据库已保存")
        except Exception as e:
            logger.error(f"❌ 金手指数据库保存失败: {e}")

    def get_system_cheats(self, system: str) -> Optional[Dict]:
        """获取指定系统的金手指"""
        return self.cheat_database.get(system)

    def get_game_cheats(self, system: str, game: str) -> Optional[Dict]:
        """获取指定游戏的金手指"""
        system_data = self.cheat_database.get(system)
        if system_data and "games" in system_data:
            return system_data["games"].get(game)
        return None

    def enable_cheat(self, system: str, cheat_type: str, cheat_name: str):
        """启用金手指"""
        try:
            if system in self.cheat_database:
                if cheat_type == "common":
                    if cheat_name in self.cheat_database[system]["common_cheats"]:
                        self.cheat_database[system]["common_cheats"][cheat_name]["enabled"] = True
                        self.active_cheats[f"{system}_{cheat_type}_{cheat_name}"] = True
                        logger.info(f"✅ 启用金手指: {system} - {cheat_name}")
                        return True
            return False
        except Exception as e:
            logger.error(f"❌ 启用金手指失败: {e}")
            return False

    def disable_cheat(self, system: str, cheat_type: str, cheat_name: str):
        """禁用金手指"""
        try:
            if system in self.cheat_database:
                if cheat_type == "common":
                    if cheat_name in self.cheat_database[system]["common_cheats"]:
                        self.cheat_database[system]["common_cheats"][cheat_name]["enabled"] = False
                        cheat_key = f"{system}_{cheat_type}_{cheat_name}"
                        if cheat_key in self.active_cheats:
                            del self.active_cheats[cheat_key]
                        logger.info(f"❌ 禁用金手指: {system} - {cheat_name}")
                        return True
            return False
        except Exception as e:
            logger.error(f"❌ 禁用金手指失败: {e}")
            return False

    def toggle_cheat(self, system: str, cheat_type: str, cheat_name: str):
        """切换金手指状态"""
        if system in self.cheat_database:
            if cheat_type == "common":
                cheat_data = self.cheat_database[system]["common_cheats"].get(cheat_name)
                if cheat_data:
                    if cheat_data["enabled"]:
                        return self.disable_cheat(system, cheat_type, cheat_name)
                    else:
                        return self.enable_cheat(system, cheat_type, cheat_name)
        return False

    def get_active_cheats(self) -> Dict:
        """获取当前激活的金手指"""
        return self.active_cheats.copy()

    def clear_all_cheats(self):
        """清除所有激活的金手指"""
        self.active_cheats.clear()

        # 重置数据库中的启用状态
        for system in self.cheat_database:
            if "common_cheats" in self.cheat_database[system]:
                for cheat_name in self.cheat_database[system]["common_cheats"]:
                    self.cheat_database[system]["common_cheats"][cheat_name]["enabled"] = False

        logger.info("🧹 已清除所有金手指")

    def export_cheat_config(self, file_path: str):
        """导出金手指配置"""
        try:
            export_data = {
                "cheat_database": self.cheat_database,
                "active_cheats": self.active_cheats,
                "export_time": "2025-06-27"
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"📤 金手指配置已导出到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 金手指配置导出失败: {e}")
            return False

    def import_cheat_config(self, file_path: str):
        """导入金手指配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            if "cheat_database" in import_data:
                self.cheat_database = import_data["cheat_database"]

            if "active_cheats" in import_data:
                self.active_cheats = import_data["active_cheats"]

            self.save_cheat_database()
            logger.info(f"📥 金手指配置已导入: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 金手指配置导入失败: {e}")
            return False

    def auto_enable_cheats_for_game(self, system: str, game_name: str = None) -> int:
        """游戏启动时自动启用金手指"""
        try:
            enabled_count = 0

            if system not in self.cheat_database:
                logger.warning(f"⚠️ 不支持的游戏系统: {system}")
                return 0

            system_data = self.cheat_database[system]
            logger.info(f"🎯 为 {system_data['system_name']} 自动启用金手指...")

            # 启用通用金手指
            common_cheats = system_data.get("common_cheats", {})
            for cheat_name, cheat_data in common_cheats.items():
                if cheat_data.get("auto_enable", False):
                    success = self.enable_cheat(system, "common", cheat_name)
                    if success:
                        enabled_count += 1
                        logger.info(f"  ✅ 已启用: {cheat_data['name']}")

            # 启用游戏特定金手指（如果指定了游戏）
            if game_name:
                games = system_data.get("games", {})
                if game_name in games:
                    game_cheats = games[game_name]
                    for cheat_name, cheat_code in game_cheats.items():
                        # 这里可以添加游戏特定金手指的启用逻辑
                        logger.info(f"  🎮 游戏特定金手指: {cheat_name} = {cheat_code}")

            if enabled_count > 0:
                logger.info(f"🎉 成功自动启用 {enabled_count} 个金手指")

                # 显示启用的金手指列表
                self._show_enabled_cheats_summary(system)
            else:
                logger.info("ℹ️ 没有需要自动启用的金手指")

            return enabled_count

        except Exception as e:
            logger.error(f"❌ 自动启用金手指失败: {e}")
            return 0

    def _show_enabled_cheats_summary(self, system: str):
        """显示已启用的金手指摘要"""
        try:
            enabled_cheats = []

            if system in self.cheat_database:
                common_cheats = self.cheat_database[system].get("common_cheats", {})
                for cheat_name, cheat_data in common_cheats.items():
                    if cheat_data.get("enabled", False):
                        enabled_cheats.append(cheat_data["name"])

            if enabled_cheats:
                logger.info("📋 当前启用的金手指:")
                for i, cheat_name in enumerate(enabled_cheats, 1):
                    logger.info(f"  {i}. {cheat_name}")

        except Exception as e:
            logger.error(f"❌ 显示金手指摘要失败: {e}")

    def get_auto_enable_cheats(self, system: str) -> List[str]:
        """获取自动启用的金手指列表"""
        auto_cheats = []

        if system in self.cheat_database:
            common_cheats = self.cheat_database[system].get("common_cheats", {})
            for cheat_name, cheat_data in common_cheats.items():
                if cheat_data.get("auto_enable", False):
                    auto_cheats.append(cheat_data["name"])

        return auto_cheats

    def set_auto_enable_cheat(self, system: str, cheat_name: str, auto_enable: bool):
        """设置金手指是否自动启用"""
        try:
            if system in self.cheat_database:
                common_cheats = self.cheat_database[system].get("common_cheats", {})
                if cheat_name in common_cheats:
                    common_cheats[cheat_name]["auto_enable"] = auto_enable
                    self.save_cheat_database()

                    status = "启用" if auto_enable else "禁用"
                    logger.info(f"⚙️ 已设置 {cheat_name} 自动{status}")
                    return True

            return False

        except Exception as e:
            logger.error(f"❌ 设置自动启用失败: {e}")
            return False

    def update_cheat_status(self, system: str, cheat_id: str, enabled: bool):
        """更新金手指启用状态"""
        try:
            if system in self.cheat_database:
                if "common_cheats" in self.cheat_database[system]:
                    if cheat_id in self.cheat_database[system]["common_cheats"]:
                        self.cheat_database[system]["common_cheats"][cheat_id]["enabled"] = enabled

                        # 保存配置到文件
                        self.save_cheat_database()

                        logger.info(f"✅ 金手指状态更新: {system}.{cheat_id} = {enabled}")
                        return True

            logger.warning(f"⚠️ 金手指不存在: {system}.{cheat_id}")
            return False

        except Exception as e:
            logger.error(f"❌ 更新金手指状态失败: {e}")
            return False

    def save_cheat_database(self):
        """保存金手指数据库到文件"""
        try:
            config_file = self.config_dir / "general_cheats.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.cheat_database, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ 金手指数据库已保存: {config_file}")
            return True

        except Exception as e:
            logger.error(f"❌ 保存金手指数据库失败: {e}")
            return False

    def is_cheat_enabled(self, system: str, cheat_id: str):
        """检查金手指是否启用"""
        try:
            return self.cheat_database.get(system, {}).get("common_cheats", {}).get(cheat_id, {}).get("enabled", False)
        except Exception:
            return False

    def get_cheat_details(self, system: str, cheat_id: str) -> Dict:
        """获取金手指详细信息"""
        try:
            return self.cheat_database.get(system, {}).get("common_cheats", {}).get(cheat_id, {})
        except Exception:
            return {}

    def get_all_cheats_for_system(self, system: str) -> Dict:
        """获取系统的所有金手指"""
        return self.cheat_database.get(system, {}).get("common_cheats", {})

    def apply_cheats_to_game(self, system: str, game_id: str, enabled_cheats: List[str]):
        """将金手指应用到游戏"""
        try:
            # 创建游戏专用的金手指文件
            cheat_file = self.project_root / "data" / "cheats" / system / f"{game_id}.cht"
            cheat_file.parent.mkdir(parents=True, exist_ok=True)

            cheat_content = []
            applied_count = 0

            for cheat_id in enabled_cheats:
                cheat_info = self.get_cheat_details(system, cheat_id)
                if cheat_info and cheat_info.get("enabled", False):
                    cheat_content.append(f"# {cheat_info.get('name', cheat_id)}")
                    cheat_content.append(f"{cheat_info.get('code', '')}")
                    cheat_content.append("")
                    applied_count += 1

            # 写入金手指文件
            with open(cheat_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(cheat_content))

            logger.info(f"✅ 已应用 {applied_count} 个金手指到游戏 {game_id}")
            return True

        except Exception as e:
            logger.error(f"❌ 应用金手指到游戏失败: {e}")
            return False
