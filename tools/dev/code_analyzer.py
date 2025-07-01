#!/usr/bin/env python3
"""
代码分析和优化工具
自动分析代码质量并提供优化建议
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any

# 依赖检测
def check_dependencies():
    """检查必要的依赖"""
    required_modules = ['ast', 'json']
    missing_deps = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_deps.append(module)
    
    if missing_deps:
        print(f"❌ 缺失必要的标准库模块: {', '.join(missing_deps)}")
        print("这些是Python标准库模块，通常应该可用")
        sys.exit(1)

# 检查依赖
check_dependencies()

# 现在可以安全导入
import ast
import json


class CodeAnalyzer:
    """代码分析器"""

    def __init__(self, project_root: str = "."):
        """TODO: Add docstring"""
        self.project_root = Path(project_root)
        self.python_files = []
        self.analysis_results = {}

        print(f"🔍 代码分析器初始化完成")
        print(f"📁 项目根目录: {self.project_root}")

    def scan_python_files(self) -> List[Path]:
        """扫描Python文件"""
        python_files = []

        # 扫描核心目录
        for pattern in ["**/*.py"]:
            python_files.extend(self.project_root.glob(pattern))

        # 过滤掉不需要分析的文件
        excluded_patterns = [
            "__pycache__",
            ".git",
            "venv",
            "env",
            ".pytest_cache",
            "build",
            "dist"
        ]

        filtered_files = []
        for file_path in python_files:
            if not any(pattern in str(file_path) for pattern in excluded_patterns):
                filtered_files.append(file_path)

        self.python_files = filtered_files
        print(f"📄 找到 {len(self.python_files)} 个Python文件")
        return self.python_files

    def analyze_file_complexity(self, file_path: Path) -> Dict[str, Any]:
        """分析文件复杂度"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # 统计信息
            stats = {
                "lines_of_code": len(content.splitlines()),
                "functions": 0,
                "classes": 0,
                "imports": 0,
                "complexity_score": 0,
                "max_function_length": 0,
                "max_class_length": 0
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    stats["functions"] += 1
                    func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    stats["max_function_length"] = max(stats["max_function_length"], func_lines)

                elif isinstance(node, ast.ClassDef):
                    stats["classes"] += 1
                    class_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    stats["max_class_length"] = max(stats["max_class_length"], class_lines)

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    stats["imports"] += 1

                elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                    stats["complexity_score"] += 1

            return stats

        except Exception as e:
            print(f"⚠️ 分析文件失败 {file_path}: {e}")
            return {}

    def check_code_style(self, file_path: Path) -> List[str]:
        """检查代码风格"""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                # 检查行长度
                if len(line.rstrip()) > 100:
                    issues.append(f"Line {i}: Line too long ({len(line.rstrip())} > 100)")

                # 检查缩进
                if line.startswith('\t'):
                    issues.append(f"Line {i}: Use spaces instead of tabs")

                # 检查尾随空格
                if line.rstrip() != line.rstrip(' \t'):
                    issues.append(f"Line {i}: Trailing whitespace")

        except Exception as e:
            issues.append(f"Error reading file: {e}")

        return issues

    def analyze_imports(self, file_path: Path) -> Dict[str, Any]:
        """分析导入语句"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            imports = {
                "standard_library": [],
                "third_party": [],
                "local": [],
                "unused_imports": [],
                "duplicate_imports": []
            }

            import_names = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_names.append(alias.name)
                        if self.is_standard_library(alias.name):
                            imports["standard_library"].append(alias.name)
                        elif self.is_local_import(alias.name):
                            imports["local"].append(alias.name)
                        else:
                            imports["third_party"].append(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    import_names.append(module)
                    if self.is_standard_library(module):
                        imports["standard_library"].append(module)
                    elif self.is_local_import(module):
                        imports["local"].append(module)
                    else:
                        imports["third_party"].append(module)

            # 检查重复导入
            seen = set()
            for name in import_names:
                if name in seen:
                    imports["duplicate_imports"].append(name)
                seen.add(name)

            return imports

        except Exception as e:
            print(f"⚠️ 分析导入失败 {file_path}: {e}")
            return {}

    def is_standard_library(self, module_name: str):
        """检查是否为标准库模块"""
        standard_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'subprocess',
            'threading', 'multiprocessing', 'collections', 'itertools',
            'functools', 'operator', 're', 'math', 'random', 'hashlib',
            'urllib', 'http', 'socket', 'ssl', 'email', 'html', 'xml',
            'sqlite3', 'pickle', 'csv', 'configparser', 'logging',
            'unittest', 'argparse', 'shutil', 'tempfile', 'glob'
        }

        return module_name.split('.')[0] in standard_modules

    def is_local_import(self, module_name: str):
        """检查是否为本地模块"""
        if not module_name:
            return False

        # 检查是否为相对导入或项目内模块
        return (module_name.startswith('.') or
                (self.project_root / f"{module_name.replace('.', '/')}.py").exists() or
                (self.project_root / module_name.replace('.', '/')).is_dir())

    def generate_optimization_suggestions(self, file_path: Path, stats: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        suggestions = []

        # 文件大小建议
        if stats.get("lines_of_code", 0) > 500:
            suggestions.append("Consider splitting this large file into smaller modules")

        # 函数复杂度建议
        if stats.get("max_function_length", 0) > 50:
            suggestions.append("Some functions are too long, consider breaking them down")

        # 类复杂度建议
        if stats.get("max_class_length", 0) > 200:
            suggestions.append("Some classes are too large, consider using composition")

        # 复杂度建议
        if stats.get("complexity_score", 0) > 20:
            suggestions.append("High cyclomatic complexity, consider refactoring")

        # 导入建议
        if stats.get("functions", 0) == 0 and stats.get("classes", 0) == 0:
            suggestions.append("File contains no functions or classes, consider if it's needed")

        return suggestions

    def run_analysis(self) -> Dict[str, Any]:
        """运行完整分析"""
        print(f"🔍 开始代码分析...")

        # 扫描文件
        self.scan_python_files()

        analysis_results = {
            "summary": {
                "total_files": len(self.python_files),
                "total_lines": 0,
                "total_functions": 0,
                "total_classes": 0,
                "issues_found": 0
            },
            "files": {},
            "recommendations": []
        }

        for file_path in self.python_files:
            print(f"📄 分析文件: {file_path.relative_to(self.project_root)}")

            # 复杂度分析
            complexity = self.analyze_file_complexity(file_path)

            # 代码风格检查
            style_issues = self.check_code_style(file_path)

            # 导入分析
            imports = self.analyze_imports(file_path)

            # 优化建议
            suggestions = self.generate_optimization_suggestions(file_path, complexity)

            file_result = {
                "path": str(file_path.relative_to(self.project_root)),
                "complexity": complexity,
                "style_issues": style_issues,
                "imports": imports,
                "suggestions": suggestions
            }

            analysis_results["files"][str(file_path.relative_to(self.project_root))] = file_result

            # 更新总计
            analysis_results["summary"]["total_lines"] += complexity.get("lines_of_code", 0)
            analysis_results["summary"]["total_functions"] += complexity.get("functions", 0)
            analysis_results["summary"]["total_classes"] += complexity.get("classes", 0)
            analysis_results["summary"]["issues_found"] += len(style_issues)

        # 生成总体建议
        analysis_results["recommendations"] = self.generate_project_recommendations(analysis_results)

        self.analysis_results = analysis_results
        print(f"✅ 代码分析完成")
        return analysis_results

    def generate_project_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """生成项目级别的建议"""
        recommendations = []

        summary = results["summary"]

        # 项目规模建议
        if summary["total_files"] > 50:
            recommendations.append("Large project: Consider organizing files into packages")

        if summary["total_lines"] > 10000:
            recommendations.append("Large codebase: Consider implementing automated testing")

        # 代码质量建议
        if summary["issues_found"] > 100:
            recommendations.append("Many style issues found: Consider using automated formatters")

        # 架构建议
        core_files = [f for f in results["files"] if "core/" in f]
        if len(core_files) > 10:
            recommendations.append("Many core files: Consider refactoring core architecture")

        return recommendations

    def save_analysis_report(self, output_file: str = "docs/code_analysis_report.json"):
        """保存分析报告"""
        try:
            output_path = self.project_root / output_file
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)

            print(f"📊 分析报告已保存: {output_path}")
            return True

        except Exception as e:
            print(f"❌ 保存分析报告失败: {e}")
            return False

    def print_summary(self):
        """打印分析摘要"""
        if not self.analysis_results:
            print("❌ 没有分析结果")
            return

        summary = self.analysis_results["summary"]

        print(f"\n📊 代码分析摘要:")
        print(f"  📄 文件总数: {summary['total_files']}")
        print(f"  📝 代码行数: {summary['total_lines']}")
        print(f"  🔧 函数总数: {summary['total_functions']}")
        print(f"  🏗️  类总数: {summary['total_classes']}")
        print(f"  ⚠️  问题总数: {summary['issues_found']}")

        print(f"\n💡 项目建议:")
        for i, rec in enumerate(self.analysis_results["recommendations"], 1):
            print(f"  {i}. {rec}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="代码分析和优化工具")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--output", default="docs/code_analysis_report.json", help="输出报告文件")
    parser.add_argument("--summary-only", action="store_true", help="只显示摘要")

    args = parser.parse_args()

    analyzer = CodeAnalyzer(args.project_root)
    results = analyzer.run_analysis()

    if args.summary_only:
        analyzer.print_summary()
    else:
        analyzer.save_analysis_report(args.output)
        analyzer.print_summary()

if __name__ == "__main__":
    main()
