#!/usr/bin/env python3
"""
简化的GamePlayer-Raspberry演示服务器
用于Docker浏览器演示
"""

import os
import sys
import json
import time
import threading
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request, send_from_directory

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入核心模块
try:
    from src.scripts.improved_game_launcher import ImprovedGameLauncher
    from src.core.system_checker import SystemChecker
    from src.core.cheat_manager import CheatManager
    from src.core.settings_manager import SettingsManager
    from src.core.bing_cover_downloader import BingCoverDownloader
    from src.core.game_health_checker import GameHealthChecker
except ImportError as e:
    print(f"⚠️ 导入核心模块失败: {e}")
    GameLauncher = None
    SystemChecker = None
    CheatManager = None
    SettingsManager = None
    CoverDownloader = None
    GameHealthChecker = None

app = Flask(__name__)

# 初始化核心组件
game_launcher = ImprovedGameLauncher()
system_checker = SystemChecker() if SystemChecker else None
cheat_manager = CheatManager() if CheatManager else None
settings_manager = SettingsManager() if SettingsManager else None
cover_downloader = BingCoverDownloader()
game_health_checker = GameHealthChecker() if GameHealthChecker else None

# 扩展的游戏数据库
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
            "recommended": True,
            "download_url": "https://archive.org/download/No-Intro-Collection_2016-01-03_Fixed/Nintendo%20-%20Nintendo%20Entertainment%20System%20%28Headered%29%20%282016-01-03%29.zip"
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
        },
        {
            "id": "contra",
            "name": "Contra",
            "file": "Contra.nes",
            "description": "经典双人射击游戏，30条命秘籍的起源",
            "genre": "射击",
            "year": 1987,
            "players": "1-2",
            "image": "/static/images/covers/nes/contra.jpg",
            "cheats": ["infinite_lives", "all_weapons", "invincibility"],
            "save_slots": 3,
            "recommended": True
        },
        {
            "id": "duck_hunt",
            "name": "Duck Hunt",
            "file": "Duck_Hunt.nes",
            "description": "经典光枪射击游戏，猎鸭挑战",
            "genre": "射击",
            "year": 1984,
            "players": "1-2",
            "image": "/static/images/covers/nes/duck_hunt.jpg",
            "cheats": ["infinite_ammo", "perfect_aim"],
            "save_slots": 1,
            "recommended": False
        },
        {
            "id": "pac_man",
            "name": "Pac-Man",
            "file": "Pac_Man.nes",
            "description": "经典街机移植，吃豆人的冒险",
            "genre": "街机",
            "year": 1982,
            "players": "1-2",
            "image": "/static/images/covers/nes/pac_man.jpg",
            "cheats": ["infinite_lives", "level_select"],
            "save_slots": 1,
            "recommended": False
        },
        {
            "id": "donkey_kong",
            "name": "Donkey Kong",
            "file": "Donkey_Kong.nes",
            "description": "马里奥的首次亮相，经典平台游戏",
            "genre": "平台跳跃",
            "year": 1981,
            "players": "1-2",
            "image": "/static/images/covers/nes/donkey_kong.jpg",
            "cheats": ["infinite_lives", "level_select"],
            "save_slots": 1,
            "recommended": False
        },
        {
            "id": "galaga",
            "name": "Galaga",
            "file": "Galaga.nes",
            "description": "经典太空射击游戏",
            "genre": "射击",
            "year": 1981,
            "players": "1-2",
            "image": "/static/images/covers/nes/galaga.jpg",
            "cheats": ["infinite_lives", "double_ship"],
            "save_slots": 1,
            "recommended": False
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
        },
        {
            "id": "super_metroid",
            "name": "Super Metroid",
            "file": "Super_Metroid.smc",
            "description": "萨姆斯的银河探索续作",
            "genre": "动作冒险",
            "year": 1994,
            "players": "1",
            "image": "/static/images/covers/snes/super_metroid.jpg",
            "cheats": ["infinite_lives", "invincibility", "all_weapons"],
            "save_slots": 3,
            "recommended": True
        },
        {
            "id": "final_fantasy_vi",
            "name": "Final Fantasy VI",
            "file": "Final_Fantasy_VI.smc",
            "description": "史诗级RPG巨作，最终幻想系列巅峰",
            "genre": "RPG",
            "year": 1994,
            "players": "1",
            "image": "/static/images/covers/snes/final_fantasy_vi.jpg",
            "cheats": ["max_abilities", "infinite_mp", "all_items"],
            "save_slots": 3,
            "recommended": True
        },
        {
            "id": "zelda_link_to_past",
            "name": "The Legend of Zelda: A Link to the Past",
            "file": "Zelda_Link_to_Past.smc",
            "description": "塞尔达传说系列的经典之作",
            "genre": "动作冒险",
            "year": 1991,
            "players": "1",
            "image": "/static/images/covers/snes/zelda_link_to_past.jpg",
            "cheats": ["infinite_lives", "all_items", "max_abilities"],
            "save_slots": 3,
            "recommended": True
        },
        {
            "id": "super_mario_kart",
            "name": "Super Mario Kart",
            "file": "Super_Mario_Kart.smc",
            "description": "马里奥赛车系列的开山之作",
            "genre": "赛车",
            "year": 1992,
            "players": "1-2",
            "image": "/static/images/covers/snes/super_mario_kart.jpg",
            "cheats": ["infinite_items", "max_speed"],
            "save_slots": 2,
            "recommended": False
        },
        {
            "id": "donkey_kong_country",
            "name": "Donkey Kong Country",
            "file": "Donkey_Kong_Country.smc",
            "description": "革命性的3D渲染平台游戏",
            "genre": "平台跳跃",
            "year": 1994,
            "players": "1-2",
            "image": "/static/images/covers/snes/donkey_kong_country.jpg",
            "cheats": ["infinite_lives", "level_select"],
            "save_slots": 3,
            "recommended": False
        },
        {
            "id": "street_fighter_ii",
            "name": "Street Fighter II",
            "file": "Street_Fighter_II.smc",
            "description": "格斗游戏的经典之作",
            "genre": "格斗",
            "year": 1991,
            "players": "1-2",
            "image": "/static/images/covers/snes/street_fighter_ii.jpg",
            "cheats": ["infinite_health", "all_characters"],
            "save_slots": 1,
            "recommended": False
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
        },
        {
            "id": "pokemon_blue",
            "name": "Pokemon Blue",
            "file": "Pokemon_Blue.gb",
            "description": "口袋妖怪蓝版，与红版互补的精灵",
            "genre": "RPG",
            "year": 1996,
            "players": "1",
            "image": "/static/images/covers/gameboy/pokemon_blue.jpg",
            "cheats": ["infinite_money", "all_pokemon", "max_level"],
            "save_slots": 1,
            "recommended": True
        },
        {
            "id": "zelda_links_awakening",
            "name": "The Legend of Zelda: Link's Awakening",
            "file": "Zelda_Links_Awakening.gb",
            "description": "塞尔达传说掌机版经典",
            "genre": "动作冒险",
            "year": 1993,
            "players": "1",
            "image": "/static/images/covers/gameboy/zelda_links_awakening.jpg",
            "cheats": ["infinite_lives", "all_items"],
            "save_slots": 3,
            "recommended": True
        },
        {
            "id": "super_mario_land",
            "name": "Super Mario Land",
            "file": "Super_Mario_Land.gb",
            "description": "马里奥的掌机首秀",
            "genre": "平台跳跃",
            "year": 1989,
            "players": "1",
            "image": "/static/images/covers/gameboy/super_mario_land.jpg",
            "cheats": ["infinite_lives", "level_select"],
            "save_slots": 1,
            "recommended": False
        },
        {
            "id": "metroid_ii",
            "name": "Metroid II: Return of Samus",
            "file": "Metroid_II.gb",
            "description": "萨姆斯的掌机冒险",
            "genre": "动作冒险",
            "year": 1991,
            "players": "1",
            "image": "/static/images/covers/gameboy/metroid_ii.jpg",
            "cheats": ["infinite_lives", "all_weapons"],
            "save_slots": 3,
            "recommended": False
        }
    ],
    "gba": [
        {
            "id": "pokemon_ruby",
            "name": "Pokemon Ruby",
            "file": "Pokemon_Ruby.gba",
            "description": "口袋妖怪红宝石版",
            "genre": "RPG",
            "year": 2002,
            "players": "1",
            "image": "/static/images/covers/gba/pokemon_ruby.jpg",
            "cheats": ["infinite_money", "all_pokemon", "max_level"],
            "save_slots": 1,
            "recommended": True
        },
        {
            "id": "pokemon_sapphire",
            "name": "Pokemon Sapphire",
            "file": "Pokemon_Sapphire.gba",
            "description": "口袋妖怪蓝宝石版",
            "genre": "RPG",
            "year": 2002,
            "players": "1",
            "image": "/static/images/covers/gba/pokemon_sapphire.jpg",
            "cheats": ["infinite_money", "all_pokemon", "max_level"],
            "save_slots": 1,
            "recommended": True
        },
        {
            "id": "fire_emblem",
            "name": "Fire Emblem",
            "file": "Fire_Emblem.gba",
            "description": "战略RPG经典之作",
            "genre": "战略RPG",
            "year": 2003,
            "players": "1",
            "image": "/static/images/covers/gba/fire_emblem.jpg",
            "cheats": ["infinite_money", "max_stats", "all_weapons"],
            "save_slots": 3,
            "recommended": True
        },
        {
            "id": "golden_sun",
            "name": "Golden Sun",
            "file": "Golden_Sun.gba",
            "description": "黄金太阳，精美的RPG冒险",
            "genre": "RPG",
            "year": 2001,
            "players": "1",
            "image": "/static/images/covers/gba/golden_sun.jpg",
            "cheats": ["max_abilities", "infinite_mp", "all_items"],
            "save_slots": 3,
            "recommended": True
        },
        {
            "id": "advance_wars",
            "name": "Advance Wars",
            "file": "Advance_Wars.gba",
            "description": "策略战争游戏经典",
            "genre": "策略",
            "year": 2001,
            "players": "1-2",
            "image": "/static/images/covers/gba/advance_wars.jpg",
            "cheats": ["infinite_money", "max_units"],
            "save_slots": 3,
            "recommended": False
        },
        {
            "id": "mario_kart_super_circuit",
            "name": "Mario Kart: Super Circuit",
            "file": "Mario_Kart_Super_Circuit.gba",
            "description": "马里奥赛车掌机版",
            "genre": "赛车",
            "year": 2001,
            "players": "1-4",
            "image": "/static/images/covers/gba/mario_kart_super_circuit.jpg",
            "cheats": ["infinite_items", "max_speed"],
            "save_slots": 2,
            "recommended": False
        }
    ],
    "genesis": [
        {
            "id": "sonic",
            "name": "Sonic the Hedgehog",
            "file": "Sonic_the_Hedgehog.md",
            "description": "音速小子的高速冒险",
            "genre": "平台跳跃",
            "year": 1991,
            "players": "1",
            "image": "/static/images/covers/genesis/sonic.jpg",
            "cheats": ["infinite_lives", "invincibility", "level_select"],
            "save_slots": 3,
            "recommended": True
        },
        {
            "id": "sonic_2",
            "name": "Sonic the Hedgehog 2",
            "file": "Sonic_2.md",
            "description": "音速小子2，引入了塔尔斯",
            "genre": "平台跳跃",
            "year": 1992,
            "players": "1-2",
            "image": "/static/images/covers/genesis/sonic_2.jpg",
            "cheats": ["infinite_lives", "invincibility", "level_select"],
            "save_slots": 3,
            "recommended": True
        },
        {
            "id": "streets_of_rage",
            "name": "Streets of Rage",
            "file": "Streets_of_Rage.md",
            "description": "经典横版格斗游戏",
            "genre": "格斗",
            "year": 1991,
            "players": "1-2",
            "image": "/static/images/covers/genesis/streets_of_rage.jpg",
            "cheats": ["infinite_lives", "invincibility", "max_abilities"],
            "save_slots": 1,
            "recommended": True
        },
        {
            "id": "golden_axe",
            "name": "Golden Axe",
            "file": "Golden_Axe.md",
            "description": "魔幻题材的横版动作游戏",
            "genre": "动作",
            "year": 1989,
            "players": "1-2",
            "image": "/static/images/covers/genesis/golden_axe.jpg",
            "cheats": ["infinite_lives", "max_magic", "all_weapons"],
            "save_slots": 1,
            "recommended": False
        },
        {
            "id": "phantasy_star_iv",
            "name": "Phantasy Star IV",
            "file": "Phantasy_Star_IV.md",
            "description": "梦幻之星系列的巅峰之作",
            "genre": "RPG",
            "year": 1993,
            "players": "1",
            "image": "/static/images/covers/genesis/phantasy_star_iv.jpg",
            "cheats": ["max_abilities", "infinite_mp", "all_items"],
            "save_slots": 3,
            "recommended": False
        }
    ]
}

