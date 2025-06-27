#!/usr/bin/env python3
"""
游戏封面源管理工具
用于管理和更新游戏封面下载源
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.enhanced_cover_downloader import EnhancedCoverDownloader

class CoverSourceManager:
    """封面源管理器"""
    
    def __init__(self):
        self.project_root = project_root
        self.config_file = self.project_root / "config" / "covers" / "cover_sources.json"
        self.downloader = EnhancedCoverDownloader()
    
    def list_sources(self, system: str = None, game_id: str = None):
        """列出封面源"""
        print("📋 当前封面源配置:")
        print("=" * 50)
        
        cover_sources = self.downloader.cover_sources
        
        if system and system in cover_sources:
            # 显示特定系统
            games = cover_sources[system]
            print(f"\n🎮 {system.upper()} 系统 ({len(games)} 个游戏):")
            
            for gid, game_data in games.items():
                if game_id and gid != game_id:
                    continue
                    
                if isinstance(game_data, dict):
                    name = game_data.get('name', gid)
                    sources = game_data.get('sources', [])
                    print(f"\n  📦 {name} ({gid}):")
                    for i, url in enumerate(sources, 1):
                        print(f"    {i}. {url}")
                else:
                    print(f"\n  📦 {gid}: 旧格式数据")
        else:
            # 显示所有系统
            for sys, games in cover_sources.items():
                print(f"\n🎮 {sys.upper()} 系统 ({len(games)} 个游戏):")
                for gid, game_data in games.items():
                    if isinstance(game_data, dict):
                        name = game_data.get('name', gid)
                        sources_count = len(game_data.get('sources', []))
                        print(f"  📦 {name}: {sources_count} 个源")
                    else:
                        print(f"  📦 {gid}: 旧格式")
    
    def add_source(self, system: str, game_id: str, url: str, game_name: str = None):
        """添加新的封面源"""
        print(f"➕ 添加封面源: {system}/{game_id}")
        
        # 加载当前配置
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 确保结构存在
        if 'game_covers' not in config:
            config['game_covers'] = {}
        
        if system not in config['game_covers']:
            config['game_covers'][system] = {}
        
        if game_id not in config['game_covers'][system]:
            config['game_covers'][system][game_id] = {
                'name': game_name or game_id.replace('_', ' ').title(),
                'sources': []
            }
        
        # 添加新源
        game_data = config['game_covers'][system][game_id]
        if isinstance(game_data, dict):
            if 'sources' not in game_data:
                game_data['sources'] = []
            
            if url not in game_data['sources']:
                game_data['sources'].append(url)
                print(f"✅ 已添加源: {url}")
            else:
                print(f"⚠️ 源已存在: {url}")
        
        # 保存配置
        self.save_config(config)
    
    def remove_source(self, system: str, game_id: str, url: str = None, index: int = None):
        """移除封面源"""
        print(f"➖ 移除封面源: {system}/{game_id}")
        
        # 加载当前配置
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if (system not in config.get('game_covers', {}) or 
            game_id not in config['game_covers'][system]):
            print(f"❌ 游戏不存在: {system}/{game_id}")
            return
        
        game_data = config['game_covers'][system][game_id]
        if not isinstance(game_data, dict) or 'sources' not in game_data:
            print(f"❌ 无效的游戏数据格式")
            return
        
        sources = game_data['sources']
        
        if url:
            # 按URL移除
            if url in sources:
                sources.remove(url)
                print(f"✅ 已移除源: {url}")
            else:
                print(f"❌ 源不存在: {url}")
        elif index is not None:
            # 按索引移除
            if 0 <= index < len(sources):
                removed_url = sources.pop(index)
                print(f"✅ 已移除源 [{index}]: {removed_url}")
            else:
                print(f"❌ 无效索引: {index}")
        else:
            print(f"❌ 请指定URL或索引")
            return
        
        # 保存配置
        self.save_config(config)
    
    def test_sources(self, system: str = None, game_id: str = None, max_games: int = 5):
        """测试封面源"""
        print("🧪 测试封面源...")
        
        cover_sources = self.downloader.cover_sources
        
        if system and system in cover_sources:
            games_to_test = {system: cover_sources[system]}
        else:
            games_to_test = cover_sources
        
        total_tested = 0
        total_success = 0
        
        for sys, games in games_to_test.items():
            print(f"\n🎮 测试 {sys.upper()} 系统:")
            
            game_items = list(games.items())
            if game_id:
                game_items = [(gid, gdata) for gid, gdata in game_items if gid == game_id]
            else:
                game_items = game_items[:max_games]  # 限制测试数量
            
            for gid, game_data in game_items:
                if isinstance(game_data, dict):
                    name = game_data.get('name', gid)
                    sources = game_data.get('sources', [])
                    
                    print(f"\n  📦 测试 {name}:")
                    
                    success = self.downloader.download_cover_from_sources(sys, gid, sources, name)
                    
                    total_tested += 1
                    if success:
                        total_success += 1
                        print(f"    ✅ 测试成功")
                    else:
                        print(f"    ❌ 测试失败")
        
        print(f"\n📊 测试结果: {total_success}/{total_tested} 成功 ({total_success/max(total_tested,1)*100:.1f}%)")
    
    def update_alternative_sources(self):
        """更新替代图片源"""
        print("🔄 更新替代图片源...")
        
        # 新的可靠图片源
        alternative_sources = {
            "nes": {
                "super_mario_bros": [
                    "https://raw.githubusercontent.com/libretro-thumbnails/Nintendo_-_Nintendo_Entertainment_System/master/Named_Boxarts/Super%20Mario%20Bros.%20(World).png",
                    "https://archive.org/download/nes-cart-scans/Super%20Mario%20Bros.%20(World).jpg",
                    "https://www.emuparadise.me/Nintendo%20Entertainment%20System/Boxes/Super%20Mario%20Bros.%20(U)%20(PRG0)%20[!].jpg"
                ],
                "zelda": [
                    "https://raw.githubusercontent.com/libretro-thumbnails/Nintendo_-_Nintendo_Entertainment_System/master/Named_Boxarts/Legend%20of%20Zelda,%20The%20(USA).png",
                    "https://archive.org/download/nes-cart-scans/Legend%20of%20Zelda,%20The%20(USA).jpg"
                ]
            }
        }
        
        # 加载当前配置
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 更新源
        for system, games in alternative_sources.items():
            for game_id, new_sources in games.items():
                if (system in config.get('game_covers', {}) and 
                    game_id in config['game_covers'][system]):
                    
                    game_data = config['game_covers'][system][game_id]
                    if isinstance(game_data, dict) and 'sources' in game_data:
                        # 添加新源（避免重复）
                        for source in new_sources:
                            if source not in game_data['sources']:
                                game_data['sources'].append(source)
                                print(f"✅ 为 {system}/{game_id} 添加新源")
        
        # 保存配置
        self.save_config(config)
        print("✅ 替代源更新完成")
    
    def save_config(self, config: Dict):
        """保存配置"""
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 配置已保存: {self.config_file}")
            
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
    
    def generate_report(self):
        """生成封面源报告"""
        print("📊 生成封面源报告...")
        
        report = self.downloader.generate_cover_report()
        
        print(f"\n📋 封面源报告:")
        print(f"  总体覆盖率: {report.get('overall_coverage', 'N/A')}")
        print(f"  总封面数: {report.get('total_covers', 0)}")
        print(f"  总游戏数: {report.get('total_games', 0)}")
        print(f"  使用源数: {report.get('sources_used', 0)}")
        
        print(f"\n📂 各系统详情:")
        for system, stats in report.get('systems', {}).items():
            print(f"  {system.upper()}:")
            print(f"    下载封面: {stats.get('downloaded_covers', 0)}")
            print(f"    可用源: {stats.get('available_sources', 0)}")
            print(f"    覆盖率: {stats.get('coverage', 'N/A')}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='游戏封面源管理工具')
    parser.add_argument('action', choices=['list', 'add', 'remove', 'test', 'update', 'report'],
                       help='操作类型')
    parser.add_argument('--system', '-s', help='游戏系统 (nes, snes, gameboy, etc.)')
    parser.add_argument('--game', '-g', help='游戏ID')
    parser.add_argument('--url', '-u', help='图片URL')
    parser.add_argument('--name', '-n', help='游戏名称')
    parser.add_argument('--index', '-i', type=int, help='源索引')
    parser.add_argument('--max-games', '-m', type=int, default=5, help='最大测试游戏数')
    
    args = parser.parse_args()
    
    manager = CoverSourceManager()
    
    if args.action == 'list':
        manager.list_sources(args.system, args.game)
    
    elif args.action == 'add':
        if not all([args.system, args.game, args.url]):
            print("❌ 添加源需要指定 --system, --game, --url")
            return
        manager.add_source(args.system, args.game, args.url, args.name)
    
    elif args.action == 'remove':
        if not all([args.system, args.game]):
            print("❌ 移除源需要指定 --system, --game")
            return
        manager.remove_source(args.system, args.game, args.url, args.index)
    
    elif args.action == 'test':
        manager.test_sources(args.system, args.game, args.max_games)
    
    elif args.action == 'update':
        manager.update_alternative_sources()
    
    elif args.action == 'report':
        manager.generate_report()

if __name__ == "__main__":
    main()
