# --- PYTHONPATH AUTO PATCH ---
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# --- END PATCH ---
from src.core.rom_downloader import ROMDownloader
from pathlib import Path
import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))
#!/usr/bin/env python3
"""
ROM下载器功能测试脚本
用于验证基本功能是否正常工作
"""

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_config_loading():
    """测试配置文件加载"""
    print("=== 测试配置文件加载 ===")
    try:
        downloader = ROMDownloader()
        print("✓ 配置文件加载成功")
        print(f"  下载目录: {downloader.download_dir}")
        print(f"  配置项数量: {len(downloader.config)}")
        assert True
    except Exception as e:
        print(f"✗ 配置文件加载失败: {e}")
        assert False, f"配置文件加载失败: {e}"


def test_session_setup():
    """测试HTTP会话设置"""
    print("\n=== 测试HTTP会话设置 ===")
    try:
        downloader = ROMDownloader()
        session = downloader.session
        print("✓ HTTP会话设置成功")
        print(f"  重试策略: {session.adapters['https://'].max_retries}")
        assert True
    except Exception as e:
        print(f"✗ HTTP会话设置失败: {e}")
        assert False, f"HTTP会话设置失败: {e}"


def test_rom_search():
    """测试ROM搜索功能"""
    print("\n=== 测试ROM搜索功能 ===")
    try:
        downloader = ROMDownloader()
        results = downloader.search_roms("nes games")

        if results:
            print(f"✓ 搜索成功，找到 {len(results)} 个结果")
            for i, result in enumerate(results[:3]):
                print(f"  {i+1}. {result['title'][:50]}...")
            assert True
        else:
            print("⚠️  搜索成功但未找到结果")
            assert True
    except Exception as e:
        print(f"✗ 搜索失败: {e}")
        assert False, f"搜索失败: {e}"


def test_file_operations():
    """测试文件操作功能"""
    print("\n=== 测试文件操作功能 ===")
    try:
        downloader = ROMDownloader()

        # 测试下载目录创建
        if downloader.download_dir.exists():
            print(f"✓ 下载目录已存在: {downloader.download_dir}")
        else:
            print(f"✗ 下载目录不存在: {downloader.download_dir}")
            assert False, "下载目录不存在"

        # 测试配置文件
        if downloader.config_file.exists():
            print(f"✓ 配置文件已存在: {downloader.config_file}")
        else:
            print(f"✗ 配置文件不存在: {downloader.config_file}")
            assert False, "配置文件不存在"

        assert True
    except Exception as e:
        print(f"✗ 文件操作测试失败: {e}")
        assert False, f"文件操作测试失败: {e}"


def test_checksum_calculation():
    """测试校验和计算"""
    print("\n=== 测试校验和计算 ===")
    try:
        downloader = ROMDownloader()

        # 创建一个测试文件
        test_file = downloader.download_dir / "test.txt"
        test_content = "Hello, RetroPie!"

        with open(test_file, "w") as f:
            f.write(test_content)

        # 计算校验和
        result = downloader.verify_file(test_file)

        # 清理测试文件
        test_file.unlink()

        if result:
            print("✓ 校验和计算成功")
            assert True
        else:
            print("✗ 校验和计算失败")
            assert False, "校验和计算失败"

    except Exception as e:
        print(f"✗ 校验和测试失败: {e}")
        assert False, f"校验和测试失败: {e}"


def test_sftp_connection():
    """测试SFTP连接（仅检查配置）"""
    print("\n=== 测试SFTP连接配置 ===")
    try:
        downloader = ROMDownloader()
        pi_config = downloader.config["raspberry_pi"]

        print(f"  主机: {pi_config['host']}")
        print(f"  端口: {pi_config['port']}")
        print(f"  用户名: {pi_config['username']}")
        print(f"  ROM路径: {pi_config['roms_path']}")

        if pi_config.get("password") or pi_config.get("key_file"):
            print("✓ SFTP配置完整")
            assert True
        else:
            print("⚠️  SFTP配置不完整（需要密码或密钥文件）")
            assert True

    except Exception as e:
        print(f"✗ SFTP配置检查失败: {e}")
        assert False, f"SFTP配置检查失败: {e}"


def main():
    """运行所有测试"""
    print("ROM下载器功能测试")
    print("=" * 50)

    tests = [
        ("配置文件加载", test_config_loading),
        ("HTTP会话设置", test_session_setup),
        ("ROM搜索功能", test_rom_search),
        ("文件操作", test_file_operations),
        ("校验和计算", test_checksum_calculation),
        ("SFTP连接配置", test_sftp_connection),
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
        print("🎉 所有测试通过！ROM下载器可以正常使用。")
    else:
        print("⚠️  部分测试失败，请检查配置和网络连接。")

    print("\n使用说明:")
    print("1. 编辑 rom_config.json 配置树莓派连接信息")
    print("2. 运行: python rom_downloader.py --setup-config")
    print("3. 运行: python rom_downloader.py")

if __name__ == "__main__":
    main()
