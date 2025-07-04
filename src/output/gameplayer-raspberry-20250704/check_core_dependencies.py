#!/usr/bin/env python3
"""
核心依赖检查脚本
检查GamePlayer-Raspberry项目的核心依赖是否已正确安装
"""

import sys
import subprocess
from pathlib import Path


def check_package_installed(package_name):
    """检查包是否已安装"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False


def check_pip_package(package_name):
    """通过pip检查包是否已安装"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'show', package_name],
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False


def main():
    """主函数"""
    print("🔍 GamePlayer-Raspberry 核心依赖检查")
    print("=" * 50)

    # 定义核心依赖
    core_dependencies = {
        # Web框架
        'flask': 'Flask',

        # 游戏开发
        'pygame': 'Pygame',

        # HTTP请求
        'requests': 'Requests',

        # 数据处理
        'numpy': 'NumPy',

        # 进度条
        'tqdm': 'tqdm',

        # AWS SDK (可选)
        'boto3': 'Boto3',
        'botocore': 'Botocore',

        # SSH连接 (可选)
        'paramiko': 'Paramiko',

        # 绘图 (可选)
        'matplotlib': 'Matplotlib',

        # 测试框架
        'pytest': 'Pytest',

        # URL解析
        'urllib3': 'urllib3'
    }

    # 检查依赖
    installed = []
    missing = []

    print("📦 检查核心依赖包:")

    for package, display_name in core_dependencies.items():
        if check_package_installed(package) or check_pip_package(package):
            print(f"  ✅ {display_name} ({package})")
            installed.append(package)
        else:
            print(f"  ❌ {display_name} ({package}) - 未安装")
            missing.append(package)

    # 检查requirements.txt文件
    print(f"\n📄 检查requirements文件:")

    project_root = Path(__file__).parent.parent.parent
    requirements_files = [
        project_root / "requirements.txt",
        project_root / "config" / "requirements.txt"
    ]

    for req_file in requirements_files:
        if req_file.exists():
            print(f"  ✅ {req_file.relative_to(project_root)} 存在")
        else:
            print(f"  ❌ {req_file.relative_to(project_root)} 不存在")

    # 检查Docker文件
    print(f"\n🐳 检查Docker文件:")

    docker_files = [
        project_root / "build" / "docker" / "Dockerfile.simple",
        project_root / "build" / "docker" / "Dockerfile.raspberry-sim",
        project_root / "Dockerfile.raspberry"
    ]

    for docker_file in docker_files:
        if docker_file.exists():
            print(f"  ✅ {docker_file.relative_to(project_root)} 存在")

            # 检查是否包含pip install
            try:
                with open(docker_file, 'r') as f:
                    content = f.read()
                    if 'pip install' in content or 'pip3 install' in content:
                        print(f"    📦 包含pip安装命令")
                    else:
                        print(f"    ⚠️ 未找到pip安装命令")
            except:
                print(f"    ⚠️ 无法读取文件")
        else:
            print(f"  ❌ {docker_file.relative_to(project_root)} 不存在")

    # 检查项目核心文件
    print(f"\n📁 检查项目核心文件:")

    core_files = [
        "src/core/rom_manager.py",
        "src/core/cheat_manager.py",
        "src/core/settings_manager.py",
        "src/scripts/enhanced_game_launcher.py",
        "src/scripts/download_roms.py",
        "data/web/index.html",
        "config/emulators/emulator_config.json"
    ]

    for core_file in core_files:
        file_path = project_root / core_file
        if file_path.exists():
            print(f"  ✅ {core_file}")
        else:
            print(f"  ❌ {core_file} - 缺失")

    # 生成安装命令
    if missing:
        print(f"\n📦 缺失依赖安装命令:")
        print(f"pip install {' '.join(missing)}")

    # 统计结果
    print(f"\n📊 检查结果:")
    print(f"  总依赖数: {len(core_dependencies)}")
    print(f"  已安装: {len(installed)}")
    print(f"  缺失: {len(missing)}")
    print(f"  安装率: {len(installed)/len(core_dependencies)*100:.1f}%")

    if missing:
        print(f"\n⚠️ 发现 {len(missing)} 个缺失的核心依赖")
        print("建议运行以下命令安装:")
        print(f"pip install {' '.join(missing)}")
        return 1
    else:
        print(f"\n🎉 所有核心依赖都已正确安装!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
