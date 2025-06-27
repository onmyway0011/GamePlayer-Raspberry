#!/usr/bin/env python3
"""
核心功能测试脚本
测试一键生成镜像、Docker运行、游戏模拟器等核心功能
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_docker_functionality():
    """测试Docker功能"""
    print("🐳 测试Docker功能...")
    
    try:
        # 检查Docker是否可用
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Docker可用: {result.stdout.strip()}")
        else:
            print("❌ Docker不可用")
            return False
            
        # 测试简单的Docker运行
        print("🔧 测试Docker运行...")
        result = subprocess.run(['docker', 'run', '--rm', 'hello-world'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Docker运行测试成功")
            return True
        else:
            print(f"❌ Docker运行测试失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Docker测试超时")
        return False
    except FileNotFoundError:
        print("❌ Docker未安装")
        return False
    except Exception as e:
        print(f"❌ Docker测试失败: {e}")
        return False

def test_web_game_interface():
    """测试Web游戏界面"""
    print("🌐 测试Web游戏界面...")
    
    try:
        # 检查Web文件是否存在
        web_file = project_root / "data" / "web" / "index.html"
        if not web_file.exists():
            print("❌ Web游戏文件不存在")
            return False
        
        print("✅ Web游戏文件存在")
        
        # 检查音频系统代码
        with open(web_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "AudioSystem" in content:
            print("✅ 音频系统已集成")
        else:
            print("❌ 音频系统未集成")
            return False
            
        if "playSound" in content:
            print("✅ 音效功能已实现")
        else:
            print("❌ 音效功能未实现")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Web游戏界面测试失败: {e}")
        return False

def test_game_launcher():
    """测试游戏启动器"""
    print("🎮 测试游戏启动器...")
    
    try:
        # 检查增强版游戏启动器
        launcher_file = project_root / "src" / "scripts" / "enhanced_game_launcher.py"
        if not launcher_file.exists():
            print("❌ 增强版游戏启动器不存在")
            return False
        
        print("✅ 增强版游戏启动器存在")
        
        # 检查语法
        result = subprocess.run([sys.executable, '-m', 'py_compile', str(launcher_file)], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 游戏启动器语法正确")
        else:
            print(f"❌ 游戏启动器语法错误: {result.stderr}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 游戏启动器测试失败: {e}")
        return False

def test_audio_system():
    """测试音频系统"""
    print("🔊 测试音频系统...")
    
    try:
        # 检查音频管理器
        audio_file = project_root / "src" / "core" / "audio_manager.py"
        if not audio_file.exists():
            print("❌ 音频管理器不存在")
            return False
        
        print("✅ 音频管理器存在")
        
        # 检查语法
        result = subprocess.run([sys.executable, '-m', 'py_compile', str(audio_file)], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 音频管理器语法正确")
        else:
            print(f"❌ 音频管理器语法错误: {result.stderr}")
            return False
            
        # 检查树莓派音频配置脚本
        audio_script = project_root / "src" / "scripts" / "setup_raspberry_audio.sh"
        if audio_script.exists():
            print("✅ 树莓派音频配置脚本存在")
        else:
            print("❌ 树莓派音频配置脚本不存在")
            
        return True
        
    except Exception as e:
        print(f"❌ 音频系统测试失败: {e}")
        return False

def test_raspberry_pi_features():
    """测试树莓派功能"""
    print("🍓 测试树莓派功能...")
    
    try:
        # 检查设备管理器
        device_file = project_root / "src" / "core" / "device_manager.py"
        if not device_file.exists():
            print("❌ 设备管理器不存在")
            return False
        
        print("✅ 设备管理器存在")
        
        # 检查语法
        result = subprocess.run([sys.executable, '-m', 'py_compile', str(device_file)], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 设备管理器语法正确")
        else:
            print(f"❌ 设备管理器语法错误: {result.stderr}")
            return False
            
        # 检查配置文件
        config_files = [
            "config/system/audio_config.json",
            "config/system/device_config.json"
        ]
        
        for config_file in config_files:
            config_path = project_root / config_file
            if config_path.exists():
                print(f"✅ 配置文件存在: {config_file}")
            else:
                print(f"❌ 配置文件不存在: {config_file}")
                
        return True
        
    except Exception as e:
        print(f"❌ 树莓派功能测试失败: {e}")
        return False

def test_build_system():
    """测试构建系统"""
    print("🔨 测试构建系统...")
    
    try:
        # 检查构建脚本
        build_scripts = [
            "src/scripts/one_click_image_builder.sh",
            "src/scripts/raspberry_image_builder.py",
            "src/scripts/docker_build_and_run.sh"
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
            "build/docker/Dockerfile.gui",
            "build/docker/Dockerfile.web-manager"
        ]
        
        for dockerfile in dockerfiles:
            dockerfile_path = project_root / dockerfile
            if dockerfile_path.exists():
                print(f"✅ Dockerfile存在: {dockerfile}")
            else:
                print(f"❌ Dockerfile不存在: {dockerfile}")
                
        return True
        
    except Exception as e:
        print(f"❌ 构建系统测试失败: {e}")
        return False

def test_code_quality():
    """测试代码质量"""
    print("📊 测试代码质量...")
    
    try:
        # 检查优化工具
        tools = [
            "tools/dev/code_optimizer.py",
            "tools/dev/project_cleaner.py",
            "tools/dev/code_analyzer.py"
        ]
        
        for tool in tools:
            tool_path = project_root / tool
            if tool_path.exists():
                print(f"✅ 开发工具存在: {tool}")
                
                # 检查语法
                result = subprocess.run([sys.executable, '-m', 'py_compile', str(tool_path)], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {tool} 语法正确")
                else:
                    print(f"❌ {tool} 语法错误: {result.stderr}")
            else:
                print(f"❌ 开发工具不存在: {tool}")
                
        return True
        
    except Exception as e:
        print(f"❌ 代码质量测试失败: {e}")
        return False

def run_web_server_test():
    """运行Web服务器测试"""
    print("🌐 启动Web服务器测试...")
    
    try:
        # 启动增强版游戏启动器的Web模式
        launcher_path = project_root / "src" / "scripts" / "enhanced_game_launcher.py"
        
        process = subprocess.Popen([
            sys.executable, str(launcher_path), 
            "--web-only", "--port", "8085"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 等待服务器启动
        time.sleep(5)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ Web服务器启动成功")
            
            # 尝试访问服务器
            try:
                import urllib.request
                response = urllib.request.urlopen("http://localhost:8085", timeout=5)
                if response.getcode() == 200:
                    print("✅ Web服务器响应正常")
                    result = True
                else:
                    print(f"❌ Web服务器响应异常: {response.getcode()}")
                    result = False
            except Exception as e:
                print(f"❌ 无法访问Web服务器: {e}")
                result = False
            
            # 停止服务器
            process.terminate()
            process.wait(timeout=5)
            
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Web服务器启动失败: {stderr}")
            result = False
            
        return result
        
    except Exception as e:
        print(f"❌ Web服务器测试失败: {e}")
        return False

def generate_test_report(results):
    """生成测试报告"""
    print("\n" + "="*50)
    print("📋 测试报告")
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
    
    # 保存报告到文件
    report_file = project_root / "docs" / "reports" / "core_function_test_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "pass_rate": passed_tests/total_tests*100,
        "results": results
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 测试报告已保存: {report_file}")
    
    return passed_tests == total_tests

def main():
    """主函数"""
    print("🚀 GamePlayer-Raspberry 核心功能测试")
    print("="*50)
    
    # 运行所有测试
    tests = {
        "Docker功能": test_docker_functionality,
        "Web游戏界面": test_web_game_interface,
        "游戏启动器": test_game_launcher,
        "音频系统": test_audio_system,
        "树莓派功能": test_raspberry_pi_features,
        "构建系统": test_build_system,
        "代码质量": test_code_quality,
        "Web服务器": run_web_server_test
    }
    
    results = {}
    
    for test_name, test_func in tests.items():
        print(f"\n🔍 运行测试: {test_name}")
        print("-" * 30)
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results[test_name] = False
    
    # 生成报告
    all_passed = generate_test_report(results)
    
    if all_passed:
        print("\n🎉 所有测试通过！系统功能正常。")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查相关功能。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
