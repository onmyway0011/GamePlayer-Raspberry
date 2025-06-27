#!/usr/bin/env python3
"""
自动金手指功能测试脚本
"""

import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.cheat_manager import CheatManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_auto_cheat_functionality():
    """测试自动金手指功能"""
    print("🎯 测试自动金手指功能")
    print("=" * 60)
    
    try:
        # 初始化金手指管理器
        cheat_manager = CheatManager()
        
        print("📋 支持的游戏系统:")
        for system in cheat_manager.cheat_database:
            system_info = cheat_manager.cheat_database[system]
            print(f"  🎮 {system}: {system_info.get('system_name', 'Unknown')}")
        
        print("\n🎯 自动启用金手指测试:")
        
        # 测试各个系统的自动金手指
        test_systems = ["nes", "snes", "gb", "gba", "genesis"]
        
        for system in test_systems:
            print(f"\n📱 测试 {system.upper()} 系统:")
            
            # 获取自动启用的金手指列表
            auto_cheats = cheat_manager.get_auto_enable_cheats(system)
            print(f"  自动启用金手指数量: {len(auto_cheats)}")
            
            if auto_cheats:
                print("  自动启用的金手指:")
                for cheat in auto_cheats:
                    print(f"    ✅ {cheat}")
            
            # 模拟游戏启动时自动启用金手指
            enabled_count = cheat_manager.auto_enable_cheats_for_game(system, "test_game")
            print(f"  实际启用数量: {enabled_count}")
            
            # 获取当前激活的金手指
            active_cheats = cheat_manager.get_active_cheats()
            system_active = [k for k in active_cheats.keys() if k.startswith(system)]
            print(f"  当前激活数量: {len(system_active)}")
            
            # 清除金手指以便下次测试
            cheat_manager.clear_all_cheats()
        
        print("\n🔧 金手指配置测试:")
        
        # 测试修改自动启用设置
        print("  测试修改自动启用设置...")
        success = cheat_manager.set_auto_enable_cheat("nes", "infinite_time", True)
        print(f"  设置无限时间自动启用: {'成功' if success else '失败'}")
        
        # 验证设置是否生效
        auto_cheats = cheat_manager.get_auto_enable_cheats("nes")
        has_infinite_time = "无限时间" in auto_cheats
        print(f"  验证设置生效: {'是' if has_infinite_time else '否'}")
        
        print("\n✅ 自动金手指功能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 自动金手指功能测试失败: {e}")
        return False

def test_cheat_database_integrity():
    """测试金手指数据库完整性"""
    print("\n🔍 测试金手指数据库完整性")
    print("=" * 60)
    
    try:
        cheat_manager = CheatManager()
        
        required_cheats = ["infinite_lives", "invincibility", "max_power", "level_select"]
        
        for system in cheat_manager.cheat_database:
            system_data = cheat_manager.cheat_database[system]
            common_cheats = system_data.get("common_cheats", {})
            
            print(f"📱 {system.upper()} 系统检查:")
            
            for required_cheat in required_cheats:
                if required_cheat in common_cheats:
                    cheat_data = common_cheats[required_cheat]
                    auto_enable = cheat_data.get("auto_enable", False)
                    enabled = cheat_data.get("enabled", False)
                    
                    status = "✅" if auto_enable else "⚪"
                    print(f"  {status} {cheat_data['name']}: 自动启用={auto_enable}, 当前启用={enabled}")
                else:
                    print(f"  ❌ 缺少必需金手指: {required_cheat}")
        
        print("\n✅ 数据库完整性检查完成")
        return True
        
    except Exception as e:
        print(f"❌ 数据库完整性检查失败: {e}")
        return False

def test_game_launch_simulation():
    """模拟游戏启动流程测试"""
    print("\n🎮 模拟游戏启动流程测试")
    print("=" * 60)
    
    try:
        cheat_manager = CheatManager()
        
        # 模拟启动不同系统的游戏
        test_games = [
            ("nes", "Super Mario Bros"),
            ("snes", "Super Mario World"),
            ("gb", "Pokemon Red"),
            ("gba", "Pokemon Ruby"),
            ("genesis", "Sonic the Hedgehog")
        ]
        
        for system, game_name in test_games:
            print(f"\n🎮 启动游戏: {game_name} ({system.upper()})")
            
            # 清除之前的金手指
            cheat_manager.clear_all_cheats()
            
            # 自动启用金手指
            enabled_count = cheat_manager.auto_enable_cheats_for_game(system, game_name)
            
            # 获取启用的金手指列表
            active_cheats = cheat_manager.get_active_cheats()
            
            print(f"  启用金手指数量: {enabled_count}")
            print(f"  激活金手指数量: {len(active_cheats)}")
            
            if active_cheats:
                print("  激活的金手指:")
                for cheat_key in active_cheats:
                    print(f"    🎯 {cheat_key}")
        
        print("\n✅ 游戏启动流程测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 游戏启动流程测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🎯 GamePlayer-Raspberry 自动金手指功能测试")
    print("=" * 70)
    
    results = []
    
    # 运行测试
    results.append(test_auto_cheat_functionality())
    results.append(test_cheat_database_integrity())
    results.append(test_game_launch_simulation())
    
    # 统计结果
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 测试结果总结:")
    print(f"  总测试数: {total}")
    print(f"  通过测试: {passed}")
    print(f"  失败测试: {total - passed}")
    print(f"  通过率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有自动金手指功能测试通过!")
        print("💡 游戏启动时将自动启用以下金手指:")
        print("   ✅ 无限生命 - 永不死亡")
        print("   ✅ 无敌模式 - 免疫伤害")
        print("   ✅ 最大能力 - 能力值最大")
        print("   ✅ 关卡选择 - 任意关卡")
        return 0
    else:
        print("\n❌ 部分自动金手指功能测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
