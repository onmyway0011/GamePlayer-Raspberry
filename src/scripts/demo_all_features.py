#!/usr/bin/env python3
"""
GamePlayer-Raspberry 完整功能演示脚本
演示所有新增的功能：真实游戏启动、金手指配置、系统设置、状态检查
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class FeatureDemo:
    """功能演示器"""
    
    def __init__(self, base_url="http://localhost:3007"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_connection(self):
        """测试连接"""
        try:
            response = self.session.get(f"{self.base_url}/api/status")
            if response.status_code == 200:
                print("✅ 服务器连接正常")
                return True
            else:
                print(f"❌ 服务器连接失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 无法连接到服务器: {e}")
            return False
    
    def demo_game_launch(self):
        """演示游戏启动功能"""
        print("\n🎮 演示游戏启动功能")
        print("=" * 50)
        
        # 测试游戏启动
        game_data = {
            "game_id": "super_mario_bros",
            "system": "nes"
        }
        
        print(f"🚀 尝试启动游戏: {game_data['game_id']}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/launch_game",
                json=game_data,
                headers={"Content-Type": "application/json"}
            )
            
            result = response.json()
            
            if result.get("success"):
                print("✅ 游戏启动成功!")
                print(f"   消息: {result.get('message')}")
                if result.get('pid'):
                    print(f"   进程ID: {result.get('pid')}")
                if result.get('enabled_cheats'):
                    print(f"   启用金手指: {len(result.get('enabled_cheats'))}个")
            else:
                print("⚠️ 游戏启动失败 (这是正常的，因为模拟器未安装)")
                print(f"   错误: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ 游戏启动测试失败: {e}")
    
    def demo_cheat_config(self):
        """演示金手指配置功能"""
        print("\n🎯 演示金手指配置功能")
        print("=" * 50)
        
        system = "nes"
        
        # 获取金手指配置
        print(f"📋 获取 {system.upper()} 金手指配置...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/cheat_config/{system}")
            result = response.json()
            
            if result.get("success"):
                cheats = result.get("cheats", {})
                print(f"✅ 找到 {len(cheats)} 个金手指:")
                
                for cheat_id, cheat_data in cheats.items():
                    status = "✅" if cheat_data.get("enabled") else "☐"
                    auto = "🔄" if cheat_data.get("auto_enable") else ""
                    print(f"   {status} {auto} {cheat_data.get('name', cheat_id)}")
                    print(f"      代码: {cheat_data.get('code', 'N/A')}")
                
                # 测试切换金手指状态
                print(f"\n🔄 测试切换金手指状态...")
                test_cheat = "infinite_lives"
                
                if test_cheat in cheats:
                    current_status = cheats[test_cheat].get("enabled", False)
                    new_status = not current_status
                    
                    toggle_data = {
                        "cheat_id": test_cheat,
                        "enabled": new_status
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/api/cheat_config/{system}",
                        json=toggle_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    result = response.json()
                    
                    if result.get("success"):
                        print(f"✅ 成功切换 {test_cheat}: {current_status} → {new_status}")
                    else:
                        print(f"❌ 切换失败: {result.get('error')}")
                
            else:
                print(f"❌ 获取金手指配置失败: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ 金手指配置测试失败: {e}")
    
    def demo_system_settings(self):
        """演示系统设置功能"""
        print("\n⚙️ 演示系统设置功能")
        print("=" * 50)
        
        # 获取系统设置
        print("📋 获取系统设置...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/settings")
            result = response.json()
            
            if result.get("success"):
                settings = result.get("settings", {})
                print(f"✅ 找到 {len(settings)} 个设置分类:")
                
                for category, category_settings in settings.items():
                    print(f"\n   📂 {category.upper()}:")
                    for setting, value in category_settings.items():
                        print(f"      • {setting}: {value}")
                
                # 测试更新设置
                print(f"\n🔄 测试更新设置...")
                
                update_data = {
                    "category": "audio",
                    "setting": "volume",
                    "value": 75
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/settings",
                    json=update_data,
                    headers={"Content-Type": "application/json"}
                )
                
                result = response.json()
                
                if result.get("success"):
                    print(f"✅ 成功更新设置: audio.volume = 75")
                else:
                    print(f"❌ 更新设置失败: {result.get('error')}")
                
            else:
                print(f"❌ 获取系统设置失败: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ 系统设置测试失败: {e}")
    
    def demo_system_check(self):
        """演示系统状态检查功能"""
        print("\n🔍 演示系统状态检查功能")
        print("=" * 50)
        
        print("🔍 执行系统状态检查...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/system_check")
            result = response.json()
            
            overall_status = result.get("overall_status", "unknown")
            status_emoji = {
                "healthy": "🟢",
                "warning": "🟡", 
                "critical": "🔴"
            }.get(overall_status, "⚪")
            
            print(f"📊 总体状态: {status_emoji} {overall_status}")
            
            checks = result.get("checks", {})
            print(f"✅ 检查项目: {len(checks)}个")
            
            for check_name, check_result in checks.items():
                status = "✅" if check_result.get("status") else "❌"
                message = check_result.get("message", "无消息")
                print(f"   {status} {check_name}: {message}")
                
                # 显示自动修复结果
                if check_result.get("fix_result"):
                    fix_result = check_result["fix_result"]
                    fix_status = "🔧✅" if fix_result.get("success") else "🔧❌"
                    fix_message = fix_result.get("message", "无消息")
                    print(f"      {fix_status} 自动修复: {fix_message}")
            
            if result.get("demo_mode"):
                print("💡 当前为演示模式")
                
        except Exception as e:
            print(f"❌ 系统检查测试失败: {e}")
    
    def demo_game_status(self):
        """演示游戏状态查询功能"""
        print("\n📊 演示游戏状态查询功能")
        print("=" * 50)
        
        game_id = "super_mario_bros"
        
        print(f"📋 查询游戏状态: {game_id}")
        
        try:
            response = self.session.get(f"{self.base_url}/api/game_status/{game_id}")
            result = response.json()
            
            if result.get("success", True):  # 默认为成功
                print(f"✅ 游戏状态查询成功:")
                print(f"   游戏ID: {result.get('game_id')}")
                print(f"   状态: {result.get('status')}")
                print(f"   运行中: {result.get('is_running')}")
                
                running_games = result.get("running_games", [])
                if running_games:
                    print(f"   正在运行的游戏: {', '.join(running_games)}")
                else:
                    print(f"   当前没有游戏在运行")
                
                if result.get("demo_mode"):
                    print("💡 当前为演示模式")
                    
            else:
                print(f"❌ 游戏状态查询失败: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ 游戏状态查询测试失败: {e}")
    
    def run_all_demos(self):
        """运行所有演示"""
        print("🎮 GamePlayer-Raspberry 完整功能演示")
        print("=" * 60)
        
        if not self.test_connection():
            print("❌ 无法连接到服务器，请确保服务器正在运行")
            print("💡 启动命令: PORT=3007 python3 src/scripts/simple_demo_server.py")
            return False
        
        # 运行所有演示
        self.demo_game_launch()
        self.demo_cheat_config()
        self.demo_system_settings()
        self.demo_system_check()
        self.demo_game_status()
        
        print("\n🎉 所有功能演示完成!")
        print("=" * 60)
        print("📱 Web界面访问: http://localhost:3007")
        print("🎮 在Web界面中可以体验完整的可视化功能")
        
        return True

def main():
    """主函数"""
    demo = FeatureDemo()
    demo.run_all_demos()

if __name__ == "__main__":
    main()
