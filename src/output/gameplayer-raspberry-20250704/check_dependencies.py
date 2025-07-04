#!/usr/bin/env python3
"""
依赖项检查脚本
分析项目中所有实际使用的依赖项，确保它们都已正确集成到镜像中
"""

import ast
import sys
import json
import subprocess
from pathlib import Path
from typing import Set, Dict, List
from collections import defaultdict

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class DependencyChecker:
    """依赖项检查器"""

    def __init__(self):
        """TODO: 添加文档字符串"""
        self.project_root = project_root
        self.third_party_imports = set()
        self.standard_library = {
            'os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'subprocess',
            'threading', 'multiprocessing', 'collections', 'itertools',
            'functools', 'operator', 're', 'math', 'random', 'hashlib',
            'urllib', 'http', 'socket', 'ssl', 'email', 'html', 'xml',
            'sqlite3', 'pickle', 'csv', 'configparser', 'logging',
            'unittest', 'argparse', 'shutil', 'tempfile', 'glob', 'ast',
            'typing', 'dataclasses', 'enum', 'abc', 'copy', 'weakref'
        }

    def find_python_files(self) -> List[Path]:
        """查找所有Python文件"""
        python_files = []

        # 扫描源码目录
        for pattern in ["src/**/*.py", "tools/**/*.py", "tests/**/*.py"]:
            python_files.extend(self.project_root.glob(pattern))

        # 添加根目录的Python文件
        python_files.extend(self.project_root.glob("*.py"))

        return python_files

    def extract_imports_from_file(self, file_path: Path) -> Set[str]:
        """从文件中提取导入的模块"""
        imports = set()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split('.')[0]
                        imports.add(module_name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module.split('.')[0]
                        imports.add(module_name)

        except Exception as e:
            print(f"⚠️ 解析文件失败 {file_path}: {e}")

        return imports

    def is_third_party(self, module_name: str):
        """判断是否为第三方库"""
        if module_name in self.standard_library:
            return False

        # 本地模块
        if module_name in ['src', 'tools', 'tests', 'config']:
            return False

        return True

    def analyze_all_imports(self) -> Dict[str, Set[str]]:
        """分析所有文件的导入"""
        print("🔍 分析项目中的所有导入...")

        python_files = self.find_python_files()
        file_imports = {}
        all_third_party = set()

        for file_path in python_files:
            imports = self.extract_imports_from_file(file_path)
            third_party = {imp for imp in imports if self.is_third_party(imp)}

            if third_party:
                file_imports[str(file_path.relative_to(self.project_root))] = third_party
                all_third_party.update(third_party)

        self.third_party_imports = all_third_party
        return file_imports

    def load_requirements_files(self) -> Dict[str, Set[str]]:
        """加载所有requirements文件"""
        requirements = {}

        # 主requirements.txt
        main_req = self.project_root / "requirements.txt"
        if main_req.exists():
            requirements["main"] = self.parse_requirements_file(main_req)

        # config/requirements.txt
        config_req = self.project_root / "config" / "requirements.txt"
        if config_req.exists():
            requirements["config"] = self.parse_requirements_file(config_req)

        return requirements

    def parse_requirements_file(self, file_path: Path) -> Set[str]:
        """解析requirements文件"""
        packages = set()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 提取包名（去除版本号）
                        package = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0]
                        package = package.replace('_', '-').lower()
                        packages.add(package)

        except Exception as e:
            print(f"⚠️ 解析requirements文件失败 {file_path}: {e}")

        return packages

    def check_installed_packages(self) -> Set[str]:
        """检查已安装的包"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list'],
                                  capture_output=True, text=True)

            installed = set()
            for line in result.stdout.split('\n')[2:]:  # 跳过头部
                if line.strip():
                    package = line.split()[0].lower()
                    installed.add(package)

            return installed

        except Exception as e:
            print(f"⚠️ 检查已安装包失败: {e}")
            return set()

    def map_import_to_package(self, import_name: str) -> str:
        """将导入名映射到包名"""
        # 常见的导入名到包名的映射
        mapping = {
            'cv2': 'opencv-python',
            'PIL': 'pillow',
            'yaml': 'pyyaml',
            'sklearn': 'scikit-learn',
            'skimage': 'scikit-image',
            'bs4': 'beautifulsoup4',
            'dateutil': 'python-dateutil',
            'dotenv': 'python-dotenv',
            'jose': 'python-jose',
            'multipart': 'python-multipart',
            'serial': 'pyserial',
            'can': 'python-can',
            'objc': 'pyobjc-core'
        }

        return mapping.get(import_name, import_name.replace('_', '-').lower())

    def generate_report(self) -> Dict:
        """生成依赖检查报告"""
        print("📊 生成依赖检查报告...")

        # 分析导入
        file_imports = self.analyze_all_imports()

        # 加载requirements文件
        requirements_files = self.load_requirements_files()

        # 检查已安装的包
        installed_packages = self.check_installed_packages()

        # 过滤掉本地模块和标准库模块
        actual_third_party = set()
        for import_name in self.third_party_imports:
            # 过滤掉明显的本地模块
            if import_name in ['cheat_manager', 'device_manager', 'save_manager', 'rom_downloader', 'logger_config']:
                continue
            # 过滤掉标准库模块
            if import_name in ['gzip', 'signal', 'socketserver', 'struct', 'tarfile', 'wave', 'webbrowser', 'zipfile', 'platform', 'concurrent']:
                continue
            actual_third_party.add(import_name)

        # 映射导入名到包名
        required_packages = set()
        for import_name in actual_third_party:
            package_name = self.map_import_to_package(import_name)
            required_packages.add(package_name)

        # 合并所有requirements文件中的包
        all_requirements = set()
        for req_set in requirements_files.values():
            all_requirements.update(req_set)

        # 分析结果
        missing_packages = required_packages - installed_packages
        unused_packages = all_requirements - required_packages

        report = {
            "summary": {
                "total_python_files": len(self.find_python_files()),
                "total_third_party_imports": len(self.third_party_imports),
                "total_required_packages": len(required_packages),
                "total_requirements": len(all_requirements),
                "total_installed": len(installed_packages),
                "missing_packages": len(missing_packages),
                "unused_packages": len(unused_packages)
            },
            "third_party_imports": sorted(list(self.third_party_imports)),
            "required_packages": sorted(list(required_packages)),
            "requirements_files": {k: sorted(list(v)) for k, v in requirements_files.items()},
            "installed_packages": sorted(list(installed_packages)),
            "missing_packages": sorted(list(missing_packages)),
            "unused_packages": sorted(list(unused_packages)),
            "file_imports": {k: sorted(list(v)) for k, v in file_imports.items()}
        }

        return report

    def print_report(self, report: Dict):
        """打印报告"""
        print("\n" + "="*60)
        print("🔍 GamePlayer-Raspberry 依赖检查报告")
        print("="*60)

        summary = report["summary"]
        print(f"\n📊 统计信息:")
        print(f"  Python文件数量: {summary['total_python_files']}")
        print(f"  第三方导入数量: {summary['total_third_party_imports']}")
        print(f"  需要的包数量: {summary['total_required_packages']}")
        print(f"  requirements中的包: {summary['total_requirements']}")
        print(f"  已安装的包: {summary['total_installed']}")
        print(f"  缺失的包: {summary['missing_packages']}")
        print(f"  未使用的包: {summary['unused_packages']}")

        print(f"\n🎯 实际使用的第三方库:")
        for imp in report["third_party_imports"]:
            print(f"  📦 {imp}")

        if report["missing_packages"]:
            print(f"\n❌ 缺失的包 ({len(report['missing_packages'])}):")
            for pkg in report["missing_packages"]:
                print(f"  ⚠️ {pkg}")
        else:
            print(f"\n✅ 所有需要的包都已安装!")

        if report["unused_packages"]:
            print(f"\n📦 requirements中未使用的包 ({len(report['unused_packages'])}):")
            for pkg in report["unused_packages"]:
                print(f"  📋 {pkg}")

        # 检查Docker文件
        self.check_docker_files(report)

    def check_docker_files(self, report: Dict):
        """检查Docker文件中的依赖"""
        print(f"\n🐳 Docker文件依赖检查:")

        docker_files = [
            "build/docker/Dockerfile.simple",
            "build/docker/Dockerfile.raspberry-sim",
            "Dockerfile.raspberry"
        ]

        for docker_file in docker_files:
            docker_path = self.project_root / docker_file
            if docker_path.exists():
                print(f"  📄 检查 {docker_file}:")
                self.analyze_dockerfile(docker_path, report["required_packages"])

    def analyze_dockerfile(self, dockerfile_path: Path, required_packages: Set[str]):
        """分析Dockerfile中的包安装"""
        try:
            with open(dockerfile_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找pip install命令
            pip_packages = set()
            for line in content.split('\n'):
                if 'pip install' in line or 'pip3 install' in line:
                    # 提取包名
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part in ['install', 'install']:
                            for pkg in parts[i+1:]:
                                if not pkg.startswith('-'):
                                    clean_pkg = pkg.strip('\\').strip()
                                    if clean_pkg and not clean_pkg.startswith('#'):
                                        pip_packages.add(clean_pkg.lower())

            # 检查覆盖情况
            covered = pip_packages.intersection(required_packages)
            missing = set(required_packages) - set(pip_packages)

            print(f"    📦 Docker中安装的包: {len(pip_packages)}")
            print(f"    ✅ 覆盖的必需包: {len(covered)}")
            print(f"    ❌ 缺失的必需包: {len(missing)}")

            if missing:
                print(f"    缺失包列表: {', '.join(sorted(missing))}")

        except Exception as e:
            print(f"    ⚠️ 分析失败: {e}")


def main():
    """主函数"""
    print("🔍 GamePlayer-Raspberry 依赖项检查")
    print("="*50)

    checker = DependencyChecker()
    report = checker.generate_report()
    checker.print_report(report)

    # 保存报告
    report_file = project_root / "docs" / "dependency_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n💾 详细报告已保存到: {report_file}")

    # 返回状态码
    if report["summary"]["missing_packages"] > 0:
        print("\n⚠️ 发现缺失的依赖包，请检查并安装")
        return 1
    else:
        print("\n🎉 所有依赖项检查通过!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
