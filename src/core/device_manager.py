#!/usr/bin/env python3
"""
设备管理器
自动连接USB手柄和蓝牙耳机
"""

import os
import sys
import time
import subprocess
import threading
import pygame
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class DeviceManager:
    """设备管理器"""
    
    def __init__(self) -> bool:
        # 初始化pygame的joystick模块
        pygame.init()
        pygame.joystick.init()
        
        # 设备状态
        self.connected_controllers = {}
        self.connected_audio_devices = {}
        self.device_monitor_thread = None
        self.monitor_enabled = True
        
        # 支持的控制器
        self.supported_controllers = {
            "Xbox": ["Xbox", "Microsoft", "xbox"],
            "PlayStation": ["PlayStation", "Sony", "DualShock", "ps"],
            "Nintendo": ["Nintendo", "Pro Controller", "Joy-Con"],
            "Generic": ["USB", "Gamepad", "Controller"]
        }
        
        # 支持的音频设备
        self.supported_audio_devices = {
            "AirPods": ["AirPods", "Apple"],
            "Sony": ["Sony", "WH-", "WF-"],
            "Bose": ["Bose", "QuietComfort"],
            "JBL": ["JBL"],
            "Generic": ["Bluetooth", "Wireless", "Headset"]
        }
        
        print(f"🎮 设备管理器初始化完成")
    
    def scan_usb_controllers(self) -> List[Dict]:
        """扫描USB控制器"""
        controllers = []
        
        try:
            # 刷新joystick列表
            pygame.joystick.quit()
            pygame.joystick.init()
            
            joystick_count = pygame.joystick.get_count()
            
            for i in range(joystick_count):
                try:
                    joystick = pygame.joystick.Joystick(i)
                    joystick.init()
                    
                    controller_info = {
                        "id": i,
                        "name": joystick.get_name(),
                        "guid": joystick.get_guid(),
                        "axes": joystick.get_numaxes(),
                        "buttons": joystick.get_numbuttons(),
                        "hats": joystick.get_numhats(),
                        "connected": True,
                        "type": self.identify_controller_type(joystick.get_name())
                    }
                    
                    controllers.append(controller_info)
                    
                except Exception as e:
                    print(f"⚠️ 初始化控制器 {i} 失败: {e}")
        
        except Exception as e:
            print(f"❌ 扫描USB控制器失败: {e}")
        
        return controllers
    
    def identify_controller_type(self, name: str) -> str:
        """识别控制器类型"""
        name_lower = name.lower()
        
        for controller_type, keywords in self.supported_controllers.items():
            for keyword in keywords:
                if keyword.lower() in name_lower:
                    return controller_type
        
        return "Unknown"
    
    def scan_bluetooth_devices(self) -> List[Dict]:
        """扫描蓝牙设备"""
        devices = []
        
        try:
            # 使用bluetoothctl扫描设备
            if sys.platform.startswith('linux'):
                devices.extend(self._scan_bluetooth_linux())
            elif sys.platform == 'darwin':
                devices.extend(self._scan_bluetooth_macos())
            elif sys.platform == 'win32':
                devices.extend(self._scan_bluetooth_windows())
        
        except Exception as e:
            print(f"❌ 扫描蓝牙设备失败: {e}")
        
        return devices
    
    def _scan_bluetooth_linux(self) -> List[Dict]:
        """Linux蓝牙设备扫描"""
        devices = []
        
        try:
            # 检查bluetoothctl是否可用
            result = subprocess.run(['which', 'bluetoothctl'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️ bluetoothctl 未安装")
                return devices
            
            # 获取已配对的设备
            result = subprocess.run(['bluetoothctl', 'devices'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.startswith('Device'):
                        parts = line.split(' ', 2)
                        if len(parts) >= 3:
                            mac_address = parts[1]
                            device_name = parts[2]
                            
                            device_info = {
                                "mac": mac_address,
                                "name": device_name,
                                "type": self.identify_audio_device_type(device_name),
                                "connected": self._check_bluetooth_connection_linux(mac_address),
                                "platform": "linux"
                            }
                            
                            devices.append(device_info)
        
        except Exception as e:
            print(f"⚠️ Linux蓝牙扫描出错: {e}")
        
        return devices
    
    def _scan_bluetooth_macos(self) -> List[Dict]:
        """macOS蓝牙设备扫描"""
        devices = []
        
        try:
            # 使用system_profiler获取蓝牙设备信息
            result = subprocess.run([
                'system_profiler', 'SPBluetoothDataType', '-json'
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                # 解析蓝牙设备信息
                bluetooth_data = data.get('SPBluetoothDataType', [])
                for item in bluetooth_data:
                    devices_info = item.get('device_title', [])
                    for device_info in devices_info:
                        device_name = device_info.get('_name', 'Unknown')
                        
                        device = {
                            "name": device_name,
                            "type": self.identify_audio_device_type(device_name),
                            "connected": device_info.get('device_isconnected', 'No') == 'Yes',
                            "platform": "macos"
                        }
                        
                        devices.append(device)
        
        except Exception as e:
            print(f"⚠️ macOS蓝牙扫描出错: {e}")
        
        return devices
    
    def _scan_bluetooth_windows(self) -> List[Dict]:
        """Windows蓝牙设备扫描"""
        devices = []
        
        try:
            # 使用PowerShell获取蓝牙设备
            powershell_cmd = """
            Get-PnpDevice | Where-Object {$_.Class -eq "Bluetooth" -and $_.Status -eq "OK"} | 
            Select-Object FriendlyName, Status | ConvertTo-Json
            """
            
            result = subprocess.run([
                'powershell', '-Command', powershell_cmd
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                if isinstance(data, list):
                    device_list = data
                else:
                    device_list = [data]
                
                for device_info in device_list:
                    device_name = device_info.get('FriendlyName', 'Unknown')
                    
                    device = {
                        "name": device_name,
                        "type": self.identify_audio_device_type(device_name),
                        "connected": device_info.get('Status') == 'OK',
                        "platform": "windows"
                    }
                    
                    devices.append(device)
        
        except Exception as e:
            print(f"⚠️ Windows蓝牙扫描出错: {e}")
        
        return devices
    
    def identify_audio_device_type(self, name: str) -> str:
        """识别音频设备类型"""
        name_lower = name.lower()
        
        for device_type, keywords in self.supported_audio_devices.items():
            for keyword in keywords:
                if keyword.lower() in name_lower:
                    return device_type
        
        return "Unknown"
    
    def _check_bluetooth_connection_linux(self, mac_address: str) -> bool:
        """检查Linux蓝牙设备连接状态"""
        try:
            result = subprocess.run([
                'bluetoothctl', 'info', mac_address
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                return 'Connected: yes' in result.stdout
        
        except Exception:
            pass
        
        return False
    
    def connect_bluetooth_device(self, device_info: Dict) -> bool:
        """连接蓝牙设备"""
        try:
            platform = device_info.get("platform", sys.platform)
            
            if platform == "linux":
                return self._connect_bluetooth_linux(device_info)
            elif platform == "darwin":
                return self._connect_bluetooth_macos(device_info)
            elif platform == "win32":
                return self._connect_bluetooth_windows(device_info)
        
        except Exception as e:
            print(f"❌ 连接蓝牙设备失败: {e}")
        
        return False
    
    def _connect_bluetooth_linux(self, device_info: Dict) -> bool:
        """Linux蓝牙设备连接"""
        try:
            mac_address = device_info.get("mac")
            if not mac_address:
                return False
            
            # 尝试连接设备
            result = subprocess.run([
                'bluetoothctl', 'connect', mac_address
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"🔗 蓝牙设备连接成功: {device_info['name']}")
                return True
            else:
                print(f"⚠️ 蓝牙设备连接失败: {result.stderr}")
                return False
        
        except Exception as e:
            print(f"❌ Linux蓝牙连接出错: {e}")
            return False
    
    def _connect_bluetooth_macos(self, device_info: Dict) -> bool:
        """macOS蓝牙设备连接"""
        # macOS的蓝牙连接通常通过系统设置进行
        print(f"ℹ️ macOS蓝牙设备请通过系统设置连接: {device_info['name']}")
        return True
    
    def _connect_bluetooth_windows(self, device_info: Dict) -> bool:
        """Windows蓝牙设备连接"""
        # Windows的蓝牙连接通常通过设置应用进行
        print(f"ℹ️ Windows蓝牙设备请通过设置应用连接: {device_info['name']}")
        return True
    
    def auto_connect_devices(self) -> Tuple[int, int]:
        """自动连接设备"""
        print(f"🔍 开始自动连接设备...")
        
        # 扫描并连接USB控制器
        controllers = self.scan_usb_controllers()
        connected_controllers = 0
        
        for controller in controllers:
            if controller["connected"]:
                self.connected_controllers[controller["id"]] = controller
                connected_controllers += 1
                print(f"🎮 USB控制器已连接: {controller['name']} ({controller['type']})")
        
        # 扫描并连接蓝牙音频设备
        audio_devices = self.scan_bluetooth_devices()
        connected_audio = 0
        
        for device in audio_devices:
            if device.get("type") != "Unknown":
                if not device.get("connected", False):
                    # 尝试连接未连接的音频设备
                    if self.connect_bluetooth_device(device):
                        connected_audio += 1
                        self.connected_audio_devices[device["name"]] = device
                else:
                    connected_audio += 1
                    self.connected_audio_devices[device["name"]] = device
                    print(f"🎧 蓝牙音频设备已连接: {device['name']} ({device['type']})")
        
        print(f"✅ 设备连接完成: {connected_controllers} 个控制器, {connected_audio} 个音频设备")
        return connected_controllers, connected_audio
    
    def start_device_monitor(self) -> bool:
        """启动设备监控"""
        if self.device_monitor_thread and self.device_monitor_thread.is_alive():
            self.monitor_enabled = False
            self.device_monitor_thread.join()
        
        self.monitor_enabled = True
        self.device_monitor_thread = threading.Thread(target=self._device_monitor_worker)
        self.device_monitor_thread.daemon = True
        self.device_monitor_thread.start()
        
        print(f"👁️ 设备监控已启动")
    
    def stop_device_monitor(self) -> bool:
        """停止设备监控"""
        self.monitor_enabled = False
        if self.device_monitor_thread and self.device_monitor_thread.is_alive():
            self.device_monitor_thread.join()
        print(f"🛑 设备监控已停止")
    
    def _device_monitor_worker(self) -> bool:
        """设备监控工作线程"""
        while self.monitor_enabled:
            try:
                # 检查控制器连接状态
                current_controllers = self.scan_usb_controllers()
                
                # 检测新连接的控制器
                for controller in current_controllers:
                    controller_id = controller["id"]
                    if controller_id not in self.connected_controllers:
                        self.connected_controllers[controller_id] = controller
                        print(f"🎮 检测到新控制器: {controller['name']}")
                
                # 检测断开的控制器
                disconnected = []
                for controller_id in self.connected_controllers:
                    if not any(c["id"] == controller_id for c in current_controllers):
                        disconnected.append(controller_id)
                
                for controller_id in disconnected:
                    controller = self.connected_controllers.pop(controller_id)
                    print(f"🎮 控制器已断开: {controller['name']}")
                
                time.sleep(5.0)  # 每5秒检查一次
                
            except Exception as e:
                print(f"⚠️ 设备监控出错: {e}")
                time.sleep(10.0)  # 出错后等待10秒
    
    def get_device_status(self) -> Dict:
        """获取设备状态"""
        return {
            "controllers": {
                "count": len(self.connected_controllers),
                "devices": list(self.connected_controllers.values())
            },
            "audio_devices": {
                "count": len(self.connected_audio_devices),
                "devices": list(self.connected_audio_devices.values())
            },
            "monitor_enabled": self.monitor_enabled
        }
    
    def get_controller_input(self, controller_id: int = 0) -> Optional[Dict]:
        """获取控制器输入"""
        try:
            if controller_id in self.connected_controllers:
                joystick = pygame.joystick.Joystick(controller_id)
                
                # 处理pygame事件
                pygame.event.pump()
                
                input_state = {
                    "axes": [joystick.get_axis(i) for i in range(joystick.get_numaxes())],
                    "buttons": [joystick.get_button(i) for i in range(joystick.get_numbuttons())],
                    "hats": [joystick.get_hat(i) for i in range(joystick.get_numhats())]
                }
                
                return input_state
        
        except Exception as e:
            print(f"⚠️ 获取控制器输入失败: {e}")
        
        return None