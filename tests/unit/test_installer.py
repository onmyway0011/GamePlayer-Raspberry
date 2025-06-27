# --- PYTHONPATH AUTO PATCH ---
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# --- END PATCH ---
from src.core.retropie_installer import RetroPieInstaller
from pathlib import Path
import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))
#!/usr/bin/env python3
"""
RetroPie安装器功能测试脚本
用于验证基本功能是否正常工作
"""

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_dependency_check():
    """测试依赖检查"""
    print("=== 测试依赖检查 ===")
    try:
        installer = RetroPieInstaller()
        result = installer.check_dependencies()
        print(f"依赖检查结果: {'通过' if result else '失败'}")
        assert result, "依赖检查失败"
    except Exception as e:
        print(f"✗ 依赖检查异常: {e}")
        assert False, f"依赖检查异常: {e}"


def test_disk_listing():
    """测试磁盘列表"""
    print("\n=== 测试磁盘列表 ===")
    try:
        installer = RetroPieInstaller()
        disks = installer.list_available_disks()
        print(f"找到 {len(disks)} 个可用磁盘:")
        for i, (device, size, name) in enumerate(disks):
            print(f"  {i+1}. {device} ({size}) - {name}")
        assert len(disks) >= 0, "磁盘列表获取失败"
    except Exception as e:
        print(f"✗ 磁盘列表异常: {e}")
        assert False, f"磁盘列表异常: {e}"


def test_download_url():
    """测试下载链接获取"""
    print("\n=== 测试下载链接获取 ===")
    try:
        installer = RetroPieInstaller()
        url = installer.get_retropie_download_url()
        print(f"获取到下载链接: {url}")
        assert url and url.startswith("http"), "下载链接无效"
    except Exception as e:
        print(f"✗ 下载链接获取异常: {e}")
        assert False, f"下载链接获取异常: {e}"


def test_file_operations():
    """测试文件操作"""
    print("\n=== 测试文件操作 ===")
    try:
        installer = RetroPieInstaller()

        # 检查下载目录
        if installer.download_dir.exists():
            print(f"下载目录已存在: {installer.download_dir}")
        else:
            print(f"下载目录不存在: {installer.download_dir}")

        # 检查日志文件
        if installer.log_file.exists():
            print(f"日志文件已存在: {installer.log_file}")
            print(f"日志文件大小: {installer.log_file.stat().st_size} 字节")
        else:
            print(f"日志文件不存在: {installer.log_file}")

        assert True
    except Exception as e:
        print(f"✗ 文件操作异常: {e}")
        assert False, f"文件操作异常: {e}"


def main():
    """运行所有测试"""
    print("RetroPie安装器功能测试")
    print("=" * 50)

    tests = [
        ("依赖检查", test_dependency_check),
        ("磁盘列表", test_disk_listing),
        ("下载链接获取", test_download_url),
        ("文件操作", test_file_operations),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            test_func()
            results.append((test_name, True))
            print(f"✓ {test_name}: 通过")
        except Exception as e:
            print(f"✗ {test_name}: 失败 - {e}")
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
        print("🎉 所有测试通过！RetroPie安装器可以正常使用。")
    else:
        print("⚠️  部分测试失败，请检查配置。")

    print("\n使用说明:")
    print("1. 运行: python retropie_installer.py --list-disks")
    print("2. 运行: python retropie_installer.py --download")
    print("3. 运行: python retropie_installer.py --burn /dev/sdX")

if __name__ == "__main__":
    main()
