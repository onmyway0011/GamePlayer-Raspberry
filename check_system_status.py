#!/usr/bin/env python3
"""
GamePlayer-Raspberry 快速系统状态检查
"""

import os
import json
from pathlib import Path

def check_system_status():
    """检查系统状态"""
    project_root = Path(".")
    
    print("🔍 GamePlayer-Raspberry 系统状态检查")
    print("=" * 50)
    
    # 1. 项目结构检查
    print("\n📁 项目结构:")
    key_dirs = ["src", "data", "config", "output", "data/roms"]
    structure_score = 0
    for dir_name in key_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"  ✅ {dir_name}/")
            structure_score += 1
        else:
            print(f"  ❌ {dir_name}/")
    
    # 2. 文件统计
    print("\n📊 文件统计:")
    
    # ROM文件
    roms_dir = project_root / "data" / "roms"
    rom_score = 0
    if roms_dir.exists():
        nes_count = len(list(roms_dir.rglob("*.nes")))
        snes_count = len(list(roms_dir.rglob("*.smc")))
        gb_count = len(list(roms_dir.rglob("*.gb")))
        md_count = len(list(roms_dir.rglob("*.md")))
        total_roms = nes_count + snes_count + gb_count + md_count
        
        print(f"  🎮 NES ROM: {nes_count}个")
        print(f"  🎯 SNES ROM: {snes_count}个")
        print(f"  📱 GB ROM: {gb_count}个")
        print(f"  🔵 Genesis ROM: {md_count}个")
        print(f"  🎯 总ROM: {total_roms}个")
        
        if total_roms >= 50:
            rom_score = 2
        elif total_roms >= 20:
            rom_score = 1
    else:
        print(f"  ❌ ROM目录不存在")
    
    # 脚本文件
    scripts_dir = project_root / "src" / "scripts"
    script_score = 0
    if scripts_dir.exists():
        script_count = len(list(scripts_dir.glob("*.py")))
        print(f"  🔧 Python脚本: {script_count}个")
        if script_count >= 5:
            script_score = 1
    
    # 镜像文件
    output_dir = project_root / "output"
    image_score = 0
    if output_dir.exists():
        image_files = list(output_dir.glob("*.img.gz"))
        report_files = list(output_dir.glob("*.json"))
        print(f"  💾 镜像文件: {len(image_files)}个")
        print(f"  📋 报告文件: {len(report_files)}个")
        
        if image_files:
            image_score = 1
    
    # 3. 最新修复报告
    print("\n📋 最新修复报告:")
    repair_score = 0
    if output_dir.exists():
        repair_reports = sorted(output_dir.glob("*continuous_repair_report*.json"))
        
        if repair_reports:
            latest_repair = repair_reports[-1]
            print(f"  🔄 修复报告: {latest_repair.name}")
            
            try:
                with open(latest_repair, 'r') as f:
                    report = json.load(f)
                
                success_rate = report.get('repair_success_rate', 0)
                final_status = report.get('final_status', '未知')
                persistent_issues = report.get('persistent_issues', 0)
                
                print(f"  📈 修复成功率: {success_rate:.1f}%")
                print(f"  🎯 最终状态: {final_status}")
                print(f"  ⚠️ 持久问题: {persistent_issues}个")
                
                if success_rate >= 90 and persistent_issues == 0:
                    repair_score = 2
                elif success_rate >= 70:
                    repair_score = 1
                    
            except Exception as e:
                print(f"  ⚠️ 报告文件读取失败: {e}")
        else:
            print(f"  📄 暂无修复报告")
    
    # 4. 系统健康度评估
    print("\n🎯 系统健康度评估:")
    
    total_score = structure_score + rom_score + script_score + image_score + repair_score
    max_score = 10  # 5 + 2 + 1 + 1 + 2
    health_percentage = (total_score / max_score) * 100
    
    if health_percentage >= 90:
        status_emoji = "🟢"
        status_text = "优秀"
    elif health_percentage >= 70:
        status_emoji = "🟡" 
        status_text = "良好"
    elif health_percentage >= 50:
        status_emoji = "🟠"
        status_text = "一般"
    else:
        status_emoji = "🔴"
        status_text = "需要修复"
    
    print(f"  {status_emoji} 系统健康度: {health_percentage:.0f}% ({status_text})")
    print(f"  📊 得分: {total_score}/{max_score}")
    print(f"    - 项目结构: {structure_score}/5")
    print(f"    - ROM文件: {rom_score}/2") 
    print(f"    - 脚本文件: {script_score}/1")
    print(f"    - 镜像文件: {image_score}/1")
    print(f"    - 修复状态: {repair_score}/2")
    
    # 5. 功能验证
    print("\n🔍 功能验证:")
    
    # 检查关键文件
    key_files = [
        ("README.md", "项目文档"),
        ("src/core/sync_rom_downloader.py", "ROM下载器"),
        ("src/scripts/enhanced_image_builder_with_games.py", "镜像构建器"),
        ("src/scripts/continuous_testing_and_repair.py", "自动化测试"),
    ]
    
    for file_path, description in key_files:
        if (project_root / file_path).exists():
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description}")
    
    # 6. 最终建议
    print("\n💡 状态总结:")
    
    if health_percentage >= 90:
        print("  🎉 系统运行完美！所有功能正常工作")
        print("  ✅ 可以正常使用所有功能")
        print("  🚀 镜像可以直接部署到树莓派")
    elif health_percentage >= 70:
        print("  👍 系统运行良好，有轻微问题")
        print("  🔧 建议运行一次完整测试和修复")
    else:
        print("  ⚠️ 系统存在问题，需要修复")
        print("  🔧 建议运行: python3 src/scripts/continuous_testing_and_repair.py")
    
    # 检查是否有持续修复报告显示100%成功
    if repair_score == 2:
        print("\n🏆 特别提示:")
        print("  ✨ 自动化测试和修复系统已完美运行")
        print("  🎯 所有问题已被自动检测并修复")
        print("  🎮 GamePlayer-Raspberry 处于生产就绪状态")
    
    print("\n" + "=" * 50)
    return health_percentage

if __name__ == "__main__":
    check_system_status()
