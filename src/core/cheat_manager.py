#!/usr/bin/env python3
"""
金手指管理器
自动开启无限条命等作弊功能
"""

import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any

class CheatManager:
    """金手指管理器"""
    
    def __init__(self, cheats_dir -> bool: str = "cheats") -> bool:
        self.cheats_dir = Path(cheats_dir)
        self.cheats_dir.mkdir(parents=True, exist_ok=True)
        
        # 作弊码状态
        self.active_cheats = {}
        self.cheat_thread = None
        self.cheat_enabled = True
        
        # 内置通用作弊码
        self.universal_cheats = {
            "infinite_lives": {
                "name": "无限条命",
                "description": "永远不会死亡",
                "enabled": True,
                "auto_enable": True,
                "memory_addresses": [
                    {"address": 0x075A, "value": 99},  # 通用生命值地址
                    {"address": 0x07A0, "value": 99},  # 备用生命值地址
                ]
            },
            "infinite_health": {
                "name": "无限血量",
                "description": "血量永远满格",
                "enabled": True,
                "auto_enable": True,
                "memory_addresses": [
                    {"address": 0x0770, "value": 255},  # 通用血量地址
                    {"address": 0x0790, "value": 255},  # 备用血量地址
                ]
            },
            "infinite_ammo": {
                "name": "无限弹药",
                "description": "弹药永远不会用完",
                "enabled": True,
                "auto_enable": True,
                "memory_addresses": [
                    {"address": 0x0780, "value": 99},  # 通用弹药地址
                ]
            },
            "invincibility": {
                "name": "无敌模式",
                "description": "免疫所有伤害",
                "enabled": True,
                "auto_enable": True,
                "memory_addresses": [
                    {"address": 0x0760, "value": 1},   # 无敌标志
                ]
            },
            "max_power": {
                "name": "最大能力",
                "description": "所有能力值最大",
                "enabled": True,
                "auto_enable": True,
                "memory_addresses": [
                    {"address": 0x0750, "value": 255}, # 力量值
                    {"address": 0x0751, "value": 255}, # 速度值
                    {"address": 0x0752, "value": 255}, # 跳跃值
                ]
            }
        }
        
        # 游戏特定作弊码
        self.game_specific_cheats = self.load_game_cheats()
        
        print(f"🎯 金手指管理器初始化完成")
        print(f"📁 作弊码目录: {self.cheats_dir}")
        print(f"🔧 通用作弊码: {len(self.universal_cheats)} 个")
    
    def load_game_cheats(self) -> Dict:
        """加载游戏特定作弊码"""
        cheats_file = self.cheats_dir / "game_cheats.json"
        
        if cheats_file.exists():
            try:
                with open(cheats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载作弊码文件失败: {e}")
        
        # 返回默认游戏作弊码
        default_cheats = {
            "super_mario_bros": {
                "name": "超级马里奥兄弟",
                "cheats": {
                    "infinite_lives": {
                        "name": "无限条命",
                        "memory_addresses": [{"address": 0x075A, "value": 99}]
                    },
                    "invincible": {
                        "name": "无敌状态",
                        "memory_addresses": [{"address": 0x079E, "value": 1}]
                    },
                    "big_mario": {
                        "name": "大马里奥",
                        "memory_addresses": [{"address": 0x0756, "value": 1}]
                    }
                }
            },
            "contra": {
                "name": "魂斗罗",
                "cheats": {
                    "infinite_lives": {
                        "name": "无限条命",
                        "memory_addresses": [{"address": 0x0032, "value": 99}]
                    },
                    "infinite_ammo": {
                        "name": "无限弹药",
                        "memory_addresses": [{"address": 0x0033, "value": 99}]
                    },
                    "spread_gun": {
                        "name": "散弹枪",
                        "memory_addresses": [{"address": 0x0034, "value": 1}]
                    }
                }
            },
            "megaman": {
                "name": "洛克人",
                "cheats": {
                    "infinite_lives": {
                        "name": "无限条命",
                        "memory_addresses": [{"address": 0x00A8, "value": 99}]
                    },
                    "infinite_energy": {
                        "name": "无限能量",
                        "memory_addresses": [{"address": 0x06C0, "value": 28}]
                    },
                    "all_weapons": {
                        "name": "所有武器",
                        "memory_addresses": [
                            {"address": 0x00BB, "value": 255},
                            {"address": 0x00BC, "value": 255}
                        ]
                    }
                }
            }
        }
        
        # 保存默认作弊码
        try:
            with open(cheats_file, 'w', encoding='utf-8') as f:
                json.dump(default_cheats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 保存默认作弊码失败: {e}")
        
        return default_cheats
    
    def get_game_id_from_rom(self, rom_path: str) -> str:
        """从ROM路径获取游戏ID"""
        rom_name = Path(rom_path).stem.lower()
        
        # 游戏名称映射
        game_mappings = {
            "super_mario": "super_mario_bros",
            "mario": "super_mario_bros",
            "contra": "contra",
            "megaman": "megaman",
            "rockman": "megaman",
            "castlevania": "castlevania",
            "zelda": "zelda",
            "metroid": "metroid"
        }
        
        for keyword, game_id in game_mappings.items():
            if keyword in rom_name:
                return game_id
        
        return "unknown"
    
    def get_available_cheats(self, rom_path: str) -> Dict:
        """获取可用的作弊码"""
        game_id = self.get_game_id_from_rom(rom_path)
        
        available_cheats = {}
        
        # 添加通用作弊码
        for cheat_id, cheat_data in self.universal_cheats.items():
            available_cheats[f"universal_{cheat_id}"] = cheat_data
        
        # 添加游戏特定作弊码
        if game_id in self.game_specific_cheats:
            game_cheats = self.game_specific_cheats[game_id].get("cheats", {})
            for cheat_id, cheat_data in game_cheats.items():
                available_cheats[f"game_{cheat_id}"] = cheat_data
        
        return available_cheats
    
    def enable_cheat(self, cheat_id: str, cheat_data: Dict) -> bool:
        """启用作弊码"""
        try:
            self.active_cheats[cheat_id] = {
                "data": cheat_data,
                "enabled": True,
                "last_applied": 0
            }
            
            print(f"🎯 作弊码已启用: {cheat_data.get('name', cheat_id)}")
            return True
            
        except Exception as e:
            print(f"❌ 启用作弊码失败: {e}")
            return False
    
    def disable_cheat(self, cheat_id: str) -> bool:
        """禁用作弊码"""
        try:
            if cheat_id in self.active_cheats:
                self.active_cheats[cheat_id]["enabled"] = False
                print(f"🚫 作弊码已禁用: {cheat_id}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ 禁用作弊码失败: {e}")
            return False
    
    def auto_enable_cheats(self, rom_path: str) -> int:
        """自动启用作弊码"""
        available_cheats = self.get_available_cheats(rom_path)
        enabled_count = 0
        
        for cheat_id, cheat_data in available_cheats.items():
            if cheat_data.get("auto_enable", False):
                if self.enable_cheat(cheat_id, cheat_data):
                    enabled_count += 1
        
        print(f"🎯 自动启用了 {enabled_count} 个作弊码")
        return enabled_count
    
    def apply_cheats(self, memory_manager) -> int:
        """应用作弊码到游戏内存"""
        applied_count = 0
        current_time = time.time()
        
        for cheat_id, cheat_info in self.active_cheats.items():
            if not cheat_info.get("enabled", False):
                continue
            
            # 限制应用频率（每秒最多一次）
            if current_time - cheat_info.get("last_applied", 0) < 1.0:
                continue
            
            cheat_data = cheat_info["data"]
            memory_addresses = cheat_data.get("memory_addresses", [])
            
            for addr_info in memory_addresses:
                address = addr_info.get("address")
                value = addr_info.get("value")
                
                if address is not None and value is not None:
                    try:
                        # 应用内存修改
                        if hasattr(memory_manager, 'write_memory'):
                            memory_manager.write_memory(address, value)
                        elif hasattr(memory_manager, 'set_memory'):
                            memory_manager.set_memory(address, value)
                        else:
                            # 模拟内存修改
                            print(f"🎯 模拟内存修改: 0x{address:04X} = {value}")
                        
                        applied_count += 1
                    except Exception as e:
                        print(f"⚠️ 应用作弊码失败 {cheat_id}: {e}")
            
            cheat_info["last_applied"] = current_time
        
        return applied_count
    
    def start_cheat_monitor(self, memory_manager) -> bool:
        """启动作弊码监控线程"""
        if self.cheat_thread and self.cheat_thread.is_alive():
            self.cheat_enabled = False
            self.cheat_thread.join()
        
        self.cheat_enabled = True
        self.cheat_thread = threading.Thread(
            target=self._cheat_monitor_worker,
            args=(memory_manager,)
        )
        self.cheat_thread.daemon = True
        self.cheat_thread.start()
        
        print(f"🎯 作弊码监控已启动")
    
    def stop_cheat_monitor(self) -> bool:
        """停止作弊码监控"""
        self.cheat_enabled = False
        if self.cheat_thread and self.cheat_thread.is_alive():
            self.cheat_thread.join()
        print(f"🛑 作弊码监控已停止")
    
    def _cheat_monitor_worker(self, memory_manager) -> bool:
        """作弊码监控工作线程"""
        while self.cheat_enabled:
            try:
                if self.active_cheats:
                    applied = self.apply_cheats(memory_manager)
                    if applied > 0:
                        print(f"🎯 应用了 {applied} 个作弊码修改")
                
                time.sleep(1.0)  # 每秒检查一次
                
            except Exception as e:
                print(f"⚠️ 作弊码监控出错: {e}")
                time.sleep(5.0)  # 出错后等待5秒
    
    def get_cheat_status(self) -> Dict:
        """获取作弊码状态"""
        status = {
            "total_cheats": len(self.active_cheats),
            "enabled_cheats": 0,
            "active_cheats": []
        }
        
        for cheat_id, cheat_info in self.active_cheats.items():
            if cheat_info.get("enabled", False):
                status["enabled_cheats"] += 1
                status["active_cheats"].append({
                    "id": cheat_id,
                    "name": cheat_info["data"].get("name", cheat_id),
                    "description": cheat_info["data"].get("description", ""),
                    "last_applied": cheat_info.get("last_applied", 0)
                })
        
        return status
    
    def save_cheat_config(self, rom_path: str) -> bool:
        """保存作弊码配置"""
        try:
            game_id = self.get_game_id_from_rom(rom_path)
            config_file = self.cheats_dir / f"{game_id}_config.json"
            
            config = {
                "game_id": game_id,
                "rom_path": rom_path,
                "active_cheats": {},
                "timestamp": time.time()
            }
            
            for cheat_id, cheat_info in self.active_cheats.items():
                config["active_cheats"][cheat_id] = {
                    "enabled": cheat_info.get("enabled", False),
                    "data": cheat_info["data"]
                }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"💾 作弊码配置已保存")
            return True
            
        except Exception as e:
            print(f"❌ 保存作弊码配置失败: {e}")
            return False
    
    def load_cheat_config(self, rom_path: str) -> bool:
        """加载作弊码配置"""
        try:
            game_id = self.get_game_id_from_rom(rom_path)
            config_file = self.cheats_dir / f"{game_id}_config.json"
            
            if not config_file.exists():
                return False
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.active_cheats = {}
            for cheat_id, cheat_config in config.get("active_cheats", {}).items():
                self.active_cheats[cheat_id] = {
                    "data": cheat_config["data"],
                    "enabled": cheat_config.get("enabled", False),
                    "last_applied": 0
                }
            
            print(f"📂 作弊码配置已加载")
            return True
            
        except Exception as e:
            print(f"❌ 加载作弊码配置失败: {e}")
            return False