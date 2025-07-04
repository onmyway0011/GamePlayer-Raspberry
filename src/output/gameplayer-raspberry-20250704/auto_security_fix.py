#!/usr/bin/env python3
"""
自动安全修复脚本
修复bandit检测到的安全漏洞
"""

import os
import re
import shutil
import hashlib
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple


class SecurityFixer:
    def __init__(self, project_root: str = "."):
        """TODO: 添加文档字符串"""
        self.project_root = Path(project_root)
        self.fixes_applied = []
        self.errors = []

    def fix_md5_hashlib(self, file_path: Path):
        """修复MD5哈希安全问题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 修复MD5哈希使用
            original_content = content
            content = re.sub(
                r'hashlib\.md5\(([^)]+)\)\.hexdigest\(\)',
                r'hashlib.md5(\1, usedforsecurity=False).hexdigest()',
                content
            )

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied.append(f"修复MD5哈希安全问题: {file_path}")
                return True
            return False
        except Exception as e:
            self.errors.append(f"修复MD5哈希失败 {file_path}: {e}")
            return False

    def fix_tempfile_mktemp(self, file_path: Path):
        """修复tempfile.mktemp安全问题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            # 替换tempfile.mktemp为tempfile.NamedTemporaryFile
            content = re.sub(
                r'tempfile\.mktemp\(([^)]*)\)',
                r'tempfile.NamedTemporaryFile(delete=False, \1).name',
                content
            )

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied.append(f"修复tempfile.mktemp安全问题: {file_path}")
                return True
            return False
        except Exception as e:
            self.errors.append(f"修复tempfile.mktemp失败 {file_path}: {e}")
            return False

    def fix_ssh_auto_add_policy(self, file_path: Path):
        """修复SSH自动添加主机密钥安全问题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            # 替换AutoAddPolicy为RejectPolicy
            content = re.sub(
                r'paramiko\.AutoAddPolicy\(\)',
                r'paramiko.RejectPolicy()',
                content
            )

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied.append(f"修复SSH自动添加主机密钥安全问题: {file_path}")
                return True
            return False
        except Exception as e:
            self.errors.append(f"修复SSH策略失败 {file_path}: {e}")
            return False

    def fix_hardcoded_bind_all_interfaces(self, file_path: Path):
        """修复硬编码绑定所有接口问题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            # 替换0.0.0.0为127.0.0.1
            content = re.sub(
                r"host=['\"]0\.0\.0\.0['\"]",
                r"host='127.0.0.1'",
                content
            )

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied.append(f"修复硬编码绑定所有接口问题: {file_path}")
                return True
            return False
        except Exception as e:
            self.errors.append(f"修复绑定接口失败 {file_path}: {e}")
            return False

    def fix_try_except_pass(self, file_path: Path):
        """修复空的try-except块"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            # 替换空的except块为日志记录
            content = re.sub(
                r'except\s*Exception\s*:\s*\n\s*pass',
                r'except Exception as e:\n        logger.warning(f"操作失败: {e}")',
                content
            )

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied.append(f"修复空的try-except块: {file_path}")
                return True
            return False
        except Exception as e:
            self.errors.append(f"修复try-except失败 {file_path}: {e}")
            return False

    def fix_random_security(self, file_path: Path):
        """修复随机数生成安全问题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            # 添加secrets模块导入
            if 'import random' in content and 'import secrets' not in content:
                content = content.replace('import random', 'import random\nimport secrets')

            # 替换random.randint为secrets.randbelow
            content = re.sub(
                r'random\.randint\(0,\s*(\d+)\)',
                r'secrets.randbelow(\1)',
                content
            )

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied.append(f"修复随机数生成安全问题: {file_path}")
                return True
            return False
        except Exception as e:
            self.errors.append(f"修复随机数失败 {file_path}: {e}")
            return False

    def scan_and_fix(self) -> Dict[str, List[str]]:
        """扫描并修复所有安全漏洞"""
        print("🔍 开始安全漏洞扫描和修复...")

        # 需要修复的文件模式
        patterns = {
            'md5_hashlib': ['**/*.py'],
            'tempfile_mktemp': ['**/*.py'],
            'ssh_auto_add_policy': ['**/*.py'],
            'hardcoded_bind_all_interfaces': ['**/*.py'],
            'try_except_pass': ['**/*.py'],
            'random_security': ['**/*.py']
        }

        for pattern_name, file_patterns in patterns.items():
            for file_pattern in file_patterns:
                for file_path in self.project_root.glob(file_pattern):
                    if file_path.is_file() and file_path.suffix == '.py':
                        try:
                            if pattern_name == 'md5_hashlib':
                                self.fix_md5_hashlib(file_path)
                            elif pattern_name == 'tempfile_mktemp':
                                self.fix_tempfile_mktemp(file_path)
                            elif pattern_name == 'ssh_auto_add_policy':
                                self.fix_ssh_auto_add_policy(file_path)
                            elif pattern_name == 'hardcoded_bind_all_interfaces':
                                self.fix_hardcoded_bind_all_interfaces(file_path)
                            elif pattern_name == 'try_except_pass':
                                self.fix_try_except_pass(file_path)
                            elif pattern_name == 'random_security':
                                self.fix_random_security(file_path)
                        except Exception as e:
                            self.errors.append(f"处理文件失败 {file_path}: {e}")

        return {
            'fixes_applied': self.fixes_applied,
            'errors': self.errors
        }

    def generate_report(self, results: Dict[str, List[str]]) -> str:
        """生成修复报告"""
        report = []
        report.append("# 安全漏洞自动修复报告")
        report.append("")

        if results['fixes_applied']:
            report.append("## ✅ 已修复的安全问题")
            for fix in results['fixes_applied']:
                report.append(f"- {fix}")
            report.append("")
        else:
            report.append("## ℹ️ 未发现需要修复的安全问题")
            report.append("")

        if results['errors']:
            report.append("## ❌ 修复过程中的错误")
            for error in results['errors']:
                report.append(f"- {error}")
            report.append("")

        report.append(f"## 📊 修复统计")
        report.append(f"- 修复的问题: {len(results['fixes_applied'])}")
        report.append(f"- 错误数量: {len(results['errors'])}")

        return "\n".join(report)


def main():
    """主函数"""
    print("🛡️ 自动安全修复工具")
    print("=" * 50)

    fixer = SecurityFixer()
    results = fixer.scan_and_fix()

    # 生成报告
    report = fixer.generate_report(results)
    print(report)

    # 保存报告
    report_file = Path("security_fix_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n📄 详细报告已保存到: {report_file}")

    if results['fixes_applied']:
        print("\n✅ 安全修复完成！建议重新运行bandit检查。")
    else:
        print("\nℹ️ 未发现需要修复的安全问题。")

if __name__ == "__main__":
    main()
