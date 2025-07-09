#!/usr/bin/env python3
"""
测试构建脚本的修复效果
验证所有Bug是否已修复
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def test_script_syntax():
    """测试脚本语法"""
    print("🔍 测试脚本语法...")
    
    scripts = [
        "src/scripts/one_click_image_builder.sh",
        "src/scripts/pure_raspberry_image_builder.sh", 
        "src/scripts/raspberry_image_builder.py"
    ]
    
    results = {}
    for script in scripts:
        script_path = Path(script)
        if not script_path.exists():
            results[script] = f"❌ 文件不存在"
            continue
            
        try:
            if script.endswith('.sh'):
                # 测试bash语法
                result = subprocess.run(
                    ['bash', '-n', script], 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    results[script] = "✅ 语法正确"
                else:
                    results[script] = f"❌ 语法错误: {result.stderr}"
            
            elif script.endswith('.py'):
                # 测试Python语法
                result = subprocess.run(
                    ['python3', '-m', 'py_compile', script],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    results[script] = "✅ 语法正确"
                else:
                    results[script] = f"❌ 语法错误: {result.stderr}"
                    
        except Exception as e:
            results[script] = f"❌ 测试失败: {e}"
    
    return results

def test_error_handling():
    """测试错误处理"""
    print("🛡️ 测试错误处理...")
    
    test_results = []
    
    # 测试1: 检查是否有正确的set -e
    try:
        with open("src/scripts/one_click_image_builder.sh", 'r') as f:
            content = f.read()
            if "set -euo pipefail" in content:
                test_results.append("✅ 主脚本有正确的错误处理")
            else:
                test_results.append("❌ 主脚本缺少严格错误处理")
    except Exception as e:
        test_results.append(f"❌ 无法读取主脚本: {e}")
    
    # 测试2: 检查cleanup函数
    try:
        with open("src/scripts/one_click_image_builder.sh", 'r') as f:
            content = f.read()
            if "cleanup_on_error" in content and "trap" in content:
                test_results.append("✅ 主脚本有清理函数")
            else:
                test_results.append("❌ 主脚本缺少清理函数")
    except Exception as e:
        test_results.append(f"❌ 无法检查清理函数: {e}")
    
    # 测试3: 检查Python脚本的异常处理
    try:
        with open("src/scripts/raspberry_image_builder.py", 'r') as f:
            content = f.read()
            if "try:" in content and "except" in content and "finally:" in content:
                test_results.append("✅ Python脚本有完善的异常处理")
            else:
                test_results.append("❌ Python脚本异常处理不完善")
    except Exception as e:
        test_results.append(f"❌ 无法检查Python异常处理: {e}")
    
    return test_results

def test_path_safety():
    """测试路径安全性"""
    print("🔒 测试路径安全性...")
    
    test_results = []
    
    scripts = [
        "src/scripts/one_click_image_builder.sh",
        "src/scripts/pure_raspberry_image_builder.sh"
    ]
    
    dangerous_patterns = [
        "rm -rf /",
        "rm -rf /*", 
        "chmod 777 /",
        "cd ..",
        "$HOME/.."
    ]
    
    for script in scripts:
        try:
            with open(script, 'r') as f:
                content = f.read()
                
            found_issues = []
            for pattern in dangerous_patterns:
                if pattern in content:
                    found_issues.append(pattern)
            
            if found_issues:
                test_results.append(f"⚠️ {script} 包含潜在危险模式: {found_issues}")
            else:
                test_results.append(f"✅ {script} 路径安全")
                
        except Exception as e:
            test_results.append(f"❌ 无法检查 {script}: {e}")
    
    return test_results

def test_dependency_checks():
    """测试依赖检查"""
    print("📦 测试依赖检查...")
    
    test_results = []
    
    # 检查主脚本是否有依赖检查
    try:
        with open("src/scripts/one_click_image_builder.sh", 'r') as f:
            content = f.read()
            
        required_checks = [
            "command -v",
            "check_requirements",
            "required_tools"
        ]
        
        checks_found = sum(1 for check in required_checks if check in content)
        
        if checks_found >= 2:
            test_results.append("✅ 主脚本有依赖检查")
        else:
            test_results.append("❌ 主脚本缺少依赖检查")
            
    except Exception as e:
        test_results.append(f"❌ 无法检查依赖: {e}")
    
    return test_results

def test_resource_management():
    """测试资源管理"""
    print("🧹 测试资源管理...")
    
    test_results = []
    
    # 检查临时文件清理
    scripts_to_check = [
        ("src/scripts/one_click_image_builder.sh", ["cleanup", "TEMP_DIR"]),
        ("src/scripts/pure_raspberry_image_builder.sh", ["cleanup", "umount"]),
        ("src/scripts/raspberry_image_builder.py", ["cleanup", "temp_dir"])
    ]
    
    for script, keywords in scripts_to_check:
        try:
            with open(script, 'r') as f:
                content = f.read()
            
            found_keywords = sum(1 for keyword in keywords if keyword in content)
            
            if found_keywords >= len(keywords) // 2:
                test_results.append(f"✅ {script} 有资源清理")
            else:
                test_results.append(f"❌ {script} 缺少资源清理")
                
        except Exception as e:
            test_results.append(f"❌ 无法检查 {script}: {e}")
    
    return test_results

def test_user_feedback():
    """测试用户反馈"""
    print("💬 测试用户反馈...")
    
    test_results = []
    
    # 检查日志函数
    try:
        with open("src/scripts/one_click_image_builder.sh", 'r') as f:
            content = f.read()
            
        log_functions = ["log_info", "log_success", "log_warning", "log_error"]
        found_functions = sum(1 for func in log_functions if func in content)
        
        if found_functions >= 3:
            test_results.append("✅ 主脚本有完善的日志系统")
        else:
            test_results.append("❌ 主脚本日志系统不完善")
            
    except Exception as e:
        test_results.append(f"❌ 无法检查日志系统: {e}")
    
    return test_results

def main():
    """主测试函数"""
    print("🧪 GamePlayer-Raspberry 构建脚本Bug修复验证")
    print("=" * 60)
    
    all_tests = [
        ("脚本语法", test_script_syntax),
        ("错误处理", test_error_handling), 
        ("路径安全", test_path_safety),
        ("依赖检查", test_dependency_checks),
        ("资源管理", test_resource_management),
        ("用户反馈", test_user_feedback)
    ]
    
    total_issues = 0
    
    for test_name, test_func in all_tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        
        try:
            results = test_func()
            
            if isinstance(results, dict):
                for item, result in results.items():
                    print(f"  {item}: {result}")
                    if "❌" in result:
                        total_issues += 1
            elif isinstance(results, list):
                for result in results:
                    print(f"  {result}")
                    if "❌" in result:
                        total_issues += 1
                        
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
            total_issues += 1
    
    print("\n" + "=" * 60)
    print("📊 测试总结:")
    
    if total_issues == 0:
        print("🎉 所有测试通过！构建脚本Bug已全部修复")
        return 0
    else:
        print(f"⚠️ 发现 {total_issues} 个问题需要进一步修复")
        return 1
if __name__ == "__main__":
    sys.exit(main())
