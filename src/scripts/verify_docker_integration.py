#!/usr/bin/env python3
"""
Docker集成验证脚本
验证所有依赖项是否正确集成到Docker镜像中
"""

import sys
import subprocess
from pathlib import Path

def check_docker_available():
    """检查Docker是否可用"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def build_docker_image(dockerfile_path, tag_name):
    """构建Docker镜像"""
    try:
        print(f"🐳 构建Docker镜像: {tag_name}")
        
        project_root = Path(__file__).parent.parent.parent
        
        cmd = [
            'docker', 'build',
            '-f', str(dockerfile_path),
            '-t', tag_name,
            str(project_root)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✅ 构建成功: {tag_name}")
            return True
        else:
            print(f"  ❌ 构建失败: {tag_name}")
            print(f"  错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ 构建异常: {e}")
        return False

def test_docker_dependencies(image_name):
    """测试Docker镜像中的依赖"""
    try:
        print(f"🔍 测试镜像依赖: {image_name}")
        
        # 核心依赖列表
        dependencies = [
            'pygame',
            'flask', 
            'requests',
            'numpy',
            'tqdm',
            'pillow',
            'pyyaml',
            'psutil'
        ]
        
        success_count = 0
        
        for dep in dependencies:
            cmd = [
                'docker', 'run', '--rm',
                image_name,
                'python3', '-c', f'import {dep}; print("✅ {dep}")'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✅ {dep}")
                success_count += 1
            else:
                print(f"  ❌ {dep} - 导入失败")
        
        print(f"  📊 依赖测试结果: {success_count}/{len(dependencies)} 通过")
        return success_count == len(dependencies)
        
    except Exception as e:
        print(f"  ❌ 测试异常: {e}")
        return False

def test_project_files(image_name):
    """测试项目文件是否存在"""
    try:
        print(f"📁 测试项目文件: {image_name}")
        
        # 核心文件列表
        core_files = [
            'src/core/rom_manager.py',
            'src/core/cheat_manager.py',
            'src/core/settings_manager.py',
            'src/scripts/enhanced_game_launcher.py',
            'data/web/index.html',
            'config/emulators/emulator_config.json'
        ]
        
        success_count = 0
        
        for file_path in core_files:
            cmd = [
                'docker', 'run', '--rm',
                image_name,
                'test', '-f', file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✅ {file_path}")
                success_count += 1
            else:
                print(f"  ❌ {file_path} - 文件不存在")
        
        print(f"  📊 文件测试结果: {success_count}/{len(core_files)} 通过")
        return success_count == len(core_files)
        
    except Exception as e:
        print(f"  ❌ 测试异常: {e}")
        return False

def test_web_server(image_name):
    """测试Web服务器启动"""
    try:
        print(f"🌐 测试Web服务器: {image_name}")
        
        # 启动容器并测试Web服务器
        cmd = [
            'docker', 'run', '--rm', '-d',
            '--name', 'gameplayer-test',
            '-p', '3003:3000',
            image_name
        ]
        
        # 启动容器
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"  ❌ 容器启动失败")
            return False
        
        container_id = result.stdout.strip()
        print(f"  🚀 容器已启动: {container_id[:12]}")
        
        # 等待服务器启动
        import time
        time.sleep(5)
        
        # 检查容器状态
        check_cmd = ['docker', 'ps', '--filter', f'id={container_id}', '--format', '{{.Status}}']
        check_result = subprocess.run(check_cmd, capture_output=True, text=True)
        
        if 'Up' in check_result.stdout:
            print(f"  ✅ 容器运行正常")
            success = True
        else:
            print(f"  ❌ 容器未正常运行")
            success = False
        
        # 停止容器
        stop_cmd = ['docker', 'stop', container_id]
        subprocess.run(stop_cmd, capture_output=True, text=True)
        
        return success
        
    except Exception as e:
        print(f"  ❌ 测试异常: {e}")
        return False

def main():
    """主函数"""
    print("🐳 GamePlayer-Raspberry Docker集成验证")
    print("=" * 60)
    
    # 检查Docker是否可用
    if not check_docker_available():
        print("❌ Docker不可用，请先安装Docker")
        return 1
    
    print("✅ Docker可用")
    
    project_root = Path(__file__).parent.parent.parent
    
    # 要测试的Docker文件
    docker_configs = [
        {
            'dockerfile': project_root / 'build/docker/Dockerfile.simple',
            'tag': 'gameplayer-simple',
            'name': '简化版镜像'
        },
        {
            'dockerfile': project_root / 'Dockerfile.raspberry',
            'tag': 'gameplayer-raspberry',
            'name': '树莓派镜像'
        }
    ]
    
    results = []
    
    for config in docker_configs:
        print(f"\n🔧 测试 {config['name']}")
        print("-" * 40)
        
        if not config['dockerfile'].exists():
            print(f"❌ Dockerfile不存在: {config['dockerfile']}")
            results.append(False)
            continue
        
        # 构建镜像
        build_success = build_docker_image(config['dockerfile'], config['tag'])
        if not build_success:
            results.append(False)
            continue
        
        # 测试依赖
        deps_success = test_docker_dependencies(config['tag'])
        
        # 测试文件
        files_success = test_project_files(config['tag'])
        
        # 测试Web服务器（仅对简化版测试）
        if config['tag'] == 'gameplayer-simple':
            web_success = test_web_server(config['tag'])
        else:
            web_success = True  # 跳过树莓派镜像的Web测试
        
        # 记录结果
        overall_success = build_success and deps_success and files_success and web_success
        results.append(overall_success)
        
        if overall_success:
            print(f"✅ {config['name']} 集成验证通过")
        else:
            print(f"❌ {config['name']} 集成验证失败")
    
    # 总结结果
    print(f"\n📊 集成验证总结:")
    print(f"  总镜像数: {len(docker_configs)}")
    print(f"  通过验证: {sum(results)}")
    print(f"  失败验证: {len(results) - sum(results)}")
    print(f"  成功率: {sum(results)/len(results)*100:.1f}%")
    
    if all(results):
        print(f"\n🎉 所有Docker镜像集成验证通过!")
        print(f"💡 所有依赖项都已正确集成到镜像中")
        return 0
    else:
        print(f"\n⚠️ 部分Docker镜像集成验证失败")
        print(f"💡 请检查失败的镜像并修复依赖问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())