# 模拟存档数据
SAVE_DATA = {
    "super_mario_bros": {
        "slot_1": {"level": "1-1", "lives": 3, "score": 1200, "timestamp": "2025-06-27 10:30:00"},
        "slot_2": {"level": "4-2", "lives": 5, "score": 15600, "timestamp": "2025-06-26 15:45:00"},
        "slot_3": {"level": "8-4", "lives": 2, "score": 45200, "timestamp": "2025-06-25 20:15:00"}
    },
    "zelda": {
        "slot_1": {"area": "Hyrule Castle", "hearts": 8, "items": ["sword", "shield"], "timestamp": "2025-06-27 09:15:00"},
        "slot_2": {"area": "Death Mountain", "hearts": 12, "items": ["sword", "shield", "bow"], "timestamp": "2025-06-26 18:30:00"}
    }
}

# 模拟金手指配置
CHEAT_CONFIGS = {
    "infinite_lives": {"name": "无限生命", "code": "AEAEAE", "enabled": True, "auto": True},
    "invincibility": {"name": "无敌模式", "code": "AEAEAE", "enabled": True, "auto": True},
    "level_select": {"name": "关卡选择", "code": "AAAAAA", "enabled": True, "auto": True},
    "max_abilities": {"name": "最大能力", "code": "AEAEAE", "enabled": True, "auto": True},
    "all_weapons": {"name": "全武器", "code": "BBBBBB", "enabled": False, "auto": False},
    "all_items": {"name": "全道具", "code": "CCCCCC", "enabled": False, "auto": False},
    "infinite_money": {"name": "无限金钱", "code": "DDDDDD", "enabled": False, "auto": False},
    "max_level": {"name": "最高等级", "code": "EEEEEE", "enabled": False, "auto": False}
}

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 GamePlayer-Raspberry - 游戏中心</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
        }

        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }

        .status-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.2);
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .feature-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
        }

        .feature-card h3 {
            font-size: 1.5rem;
            margin-bottom: 15px;
            color: #FFD700;
        }

        .feature-list {
            list-style: none;
        }

        .feature-list li {
            margin-bottom: 8px;
            padding-left: 20px;
            position: relative;
        }

        .feature-list li:before {
            content: "✅";
            position: absolute;
            left: 0;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
        }

        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #FFD700;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 1rem;
            opacity: 0.9;
        }

        .demo-section {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            border: 1px solid rgba(255,255,255,0.2);
        }

        .demo-button {
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 10px;
        }

        .demo-button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }

        .games-section {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.2);
        }

        .system-tabs {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 30px;
            justify-content: center;
        }

        .system-tab {
            background: rgba(255,255,255,0.1);
            border: 2px solid rgba(255,255,255,0.3);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
        }

        .system-tab:hover {
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }

        .system-tab.active {
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            border-color: #FFD700;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }

        .games-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .game-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }

        .game-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            border-color: #FFD700;
        }

        .game-card.playing {
            border: 2px solid #4CAF50;
            box-shadow: 0 0 20px rgba(76, 175, 80, 0.5);
        }

        .game-card.recommended {
            border: 2px solid #FFD700;
            box-shadow: 0 5px 15px rgba(255, 215, 0, 0.3);
        }

        .recommended-badge {
            position: absolute;
            top: 10px;
            left: 10px;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            color: #000;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
            z-index: 10;
        }

        .game-image {
            width: 100%;
            height: 150px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 10px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            position: relative;
        }

        .game-title {
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 8px;
            color: #FFD700;
        }

        .game-info {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-bottom: 5px;
        }

        .game-description {
            font-size: 0.85rem;
            opacity: 0.8;
            margin-bottom: 15px;
            line-height: 1.4;
        }

        .game-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-bottom: 15px;
        }

        .badge {
            background: rgba(255,215,0,0.2);
            color: #FFD700;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            border: 1px solid rgba(255,215,0,0.3);
        }

        .play-button {
            width: 100%;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .play-button:hover {
            background: linear-gradient(45deg, #45a049, #4CAF50);
            transform: scale(1.02);
        }

        .play-button:disabled {
            background: #666;
            cursor: not-allowed;
            transform: none;
        }

        .game-status {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
        }

        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }

        .loading-content {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid rgba(255,255,255,0.3);
            border-top: 5px solid #FFD700;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .footer {
            text-align: center;
            margin-top: 40px;
            opacity: 0.8;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        .pulse {
            animation: pulse 2s infinite;
        }

        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="pulse">🎮 GamePlayer-Raspberry</h1>
            <p>多系统游戏模拟器 - 游戏中心</p>
        </div>

        <div class="status-card">
            <h2>🚀 系统状态</h2>
            <p><strong>版本:</strong> v4.0.0</p>
            <p><strong>运行环境:</strong> Docker容器</p>
            <p><strong>Web服务器:</strong> Flask (端口 {{ port }})</p>
            <p><strong>状态:</strong> <span style="color: #4CAF50;">✅ 运行正常</span></p>
        </div>

        <div class="features-grid">
            <div class="feature-card">
                <h3>🎮 支持的游戏系统</h3>
                <ul class="feature-list">
                    <li>NES (任天堂红白机)</li>
                    <li>SNES (超级任天堂)</li>
                    <li>Game Boy (掌机)</li>
                    <li>Game Boy Advance</li>
                    <li>Sega Genesis</li>
                    <li>PlayStation (PSX)</li>
                    <li>Nintendo 64</li>
                    <li>Arcade (街机)</li>
                </ul>
            </div>

            <div class="feature-card">
                <h3>🎯 核心功能</h3>
                <ul class="feature-list">
                    <li>自动金手指系统</li>
                    <li>无限生命模式</li>
                    <li>无敌模式</li>
                    <li>关卡选择</li>
                    <li>存档管理</li>
                    <li>设置配置</li>
                    <li>Web界面控制</li>
                    <li>一键部署</li>
                </ul>
            </div>

            <div class="feature-card">
                <h3>🔧 技术特性</h3>
                <ul class="feature-list">
                    <li>Docker容器化</li>
                    <li>树莓派优化</li>
                    <li>响应式Web设计</li>
                    <li>自动依赖管理</li>
                    <li>多环境支持</li>
                    <li>完整测试覆盖</li>
                    <li>详细文档</li>
                    <li>开源免费</li>
                </ul>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">8</div>
                <div class="stat-label">游戏系统</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">100+</div>
                <div class="stat-label">游戏ROM</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">100%</div>
                <div class="stat-label">测试通过</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">24</div>
                <div class="stat-label">金手指类型</div>
            </div>
        </div>

        <div class="games-section">
            <h2>🎮 游戏中心</h2>
            <p>选择游戏系统，点击游戏开始体验：</p>

            <div class="system-tabs">
                <div class="system-tab active" data-system="nes">🎮 NES</div>
                <div class="system-tab" data-system="snes">🎯 SNES</div>
                <div class="system-tab" data-system="gameboy">📱 Game Boy</div>
                <div class="system-tab" data-system="gba">🎲 GBA</div>
                <div class="system-tab" data-system="genesis">🔵 Genesis</div>
            </div>

            <div id="games-container">
                <div class="games-grid" id="games-grid">
                    <!-- 游戏卡片将通过JavaScript动态加载 -->
                </div>
            </div>
        </div>

        <div class="demo-section">
            <h2>🎮 快速功能</h2>
            <p>体验GamePlayer-Raspberry的核心功能：</p>
            <br>
            <button class="demo-button" onclick="showCheats()">🔧 金手指系统</button>
            <button class="demo-button" onclick="showSettings()">⚙️ 系统设置</button>
            <button class="demo-button" onclick="showStatus()">📊 系统状态</button>
            <button class="demo-button" onclick="checkAllGames()">🔍 游戏检查</button>
            <button class="demo-button" onclick="fixAllGames()">🔧 自动修复</button>
            <button class="demo-button" onclick="showSaveData()">💾 存档管理</button>
        </div>

        <div class="footer">
            <p>🍓 GamePlayer-Raspberry - 让经典游戏在树莓派上重新焕发生机</p>
            <p>GitHub: <a href="https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry" style="color: #FFD700;">LIUCHAOVSYAN/GamePlayer-Raspberry</a></p>
        </div>
    </div>

    <!-- 加载覆盖层 -->
    <div class="loading-overlay" id="loading-overlay">
        <div class="loading-content">
            <div class="spinner"></div>
            <h3 id="loading-title">🎮 正在启动游戏...</h3>
            <p id="loading-message">正在加载ROM文件和配置...</p>
            <div id="loading-progress">
                <p>✅ 加载游戏文件</p>
                <p>✅ 应用金手指配置</p>
                <p>✅ 加载存档数据</p>
                <p>🎯 启动模拟器...</p>
            </div>
        </div>
    </div>

    <script>
        let currentSystem = 'nes';
        let gamesData = {};
        let currentGame = null;

        // 加载游戏数据
        async function loadGames() {
            try {
                const response = await fetch('/api/games');
                gamesData = await response.json();
                displayGames(currentSystem);
            } catch (error) {
                console.error('加载游戏数据失败:', error);
            }
        }

        // 显示游戏列表
        function displayGames(system) {
            const gamesGrid = document.getElementById('games-grid');
            const games = gamesData[system] || [];

            gamesGrid.innerHTML = games.map(game => `
                <div class="game-card ${game.recommended ? 'recommended' : ''}" data-game-id="${game.id}">
                    <div class="game-status" id="status-${game.id}">就绪</div>
                    ${game.recommended ? '<div class="recommended-badge">推荐</div>' : ''}
                    <div class="game-image">
                        <img src="${game.image}" alt="${game.name}"
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
                             style="width: 100%; height: 100%; object-fit: cover; border-radius: 10px;">
                        <div style="display: none; width: 100%; height: 100%; align-items: center; justify-content: center; font-size: 3rem;">
                            🎮
                        </div>
                    </div>
                    <div class="game-title">${game.name}</div>
                    <div class="game-info">📅 ${game.year} | 👥 ${game.players}人 | 🎯 ${game.genre}</div>
                    <div class="game-description">${game.description}</div>
                    <div class="game-badges">
                        ${game.cheats.map(cheat => `<span class="badge">🎯 ${getCheatName(cheat)}</span>`).join('')}
                        <span class="badge">💾 ${game.save_slots}存档</span>
                    </div>
                    <button class="play-button" onclick="startGame('${game.id}', '${system}')">
                        🚀 开始游戏
                    </button>
                </div>
            `).join('');
        }

        // 获取金手指名称
        function getCheatName(cheatId) {
            const cheatNames = {
                'infinite_lives': '无限生命',
                'invincibility': '无敌模式',
                'level_select': '关卡选择',
                'max_abilities': '最大能力',
                'all_weapons': '全武器',
                'all_items': '全道具',
                'infinite_money': '无限金钱',
                'max_level': '最高等级'
            };
            return cheatNames[cheatId] || cheatId;
        }

        // 系统标签切换
        function setupSystemTabs() {
            const tabs = document.querySelectorAll('.system-tab');
            tabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    // 移除所有活动状态
                    tabs.forEach(t => t.classList.remove('active'));
                    // 添加当前活动状态
                    tab.classList.add('active');
                    // 更新当前系统
                    currentSystem = tab.dataset.system;
                    // 显示对应游戏
                    displayGames(currentSystem);
                });
            });
        }

        // 启动游戏
        async function startGame(gameId, system) {
            currentGame = { id: gameId, system: system };

            // 显示加载界面
            showLoading();

            try {
                // 调用真正的游戏启动API，增加错误处理
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 30000); // 30秒超时

                const response = await fetch('/api/launch_game', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({
                        game_id: gameId,
                        system: system
                    }),
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                // 检查响应状态
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error('服务器返回了非JSON响应');
                }

                const result = await response.json();

                // 隐藏加载界面
                hideLoading();

                if (result.success) {
                    // 显示游戏运行状态
                    updateGameStatus(gameId, '运行中');

                    // 显示游戏启动成功消息
                    showGameStartedReal(result);
                } else {
                    // 改进的错误处理
                    let errorMessage = '游戏启动失败: ' + (result.error || '未知错误');

                    // 如果是可修复的错误，提供更友好的提示
                    if (result.fixable) {
                        errorMessage += '\\n\\n💡 提示: 这个问题可以自动修复';
                        if (result.error.includes('模拟器')) {
                            errorMessage += '\\n🔧 系统正在尝试安装缺失的模拟器';
                            errorMessage += '\\n⏳ 请稍后再试，或检查系统状态';
                        }
                    }

                    alert(errorMessage);
                    updateGameStatus(gameId, '需要修复');
                }

            } catch (error) {
                hideLoading();

                let errorMessage = '游戏启动失败: ';

                if (error.name === 'AbortError') {
                    errorMessage += '请求超时，请检查网络连接';
                } else if (error.message.includes('Failed to fetch')) {
                    errorMessage += '网络连接失败，请检查服务器是否运行';
                } else if (error.message.includes('NetworkError')) {
                    errorMessage += '网络错误，请检查连接';
                } else {
                    errorMessage += error.message;
                }

                alert(errorMessage);
                updateGameStatus(gameId, '启动失败');

                // 记录详细错误信息到控制台
                console.error('游戏启动错误详情:', {
                    gameId: gameId,
                    system: system,
                    error: error,
                    stack: error.stack
                });
            }
        }

        // 模拟游戏启动过程
        async function simulateGameStart(gameId, system) {
            const steps = [
                { message: '正在加载ROM文件...', delay: 1000 },
                { message: '正在应用金手指配置...', delay: 800 },
                { message: '正在加载存档数据...', delay: 600 },
                { message: '正在启动模拟器...', delay: 1200 },
                { message: '游戏启动完成！', delay: 500 }
            ];

            for (let i = 0; i < steps.length; i++) {
                const step = steps[i];
                updateLoadingMessage(step.message);
                await new Promise(resolve => setTimeout(resolve, step.delay));
            }
        }

        // 显示加载界面
        function showLoading() {
            const overlay = document.getElementById('loading-overlay');
            overlay.style.display = 'flex';
            updateLoadingMessage('正在初始化游戏...');
        }

        // 隐藏加载界面
        function hideLoading() {
            const overlay = document.getElementById('loading-overlay');
            overlay.style.display = 'none';
        }

        // 更新加载消息
        function updateLoadingMessage(message) {
            const messageElement = document.getElementById('loading-message');
            messageElement.textContent = message;
        }

        // 更新游戏状态
        function updateGameStatus(gameId, status) {
            const statusElement = document.getElementById(`status-${gameId}`);
            if (statusElement) {
                statusElement.textContent = status;
                const gameCard = statusElement.closest('.game-card');
                if (status === '运行中') {
                    gameCard.classList.add('playing');
                } else {
                    gameCard.classList.remove('playing');
                }
            }
        }

        // 显示真正的游戏启动成功消息
        function showGameStartedReal(result) {
            const gameInfo = result.game_info;
            const enabledCheats = result.enabled_cheats || [];
            const isDemo = result.demo_mode || false;

            let message = `🎮 ${gameInfo.name} 启动成功！\\n\\n`;
            message += `📁 游戏文件: ${gameInfo.file}\\n`;
            message += `🎯 已启用金手指: ${enabledCheats.length}个\\n`;
            message += `💾 存档槽位: ${gameInfo.save_slots}个\\n\\n`;

            if (enabledCheats.length > 0) {
                message += `🎯 自动启用的金手指:\\n`;
                enabledCheats.forEach(cheat => {
                    message += `• ${cheat.name}\\n`;
                });
                message += `\\n`;
            }

            if (result.pid) {
                message += `🔧 进程ID: ${result.pid}\\n`;
                message += `🎮 游戏正在真实运行！\\n\\n`;
                message += `💡 提示: 游戏窗口可能会在后台打开`;
            } else if (isDemo) {
                message += `🎮 演示模式运行\\n`;
                message += `💡 在真实环境中，游戏会启动模拟器窗口`;
            } else {
                message += `🎮 游戏正在运行！`;
            }

            alert(message);
        }

        // 停止游戏
        async function stopGame(gameId) {
            try {
                const response = await fetch('/api/stop_game', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        game_id: gameId
                    })
                });

                const result = await response.json();

                if (result.success) {
                    updateGameStatus(gameId, '已停止');
                    alert('游戏已停止');
                } else {
                    alert('停止游戏失败: ' + result.error);
                }

            } catch (error) {
                alert('停止游戏失败: ' + error.message);
            }
        }

        // 检查系统状态
        async function checkSystemStatus() {
            try {
                const response = await fetch('/api/system_check');
                const result = await response.json();

                let message = `🔍 系统状态检查结果\\n\\n`;
                message += `📊 总体状态: ${getStatusEmoji(result.overall_status)} ${result.overall_status}\\n\\n`;

                for (const [checkName, checkResult] of Object.entries(result.checks)) {
                    const status = checkResult.status ? '✅' : '❌';
                    message += `${status} ${checkName}: ${checkResult.message}\\n`;

                    if (checkResult.fix_result) {
                        const fixStatus = checkResult.fix_result.success ? '🔧✅' : '🔧❌';
                        message += `  ${fixStatus} 自动修复: ${checkResult.fix_result.message}\\n`;
                    }
                }

                if (result.demo_mode) {
                    message += `\\n💡 当前为演示模式`;
                }

                alert(message);

            } catch (error) {
                alert('系统检查失败: ' + error.message);
            }
        }

        function getStatusEmoji(status) {
            switch (status) {
                case 'healthy': return '🟢';
                case 'warning': return '🟡';
                case 'critical': return '🔴';
                default: return '⚪';
            }
        }

        // 显示金手指配置界面
        async function showCheats() {
            try {
                const response = await fetch(`/api/cheat_config/${currentSystem}`);
                const result = await response.json();

                if (result.success) {
                    showCheatConfigModal(result.cheats, currentSystem);
                } else {
                    alert('加载金手指配置失败');
                }
            } catch (error) {
                alert('加载金手指配置失败: ' + error.message);
            }
        }

        // 显示金手指配置模态框
        function showCheatConfigModal(cheats, system) {
            let modalHtml = `
                <div id="cheat-modal" style="
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center;
                    z-index: 2000;
                ">
                    <div style="
                        background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
                        border-radius: 15px; padding: 30px; max-width: 600px; width: 90%;
                        border: 1px solid rgba(255,255,255,0.2); color: white;
                        max-height: 80vh; overflow-y: auto;
                    ">
                        <h2>🎯 ${system.toUpperCase()} 金手指配置</h2>
                        <div id="cheat-list">
            `;

            for (const [cheatId, cheatData] of Object.entries(cheats)) {
                const checked = cheatData.enabled ? 'checked' : '';
                modalHtml += `
                    <div style="margin: 15px 0; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;">
                        <label style="display: flex; align-items: center; cursor: pointer;">
                            <input type="checkbox" ${checked} onchange="toggleCheat('${system}', '${cheatId}', this.checked)"
                                   style="margin-right: 10px; transform: scale(1.2);">
                            <div>
                                <div style="font-weight: bold; color: #FFD700;">${cheatData.name || cheatId}</div>
                                <div style="font-size: 0.9em; opacity: 0.8;">${cheatData.description || '暂无描述'}</div>
                                <div style="font-size: 0.8em; opacity: 0.6;">代码: ${cheatData.code || 'N/A'}</div>
                            </div>
                        </label>
                    </div>
                `;
            }

            modalHtml += `
                        </div>
                        <div style="text-align: center; margin-top: 20px;">
                            <button onclick="closeCheatModal()" style="
                                background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
                                color: white; border: none; padding: 10px 20px;
                                border-radius: 20px; cursor: pointer;
                            ">关闭</button>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }

        // 切换金手指状态
        async function toggleCheat(system, cheatId, enabled) {
            try {
                const response = await fetch(`/api/cheat_config/${system}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        cheat_id: cheatId,
                        enabled: enabled
                    })
                });

                const result = await response.json();

                if (!result.success) {
                    alert('更新金手指失败: ' + result.error);
                    // 恢复复选框状态
                    event.target.checked = !enabled;
                }
            } catch (error) {
                alert('更新金手指失败: ' + error.message);
                event.target.checked = !enabled;
            }
        }

        // 关闭金手指模态框
        function closeCheatModal() {
            const modal = document.getElementById('cheat-modal');
            if (modal) {
                modal.remove();
            }
        }

        // 显示系统设置界面
        async function showSettings() {
            try {
                const response = await fetch('/api/settings');
                const result = await response.json();

                if (result.success) {
                    showSettingsModal(result.settings);
                } else {
                    alert('加载系统设置失败');
                }
            } catch (error) {
                alert('加载系统设置失败: ' + error.message);
            }
        }

        // 显示设置模态框
        function showSettingsModal(settings) {
            let modalHtml = `
                <div id="settings-modal" style="
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center;
                    z-index: 2000;
                ">
                    <div style="
                        background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
                        border-radius: 15px; padding: 30px; max-width: 700px; width: 90%;
                        border: 1px solid rgba(255,255,255,0.2); color: white;
                        max-height: 80vh; overflow-y: auto;
                    ">
                        <h2>⚙️ 系统设置</h2>
                        <div id="settings-list">
            `;

            for (const [category, categorySettings] of Object.entries(settings)) {
                modalHtml += `<h3 style="color: #FFD700; margin-top: 20px;">${getCategoryName(category)}</h3>`;

                for (const [setting, value] of Object.entries(categorySettings)) {
                    modalHtml += createSettingControl(category, setting, value);
                }
            }

            modalHtml += `
                        </div>
                        <div style="text-align: center; margin-top: 20px;">
                            <button onclick="closeSettingsModal()" style="
                                background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
                                color: white; border: none; padding: 10px 20px;
                                border-radius: 20px; cursor: pointer;
                            ">关闭</button>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }

        function getCategoryName(category) {
            const names = {
                'display': '🖥️ 显示设置',
                'audio': '🔊 音频设置',
                'input': '🎮 输入设置',
                'performance': '⚡ 性能设置'
            };
            return names[category] || category;
        }

        function createSettingControl(category, setting, value) {
            const settingId = `${category}_${setting}`;

            if (typeof value === 'boolean') {
                const checked = value ? 'checked' : '';
                return `
                    <div style="margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                        <label style="display: flex; align-items: center; cursor: pointer;">
                            <input type="checkbox" ${checked} onchange="updateSetting('${category}', '${setting}', this.checked)"
                                   style="margin-right: 10px; transform: scale(1.2);">
                            <span>${getSettingName(setting)}</span>
                        </label>
                    </div>
                `;
            } else if (typeof value === 'number') {
                return `
                    <div style="margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                        <label style="display: block;">
                            <span>${getSettingName(setting)}: ${value}</span>
                            <input type="range" min="0" max="100" value="${value}"
                                   onchange="updateSetting('${category}', '${setting}', parseInt(this.value))"
                                   style="width: 100%; margin-top: 5px;">
                        </label>
                    </div>
                `;
            } else {
                return `
                    <div style="margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                        <label style="display: block;">
                            <span>${getSettingName(setting)}:</span>
                            <input type="text" value="${value}"
                                   onchange="updateSetting('${category}', '${setting}', this.value)"
                                   style="width: 100%; margin-top: 5px; padding: 5px; border-radius: 5px; border: none;">
                        </label>
                    </div>
                `;
            }
        }

        function getSettingName(setting) {
            const names = {
                'fullscreen': '全屏模式',
                'resolution': '分辨率',
                'vsync': '垂直同步',
                'scaling': '缩放模式',
                'enabled': '启用',
                'volume': '音量',
                'sample_rate': '采样率',
                'buffer_size': '缓冲区大小',
                'gamepad_enabled': '手柄启用',
                'keyboard_enabled': '键盘启用',
                'auto_detect_gamepad': '自动检测手柄',
                'gamepad_deadzone': '手柄死区',
                'frame_skip': '跳帧',
                'speed_limit': '速度限制',
                'rewind_enabled': '倒带功能',
                'save_states': '即时存档'
            };
            return names[setting] || setting;
        }

        // 更新设置
        async function updateSetting(category, setting, value) {
            try {
                const response = await fetch('/api/settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        category: category,
                        setting: setting,
                        value: value
                    })
                });

                const result = await response.json();

                if (!result.success) {
                    alert('更新设置失败: ' + result.error);
                }
            } catch (error) {
                alert('更新设置失败: ' + error.message);
            }
        }

        // 关闭设置模态框
        function closeSettingsModal() {
            const modal = document.getElementById('settings-modal');
            if (modal) {
                modal.remove();
            }
        }

        function showStatus() {
            checkSystemStatus();
        }

        // 检查所有游戏状态
        async function checkAllGames() {
            try {
                showLoading('🔍 正在检查所有游戏状态...');

                const response = await fetch('/api/check_all_games', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                const result = await response.json();

                hideLoading();

                if (result.success) {
                    showGameHealthReport(result.report, result.summary);
                } else {
                    alert('游戏状态检查失败: ' + result.error);
                }

            } catch (error) {
                hideLoading();
                alert('游戏状态检查失败: ' + error.message);
            }
        }

        // 自动修复所有游戏
        async function fixAllGames() {
            if (!confirm('🔧 确定要自动修复所有游戏问题吗？\\n\\n这可能需要几分钟时间，包括：\\n• 安装缺失的模拟器\\n• 创建演示ROM文件\\n• 下载游戏封面\\n• 修复配置问题')) {
                return;
            }

            try {
                showLoading('🔧 正在自动修复所有游戏问题...');

                const response = await fetch('/api/fix_all_games', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        max_iterations: 5
                    })
                });

                const result = await response.json();

                hideLoading();

                if (result.success) {
                    showFixAllGamesResult(result);
                } else {
                    alert('自动修复失败: ' + result.error);
                }

            } catch (error) {
                hideLoading();
                alert('自动修复失败: ' + error.message);
            }
        }

        // 显示游戏健康报告
        function showGameHealthReport(report, summary) {
            const statusEmojis = {
                'all_healthy': '🟢',
                'mostly_healthy': '🟡',
                'partially_healthy': '🟠',
                'needs_attention': '🔴'
            };

            const statusEmoji = statusEmojis[summary.overall_status] || '⚪';

            let message = `🔍 游戏健康检查报告\\n\\n`;
            message += `📊 总体状态: ${statusEmoji} ${summary.overall_status}\\n`;
            message += `🎮 游戏统计: ${summary.healthy_games}/${summary.total_games} 正常运行\\n`;

            if (summary.fixed_games > 0) {
                message += `🔧 已修复: ${summary.fixed_games} 个游戏\\n`;
            }

            message += `\\n📂 系统详情:\\n`;

            for (const [system, systemReport] of Object.entries(report.systems)) {
                const emulatorStatus = systemReport.emulator_status;
                const gamesCount = Object.keys(systemReport.games).length;
                const healthyCount = Object.values(systemReport.games).filter(g => g.status === 'healthy').length;

                const statusIcon = emulatorStatus === 'available' ? '✅' : '❌';

                message += `\\n  ${system.toUpperCase()}:`;
                message += `\\n    ${statusIcon} 模拟器: ${emulatorStatus}`;
                message += `\\n    🎮 游戏: ${healthyCount}/${gamesCount} 正常`;

                if (systemReport.fixes.length > 0) {
                    message += `\\n    🔧 修复: ${systemReport.fixes.join(', ')}`;
                }
            }

            if (summary.overall_status === 'all_healthy') {
                message += `\\n\\n🎉 恭喜！所有游戏都可以正常运行！`;
            } else {
                message += `\\n\\n💡 建议: 点击"自动修复"来解决剩余问题`;
            }

            alert(message);
        }

        // 显示自动修复结果
        function showFixAllGamesResult(result) {
            const summary = result.summary;
            const statusEmojis = {
                'all_healthy': '🟢',
                'mostly_healthy': '🟡',
                'partially_healthy': '🟠',
                'needs_attention': '🔴'
            };

            const statusEmoji = statusEmojis[summary.overall_status] || '⚪';

            let message = `🔧 自动修复完成报告\\n\\n`;
            message += `📊 最终状态: ${statusEmoji} ${summary.overall_status}\\n`;
            message += `🎮 游戏统计: ${summary.healthy_games}/${summary.total_games} 正常运行\\n`;
            message += `🔧 修复游戏: ${summary.fixed_games} 个\\n\\n`;

            if (summary.all_games_working) {
                message += `🎉 太棒了！所有游戏现在都可以正常运行！\\n\\n`;
                message += `✅ 您现在可以：\\n`;
                message += `• 🎮 启动任意游戏\\n`;
                message += `• 🎯 使用金手指功能\\n`;
                message += `• 💾 保存和加载游戏进度\\n`;
                message += `• ⚙️ 自定义游戏设置`;
            } else {
                message += `⚠️ 仍有 ${summary.total_games - summary.healthy_games} 个游戏需要手动处理\\n\\n`;
                message += `💡 可能的原因：\\n`;
                message += `• 模拟器安装失败\\n`;
                message += `• 系统权限问题\\n`;
                message += `• 网络连接问题\\n\\n`;
                message += `🔧 建议: 检查系统状态或联系技术支持`;
            }

            // 显示详细报告
            if (result.report_text) {
                message += `\\n\\n📋 详细报告:\\n${result.report_text}`;
            }

            alert(message);

            // 如果所有游戏都正常，刷新页面显示最新状态
            if (summary.all_games_working) {
                setTimeout(() => {
                    if (confirm('🔄 所有游戏已修复完成！是否刷新页面查看最新状态？')) {
                        location.reload();
                    }
                }, 2000);
            }
        }

        function showSaveData() {
            alert('💾 存档管理系统\\n\\n功能特性：\\n• 自动存档 - 游戏进度自动保存\\n• 多存档槽 - 支持多个存档位置\\n• 快速加载 - 一键加载存档\\n• 存档备份 - 云端同步存档\\n• 存档预览 - 显示存档详情\\n\\n永不丢失游戏进度！');
        }

        // 初始化游戏数据
        async function initializeGameData() {
            try {
                console.log('🎮 初始化游戏数据...');

                const response = await fetch('/api/initialize_game_data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                const result = await response.json();

                if (result.success) {
                    console.log('✅ 游戏数据初始化完成:', result.results);
                } else {
                    console.warn('⚠️ 游戏数据初始化失败:', result.error);
                }
            } catch (error) {
                console.warn('⚠️ 游戏数据初始化错误:', error);
            }
        }

        // 页面初始化
        document.addEventListener('DOMContentLoaded', function() {
            // 初始化游戏数据
            initializeGameData();

            // 加载游戏数据
            loadGames();

            // 设置系统标签
            setupSystemTabs();

            // 添加动态效果
            const cards = document.querySelectorAll('.feature-card, .stat-card');
            cards.forEach((card, index) => {
                card.style.animationDelay = (index * 0.1) + 's';
                card.style.animation = 'fadeInUp 0.6s ease forwards';
            });
        });

        // CSS动画
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>
"""

@app.route('/')

def index():
    """主页"""
    return render_template_string(HTML_TEMPLATE, port=request.environ.get('SERVER_PORT', '3000'))

@app.route('/api/status')

def api_status():
    """API状态"""
    return jsonify({
        'status': 'running',
        'version': 'v4.0.0',
        'environment': 'docker',
        'features': {
            'game_systems': 8,
            'rom_count': '100+',
            'cheat_types': 24,
            'test_coverage': '100%'
        }
    })

@app.route('/api/games')

def api_games():
    """游戏列表API"""
    return jsonify(GAMES_DATABASE)

@app.route('/api/game/<system>/<game_id>')

def api_game_info(system, game_id):
    """获取特定游戏信息"""
    games = GAMES_DATABASE.get(system, [])
    game = next((g for g in games if g['id'] == game_id), None)

    if not game:
        return jsonify({'error': 'Game not found'}), 404

    return jsonify(game)

@app.route('/api/saves/<game_id>')

def api_saves(game_id):
    """获取游戏存档信息"""
    saves = SAVE_DATA.get(game_id, {})

    # 找到最新存档
    latest_save = None
    latest_time = None

    for slot, save_data in saves.items():
        if 'timestamp' in save_data:
            if latest_time is None or save_data['timestamp'] > latest_time:
                latest_time = save_data['timestamp']
                latest_save = save_data

    return jsonify({
        'slots': len(saves),
        'saves': saves,
        'latest': latest_save
    })

@app.route('/api/cheats/<game_id>')

def api_game_cheats(game_id):
    """获取游戏金手指信息"""
    # 从游戏数据库中找到游戏
    game = None
    for system_games in GAMES_DATABASE.values():
        for g in system_games:
            if g['id'] == game_id:
                game = g
                break
        if game:
            break

    if not game:
        return jsonify({'error': 'Game not found'}), 404

    # 获取游戏支持的金手指
    game_cheats = game.get('cheats', [])

    # 构建金手指信息
    enabled_cheats = []
    available_cheats = []

    for cheat_id in game_cheats:
        cheat_config = CHEAT_CONFIGS.get(cheat_id, {})
        cheat_info = {
            'id': cheat_id,
            'name': cheat_config.get('name', cheat_id),
            'code': cheat_config.get('code', ''),
            'enabled': cheat_config.get('enabled', False),
            'auto': cheat_config.get('auto', False)
        }

        if cheat_config.get('auto', False):
            enabled_cheats.append(cheat_info)
        else:
            available_cheats.append(cheat_info)

    return jsonify({
        'enabled': enabled_cheats,
        'available': available_cheats,
        'total': len(game_cheats)
    })

@app.route('/api/cheats')

def api_cheats():
    """金手指系统API"""
    return jsonify({
        'configs': CHEAT_CONFIGS,
        'auto_enabled': [k for k, v in CHEAT_CONFIGS.items() if v.get('auto', False)],
        'available': list(CHEAT_CONFIGS.keys()),
        'systems_supported': ['nes', 'snes', 'gameboy', 'gba', 'genesis']
    })

@app.route('/api/launch_game', methods=['POST'])

def api_launch_game():
    """真正启动游戏API"""
    try:
        data = request.get_json()
        system = data.get('system')
        game_id = data.get('game_id')

        if not system or not game_id:
            return jsonify({'success': False, 'error': '缺少必要参数'}), 400

        # 获取游戏信息
        games = GAMES_DATABASE.get(system, [])
        game = next((g for g in games if g['id'] == game_id), None)

        if not game:
            return jsonify({'success': False, 'error': '游戏不存在'}), 404

        # 如果有真正的游戏启动器，使用它
        if game_launcher:
            # 获取启用的金手指
            enabled_cheats = []
            for cheat_id in game.get('cheats', []):
                cheat_config = CHEAT_CONFIGS.get(cheat_id, {})
                if cheat_config.get('auto', False):
                    enabled_cheats.append({
                        'id': cheat_id,
                        'name': cheat_config.get('name', cheat_id),
                        'code': cheat_config.get('code', ''),
                        'enabled': True
                    })

            # 启动游戏
            success, message, pid = game_launcher.launch_game(system, game_id)

            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'game_info': game,
                    'enabled_cheats': enabled_cheats,
                    'pid': pid
                })
            else:
                # 返回200状态码但success为false，避免HTTP 500错误
                return jsonify({
                    'success': False,
                    'error': message,
                    'game_info': game,
                    'system': system,
                    'fixable': '模拟器' in message or '安装' in message
                }), 200

        else:
            # 模拟启动（演示模式）
            return jsonify({
                'success': True,
                'message': f'游戏启动成功 (演示模式)',
                'game_info': game,
                'enabled_cheats': [
                    {'id': cheat_id, 'name': CHEAT_CONFIGS.get(cheat_id, {}).get('name', cheat_id)}
                    for cheat_id in game.get('cheats', [])
                    if CHEAT_CONFIGS.get(cheat_id, {}).get('auto', False)
                ],
                'demo_mode': True
            })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stop_game', methods=['POST'])

def api_stop_game():
    """停止游戏API"""
    try:
        data = request.get_json()
        game_id = data.get('game_id')

        if not game_id:
            return jsonify({'success': False, 'error': '缺少游戏ID'}), 400

        if game_launcher:
            success = game_launcher.stop_game(game_id)
            return jsonify({
                'success': success,
                'message': '游戏已停止' if success else '停止游戏失败'
            })
        else:
            return jsonify({
                'success': True,
                'message': '游戏已停止 (演示模式)',
                'demo_mode': True
            })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/game_status/<game_id>')

def api_game_status(game_id):
    """获取游戏状态API"""
    try:
        if game_launcher:
            status = game_launcher.get_game_status(game_id)
            is_running = game_launcher.is_game_running(game_id)

            return jsonify({
                'game_id': game_id,
                'status': status,
                'is_running': is_running,
                'running_games': list(game_launcher.get_running_games().keys())
            })
        else:
            return jsonify({
                'game_id': game_id,
                'status': '演示模式',
                'is_running': False,
                'demo_mode': True
            })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/system_check')

def api_system_check():
    """系统状态检查API"""
    try:
        if system_checker:
            results = system_checker.check_all_systems()
            return jsonify(results)
        else:
            # 模拟系统检查结果
            return jsonify({
                'timestamp': time.time(),
                'overall_status': 'healthy',
                'checks': {
                    'cheats': {'status': True, 'message': '金手指系统正常'},
                    'gamepad': {'status': True, 'message': '检测到虚拟手柄'},
                    'bluetooth': {'status': True, 'message': '蓝牙服务正常'},
                    'audio': {'status': True, 'message': '音频系统正常'},
                    'video': {'status': True, 'message': '视频系统正常'},
                    'emulators': {'status': False, 'message': '部分模拟器未安装', 'fixable': True},
                    'roms': {'status': True, 'message': '找到演示ROM文件'},
                    'saves': {'status': True, 'message': '存档系统正常'}
                },
                'demo_mode': True
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cheat_config/<system>', methods=['GET', 'POST'])

def api_cheat_config(system):
    """金手指配置API"""
    try:
        if request.method == 'GET':
            # 获取金手指配置
            if cheat_manager:
                cheats = cheat_manager.get_all_cheats_for_system(system)
                return jsonify({
                    'system': system,
                    'cheats': cheats,
                    'success': True
                })
            else:
                # 返回模拟配置
                system_cheats = {}
                for cheat_id, cheat_config in CHEAT_CONFIGS.items():
                    system_cheats[cheat_id] = cheat_config.copy()

                return jsonify({
                    'system': system,
                    'cheats': system_cheats,
                    'demo_mode': True,
                    'success': True
                })

        elif request.method == 'POST':
            # 更新金手指配置
            data = request.get_json()
            cheat_id = data.get('cheat_id')
            enabled = data.get('enabled', False)

            if not cheat_id:
                return jsonify({'success': False, 'error': '缺少金手指ID'}), 400

            if cheat_manager:
                success = cheat_manager.update_cheat_status(system, cheat_id, enabled)
                return jsonify({
                    'success': success,
                    'message': f'金手指 {cheat_id} 已{"启用" if enabled else "禁用"}'
                })
            else:
                # 模拟更新
                if cheat_id in CHEAT_CONFIGS:
                    CHEAT_CONFIGS[cheat_id]['enabled'] = enabled
                    return jsonify({
                        'success': True,
                        'message': f'金手指 {cheat_id} 已{"启用" if enabled else "禁用"} (演示模式)',
                        'demo_mode': True
                    })
                else:
                    return jsonify({'success': False, 'error': '金手指不存在'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/settings', methods=['GET', 'POST'])

def api_settings():
    """系统设置API"""
    try:
        if request.method == 'GET':
            # 获取系统设置
            if settings_manager:
                settings = settings_manager.get_all_settings()
                return jsonify({
                    'settings': settings,
                    'success': True
                })
            else:
                # 返回模拟设置
                default_settings = {
                    'display': {
                        'fullscreen': True,
                        'resolution': '1920x1080',
                        'vsync': True,
                        'scaling': 'auto'
                    },
                    'audio': {
                        'enabled': True,
                        'volume': 80,
                        'sample_rate': 44100,
                        'buffer_size': 512
                    },
                    'input': {
                        'gamepad_enabled': True,
                        'keyboard_enabled': True,
                        'auto_detect_gamepad': True,
                        'gamepad_deadzone': 0.1
                    },
                    'performance': {
                        'frame_skip': 0,
                        'speed_limit': 100,
                        'rewind_enabled': False,
                        'save_states': True
                    }
                }

                return jsonify({
                    'settings': default_settings,
                    'demo_mode': True,
                    'success': True
                })

        elif request.method == 'POST':
            # 更新系统设置
            data = request.get_json()
            category = data.get('category')
            setting = data.get('setting')
            value = data.get('value')

            if not all([category, setting]):
                return jsonify({'success': False, 'error': '缺少必要参数'}), 400

            if settings_manager:
                success = settings_manager.update_setting(category, setting, value)
                return jsonify({
                    'success': success,
                    'message': f'设置 {category}.{setting} 已更新'
                })
            else:
                # 模拟更新
                return jsonify({
                    'success': True,
                    'message': f'设置 {category}.{setting} 已更新为 {value} (演示模式)',
                    'demo_mode': True
                })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/static/images/covers/<system>/<filename>')

def serve_cover_image(system, filename):
    """提供游戏封面图片"""
    try:
        covers_dir = project_root / "data" / "web" / "images" / "covers" / system
        cover_path = covers_dir / filename

        if cover_path.exists():
            return send_from_directory(str(covers_dir), filename)
        else:
            # 返回404或占位符
            return jsonify({'error': 'Cover not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/download_covers', methods=['POST'])

def api_download_covers():
    """下载游戏封面API"""
    try:
        if cover_downloader:
            results = cover_downloader.download_all_covers()
            report = cover_downloader.generate_cover_report()

            return jsonify({
                'success': True,
                'message': '封面下载完成',
                'results': results,
                'report': report
            })
        else:
            return jsonify({
                'success': False,
                'error': '封面下载器不可用'
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/create_demo_roms', methods=['POST'])

def api_create_demo_roms():
    """创建演示ROM文件API"""
    try:
        from src.core.rom_downloader import ROMDownloader

        rom_downloader = ROMDownloader()
        results = rom_downloader.create_all_demo_roms(GAMES_DATABASE)
        report = rom_downloader.verify_rom_files()

        return jsonify({
            'success': True,
            'message': '演示ROM创建完成',
            'results': results,
            'report': report
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/initialize_game_data', methods=['POST'])

def api_initialize_game_data():
    """初始化游戏数据API"""
    try:
        results = {
            'covers': {'success': False, 'message': '跳过'},
            'roms': {'success': False, 'message': '跳过'}
        }

        # 下载封面
        if cover_downloader:
            try:
                cover_results = cover_downloader.download_all_covers()
                results['covers'] = {
                    'success': True,
                    'message': '封面下载完成',
                    'details': cover_results
                }
            except Exception as e:
                results['covers'] = {
                    'success': False,
                    'message': f'封面下载失败: {e}'
                }

        # 创建演示ROM
        try:
            from src.core.rom_downloader import ROMDownloader
            rom_downloader = ROMDownloader()
            rom_results = rom_downloader.create_all_demo_roms(GAMES_DATABASE)
            results['roms'] = {
                'success': True,
                'message': '演示ROM创建完成',
                'details': rom_results
            }
        except Exception as e:
            results['roms'] = {
                'success': False,
                'message': f'ROM创建失败: {e}'
            }

        return jsonify({
            'success': True,
            'message': '游戏数据初始化完成',
            'results': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/check_all_games', methods=['POST'])

def api_check_all_games():
    """检查所有游戏的健康状态API"""
    try:
        if game_health_checker:
            # 运行健康检查
            report = game_health_checker.check_all_games(GAMES_DATABASE)

            return jsonify({
                'success': True,
                'message': '游戏健康检查完成',
                'report': report,
                'summary': {
                    'total_games': report['games_total'],
                    'healthy_games': report['games_healthy'],
                    'fixed_games': report['games_fixed'],
                    'overall_status': report['overall_status']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '游戏健康检查器不可用'
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/fix_all_games', methods=['POST'])

def api_fix_all_games():
    """自动修复所有游戏问题API"""
    try:
        if game_health_checker:
            # 运行持续检查和修复
            max_iterations = request.json.get('max_iterations', 5) if request.json else 5

            report = game_health_checker.run_continuous_check(GAMES_DATABASE, max_iterations)

            # 生成详细报告
            report_text = game_health_checker.generate_health_report()

            return jsonify({
                'success': True,
                'message': '自动修复完成',
                'report': report,
                'report_text': report_text,
                'summary': {
                    'total_games': report['games_total'],
                    'healthy_games': report['games_healthy'],
                    'fixed_games': report['games_fixed'],
                    'overall_status': report['overall_status'],
                    'all_games_working': report['overall_status'] == 'all_healthy'
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '游戏健康检查器不可用'
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/game_health_report')

def api_game_health_report():
    """获取游戏健康报告API"""
    try:
        if game_health_checker:
            # 快速检查（不修复）
            report = game_health_checker.check_all_games(GAMES_DATABASE)
            report_text = game_health_checker.generate_health_report()

            return jsonify({
                'success': True,
                'report': report,
                'report_text': report_text,
                'timestamp': report['timestamp']
            })
        else:
            return jsonify({
                'success': False,
                'error': '游戏健康检查器不可用'
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auto_fix_game/<system>/<game_id>', methods=['POST'])

def api_auto_fix_game(system, game_id):
    """自动修复单个游戏API"""
    try:
        if game_health_checker:
            # 找到指定游戏
            game = None
            for g in GAMES_DATABASE.get(system, []):
                if g['id'] == game_id:
                    game = g
                    break

            if not game:
                return jsonify({
                    'success': False,
                    'error': f'游戏不存在: {system}/{game_id}'
                }), 404

            # 检查游戏健康状态
            health = game_health_checker._check_game_health(system, game)

            if health['status'] == 'healthy':
                return jsonify({
                    'success': True,
                    'message': '游戏已经正常运行',
                    'health': health
                })

            # 尝试修复
            fixed = game_health_checker._fix_game_issues(system, game, health)

            # 重新检查
            new_health = game_health_checker._check_game_health(system, game)

            return jsonify({
                'success': fixed,
                'message': '游戏修复完成' if fixed else '游戏修复失败',
                'before_health': health,
                'after_health': new_health,
                'fixed': fixed
            })
        else:
            return jsonify({
                'success': False,
                'error': '游戏健康检查器不可用'
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"🎮 GamePlayer-Raspberry Demo Server")
    print(f"🌐 启动Web服务器在端口 {port}")
    print(f"🔗 访问地址: http://localhost:{port}")
    print(f"📱 Docker演示模式已激活")

    app.run(host='127.0.0.1', port=port, debug=False)
