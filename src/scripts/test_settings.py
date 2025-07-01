#!/usr/bin/env python3
"""
设置管理器测试脚本
"""

import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.settings_manager import SettingsManager
from src.core.cheat_manager import CheatManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_settings_manager():
    """测试设置管理器"""
    print("🔧 测试设置管理器")
    print("=" * 50)

    try:
        # 初始化设置管理器
        settings_manager = SettingsManager()

        print("📋 当前设置:")

        # 测试显示设置
        display_settings = settings_manager.get_display_settings()
        print(f"  显示设置: {display_settings}")

        # 测试音频设置
        audio_settings = settings_manager.get_audio_settings()
        print(f"  音频设置: {audio_settings}")

        # 测试输入设置
        input_settings = settings_manager.get_input_settings()
        print(f"  输入设置: {input_settings}")

        # 测试模拟设置
        emulation_settings = settings_manager.get_emulation_settings()
        print(f"  模拟设置: {emulation_settings}")

        print("\n🔧 测试设置修改:")

        # 修改音量设置
        original_volume = settings_manager.get_setting("audio_settings.master_volume")
        print(f"  原始音量: {original_volume}")

        settings_manager.set_setting("audio_settings.master_volume", 90)
        new_volume = settings_manager.get_setting("audio_settings.master_volume")
        print(f"  新音量: {new_volume}")

        # 修改分辨率设置
        settings_manager.set_setting("display_settings.resolution.width", 1280)
        settings_manager.set_setting("display_settings.resolution.height", 720)

        resolution = settings_manager.get_setting("display_settings.resolution")
        print(f"  新分辨率: {resolution}")

        # 保存设置
        settings_manager.save_settings()
        print("💾 设置已保存")

        # 测试按键映射
        key_mappings = settings_manager.get_key_mappings(1)
        print(f"  玩家1按键映射: {key_mappings}")

        # 测试树莓派设置
        pi_settings = settings_manager.get_raspberry_pi_settings()
        print(f"  树莓派设置: {pi_settings}")

        print("✅ 设置管理器测试完成")
        return True

    except Exception as e:
        print(f"❌ 设置管理器测试失败: {e}")
        return False


def test_cheat_manager():
    """测试金手指管理器"""
    print("\n🎯 测试金手指管理器")
    print("=" * 50)

    try:
        # 初始化金手指管理器
        cheat_manager = CheatManager()

        print("📋 支持的系统:")
        for system in cheat_manager.cheat_database:
            system_info = cheat_manager.cheat_database[system]
            print(f"  {system}: {system_info.get('system_name', 'Unknown')}")

        # 测试NES金手指
        nes_cheats = cheat_manager.get_system_cheats("nes")
        if nes_cheats:
            print(f"\n🎮 NES金手指:")
            common_cheats = nes_cheats.get("common_cheats", {})
            for cheat_id, cheat_info in common_cheats.items():
                print(f"  {cheat_id}: {cheat_info['name']} - {cheat_info['description']}")

        # 测试启用/禁用金手指
        print(f"\n🔧 测试金手指操作:")

        # 启用无限生命
        success = cheat_manager.enable_cheat("nes", "common", "infinite_lives")
        print(f"  启用无限生命: {'成功' if success else '失败'}")

        # 获取激活的金手指
        active_cheats = cheat_manager.get_active_cheats()
        print(f"  激活的金手指: {len(active_cheats)} 个")

        # 禁用金手指
        success = cheat_manager.disable_cheat("nes", "common", "infinite_lives")
        print(f"  禁用无限生命: {'成功' if success else '失败'}")

        # 清除所有金手指
        cheat_manager.clear_all_cheats()
        print(f"  已清除所有金手指")

        print("✅ 金手指管理器测试完成")
        return True

    except Exception as e:
        print(f"❌ 金手指管理器测试失败: {e}")
        return False


def test_integration():
    """测试集成功能"""
    print("\n🔗 测试集成功能")
    print("=" * 50)

    try:
        settings_manager = SettingsManager()
        cheat_manager = CheatManager()

        # 测试金手指功能是否启用
        cheats_enabled = settings_manager.is_feature_enabled("emulation_settings.cheats.enabled")
        print(f"  金手指功能启用: {cheats_enabled}")

        # 测试自动保存功能
        auto_save = settings_manager.is_feature_enabled("emulation_settings.save_states.auto_save")
        print(f"  自动保存启用: {auto_save}")

        # 测试手柄功能
        gamepad_enabled = settings_manager.is_feature_enabled("input_settings.gamepad.enabled")
        print(f"  手柄功能启用: {gamepad_enabled}")

        # 测试音效功能
        sound_enabled = settings_manager.is_feature_enabled("audio_settings.sound_effects")
        print(f"  音效功能启用: {sound_enabled}")

        print("✅ 集成功能测试完成")
        return True

    except Exception as e:
        print(f"❌ 集成功能测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🎮 GamePlayer-Raspberry 设置系统测试")
    print("=" * 60)

    results = []

    # 运行测试
    results.append(test_settings_manager())
    results.append(test_cheat_manager())
    results.append(test_integration())

    # 统计结果
    passed = sum(results)
    total = len(results)

    print(f"\n📊 测试结果:")
    print(f"  总测试数: {total}")
    print(f"  通过测试: {passed}")
    print(f"  失败测试: {total - passed}")
    print(f"  通过率: {passed/total*100:.1f}%")

    if passed == total:
        print("🎉 所有测试通过!")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
