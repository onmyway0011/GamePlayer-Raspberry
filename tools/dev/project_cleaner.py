#!/usr/bin/env python3
"""
项目清理工具
清理重复文件、无用文件、优化项目结构
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class ProjectCleaner:
    """项目清理器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.duplicate_files = []
        self.empty_files = []
        self.large_files = []
        self.unused_files = []
        
    def find_duplicate_files(self) -> List[Tuple[str, List[str]]]:
        """查找重复文件"""
        print("🔍 查找重复文件...")
        
        file_hashes = defaultdict(list)
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not self._should_skip_file(file_path):
                try:
                    file_hash = self._calculate_file_hash(file_path)
                    file_hashes[file_hash].append(str(file_path))
                except Exception as e:
                    print(f"⚠️ 无法计算文件哈希 {file_path}: {e}")
        
        # 找出重复文件
        duplicates = []
        for file_hash, file_list in file_hashes.items():
            if len(file_list) > 1:
                duplicates.append((file_hash, file_list))
        
        self.duplicate_files = duplicates
        print(f"📄 找到 {len(duplicates)} 组重复文件")
        
        return duplicates
    
    def find_empty_files(self) -> List[str]:
        """查找空文件"""
        print("🔍 查找空文件...")
        
        empty_files = []
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not self._should_skip_file(file_path):
                try:
                    if file_path.stat().st_size == 0:
                        empty_files.append(str(file_path))
                except Exception as e:
                    print(f"⚠️ 无法检查文件大小 {file_path}: {e}")
        
        self.empty_files = empty_files
        print(f"📄 找到 {len(empty_files)} 个空文件")
        
        return empty_files
    
    def find_large_files(self, size_limit_mb: int = 10) -> List[Tuple[str, int]]:
        """查找大文件"""
        print(f"🔍 查找大于 {size_limit_mb}MB 的文件...")
        
        large_files = []
        size_limit_bytes = size_limit_mb * 1024 * 1024
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not self._should_skip_file(file_path):
                try:
                    file_size = file_path.stat().st_size
                    if file_size > size_limit_bytes:
                        large_files.append((str(file_path), file_size))
                except Exception as e:
                    print(f"⚠️ 无法检查文件大小 {file_path}: {e}")
        
        # 按大小排序
        large_files.sort(key=lambda x: x[1], reverse=True)
        
        self.large_files = large_files
        print(f"📄 找到 {len(large_files)} 个大文件")
        
        return large_files
    
    def find_unused_files(self) -> List[str]:
        """查找可能未使用的文件"""
        print("🔍 查找可能未使用的文件...")
        
        unused_patterns = [
            "*.tmp", "*.temp", "*.bak", "*.backup", "*.old",
            "*.log", "*.cache", "*.pyc", "*.pyo", "*.pyd",
            ".DS_Store", "Thumbs.db", "desktop.ini"
        ]
        
        unused_files = []
        
        for pattern in unused_patterns:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file():
                    unused_files.append(str(file_path))
        
        self.unused_files = unused_files
        print(f"📄 找到 {len(unused_files)} 个可能未使用的文件")
        
        return unused_files
    
    def clean_empty_directories(self) -> List[str]:
        """清理空目录"""
        print("🔍 清理空目录...")
        
        removed_dirs = []
        
        # 多次遍历，因为删除子目录可能使父目录变空
        for _ in range(5):  # 最多5次迭代
            empty_dirs = []
            
            for dir_path in self.project_root.rglob("*"):
                if dir_path.is_dir() and not self._should_skip_directory(dir_path):
                    try:
                        # 检查目录是否为空
                        if not any(dir_path.iterdir()):
                            empty_dirs.append(dir_path)
                    except Exception as e:
                        print(f"⚠️ 无法检查目录 {dir_path}: {e}")
            
            if not empty_dirs:
                break
            
            # 删除空目录
            for dir_path in empty_dirs:
                try:
                    dir_path.rmdir()
                    removed_dirs.append(str(dir_path))
                    print(f"🗑️ 删除空目录: {dir_path}")
                except Exception as e:
                    print(f"⚠️ 无法删除目录 {dir_path}: {e}")
        
        print(f"🗑️ 删除了 {len(removed_dirs)} 个空目录")
        return removed_dirs
    
    def remove_duplicate_files(self, keep_first: bool = True) -> List[str]:
        """删除重复文件"""
        print("🗑️ 删除重复文件...")
        
        removed_files = []
        
        for file_hash, file_list in self.duplicate_files:
            if len(file_list) > 1:
                # 保留第一个文件，删除其他的
                files_to_remove = file_list[1:] if keep_first else file_list[:-1]
                
                for file_path in files_to_remove:
                    try:
                        Path(file_path).unlink()
                        removed_files.append(file_path)
                        print(f"🗑️ 删除重复文件: {file_path}")
                    except Exception as e:
                        print(f"⚠️ 无法删除文件 {file_path}: {e}")
        
        print(f"🗑️ 删除了 {len(removed_files)} 个重复文件")
        return removed_files
    
    def remove_unused_files(self) -> List[str]:
        """删除未使用的文件"""
        print("🗑️ 删除未使用的文件...")
        
        removed_files = []
        
        for file_path in self.unused_files:
            try:
                Path(file_path).unlink()
                removed_files.append(file_path)
                print(f"🗑️ 删除未使用文件: {file_path}")
            except Exception as e:
                print(f"⚠️ 无法删除文件 {file_path}: {e}")
        
        print(f"🗑️ 删除了 {len(removed_files)} 个未使用文件")
        return removed_files
    
    def optimize_project_structure(self) -> Dict[str, List[str]]:
        """优化项目结构"""
        print("🔧 优化项目结构...")
        
        optimizations = {
            "moved_files": [],
            "created_directories": [],
            "updated_imports": []
        }
        
        # 确保标准目录存在
        standard_dirs = [
            "src", "tests", "docs", "config", "data", "build", "tools"
        ]
        
        for dir_name in standard_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                optimizations["created_directories"].append(str(dir_path))
                print(f"📁 创建目录: {dir_path}")
        
        return optimizations
    
    def generate_cleanup_report(self) -> Dict:
        """生成清理报告"""
        return {
            "duplicate_files": len(self.duplicate_files),
            "empty_files": len(self.empty_files),
            "large_files": len(self.large_files),
            "unused_files": len(self.unused_files),
            "duplicate_file_details": [
                {
                    "hash": file_hash,
                    "files": file_list,
                    "count": len(file_list)
                }
                for file_hash, file_list in self.duplicate_files
            ],
            "large_file_details": [
                {
                    "file": file_path,
                    "size_mb": round(size / (1024 * 1024), 2)
                }
                for file_path, size in self.large_files
            ]
        }
    
    def run_full_cleanup(self, remove_duplicates: bool = True, 
                        remove_unused: bool = True) -> Dict:
        """运行完整清理"""
        print("🚀 开始项目清理...")
        
        # 分析阶段
        self.find_duplicate_files()
        self.find_empty_files()
        self.find_large_files()
        self.find_unused_files()
        
        # 清理阶段
        removed_files = []
        removed_dirs = []
        
        if remove_duplicates:
            removed_files.extend(self.remove_duplicate_files())
        
        if remove_unused:
            removed_files.extend(self.remove_unused_files())
        
        removed_dirs.extend(self.clean_empty_directories())
        
        # 优化阶段
        optimizations = self.optimize_project_structure()
        
        # 生成报告
        report = self.generate_cleanup_report()
        report.update({
            "removed_files": len(removed_files),
            "removed_directories": len(removed_dirs),
            "optimizations": optimizations
        })
        
        print("✅ 项目清理完成!")
        print(f"📊 清理统计:")
        print(f"  - 删除文件: {len(removed_files)}")
        print(f"  - 删除目录: {len(removed_dirs)}")
        print(f"  - 重复文件组: {len(self.duplicate_files)}")
        print(f"  - 大文件: {len(self.large_files)}")
        
        return report
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = [
            ".git", "__pycache__", ".pytest_cache", "node_modules",
            ".venv", "venv", "env", ".tox", "build", "dist"
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _should_skip_directory(self, dir_path: Path) -> bool:
        """判断是否应该跳过目录"""
        skip_dirs = {
            ".git", "__pycache__", ".pytest_cache", "node_modules",
            ".venv", "venv", "env", ".tox"
        }
        
        return dir_path.name in skip_dirs

def main():
    """主函数"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="项目清理工具")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--output", default="docs/reports/cleanup_report.json", help="输出报告文件")
    parser.add_argument("--no-remove-duplicates", action="store_true", help="不删除重复文件")
    parser.add_argument("--no-remove-unused", action="store_true", help="不删除未使用文件")
    parser.add_argument("--dry-run", action="store_true", help="只分析不删除")
    
    args = parser.parse_args()
    
    cleaner = ProjectCleaner(args.project_root)
    
    if args.dry_run:
        print("🔍 运行分析模式（不删除文件）...")
        cleaner.find_duplicate_files()
        cleaner.find_empty_files()
        cleaner.find_large_files()
        cleaner.find_unused_files()
        report = cleaner.generate_cleanup_report()
    else:
        report = cleaner.run_full_cleanup(
            remove_duplicates=not args.no_remove_duplicates,
            remove_unused=not args.no_remove_unused
        )
    
    # 保存报告
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📄 清理报告已保存: {args.output}")

if __name__ == "__main__":
    main()
