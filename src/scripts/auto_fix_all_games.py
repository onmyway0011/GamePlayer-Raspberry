#!/usr/bin/env python3
"""
自动检查和修复所有游戏
确保所有游戏都能正常运行
"""

import os
import sys
import json
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.game_health_checker import GameHealthChecker

# 完整的游戏数据库
GAMES_DATABASE = {
    "nes": [
        {
            "id": "super_mario_bros",
            "name": "Super Mario Bros",
            "file": "Super_Mario_Bros.nes",
            "description": "经典的横版跳跃游戏，马里奥的冒险之旅",
            "genre": "平台跳跃",
            "year": 1985,
            "players": "1-2",
            "image": "/static/images/covers/nes/super_mario_bros.jpg",
            "cheats": ["infinite_lives", "invincibility", "level_select"],
            "save_slots": 3,
            "recommended": True
        },
        {
            "id": "zelda",
            "name": "The Legend of Zelda",
            "file": "Legend_of_Zelda.nes",
            "description": "史诗级冒险RPG，林克的传说开始",
            "genre": "动作冒险",
            "year": 1986,
            "players": "1",
            "image": "/static/images/covers/nes/zelda.jpg",
            "cheats": ["infinite_lives", "max_abilities", "all_items"],
            "save_slots": 3,
            "recommended": True
        },
        {
            "id": "metroid",
            "name": "Metroid",
            "file": "Metroid.nes",
            "description": "科幻探索游戏，萨姆斯的银河冒险",
            "genre": "动作冒险",
            "year": 1986,
            "players": "1",
            "image": "/static/images/covers/nes/metroid.jpg",
            "cheats": ["infinite_lives", "invincibility", "all_weapons"],
            "save_slots": 3,
            "recommended": True
        },
        {
            "id": "castlevania",
            "name": "Castlevania",
            "file": "Castlevania.nes",
            "description": "哥特式动作游戏，对抗德古拉伯爵",
            "genre": "动作",
            "year": 1986,
            "players": "1",
            "image": "/static/images/covers/nes/castlevania.jpg",
            "cheats": ["infinite_lives", "invincibility", "max_abilities"],
            "save_slots": 3,
            "recommended": True
        },
        {
            "id": "mega_man",
            "name": "Mega Man",
            "file": "Mega_Man.nes",
            "description": "机器人动作游戏，洛克人的战斗",
            "genre": "动作",
            "year": 1987,
            "players": "1",
            "image": "/static/images/covers/nes/mega_man.jpg",
            "cheats": ["infinite_lives", "all_weapons", "invincibility"],
            "save_slots": 3,
            "recommended": True
        }
    ],
    "snes": [
        {
            "id": "super_mario_world",
            "name": "Super Mario World",
            "file": "Super_Mario_World.smc",
            "description": "超级马里奥的恐龙岛冒险",
            "genre": "平台跳跃",
            "year": 1990,
            "players": "1-2",
            "image": "/static/images/covers/snes/super_mario_world.jpg",
            "cheats": ["infinite_lives", "invincibility", "level_select"],
            "save_slots": 4,
            "recommended": True
        },
        {
            "id": "chrono_trigger",
            "name": "Chrono Trigger",
            "file": "Chrono_Trigger.smc",
            "description": "时空穿越RPG经典之作",
            "genre": "RPG",
            "year": 1995,
            "players": "1",
            "image": "/static/images/covers/snes/chrono_trigger.jpg",
            "cheats": ["max_abilities", "infinite_mp", "all_items"],
            "save_slots": 3,
            "recommended": True
        }
    ],
    "gameboy": [
        {
            "id": "tetris",
            "name": "Tetris",
            "file": "Tetris.gb",
            "description": "经典俄罗斯方块游戏",
            "genre": "益智",
            "year": 1989,
            "players": "1-2",
            "image": "/static/images/covers/gameboy/tetris.jpg",
            "cheats": ["infinite_time", "level_select"],
            "save_slots": 1,
            "recommended": True
        },
        {
            "id": "pokemon_red",
            "name": "Pokemon Red",
            "file": "Pokemon_Red.gb",
            "description": "口袋妖怪红版，收集所有精灵",
            "genre": "RPG",
            "year": 1996,
            "players": "1",
            "image": "/static/images/covers/gameboy/pokemon_red.jpg",
            "cheats": ["infinite_money", "all_pokemon", "max_level"],
            "save_slots": 1,
            "recommended": True
        }
    ]
}


