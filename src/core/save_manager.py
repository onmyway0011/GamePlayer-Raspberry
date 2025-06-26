#!/usr/bin/env python3
"""
游戏存档管理器
支持本地存档和云端同步
"""

import os
import json
import time
import hashlib
import pickle
import threading
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
import requests

class SaveManager:
    """游戏存档管理器"""
    
    def __init__(self, saves_dir -> bool: str = "saves", cloud_config -> bool: Optional[Dict] = None) -> bool:
        self.saves_dir = Path(saves_dir)
        self.saves_dir.mkdir(parents=True, exist_ok=True)
        
        # 云端配置
        self.cloud_config = cloud_config or {}
        self.cloud_enabled = bool(self.cloud_config.get("enabled", False))
        self.cloud_url = self.cloud_config.get("url", "")
        self.cloud_token = self.cloud_config.get("token", "")
        
        # 自动保存配置
        self.auto_save_interval = 30  # 30秒自动保存
        self.max_save_slots = 10
        self.auto_save_thread = None
        self.auto_save_enabled = True
        
        # 当前游戏状态
        self.current_game = None
        self.current_save_data = {}
        self.last_save_time = 0
        
        print(f"💾 存档管理器初始化完成")
        print(f"📁 本地存档目录: {self.saves_dir}")
        if self.cloud_enabled:
            print(f"☁️ 云端存档已启用: {self.cloud_url}")
    
    def get_game_id(self, rom_path: str) -> str:
        """获取游戏唯一ID"""
        rom_file = Path(rom_path)
        
        # 使用ROM文件的MD5作为游戏ID
        try:
            with open(rom_file, 'rb') as f:
                content = f.read()
                game_id = hashlib.md5(content).hexdigest()[:16]
        except Exception:
            # 如果无法读取文件，使用文件名
            game_id = hashlib.md5(rom_file.name.encode()).hexdigest()[:16]
        
        return game_id
    
    def get_save_path(self, game_id: str, slot: int = 0) -> Path:
        """获取存档文件路径"""
        return self.saves_dir / f"{game_id}_slot_{slot}.save"
    
    def get_save_info_path(self, game_id: str) -> Path:
        """获取存档信息文件路径"""
        return self.saves_dir / f"{game_id}_info.json"
    
    def create_save_data(self, game_state: Dict) -> Dict:
        """创建存档数据"""
        return {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "game_state": game_state,
            "version": "1.0",
            "checksum": hashlib.md5(str(game_state).encode()).hexdigest()
        }
    
    def save_game(self, rom_path: str, game_state: Dict, slot: int = 0) -> bool:
        """保存游戏进度"""
        try:
            game_id = self.get_game_id(rom_path)
            save_path = self.get_save_path(game_id, slot)
            info_path = self.get_save_info_path(game_id)
            
            # 创建存档数据
            save_data = self.create_save_data(game_state)
            
            # 保存存档文件
            with open(save_path, 'wb') as f:
                pickle.dump(save_data, f)
            
            # 更新存档信息
            save_info = self.load_save_info(game_id)
            save_info["slots"][str(slot)] = {
                "timestamp": save_data["timestamp"],
                "datetime": save_data["datetime"],
                "size": save_path.stat().st_size,
                "checksum": save_data["checksum"]
            }
            save_info["last_played"] = save_data["timestamp"]
            save_info["total_saves"] = save_info.get("total_saves", 0) + 1
            
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(save_info, f, indent=2, ensure_ascii=False)
            
            print(f"💾 游戏存档已保存: 插槽 {slot}")
            
            # 云端同步
            if self.cloud_enabled:
                self.sync_to_cloud(game_id, slot, save_data)
            
            return True
            
        except Exception as e:
            print(f"❌ 保存游戏失败: {e}")
            return False
    
    def load_game(self, rom_path: str, slot: int = 0) -> Optional[Dict]:
        """加载游戏进度"""
        try:
            game_id = self.get_game_id(rom_path)
            save_path = self.get_save_path(game_id, slot)
            
            if not save_path.exists():
                print(f"📁 存档文件不存在: 插槽 {slot}")
                return None
            
            # 加载存档文件
            with open(save_path, 'rb') as f:
                save_data = pickle.load(f)
            
            # 验证存档完整性
            game_state = save_data.get("game_state", {})
            expected_checksum = save_data.get("checksum", "")
            actual_checksum = hashlib.md5(str(game_state).encode()).hexdigest()
            
            if expected_checksum != actual_checksum:
                print(f"⚠️ 存档文件可能已损坏: 插槽 {slot}")
                return None
            
            print(f"📂 游戏存档已加载: 插槽 {slot}")
            print(f"📅 保存时间: {save_data.get('datetime', '未知')}")
            
            return game_state
            
        except Exception as e:
            print(f"❌ 加载游戏失败: {e}")
            return None
    
    def load_save_info(self, game_id: str) -> Dict:
        """加载存档信息"""
        info_path = self.get_save_info_path(game_id)
        
        if info_path.exists():
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # 返回默认信息
        return {
            "game_id": game_id,
            "slots": {},
            "last_played": 0,
            "total_saves": 0,
            "created": time.time()
        }
    
    def list_saves(self, rom_path: str) -> Dict:
        """列出游戏的所有存档"""
        game_id = self.get_game_id(rom_path)
        save_info = self.load_save_info(game_id)
        
        saves = {}
        for slot_str, slot_info in save_info.get("slots", {}).items():
            slot = int(slot_str)
            save_path = self.get_save_path(game_id, slot)
            
            if save_path.exists():
                saves[slot] = {
                    "exists": True,
                    "timestamp": slot_info.get("timestamp", 0),
                    "datetime": slot_info.get("datetime", "未知"),
                    "size": slot_info.get("size", 0),
                    "path": str(save_path)
                }
            else:
                saves[slot] = {"exists": False}
        
        return saves
    
    def delete_save(self, rom_path: str, slot: int = 0) -> bool:
        """删除存档"""
        try:
            game_id = self.get_game_id(rom_path)
            save_path = self.get_save_path(game_id, slot)
            
            if save_path.exists():
                save_path.unlink()
                
                # 更新存档信息
                info_path = self.get_save_info_path(game_id)
                save_info = self.load_save_info(game_id)
                if str(slot) in save_info.get("slots", {}):
                    del save_info["slots"][str(slot)]
                
                with open(info_path, 'w', encoding='utf-8') as f:
                    json.dump(save_info, f, indent=2, ensure_ascii=False)
                
                print(f"🗑️ 存档已删除: 插槽 {slot}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ 删除存档失败: {e}")
            return False
    
    def start_auto_save(self, rom_path -> bool: str, get_game_state_func) -> bool:
        """启动自动保存"""
        self.current_game = rom_path
        self.get_game_state = get_game_state_func
        
        if self.auto_save_thread and self.auto_save_thread.is_alive():
            self.auto_save_enabled = False
            self.auto_save_thread.join()
        
        self.auto_save_enabled = True
        self.auto_save_thread = threading.Thread(target=self._auto_save_worker)
        self.auto_save_thread.daemon = True
        self.auto_save_thread.start()
        
        print(f"⏰ 自动保存已启动 (间隔: {self.auto_save_interval}秒)")
    
    def stop_auto_save(self) -> bool:
        """停止自动保存"""
        self.auto_save_enabled = False
        if self.auto_save_thread and self.auto_save_thread.is_alive():
            self.auto_save_thread.join()
        print(f"⏹️ 自动保存已停止")
    
    def _auto_save_worker(self) -> bool:
        """自动保存工作线程"""
        while self.auto_save_enabled:
            try:
                time.sleep(self.auto_save_interval)
                
                if not self.auto_save_enabled:
                    break
                
                if self.current_game and hasattr(self, 'get_game_state'):
                    game_state = self.get_game_state()
                    if game_state:
                        # 使用插槽0作为自动保存
                        self.save_game(self.current_game, game_state, slot=0)
                        self.last_save_time = time.time()
                
            except Exception as e:
                print(f"⚠️ 自动保存出错: {e}")
    
    def sync_to_cloud(self, game_id: str, slot: int, save_data: Dict) -> bool:
        """同步存档到云端"""
        if not self.cloud_enabled:
            return False
        
        try:
            # 准备上传数据
            upload_data = {
                "game_id": game_id,
                "slot": slot,
                "save_data": save_data,
                "timestamp": time.time()
            }
            
            headers = {
                "Authorization": f"Bearer {self.cloud_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.cloud_url}/api/saves/upload",
                json=upload_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"☁️ 存档已同步到云端: 插槽 {slot}")
                return True
            else:
                print(f"⚠️ 云端同步失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 云端同步出错: {e}")
            return False
    
    def sync_from_cloud(self, game_id: str, slot: int) -> Optional[Dict]:
        """从云端同步存档"""
        if not self.cloud_enabled:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.cloud_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.cloud_url}/api/saves/download/{game_id}/{slot}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                cloud_data = response.json()
                print(f"☁️ 从云端下载存档: 插槽 {slot}")
                return cloud_data.get("save_data", {}).get("game_state")
            else:
                print(f"⚠️ 云端下载失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 云端下载出错: {e}")
            return None