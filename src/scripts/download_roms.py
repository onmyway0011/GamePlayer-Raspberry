#!/usr/bin/env python3
"""
ROM下载脚本
自动下载和管理游戏ROM文件
"""

import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.rom_manager import ROMManager, EmulatorManager

# 创建日志目录
Path("logs").mkdir(exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/rom_download.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """主函数"""
    print("🎮 GamePlayer-Raspberry ROM下载器")
    print("=" * 50)
    
    try:
        # 创建日志目录
        Path("logs").mkdir(exist_ok=True)
        
        # 初始化ROM管理器
        rom_manager = ROMManager()
        
        print("📋 支持的游戏系统:")
        systems = rom_manager.get_supported_systems()
        for i, system in enumerate(systems, 1):
            system_info = rom_manager.get_system_info(system)
            print(f"  {i}. {system_info['name']} ({system_info['short_name']}) {system_info['icon']}")
        
        print(f"\n🚀 开始初始化ROM收藏...")
        
        # 初始化ROM收藏
        success = rom_manager.initialize_rom_collection()
        
        if success:
            print("\n✅ ROM收藏初始化成功!")
            
            # 显示统计信息
            stats = rom_manager.get_download_stats()
            print(f"\n📊 下载统计:")
            print(f"  总下载数: {stats['total_downloaded']}")
            print(f"  成功下载: {stats['successful_downloads']}")
            print(f"  失败下载: {stats['failed_downloads']}")
            
            # 扫描ROM数据库
            rom_database = rom_manager.scan_existing_roms()
            
            print(f"\n📚 ROM数据库:")
            total_roms = 0
            for system, roms in rom_database.items():
                if roms:
                    system_info = rom_manager.get_system_info(system)
                    print(f"  {system_info['name']}: {len(roms)} 个游戏")
                    total_roms += len(roms)
            
            print(f"\n🎯 总计: {total_roms} 个游戏ROM")
            
            if total_roms >= 50:
                print("🎉 已达到推荐的ROM数量!")
            elif total_roms >= 20:
                print("✅ ROM数量良好!")
            else:
                print("⚠️ ROM数量较少，建议添加更多游戏")
            
            # 生成ROM列表文件
            generate_rom_list(rom_database)
            
        else:
            print("❌ ROM收藏初始化失败")
            return 1
            
    except Exception as e:
        logger.error(f"❌ 程序执行失败: {e}")
        print(f"❌ 错误: {e}")
        return 1
    
    return 0

def generate_rom_list(rom_database: dict):
    """生成ROM列表文件"""
    try:
        # 创建Web可访问的ROM列表
        web_rom_list = {
            "systems": {},
            "total_roms": 0,
            "last_updated": "2025-06-27"
        }
        
        for system, roms in rom_database.items():
            if not roms:
                continue
                
            # 获取系统信息
            rom_manager = ROMManager()
            system_info = rom_manager.get_system_info(system)
            
            web_rom_list["systems"][system] = {
                "name": system_info["name"],
                "short_name": system_info["short_name"],
                "icon": system_info["icon"],
                "description": system_info["description"],
                "rom_count": len(roms),
                "games": []
            }
            
            # 添加游戏信息
            for rom in roms:
                game_info = {
                    "name": rom["name"],
                    "description": rom.get("description", ""),
                    "size": rom.get("size", "未知"),
                    "demo": rom.get("demo", False),
                    "file_name": Path(rom["file_path"]).name
                }
                web_rom_list["systems"][system]["games"].append(game_info)
            
            web_rom_list["total_roms"] += len(roms)
        
        # 保存ROM列表到Web目录
        web_dir = Path("data/web")
        web_dir.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(web_dir / "rom_list.json", 'w', encoding='utf-8') as f:
            json.dump(web_rom_list, f, indent=2, ensure_ascii=False)
        
        print(f"📄 ROM列表已保存到: {web_dir / 'rom_list.json'}")
        
        # 生成Markdown格式的ROM列表
        generate_markdown_rom_list(web_rom_list)
        
    except Exception as e:
        logger.error(f"❌ ROM列表生成失败: {e}")

def generate_markdown_rom_list(rom_list: dict):
    """生成Markdown格式的ROM列表"""
    try:
        docs_dir = Path("docs")
        docs_dir.mkdir(exist_ok=True)
        
        markdown_content = f"""# GamePlayer-Raspberry ROM列表

**最后更新**: {rom_list['last_updated']}  
**总游戏数**: {rom_list['total_roms']}

## 支持的游戏系统

"""
        
        for system_id, system_info in rom_list["systems"].items():
            markdown_content += f"""### {system_info['icon']} {system_info['name']}

**系统简称**: {system_info['short_name']}  
**描述**: {system_info['description']}  
**游戏数量**: {system_info['rom_count']}

#### 游戏列表

| 游戏名称 | 描述 | 大小 | 类型 |
|---------|------|------|------|
"""
            
            for game in system_info["games"]:
                game_type = "演示版" if game["demo"] else "完整版"
                markdown_content += f"| {game['name']} | {game['description']} | {game['size']} | {game_type} |\n"
            
            markdown_content += "\n"
        
        markdown_content += f"""
## 使用说明

1. **启动游戏**: 在Web界面中选择对应的游戏系统和游戏
2. **控制方式**: 支持键盘、USB手柄和蓝牙手柄
3. **保存进度**: 游戏支持自动保存和手动保存
4. **金手指**: 部分游戏支持作弊码功能

## 技术信息

- **ROM格式**: 支持各系统的标准ROM格式
- **模拟器**: 使用开源模拟器引擎
- **兼容性**: 针对树莓派优化
- **性能**: 支持60FPS流畅运行

---

*注意: 所有ROM文件均为合法的自制游戏或演示版本*
"""
        
        with open(docs_dir / "ROM_LIST.md", 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"📄 Markdown ROM列表已保存到: {docs_dir / 'ROM_LIST.md'}")
        
    except Exception as e:
        logger.error(f"❌ Markdown ROM列表生成失败: {e}")

if __name__ == "__main__":
    sys.exit(main())
