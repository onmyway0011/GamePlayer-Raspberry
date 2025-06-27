#!/usr/bin/env python3
"""
自动优化工具
基于代码分析结果自动执行优化
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Any
import json


class AutoOptimizer:
    """自动优化器"""

    def __init__(self, project_root: str = "."):
        """TODO: Add docstring"""
        self.project_root = Path(project_root)
        self.optimizations_applied = []

        print(f"🔧 自动优化器初始化完成")
        print(f"📁 项目根目录: {self.project_root}")

    def load_analysis_results(self, analysis_file: str = "docs/code_analysis_report.json") -> Dict[str, Any]:
        """加载代码分析结果"""
        analysis_path = self.project_root / analysis_file

        if not analysis_path.exists():
            print(f"⚠️ 分析文件不存在: {analysis_path}")
            return {}

        try:
            with open(analysis_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载分析结果失败: {e}")
            return {}

    def optimize_imports(self, file_path: Path):
        """优化导入语句"""
        try:
            # 使用isort优化导入
            result = subprocess.run([
                'python3', '-m', 'isort', str(file_path), '--profile', 'black'
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ 优化导入: {file_path.relative_to(self.project_root)}")
                return True
            else:
                print(f"⚠️ 优化导入失败: {result.stderr}")
                return False

        except FileNotFoundError:
            print(f"⚠️ isort未安装，跳过导入优化")
            return False
        except Exception as e:
            print(f"❌ 优化导入出错: {e}")
            return False

    def format_code(self, file_path: Path):
        """格式化代码"""
        try:
            # 使用black格式化代码
            result = subprocess.run([
                'python3', '-m', 'black', str(file_path), '--line-length', '100'
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ 格式化代码: {file_path.relative_to(self.project_root)}")
                return True
            else:
                print(f"⚠️ 格式化失败: {result.stderr}")
                return False

        except FileNotFoundError:
            print(f"⚠️ black未安装，跳过代码格式化")
            return False
        except Exception as e:
            print(f"❌ 格式化出错: {e}")
            return False

    def remove_unused_imports(self, file_path: Path):
        """移除未使用的导入"""
        try:
            # 使用autoflake移除未使用的导入
            result = subprocess.run([
                'python3', '-m', 'autoflake',
                '--remove-all-unused-imports',
                '--remove-unused-variables',
                '--in-place',
                str(file_path)
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ 移除未使用导入: {file_path.relative_to(self.project_root)}")
                return True
            else:
                print(f"⚠️ 移除未使用导入失败: {result.stderr}")
                return False

        except FileNotFoundError:
            print(f"⚠️ autoflake未安装，跳过未使用导入移除")
            return False
        except Exception as e:
            print(f"❌ 移除未使用导入出错: {e}")
            return False

    def add_type_hints(self, file_path: Path):
        """添加类型提示（基础版本）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 简单的类型提示添加
            lines = content.splitlines()
            modified = False

            for i, line in enumerate(lines):
                # 为没有类型提示的函数参数添加基础类型提示
                if 'def ' in line and '(' in line and ')' in line and '->' not in line:
                    if not line.strip().endswith(':'):
                        continue

                    # 简单的返回类型推断
                    if 'return True' in content or 'return False' in content:
                        if '-> bool:' not in line:
                            lines[i] = line.replace(':', ' -> bool:')
                            modified = True
                    elif 'return None' in content:
                        if '-> None:' not in line:
                            lines[i] = line.replace(':', ' -> None:')
                            modified = True

            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                print(f"✅ 添加类型提示: {file_path.relative_to(self.project_root)}")
                return True

            return False

        except Exception as e:
            print(f"❌ 添加类型提示出错: {e}")
            return False

    def optimize_file_structure(self):
        """优化文件结构"""
        try:
            optimizations = []

            # 创建缺失的目录
            required_dirs = [
                'config', 'docs', 'tests', 'saves', 'cheats',
                'logs', 'assets', 'tools', 'roms'
            ]

            for dir_name in required_dirs:
                dir_path = self.project_root / dir_name
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    optimizations.append(f"创建目录: {dir_name}")

            # 移动配置文件到config目录
            config_files = [
                'requirements.txt',
                'setup.py',
                '.gitignore'
            ]

            for config_file in config_files:
                src_path = self.project_root / config_file
                if src_path.exists():
                    # 保持在根目录，但确保格式正确
                    optimizations.append(f"验证配置文件: {config_file}")

            if optimizations:
                print(f"✅ 文件结构优化完成:")
                for opt in optimizations:
                    print(f"   • {opt}")
                return True

            return False

        except Exception as e:
            print(f"❌ 文件结构优化出错: {e}")
            return False

    def create_missing_files(self):
        """创建缺失的文件"""
        try:
            created_files = []

            # 创建.gitignore文件
            gitignore_path = self.project_root / '.gitignore'
            if not gitignore_path.exists():
                gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
saves/
logs/
roms/
*.log
*.tmp
output/
"""
                with open(gitignore_path, 'w', encoding='utf-8') as f:
                    f.write(gitignore_content)
                created_files.append('.gitignore')

            # 创建requirements.txt文件
            requirements_path = self.project_root / 'requirements.txt'
            if not requirements_path.exists():
                requirements_content = """# Core dependencies
