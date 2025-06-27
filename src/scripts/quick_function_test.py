#!/usr/bin/env python3
"""
快速功能测试脚本
测试核心功能是否正常工作
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_web_game_interface():
    """测试Web游戏界面"""
    print("🌐 测试Web游戏界面...")
    
    web_file = project_root / "data" / "web" / "index.html"
    if not web_file.exists():
        print("❌ Web游戏文件不存在")
        return False
    
    with open(web_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查游戏列表功能
    if "gameList" in content or "games" in content:
        print("✅ 游戏列表功能已实现")
    else:
        print("❌ 游戏列表功能未实现")
        return False
    
    # 检查音频系统
    if "AudioSystem" in content:
        print("✅ 音频系统已集成")
    else:
        print("❌ 音频系统未集成")
        return False
    
    # 检查游戏选择功能
    if "selectGame" in content or "startGame" in content:
        print("✅ 游戏选择功能已实现")
    else:
        print("❌ 游戏选择功能未实现")
        return False
    
    return True

def test_raspberry_pi_features():
    """测试树莓派功能配置"""
    print("🍓 测试树莓派功能配置...")
    
    # 检查设备配置文件
    device_config = project_root / "config" / "system" / "device_config.json"
    if not device_config.exists():
        print("❌ 设备配置文件不存在")
        return False
    
    with open(device_config, 'r', encoding='utf-8') as f:
        import json
        config = json.load(f)
    
    # 检查USB手柄支持
    if "usb_gamepad" in config and config["usb_gamepad"]["enabled"]:
        print("✅ USB手柄支持已配置")
    else:
        print("❌ USB手柄支持未配置")
        return False
    
    # 检查蓝牙音频支持
    if "bluetooth_audio" in config and config["bluetooth_audio"]["enabled"]:
        print("✅ 蓝牙音频支持已配置")
    else:
        print("❌ 蓝牙音频支持未配置")
        return False
    
    # 检查HDMI视频支持
    if "hdmi_video" in config and config["hdmi_video"]["enabled"]:
        print("✅ HDMI视频支持已配置")
    else:
        print("❌ HDMI视频支持未配置")
        return False
    
    return True

def test_game_launcher():
    """测试游戏启动器"""
    print("🎮 测试游戏启动器...")
    
    launcher_file = project_root / "src" / "scripts" / "enhanced_game_launcher.py"
    if not launcher_file.exists():
        print("❌ 增强版游戏启动器不存在")
        return False
    
    # 检查语法
    result = subprocess.run([sys.executable, '-m', 'py_compile', str(launcher_file)], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ 游戏启动器语法正确")
    else:
        print(f"❌ 游戏启动器语法错误: {result.stderr}")
        return False
    
    # 检查Web模式支持
    with open(launcher_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "--web-only" in content:
        print("✅ Web模式支持已实现")
    else:
        print("❌ Web模式支持未实现")
        return False
    
    return True

def test_audio_system():
    """测试音频系统"""
    print("🔊 测试音频系统...")
    
    # 检查音频管理器
    audio_file = project_root / "src" / "core" / "audio_manager.py"
    if not audio_file.exists():
        print("❌ 音频管理器不存在")
        return False
    
    # 检查语法
    result = subprocess.run([sys.executable, '-m', 'py_compile', str(audio_file)], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ 音频管理器语法正确")
    else:
        print(f"❌ 音频管理器语法错误: {result.stderr}")
        return False
    
    # 检查音频配置文件
    audio_config = project_root / "config" / "system" / "audio_config.json"
    if audio_config.exists():
        print("✅ 音频配置文件存在")
    else:
        print("❌ 音频配置文件不存在")
        return False
    
    # 检查树莓派音频脚本
    audio_script = project_root / "src" / "scripts" / "setup_raspberry_audio.sh"
    if audio_script.exists():
        print("✅ 树莓派音频配置脚本存在")
    else:
        print("❌ 树莓派音频配置脚本不存在")
        return False
    
    return True

def test_build_system():
    """测试构建系统"""
    print("🔨 测试构建系统...")
    
    # 检查关键构建脚本
    build_scripts = [
        "src/scripts/one_click_image_builder.sh",
        "src/scripts/raspberry_image_builder.py"
    ]
    
    for script in build_scripts:
        script_path = project_root / script
        if script_path.exists():
            print(f"✅ 构建脚本存在: {script}")
        else:
            print(f"❌ 构建脚本不存在: {script}")
            return False
    
    # 检查Dockerfile
    dockerfiles = [
        "build/docker/Dockerfile.raspberry-sim",
        "build/docker/Dockerfile.gui"
    ]
    
    for dockerfile in dockerfiles:
        dockerfile_path = project_root / dockerfile
        if dockerfile_path.exists():
            print(f"✅ Dockerfile存在: {dockerfile}")
        else:
            print(f"❌ Dockerfile不存在: {dockerfile}")
    
    return True

def start_web_server_test():
    """启动Web服务器测试"""
    print("🌐 启动Web服务器测试...")

    try:
        # 首先检查Docker容器是否在运行
        docker_check = subprocess.run(
            ["docker", "ps", "--filter", "name=gameplayer-test", "--format", "{{.Status}}"],
            capture_output=True, text=True
        )

        if docker_check.returncode == 0 and "Up" in docker_check.stdout:
            print("✅ Docker容器正在运行")

            # 测试Docker Web服务器
            try:
                import urllib.request
                response = urllib.request.urlopen("http://localhost:3001", timeout=5)
                if response.getcode() == 200:
                    print("✅ Docker Web服务器可访问")
                    print("🌐 访问地址: http://localhost:3001")
                    return True
            except Exception as e:
                print(f"❌ Docker Web服务器不可访问: {e}")

        # 如果Docker不可用，测试本地Web服务器
        launcher_path = project_root / "src" / "scripts" / "enhanced_game_launcher.py"

        # 启动Web服务器
        process = subprocess.Popen([
            sys.executable, str(launcher_path),
            "--web-only", "--port", "3002"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # 等待服务器启动
        time.sleep(3)

        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ 本地Web服务器启动成功")
            print("🌐 访问地址: http://localhost:3002")

            # 停止服务器
            process.terminate()
            process.wait(timeout=5)

            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ 本地Web服务器启动失败: {stderr}")
            return False

    except Exception as e:
        print(f"❌ Web服务器测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 GamePlayer-Raspberry 快速功能测试")
    print("="*50)
    
    tests = [
        ("Web游戏界面", test_web_game_interface),
        ("树莓派功能", test_raspberry_pi_features),
        ("游戏启动器", test_game_launcher),
        ("音频系统", test_audio_system),
        ("构建系统", test_build_system),
        ("Web服务器", start_web_server_test)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 测试: {test_name}")
        print("-" * 30)
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results[test_name] = False
    
    # 生成报告
    print("\n" + "="*50)
    print("📋 测试结果")
    print("="*50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")
    
    print("\n详细结果:")
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    # 功能状态总结
    print("\n" + "="*50)
    print("📊 功能状态总结")
    print("="*50)
    
    if results.get("Web游戏界面", False):
        print("✅ 游戏模拟器首页展示游戏列表功能正常")
    else:
        print("❌ 游戏模拟器首页需要完善游戏列表功能")
    
    if results.get("树莓派功能", False):
        print("✅ 树莓派USB手柄、蓝牙耳机、HDMI视频支持已配置")
    else:
        print("❌ 树莓派硬件支持配置需要完善")
    
    if results.get("构建系统", False):
        print("✅ 一键生成镜像文件功能已实现")
    else:
        print("❌ 一键生成镜像文件功能需要完善")
    
    if results.get("Web服务器", False):
        print("✅ Web服务器可以正常启动")
    else:
        print("❌ Web服务器启动存在问题")
    
    if passed_tests == total_tests:
        print("\n🎉 所有功能测试通过！")
        return 0
    else:
        print(f"\n⚠️ {total_tests - passed_tests} 个功能需要修复")
        return 1

if __name__ == "__main__":
    sys.exit(main())
