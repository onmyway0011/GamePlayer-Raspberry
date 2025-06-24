#!/usr/bin/env python3
"""
RetroPie 安装器测试脚本
用于验证基本功能是否正常工作
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from retropie_installer import RetroPieInstaller

def test_dependency_check():
    """测试依赖检查功能"""
    print("=== 测试依赖检查 ===")
    installer = RetroPieInstaller()
    result = installer.check_dependencies()
    print(f"依赖检查结果: {'通过' if result else '失败'}")
    return result

def test_disk_listing():
    """测试磁盘列表功能"""
    print("\n=== 测试磁盘列表 ===")
    installer = RetroPieInstaller()
    disks = installer.list_available_disks()
    print(f"找到 {len(disks)} 个可用磁盘:")
    for i, (device, size, name) in enumerate(disks):
        print(f"  {i+1}. {device} ({size}) - {name}")
    return len(disks) > 0

def test_download_url():
    """测试下载链接获取功能"""
    print("\n=== 测试下载链接获取 ===")
    installer = RetroPieInstaller()
    url = installer.get_retropie_download_url()
    if url:
        print(f"获取到下载链接: {url}")
        return True
    else:
        print("未能获取下载链接")
        return False

def test_file_operations():
    """测试文件操作功能"""
    print("\n=== 测试文件操作 ===")
    installer = RetroPieInstaller()
    
    # 测试下载目录创建
    if installer.download_dir.exists():
        print(f"下载目录已存在: {installer.download_dir}")
    else:
        print(f"下载目录不存在: {installer.download_dir}")
    
    # 测试日志文件创建
    log_file = Path("retropie_installer.log")
    if log_file.exists():
        print(f"日志文件已存在: {log_file}")
        print(f"日志文件大小: {log_file.stat().st_size} 字节")
    else:
        print("日志文件不存在")
    
    return True

def main():
    """运行所有测试"""
    print("RetroPie 安装器功能测试")
    print("=" * 50)
    
    tests = [
        ("依赖检查", test_dependency_check),
        ("磁盘列表", test_disk_listing),
        ("下载链接", test_download_url),
        ("文件操作", test_file_operations),
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
        print("🎉 所有测试通过！安装器可以正常使用。")
    else:
        print("⚠️  部分测试失败，请检查系统配置。")

if __name__ == "__main__":
    main() 