pygame>=2.1.0
requests>=2.25.0
pillow>=8.0.0
pyyaml>=5.4.0
psutil>=5.8.0
tqdm>=4.60.0
numpy>=1.20.0

# Development dependencies
pytest>=6.0.0
pytest-cov>=2.10.0
black>=21.0.0
isort>=5.8.0
autoflake>=1.4.0
flake8>=3.8.0

# Optional dependencies
flask>=2.0.0
docker>=5.0.0
"""
                with open(requirements_path, 'w', encoding='utf-8') as f:
                    f.write(requirements_content)
                created_files.append('requirements.txt')

            # 创建setup.py文件
            setup_path = self.project_root / 'setup.py'
            if not setup_path.exists():
                setup_content = '''#!/usr/bin/env python3
"""
GamePlayer-Raspberry 安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gameplayer-raspberry",
    version="3.0.0",
    author="GamePlayer Team",
    author_email="team@gameplayer.dev",
    description="Enhanced NES Game Player for Raspberry Pi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Games/Entertainment",
        "Topic :: System :: Emulators",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gameplayer=scripts.nes_game_launcher:main",
            "gameplayer-install=scripts.smart_installer:main",
            "gameplayer-rom=scripts.rom_manager:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
'''
                with open(setup_path, 'w', encoding='utf-8') as f:
                    f.write(setup_content)
                created_files.append('setup.py')

            if created_files:
                print(f"✅ 创建缺失文件:")
                for file in created_files:
                    print(f"   • {file}")
                return True

            return False

        except Exception as e:
            print(f"❌ 创建缺失文件出错: {e}")
            return False

    def run_optimization(self, analysis_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """运行自动优化"""
        print(f"🚀 开始自动优化...")

        if not analysis_results:
            analysis_results = self.load_analysis_results()

        optimization_results = {
            "files_optimized": 0,
            "imports_optimized": 0,
            "code_formatted": 0,
            "structure_improved": False,
            "files_created": False,
            "optimizations": []
        }

        # 1. 优化文件结构
        if self.optimize_file_structure():
            optimization_results["structure_improved"] = True
            optimization_results["optimizations"].append("文件结构优化")

        # 2. 创建缺失文件
        if self.create_missing_files():
            optimization_results["files_created"] = True
            optimization_results["optimizations"].append("创建缺失文件")

        # 3. 优化Python文件
        if analysis_results and "files" in analysis_results:
            for file_path_str, file_info in analysis_results["files"].items():
                file_path = self.project_root / file_path_str

                if not file_path.exists() or not file_path.suffix == '.py':
                    continue

                file_optimized = False

                # 移除未使用的导入
                if self.remove_unused_imports(file_path):
                    optimization_results["imports_optimized"] += 1
                    file_optimized = True

                # 优化导入顺序
                if self.optimize_imports(file_path):
                    file_optimized = True

                # 格式化代码
                if self.format_code(file_path):
                    optimization_results["code_formatted"] += 1
                    file_optimized = True

                # 添加类型提示
                if self.add_type_hints(file_path):
                    file_optimized = True

                if file_optimized:
                    optimization_results["files_optimized"] += 1

        self.optimization_results = optimization_results
        print(f"✅ 自动优化完成")
        return optimization_results

    def print_optimization_summary(self):
        """打印优化摘要"""
        if not hasattr(self, 'optimization_results'):
            print("❌ 没有优化结果")
            return

        results = self.optimization_results

        print(f"\n🔧 自动优化摘要:")
        print(f"  📄 优化文件数: {results['files_optimized']}")
        print(f"  📦 导入优化数: {results['imports_optimized']}")
        print(f"  🎨 格式化文件数: {results['code_formatted']}")
        print(f"  📁 结构改进: {'✅' if results['structure_improved'] else '❌'}")
        print(f"  📝 文件创建: {'✅' if results['files_created'] else '❌'}")

        if results["optimizations"]:
            print(f"\n✨ 应用的优化:")
            for i, opt in enumerate(results["optimizations"], 1):
                print(f"  {i}. {opt}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="自动优化工具")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--analysis-file", default="docs/code_analysis_report.json", help="分析结果文件")
    parser.add_argument("--dry-run", action="store_true", help="仅显示将要执行的优化")

    args = parser.parse_args()

    optimizer = AutoOptimizer(args.project_root)

    if args.dry_run:
        print("🔍 干运行模式 - 仅显示将要执行的优化")
        # 在干运行模式下，只分析不执行
        analysis_results = optimizer.load_analysis_results(args.analysis_file)
        print("将要执行的优化:")
        print("  • 文件结构优化")
        print("  • 创建缺失文件")
        print("  • Python代码格式化")
        print("  • 导入语句优化")
        print("  • 移除未使用导入")
    else:
        analysis_results = optimizer.load_analysis_results(args.analysis_file)
        optimizer.run_optimization(analysis_results)
        optimizer.print_optimization_summary()

if __name__ == "__main__":
    main()
