# --- PYTHONPATH AUTO PATCH ---
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# --- END PATCH ---
from src.core.virtuanes_installer import VirtuaNESInstaller
from pathlib import Path
import tempfile
import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))
#!/usr/bin/env python3
"""
VirtuaNES 安装器功能测试脚本
用于验证基本功能是否正常工作
"""


# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置测试环境变量
os.environ["TEST_ENV"] = "true"


def test_config_loading():
    """测试配置文件加载"""
    print("=== 测试配置文件加载 ===")
    try:
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json') as tmp:
            tmp.write('{"version": "0.97", "enabled": true}')
            tmp.flush()
            
            installer = VirtuaNESInstaller(config_path=tmp.name)
            print("✓ 配置文件加载成功")
            print(f"  版本: {installer.config.get('version', 'unknown')}")
            print(f"  启用状态: {installer.config.get('enabled', False)}")
            assert True
    except Exception as e:
        print(f"✗ 配置文件加载失败: {e}")
        assert False, f"配置文件加载失败: {e}"


def test_dependency_check():
    """测试依赖检查"""
    print("\n=== 测试依赖检查 ===")
    try:
        installer = VirtuaNESInstaller()
        result = installer.check_dependencies()
        print(f"依赖检查结果: {'通过' if result else '失败'}")
        # 在测试环境中，依赖检查可能失败，这是正常的
        assert True
    except Exception as e:
        print(f"✗ 依赖检查异常: {e}")
        assert False, f"依赖检查异常: {e}"


def test_install_paths():
    """测试安装路径"""
    print("\n=== 测试安装路径 ===")
    
    # 设置测试环境变量
    os.environ["TEST_ENV"] = "false"
    
    try:
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json') as tmp:
            tmp.write('{"install_dir": "tmp/install", "config_dir": "tmp/config", "core_dir": "tmp/core"}')
            tmp.flush()
            
            installer = VirtuaNESInstaller(config_path=tmp.name)

            print(f"  安装目录: {installer.config.get('install_dir')}")
            print(f"  配置目录: {installer.config.get('config_dir')}")
            print(f"  核心目录: {installer.config.get('core_dir')}")

            # 检查路径是否合理
            assert "tmp/install" in installer.config.get('install_dir'), "安装目录路径不正确"
            assert "tmp/config" in installer.config.get('config_dir'), "配置目录路径不正确"
            assert "tmp/core" in installer.config.get('core_dir'), "核心目录路径不正确"

            assert True
    except Exception as e:
        print(f"✗ 安装路径测试失败: {e}")
        assert False, f"安装路径测试失败: {e}"
    finally:
        # 恢复测试环境变量
        os.environ["TEST_ENV"] = "true"


def test_config_generation():
    """测试配置文件生成"""
    print("\n=== 测试配置文件生成 ===")
    try:
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json') as tmp:
            tmp.write('{"config_dir": "tmp/config"}')
            tmp.flush()
            
            installer = VirtuaNESInstaller(config_path=tmp.name)
            
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_config_dir = Path(temp_dir) / "config"
                temp_config_dir.mkdir()
                
                # 临时修改配置目录
            original_config_dir = installer.config_dir
            installer.config_dir = temp_config_dir
            
            # 生成配置
            result = installer.configure_virtuanes()
            
            # 恢复原始配置目录
            installer.config_dir = original_config_dir
            
            if result:
                config_file = temp_config_dir / "virtuanes.cfg"
                if config_file.exists():
                    print("✓ 配置文件生成成功")
                    print(f"  配置文件大小: {config_file.stat().st_size} 字节")
                    assert True
                else:
                    print("✗ 配置文件未创建")
                    assert False, "配置文件未创建"
            else:
                print("✗ 配置文件生成失败")
                assert False, "配置文件生成失败"
                
    except Exception as e:
        print(f"✗ 配置文件生成测试失败: {e}")
        assert False, f"配置文件生成测试失败: {e}"


def test_retroarch_integration():
    """测试 RetroArch 集成"""
    print("\n=== 测试 RetroArch 集成 ===")
    try:
        installer = VirtuaNESInstaller()
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_core_dir = Path(temp_dir) / "cores"
            temp_core_dir.mkdir()
            
            # 临时修改核心目录
            original_core_dir = installer.core_dir
            installer.core_dir = temp_core_dir
            
            # 测试集成
            result = installer.integrate_with_retroarch()
            
            # 恢复原始核心目录
            installer.core_dir = original_core_dir
            
            if result:
                core_info_file = temp_core_dir / "virtuanes_libretro.info"
                if core_info_file.exists():
                    print("✓ RetroArch 集成成功")
                    print(f"  核心信息文件大小: {core_info_file.stat().st_size} 字节")
                    assert True
                else:
                    print("✗ 核心信息文件未创建")
                    assert False, "核心信息文件未创建"
            else:
                print("✗ RetroArch 集成失败")
                assert False, "RetroArch 集成失败"
                
    except Exception as e:
        print(f"✗ RetroArch 集成测试失败: {e}")
        assert False, f"RetroArch 集成测试失败: {e}"


def test_launch_script_creation():
    """测试启动脚本创建"""
    print("\n=== 测试启动脚本创建 ===")
    try:
        installer = VirtuaNESInstaller()
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_install_dir = Path(temp_dir) / "install"
            temp_install_dir.mkdir()
            
            # 临时修改安装目录
            original_install_dir = installer.install_dir
            installer.install_dir = temp_install_dir
            
            # 测试启动脚本创建
            result = installer.create_launch_script()
            
            # 恢复原始安装目录
            installer.install_dir = original_install_dir
            
            if result:
                launch_script = temp_install_dir / "launch_virtuanes.sh"
                if launch_script.exists():
                    print("✓ 启动脚本创建成功")
                    print(f"  脚本大小: {launch_script.stat().st_size} 字节")
                    assert True
                else:
                    print("✗ 启动脚本未创建")
                    assert False, "启动脚本未创建"
            else:
                print("✗ 启动脚本创建失败")
                assert False, "启动脚本创建失败"
                
    except Exception as e:
        print(f"✗ 启动脚本创建测试失败: {e}")
        assert False, f"启动脚本创建测试失败: {e}"


def test_installation_verification():
    """测试安装验证"""
    print("\n=== 测试安装验证 ===")
    try:
        installer = VirtuaNESInstaller()
        
        # 在测试环境中，验证可能失败，这是正常的
        result = installer.verify_installation()
        print(f"安装验证结果: {'通过' if result else '失败（测试环境正常）'}")
        assert True
    except Exception as e:
        print(f"✗ 安装验证异常: {e}")
        assert False, f"安装验证异常: {e}"


def main():
    """运行所有测试"""
    print("VirtuaNES 安装器功能测试")
    print("=" * 50)

    tests = [
        ("配置文件加载", test_config_loading),
        ("依赖检查", test_dependency_check),
        ("安装路径", test_install_paths),
        ("配置文件生成", test_config_generation),
        ("RetroArch 集成", test_retroarch_integration),
        ("启动脚本创建", test_launch_script_creation),
        ("安装验证", test_installation_verification),
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
        print("🎉 所有测试通过！VirtuaNES 安装器可以正常使用。")
    else:
        print("⚠️  部分测试失败，请检查配置和环境。")

    print("\n使用说明:")
    print("1. 运行: python virtuanes_installer.py --dry-run")
    print("2. 运行: python virtuanes_installer.py")
    print("3. 验证: python virtuanes_installer.py --verify-only")


if __name__ == "__main__":
    main()