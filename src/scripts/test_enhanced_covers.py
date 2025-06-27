#!/usr/bin/env python3
"""
测试增强的封面下载系统
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.enhanced_cover_downloader import EnhancedCoverDownloader

def test_config_loading():
    """测试配置加载"""
    print("🧪 测试配置加载...")
    
    downloader = EnhancedCoverDownloader()
    
    print(f"✅ 配置加载成功")
    print(f"📊 游戏系统数: {len(downloader.cover_sources)}")
    
    for system, games in downloader.cover_sources.items():
        print(f"  {system.upper()}: {len(games)} 个游戏")
        
        # 显示前3个游戏的详情
        for i, (game_id, game_data) in enumerate(list(games.items())[:3]):
            if isinstance(game_data, dict):
                name = game_data.get('name', game_id)
                sources_count = len(game_data.get('sources', []))
                print(f"    - {name}: {sources_count} 个图片源")
            else:
                print(f"    - {game_id}: 旧格式数据")
    
    return True

def test_single_download():
    """测试单个游戏封面下载"""
    print("\n🧪 测试单个游戏封面下载...")
    
    downloader = EnhancedCoverDownloader()
    
    # 测试NES系统的Super Mario Bros
    if 'nes' in downloader.cover_sources and 'super_mario_bros' in downloader.cover_sources['nes']:
        game_data = downloader.cover_sources['nes']['super_mario_bros']
        
        if isinstance(game_data, dict):
            sources = game_data.get('sources', [])
            game_name = game_data.get('name', 'Super Mario Bros')
            
            print(f"🎮 测试游戏: {game_name}")
            print(f"📊 图片源数量: {len(sources)}")
            
            # 尝试下载
            success = downloader.download_cover_from_sources('nes', 'super_mario_bros', sources, game_name)
            
            if success:
                print("✅ 单个下载测试成功")
                return True
            else:
                print("❌ 单个下载测试失败")
                return False
    
    print("⚠️ 未找到测试游戏")
    return False

def test_placeholder_creation():
    """测试占位符创建"""
    print("\n🧪 测试占位符创建...")
    
    downloader = EnhancedCoverDownloader()
    
    # 创建测试占位符
    success = downloader.create_placeholder_cover('test', 'test_game', 'Test Game')
    
    if success:
        print("✅ 占位符创建测试成功")
        
        # 检查文件是否存在
        placeholder_path = downloader.covers_dir / 'test' / 'test_game.jpg'
        if placeholder_path.exists():
            print(f"✅ 占位符文件存在: {placeholder_path}")
            print(f"📊 文件大小: {placeholder_path.stat().st_size} bytes")
            return True
        else:
            print("❌ 占位符文件不存在")
            return False
    else:
        print("❌ 占位符创建失败")
        return False

def test_batch_download():
    """测试批量下载"""
    print("\n🧪 测试批量下载...")
    
    downloader = EnhancedCoverDownloader()
    
    # 只下载NES系统的封面进行测试
    if 'nes' in downloader.cover_sources:
        nes_games = downloader.cover_sources['nes']
        
        print(f"🎮 开始下载 {len(nes_games)} 个NES游戏封面...")
        
        # 临时修改cover_sources只包含NES
        original_sources = downloader.cover_sources
        downloader.cover_sources = {'nes': nes_games}
        
        try:
            results = downloader.download_all_covers()
            
            if 'nes' in results:
                nes_result = results['nes']
                print(f"✅ 批量下载完成")
                print(f"📊 成功: {nes_result['success']}/{nes_result['total']} ({nes_result['rate']})")
                return True
            else:
                print("❌ 批量下载失败")
                return False
        finally:
            # 恢复原始配置
            downloader.cover_sources = original_sources
    else:
        print("⚠️ 未找到NES游戏配置")
        return False

def test_cover_report():
    """测试封面报告生成"""
    print("\n🧪 测试封面报告生成...")
    
    downloader = EnhancedCoverDownloader()
    
    report = downloader.generate_cover_report()
    
    print("✅ 报告生成成功")
    print(f"📊 总体覆盖率: {report.get('overall_coverage', 'N/A')}")
    print(f"📊 总封面数: {report.get('total_covers', 0)}")
    print(f"📊 总游戏数: {report.get('total_games', 0)}")
    
    for system, stats in report.get('systems', {}).items():
        print(f"  {system.upper()}: {stats.get('coverage', 'N/A')}")
    
    return True

def test_url_validation():
    """测试URL验证"""
    print("\n🧪 测试URL验证...")
    
    downloader = EnhancedCoverDownloader()
    
    # 测试有效URL
    test_urls = [
        "https://via.placeholder.com/300x400/667eea/ffffff?text=Test",
        "https://httpbin.org/status/404",  # 这个会返回404
        "https://invalid-url-that-does-not-exist.com/image.jpg"  # 这个会连接失败
    ]
    
    for i, url in enumerate(test_urls):
        print(f"🔗 测试URL {i+1}: {url[:50]}...")
        
        success = downloader.download_cover_from_sources('test', f'url_test_{i}', [url], f'URL Test {i}')
        
        if success:
            print(f"  ✅ URL {i+1} 处理成功")
        else:
            print(f"  ❌ URL {i+1} 处理失败")
    
    return True

def main():
    """主函数"""
    print("🖼️ 增强封面下载器测试套件")
    print("=" * 50)
    
    tests = [
        ("配置加载", test_config_loading),
        ("单个下载", test_single_download),
        ("占位符创建", test_placeholder_creation),
        ("批量下载", test_batch_download),
        ("封面报告", test_cover_report),
        ("URL验证", test_url_validation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print(f"\n{'='*50}")
    print(f"🎯 测试结果: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有测试通过！增强封面下载器工作正常")
    else:
        print("⚠️ 部分测试失败，请检查配置和网络连接")

if __name__ == "__main__":
    main()
