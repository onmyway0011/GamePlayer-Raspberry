#!/usr/bin/env python3
"""
HDMI配置器功能测试脚本
用于验证基本功能是否正常工作
"""

import sys
import os
import tempfile
from pathlib import Path
import pytest
# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.hdmi_config import BaseInstaller as HDMIConfigurator

def create_test_config(content: str) -> Path:
    """创建测试配置文件"""
    test_file = Path(tempfile.mktemp(suffix='.txt'))
    with open(test_file, 'w') as f:
        f.write(content)
    return test_file

def test_config_parsing():
    """测试配置解析功能"""
    print("=== 测试配置解析功能 ===")
    
    # 创建测试配置
    test_content = """
# 测试配置文件
hdmi_group=1
hdmi_mode=4
gpu_mem=128
# 注释行
disable_overscan=0
"""
    
    test_file = create_test_config(test_content)
    
    try:
        configurator = HDMIConfigurator(str(test_file))
        
        # 测试解析
        lines = configurator.read_config()
        print(f"✓ 读取配置成功，共 {len(lines)} 行")
        
        # 测试查找配置项
        hdmi_group_line = configurator.find_config_line(lines, "hdmi_group")
        assert hdmi_group_line is not None, "未找到 hdmi_group"
        print(f"✓ 找到 hdmi_group 在第 {hdmi_group_line + 1} 行")
        
        # 测试更新配置
        updated_lines = configurator.update_config(lines, "hdmi_mode", "16")
        updated_lines = configurator.update_config(updated_lines, "gpu_mem", "256")
        
        # 验证更新
        new_hdmi_mode_line = configurator.find_config_line(updated_lines, "hdmi_mode")
        assert new_hdmi_mode_line is not None, "未找到更新后的 hdmi_mode"
        parsed = configurator.parse_config_line(updated_lines[new_hdmi_mode_line])
        assert parsed and parsed['value'] == '16', "配置更新失败"
        print("✓ 配置更新成功")
        
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()

def test_hdmi_configs():
    """测试HDMI配置项"""
    print("\n=== 测试HDMI配置项 ===")
    
    configurator = HDMIConfigurator()
    
    print("HDMI配置项:")
    for key, value in configurator.hdmi_configs.items():
        print(f"  {key}={value}")
    
    # 检查关键配置项
    required_keys = ['hdmi_group', 'hdmi_mode', 'gpu_mem', 'disable_overscan']
    for key in required_keys:
        assert key in configurator.hdmi_configs, f"缺少配置项: {key}"
        print(f"✓ 包含配置项: {key}")

def test_backup_functionality():
    """测试备份功能"""
    print("\n=== 测试备份功能 ===")
    
    # 创建测试配置
    test_content = "hdmi_group=1\nhdmi_mode=4\n"
    test_file = create_test_config(test_content)
    
    try:
        configurator = HDMIConfigurator(str(test_file))
        
        # 测试备份
        assert configurator.backup_config(), "备份功能失败"
        print("✓ 备份功能正常")
        
        # 检查备份文件
        assert configurator.backup_path.exists(), "备份文件未创建"
        print(f"✓ 备份文件已创建: {configurator.backup_path}")
        
        # 验证备份内容
        with open(configurator.backup_path, 'r') as f:
            backup_content = f.read()
        assert backup_content == test_content, "备份内容不正确"
        print("✓ 备份内容正确")
        
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()
        if configurator.backup_path.exists():
            configurator.backup_path.unlink()

def test_config_validation():
    """测试配置验证功能"""
    print("\n=== 测试配置验证功能 ===")
    
    # 创建测试配置
    test_content = """
hdmi_group=1
hdmi_mode=16
gpu_mem=256
disable_overscan=1
"""
    
    test_file = create_test_config(test_content)
    
    try:
        configurator = HDMIConfigurator(str(test_file))
        
        # 测试验证
        assert configurator.validate_config(), "配置验证失败"
        print("✓ 配置验证通过")
        
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()

def test_dry_run():
    """测试模拟运行功能"""
    print("\n=== 测试模拟运行功能 ===")
    
    # 创建测试配置
    test_content = "hdmi_group=1\nhdmi_mode=4\n"
    test_file = create_test_config(test_content)
    
    try:
        configurator = HDMIConfigurator(str(test_file))
        
        # 显示当前配置
        configurator.show_current_config()
        
        # 显示将要应用的更改
        configurator.show_changes()
        
        print("✓ 模拟运行功能正常")
        
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()

def test_apply_hdmi_configs(tmp_path):
    config_path = tmp_path / 'config.txt'
    config_path.write_text('# config for test\n')
    configurator = HDMIConfigurator(str(config_path))
    assert configurator.apply_hdmi_configs() is True

def main():
    """运行所有测试"""
    print("HDMI配置器功能测试")
    print("=" * 50)
    
    tests = [
        ("配置解析功能", test_config_parsing),
        ("HDMI配置项", test_hdmi_configs),
        ("备份功能", test_backup_functionality),
        ("配置验证功能", test_config_validation),
        ("模拟运行功能", test_dry_run),
        ("应用配置功能", test_apply_hdmi_configs),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✓ {test_name}: {'通过' if result else '失败'}")
        except Exception as e:
            print(f"✗ {test_name}: 错误 - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
    
    print(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！HDMI配置器可以正常使用。")
    else:
        print("⚠️  部分测试失败，请检查代码。")
    
    print("\n使用说明:")
    print("1. 查看当前配置: python hdmi_config.py --show")
    print("2. 模拟运行: python hdmi_config.py --dry-run")
    print("3. 应用配置: sudo python hdmi_config.py")
    print("4. 恢复配置: sudo python hdmi_config.py --restore")

if __name__ == "__main__":
    main()