class AutoGameFixer:
    """自动游戏修复器"""

    def __init__(self):
        """TODO: Add docstring"""
        self.health_checker = GameHealthChecker()
        self.total_games = 0
        self.healthy_games = 0
        self.fixed_games = 0

    def run_auto_fix(self, max_iterations=5):
        """运行自动修复"""
        print("🎮 GamePlayer-Raspberry 自动游戏修复器")
        print("=" * 60)
        print("🔍 开始检查所有游戏状态...")

        # 计算总游戏数
        self.total_games = sum(len(games) for games in GAMES_DATABASE.values())
        print(f"📊 发现 {self.total_games} 个游戏需要检查")

        # 运行持续检查和修复
        final_report = self.health_checker.run_continuous_check(GAMES_DATABASE, max_iterations)

        # 更新统计
        self.healthy_games = final_report['games_healthy']
        self.fixed_games = final_report['games_fixed']

        # 显示最终结果
        self.show_final_results(final_report)

        return final_report

    def show_final_results(self, report):
        """显示最终结果"""
        print("\n" + "=" * 60)
        print("🎉 自动修复完成！")
        print("=" * 60)

        # 显示统计
        print(f"📊 游戏统计:")
        print(f"   总游戏数: {self.total_games}")
        print(f"   正常运行: {self.healthy_games}")
        print(f"   修复游戏: {self.fixed_games}")
        print(f"   成功率: {self.healthy_games/self.total_games*100:.1f}%")

        # 显示状态
        status_messages = {
            'all_healthy': '🟢 所有游戏都正常运行！',
            'mostly_healthy': '🟡 大部分游戏正常运行',
            'partially_healthy': '🟠 部分游戏正常运行',
            'needs_attention': '🔴 需要手动处理'
        }

        overall_status = report['overall_status']
        print(f"\n📈 总体状态: {status_messages.get(overall_status, overall_status)}")

        # 显示系统详情
        print(f"\n📂 系统详情:")
        for system, system_report in report['systems'].items():
            emulator_status = system_report['emulator_status']
            games_count = len(system_report['games'])
            healthy_count = sum(1 for g in system_report['games'].values() if g['status'] == 'healthy')

            status_icon = "✅" if emulator_status == 'available' else "❌"
            print(f"   {system.upper()}:")
            print(f"     {status_icon} 模拟器: {emulator_status}")
            print(f"     🎮 游戏: {healthy_count}/{games_count} 正常")

            if system_report['fixes']:
                print(f"     🔧 修复: {', '.join(system_report['fixes'])}")

        # 显示应用的修复
        if report['fixes_applied']:
            print(f"\n🔧 应用的修复:")
            for fix in report['fixes_applied']:
                print(f"   • {fix}")

        # 显示建议
        if overall_status == 'all_healthy':
            print(f"\n🎉 恭喜！所有游戏都可以正常运行！")
            print(f"🎮 您现在可以启动任意游戏并享受游戏体验。")
        else:
            print(f"\n💡 建议:")
            if self.healthy_games < self.total_games:
                print(f"   • 检查系统日志了解详细错误信息")
                print(f"   • 确保有足够的磁盘空间和网络连接")
                print(f"   • 手动安装失败的模拟器")

            print(f"   • 运行 'python3 src/scripts/simple_demo_server.py' 启动Web界面")
            print(f"   • 在Web界面中使用'自动修复'功能")

        # 保存报告
        self.save_report(report)

    def save_report(self, report):
        """保存报告到文件"""
        try:
            reports_dir = project_root / "reports"
            reports_dir.mkdir(exist_ok=True)

            timestamp = time.strftime('%Y%m%d_%H%M%S')
            report_file = reports_dir / f"game_health_report_{timestamp}.json"

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            print(f"\n📄 详细报告已保存: {report_file}")

        except Exception as e:
            print(f"⚠️ 保存报告失败: {e}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='自动检查和修复所有游戏')
    parser.add_argument('--max-iterations', type=int, default=5,
                       help='最大修复迭代次数 (默认: 5)')
    parser.add_argument('--check-only', action='store_true',
                       help='仅检查状态，不进行修复')

    args = parser.parse_args()

    fixer = AutoGameFixer()

    if args.check_only:
        print("🔍 仅检查模式 - 不会进行任何修复")
        report = fixer.health_checker.check_all_games(GAMES_DATABASE)
        fixer.healthy_games = report['games_healthy']
        fixer.total_games = report['games_total']
        fixer.show_final_results(report)
    else:
        fixer.run_auto_fix(args.max_iterations)

if __name__ == "__main__":
    main()
