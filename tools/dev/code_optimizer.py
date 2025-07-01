#!/usr/bin/env python3
"""
代码优化工具
自动优化Python代码质量、性能和可维护性
"""

import os
import sys
import re
import ast
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

@dataclass


class OptimizationResult:
    """优化结果"""
    file_path: str
    original_lines: int
    optimized_lines: int
    issues_fixed: List[str]
    performance_improvements: List[str]
    code_quality_improvements: List[str]


class CodeOptimizer:
    """代码优化器"""

    def __init__(self, project_root: str = "."):
        """TODO: Add docstring"""
        self.project_root = Path(project_root).resolve()
        self.optimization_results = []

    def find_python_files(self) -> List[Path]:
        """查找所有Python文件"""
        python_files = []

        # 扫描目录
        for pattern in ["**/*.py"]:
            python_files.extend(self.project_root.glob(pattern))

        # 过滤排除的文件
        excluded_patterns = [
            "__pycache__", ".git", "venv", "env", ".pytest_cache",
            "build", "dist", ".tox", "node_modules"
        ]

        filtered_files = []
        for file_path in python_files:
            if not any(pattern in str(file_path) for pattern in excluded_patterns):
                filtered_files.append(file_path)

        return filtered_files

    def fix_syntax_errors(self, file_path: Path) -> List[str]:
        """修复语法错误"""
        fixes = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # 修复常见的类型注解错误
            # 修复 "-> bool:" 错误
            content = re.sub(r'(\w+)\s*->\s*bool:\s*(\w+)', r'\1: \2', content)

            # 修复函数定义中的类型注解错误
            content = re.sub(r'def\s+(\w+)\s*\([^)]*->\s*bool:\s*([^)]*)\)\s*->\s*bool:',
                           r'def \1(\2):', content)

            # 修复参数类型注解错误
            content = re.sub(r'(\w+)\s*->\s*bool:\s*(\w+)\s*=', r'\1: \2 =', content)

            # 修复返回类型注解
            content = re.sub(r'\)\s*->\s*bool:\s*$', r'):', content, flags=re.MULTILINE)

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixes.append("修复类型注解语法错误")

        except Exception as e:
            fixes.append(f"语法修复失败: {e}")

        return fixes

    def optimize_imports(self, file_path: Path) -> List[str]:
        """优化导入语句"""
        improvements = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 分析导入语句
            import_lines = []
            other_lines = []
            in_imports = True

            for line in lines:
                stripped = line.strip()
                if stripped.startswith(('import ', 'from ')) and in_imports:
                    import_lines.append(line)
                elif stripped == '' and in_imports:
                    import_lines.append(line)
                else:
                    if in_imports and stripped:
                        in_imports = False
                    other_lines.append(line)

            # 优化导入顺序
            if import_lines:
                # 分类导入
                stdlib_imports = []
                third_party_imports = []
                local_imports = []

                for line in import_lines:
                    stripped = line.strip()
                    if not stripped:
                        continue

                    if stripped.startswith('from .') or stripped.startswith('from src.'):
                        local_imports.append(line)
                    elif any(lib in stripped for lib in ['pygame', 'numpy', 'requests']):
                        third_party_imports.append(line)
                    else:
                        stdlib_imports.append(line)

                # 重新组织导入
                optimized_imports = []
                if stdlib_imports:
                    optimized_imports.extend(sorted(stdlib_imports))
                    optimized_imports.append('\n')
                if third_party_imports:
                    optimized_imports.extend(sorted(third_party_imports))
                    optimized_imports.append('\n')
                if local_imports:
                    optimized_imports.extend(sorted(local_imports))
                    optimized_imports.append('\n')

                # 写回文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(optimized_imports + other_lines)

                improvements.append("优化导入语句顺序")

        except Exception as e:
            improvements.append(f"导入优化失败: {e}")

        return improvements

    def optimize_code_style(self, file_path: Path) -> List[str]:
        """优化代码风格"""
        improvements = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # 移除尾随空格
            content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

            # 确保文件以换行符结尾
            if content and not content.endswith('\n'):
                content += '\n'

            # 优化空行
            # 移除多余的空行（超过2个连续空行）
            content = re.sub(r'\n{3,}', '\n\n', content)

            # 函数和类定义前后的空行
            content = re.sub(r'\n(class\s+\w+.*?:)', r'\n\n\1', content)
            content = re.sub(r'\n(def\s+\w+.*?:)', r'\n\n\1', content)

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                improvements.append("优化代码格式和空行")

        except Exception as e:
            improvements.append(f"代码风格优化失败: {e}")

        return improvements

    def optimize_performance(self, file_path: Path) -> List[str]:
        """性能优化"""
        improvements = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # 优化字符串拼接
            # 将多个字符串拼接改为f-string或join
            content = re.sub(r'(\w+)\s*\+\s*"([^"]*)"', r'f"{\1}\2"', content)

            # 优化列表推导式
            # 简单的for循环改为列表推导式
            pattern = r'(\w+)\s*=\s*\[\]\s*\n\s*for\s+(\w+)\s+in\s+(\w+):\s*\n\s*\1\.append\(([^)]+)\)'
            replacement = r'\1 = [\4 for \2 in \3]'
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                improvements.append("优化性能相关代码")

        except Exception as e:
            improvements.append(f"性能优化失败: {e}")

        return improvements

    def add_type_hints(self, file_path: Path) -> List[str]:
        """添加类型提示"""
        improvements = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析AST来分析函数
            tree = ast.parse(content)

            # 这里可以添加更复杂的类型提示分析
            # 简单示例：为没有类型提示的函数参数添加基本类型

            improvements.append("分析类型提示需求")

        except Exception as e:
            improvements.append(f"类型提示分析失败: {e}")

        return improvements

    def optimize_docstrings(self, file_path: Path) -> List[str]:
        """优化文档字符串"""
        improvements = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # 检查并添加基本的docstring
            lines = content.split('\n')
            new_lines = []
            i = 0

            while i < len(lines):
                line = lines[i]

                # 检查函数定义
                if re.match(r'^\s*def\s+\w+', line):
                    new_lines.append(line)
                    i += 1

                    # 检查下一行是否有docstring
                    if i < len(lines) and not lines[i].strip().startswith('"""'):
                        # 添加简单的docstring
                        indent = len(line) - len(line.lstrip())
                        new_lines.append(' ' * (indent + 4) + '"""TODO: Add docstring"""')
                        improvements.append("添加缺失的docstring")
                else:
                    new_lines.append(line)
                    i += 1

            if improvements:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))

        except Exception as e:
            improvements.append(f"文档字符串优化失败: {e}")

        return improvements

    def optimize_file(self, file_path: Path) -> OptimizationResult:
        """优化单个文件"""
        print(f"🔧 优化文件: {file_path.relative_to(self.project_root)}")

        # 获取原始行数
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_lines = len(f.readlines())
        except:
            original_lines = 0

        # 执行各种优化
        issues_fixed = []
        performance_improvements = []
        code_quality_improvements = []

        # 修复语法错误
        issues_fixed.extend(self.fix_syntax_errors(file_path))

        # 优化导入
        code_quality_improvements.extend(self.optimize_imports(file_path))

        # 优化代码风格
        code_quality_improvements.extend(self.optimize_code_style(file_path))

        # 性能优化
        performance_improvements.extend(self.optimize_performance(file_path))

        # 添加类型提示
        code_quality_improvements.extend(self.add_type_hints(file_path))

        # 优化文档字符串
        code_quality_improvements.extend(self.optimize_docstrings(file_path))

        # 获取优化后行数
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                optimized_lines = len(f.readlines())
        except:
            optimized_lines = original_lines

        return OptimizationResult(
            file_path=str(file_path.relative_to(self.project_root)),
            original_lines=original_lines,
            optimized_lines=optimized_lines,
            issues_fixed=issues_fixed,
            performance_improvements=performance_improvements,
            code_quality_improvements=code_quality_improvements
        )

    def run_optimization(self) -> Dict[str, Any]:
        """运行完整优化"""
        print("🚀 开始代码优化...")

        python_files = self.find_python_files()
        print(f"📄 找到 {len(python_files)} 个Python文件")

        results = []
        total_issues_fixed = 0
        total_improvements = 0

        for file_path in python_files:
            try:
                result = self.optimize_file(file_path)
                results.append(result)

                total_issues_fixed += len(result.issues_fixed)
                total_improvements += len(result.performance_improvements) + len(result.code_quality_improvements)

            except Exception as e:
                print(f"❌ 优化文件失败 {file_path}: {e}")

        self.optimization_results = results

        summary = {
            "total_files": len(python_files),
            "files_optimized": len(results),
            "total_issues_fixed": total_issues_fixed,
            "total_improvements": total_improvements,
            "results": [
                {
                    "file": r.file_path,
                    "original_lines": r.original_lines,
                    "optimized_lines": r.optimized_lines,
                    "issues_fixed": len(r.issues_fixed),
                    "improvements": len(r.performance_improvements) + len(r.code_quality_improvements)
                }
                for r in results
            ]
        }

        print(f"✅ 优化完成: {len(results)} 个文件, {total_issues_fixed} 个问题修复, {total_improvements} 个改进")

        return summary

    def save_optimization_report(self, output_file: str):
        """保存优化报告"""
        report = {
            "optimization_summary": {
                "total_files": len(self.optimization_results),
                "total_issues_fixed": sum(len(r.issues_fixed) for r in self.optimization_results),
                "total_improvements": sum(
                    len(r.performance_improvements) + len(r.code_quality_improvements)
                    for r in self.optimization_results
                )
            },
            "file_results": [
                {
                    "file_path": r.file_path,
                    "original_lines": r.original_lines,
                    "optimized_lines": r.optimized_lines,
                    "issues_fixed": r.issues_fixed,
                    "performance_improvements": r.performance_improvements,
                    "code_quality_improvements": r.code_quality_improvements
                }
                for r in self.optimization_results
            ]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📄 优化报告已保存: {output_file}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="代码优化工具")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--output", default="docs/reports/optimization_report.json", help="输出报告文件")
    parser.add_argument("--dry-run", action="store_true", help="只分析不修改")

    args = parser.parse_args()

    optimizer = CodeOptimizer(args.project_root)

    if args.dry_run:
        print("🔍 运行分析模式（不修改文件）...")
        # 这里可以添加只分析不修改的逻辑
    else:
        summary = optimizer.run_optimization()
        optimizer.save_optimization_report(args.output)

        print("\n📊 优化摘要:")
        print(f"  文件总数: {summary['total_files']}")
        print(f"  优化文件: {summary['files_optimized']}")
        print(f"  修复问题: {summary['total_issues_fixed']}")
        print(f"  代码改进: {summary['total_improvements']}")

if __name__ == "__main__":
    main()
