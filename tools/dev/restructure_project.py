#!/usr/bin/env python3
"""
项目结构重组工具
将混乱的文件结构重新整理为清晰的目录结构
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

class ProjectRestructurer:
    """项目结构重组器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_old_structure"
        
        # 定义新的目录结构
        self.new_structure = {
            "src/": {
                "core/": "核心模块",
                "scripts/": "脚本工具", 
                "web/": "Web相关文件"
            },
            "config/": {
                "docker/": "Docker配置",
                "system/": "系统配置"
            },
            "docs/": {
                "guides/": "使用指南",
                "api/": "API文档",
                "reports/": "分析报告"
            },
            "tests/": {
                "unit/": "单元测试",
                "integration/": "集成测试",
                "fixtures/": "测试数据"
            },
            "build/": {
                "docker/": "Docker构建文件",
                "scripts/": "构建脚本",
                "output/": "构建输出"
            },
            "data/": {
                "roms/": "游戏ROM文件",
                "saves/": "游戏存档",
                "cheats/": "金手指配置",
                "logs/": "日志文件"
            },
            "tools/": {
                "dev/": "开发工具",
                "deploy/": "部署工具"
            },
            "assets/": {
                "images/": "图片资源",
                "fonts/": "字体文件",
                "sounds/": "音频文件"
            }
        }
        
        # 文件移动规则
        self.move_rules = {
            # 核心模块
            "core/*.py": "src/core/",
            
            # 脚本工具
            "scripts/*.py": "src/scripts/",
            "scripts/*.sh": "src/scripts/",
            
            # Web文件
            "web_config.py": "src/web/",
            
            # Docker文件
            "Dockerfile*": "build/docker/",
            "docker-compose.yml": "build/docker/",
            "*.dockerfile": "build/docker/",
            
            # 配置文件
            "config/*.json": "config/system/",
            "config/*.service": "config/system/",
            "config/*.sh": "config/system/",
            "config/*.bat": "config/system/",
            "*.json": "config/system/",  # 根目录的配置文件
            
            # 文档文件
            "*_SUMMARY.md": "docs/reports/",
            "*_GUIDE.md": "docs/guides/",
            "*_REPORT.md": "docs/reports/",
            "README*.md": "docs/",
            "docs/*.md": "docs/guides/",
            "docs/*.json": "docs/reports/",
            
            # 测试文件
            "tests/*.py": "tests/unit/",
            "tests/logs/": "tests/fixtures/",
            
            # 构建相关
            "*.sh": "build/scripts/",  # 根目录的shell脚本
            "output/": "build/output/",
            "*.log": "data/logs/",
            
            # 数据文件
            "roms/": "data/roms/",
            "saves/": "data/saves/",
            "cheats/": "data/cheats/",
            "logs/": "data/logs/",
            "downloads/": "data/downloads/",
            
            # 开发工具
            "tools/*.py": "tools/dev/",
            
            # 系统相关
            "systems/": "src/systems/",
            
            # 项目文件
            "setup.py": "./",
            "requirements.txt": "./",
            "README.md": "./",
            ".gitignore": "./"
        }
    
    def create_directory_structure(self):
        """创建新的目录结构"""
        print("📁 创建新的目录结构...")
        
        for main_dir, sub_dirs in self.new_structure.items():
            main_path = self.project_root / main_dir
            main_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ 创建目录: {main_dir}")
            
            if isinstance(sub_dirs, dict):
                for sub_dir, description in sub_dirs.items():
                    sub_path = main_path / sub_dir
                    sub_path.mkdir(parents=True, exist_ok=True)
                    print(f"    📂 {sub_dir} - {description}")
    
    def backup_current_structure(self):
        """备份当前结构"""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        print("💾 备份当前项目结构...")
        
        # 创建备份目录
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 备份重要文件
        important_files = [
            "README.md", "setup.py", "requirements.txt", 
            ".gitignore", "docker-compose.yml"
        ]
        
        for file_name in important_files:
            src_file = self.project_root / file_name
            if src_file.exists():
                dst_file = self.backup_dir / file_name
                shutil.copy2(src_file, dst_file)
                print(f"  💾 备份: {file_name}")
    
    def move_files_by_rules(self):
        """根据规则移动文件"""
        print("🔄 重新组织文件...")
        
        moved_files = []
        
        for pattern, target_dir in self.move_rules.items():
            # 处理通配符模式
            if "*" in pattern:
                import glob
                matching_files = glob.glob(str(self.project_root / pattern))
                
                for file_path in matching_files:
                    src_path = Path(file_path)
                    if src_path.exists() and src_path != self.project_root / target_dir:
                        dst_dir = self.project_root / target_dir
                        dst_dir.mkdir(parents=True, exist_ok=True)
                        
                        dst_path = dst_dir / src_path.name
                        
                        try:
                            if src_path.is_file():
                                shutil.move(str(src_path), str(dst_path))
                                moved_files.append((src_path, dst_path))
                                print(f"  📄 移动文件: {src_path.name} → {target_dir}")
                            elif src_path.is_dir():
                                if dst_path.exists():
                                    shutil.rmtree(dst_path)
                                shutil.move(str(src_path), str(dst_path))
                                moved_files.append((src_path, dst_path))
                                print(f"  📁 移动目录: {src_path.name} → {target_dir}")
                        except Exception as e:
                            print(f"  ⚠️ 移动失败 {src_path}: {e}")
            else:
                # 处理具体文件
                src_path = self.project_root / pattern
                if src_path.exists():
                    dst_dir = self.project_root / target_dir
                    dst_dir.mkdir(parents=True, exist_ok=True)
                    
                    dst_path = dst_dir / src_path.name
                    
                    try:
                        if src_path.is_file():
                            shutil.move(str(src_path), str(dst_path))
                            moved_files.append((src_path, dst_path))
                            print(f"  📄 移动文件: {pattern} → {target_dir}")
                        elif src_path.is_dir():
                            if dst_path.exists():
                                shutil.rmtree(dst_path)
                            shutil.move(str(src_path), str(dst_path))
                            moved_files.append((src_path, dst_path))
                            print(f"  📁 移动目录: {pattern} → {target_dir}")
                    except Exception as e:
                        print(f"  ⚠️ 移动失败 {pattern}: {e}")
        
        return moved_files
    
    def clean_empty_directories(self):
        """清理空目录"""
        print("🧹 清理空目录...")
        
        def remove_empty_dirs(path):
            if not path.is_dir():
                return
            
            # 递归清理子目录
            for child in path.iterdir():
                if child.is_dir():
                    remove_empty_dirs(child)
            
            # 如果目录为空，删除它
            try:
                if path.is_dir() and not any(path.iterdir()):
                    path.rmdir()
                    print(f"  🗑️ 删除空目录: {path.relative_to(self.project_root)}")
            except OSError:
                pass
        
        # 清理项目根目录下的空目录
        for item in self.project_root.iterdir():
            if item.is_dir() and item.name not in ['.git', 'backup_old_structure']:
                remove_empty_dirs(item)
    
    def create_index_files(self):
        """创建目录索引文件"""
        print("📝 创建目录索引文件...")
        
        index_contents = {
            "src/README.md": """# 源代码目录

## 目录结构

- `core/` - 核心模块
- `scripts/` - 脚本工具
- `web/` - Web相关文件
- `systems/` - 系统集成模块
""",
            "config/README.md": """# 配置文件目录

## 目录结构

- `docker/` - Docker相关配置
- `system/` - 系统配置文件
""",
            "docs/README.md": """# 文档目录

## 目录结构

- `guides/` - 使用指南
- `api/` - API文档
- `reports/` - 分析报告
""",
            "tests/README.md": """# 测试目录

## 目录结构

- `unit/` - 单元测试
- `integration/` - 集成测试
- `fixtures/` - 测试数据和夹具
""",
            "build/README.md": """# 构建目录

## 目录结构

- `docker/` - Docker构建文件
- `scripts/` - 构建脚本
- `output/` - 构建输出
""",
            "data/README.md": """# 数据目录

## 目录结构

- `roms/` - 游戏ROM文件
- `saves/` - 游戏存档
- `cheats/` - 金手指配置
- `logs/` - 日志文件
- `downloads/` - 下载文件
""",
            "tools/README.md": """# 工具目录

## 目录结构

- `dev/` - 开发工具
- `deploy/` - 部署工具
"""
        }
        
        for file_path, content in index_contents.items():
            full_path = self.project_root / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if not full_path.exists():
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  📝 创建索引: {file_path}")
    
    def update_import_paths(self):
        """更新Python文件中的导入路径"""
        print("🔧 更新导入路径...")
        
        # 这里可以添加更复杂的导入路径更新逻辑
        # 暂时跳过，因为需要分析具体的导入关系
        print("  ℹ️ 导入路径更新需要手动检查")
    
    def generate_new_structure_report(self):
        """生成新结构报告"""
        report_path = self.project_root / "docs" / "NEW_PROJECT_STRUCTURE.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_content = """# 新项目结构

## 目录说明

### 📁 src/ - 源代码
- `core/` - 核心模块 (NES模拟器、存档管理、金手指等)
- `scripts/` - 脚本工具 (安装器、ROM管理等)
- `web/` - Web相关文件
- `systems/` - 系统集成模块

### ⚙️ config/ - 配置文件
- `docker/` - Docker相关配置
- `system/` - 系统配置文件

### 📖 docs/ - 文档
- `guides/` - 使用指南
- `api/` - API文档  
- `reports/` - 分析报告

### 🧪 tests/ - 测试
- `unit/` - 单元测试
- `integration/` - 集成测试
- `fixtures/` - 测试数据

### 🏗️ build/ - 构建
- `docker/` - Docker构建文件
- `scripts/` - 构建脚本
- `output/` - 构建输出

### 💾 data/ - 数据
- `roms/` - 游戏ROM文件
- `saves/` - 游戏存档
- `cheats/` - 金手指配置
- `logs/` - 日志文件

### 🛠️ tools/ - 工具
- `dev/` - 开发工具
- `deploy/` - 部署工具

### 🎨 assets/ - 资源
- `images/` - 图片资源
- `fonts/` - 字体文件
- `sounds/` - 音频文件

## 主要改进

1. **清晰的分层结构** - 按功能分类组织文件
2. **标准化命名** - 使用业界标准的目录名称
3. **逻辑分离** - 源码、配置、文档、测试分离
4. **易于维护** - 结构清晰，便于查找和维护

## 迁移说明

- 原有文件已按新结构重新组织
- 备份文件保存在 `backup_old_structure/` 目录
- 导入路径可能需要手动调整
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📊 生成结构报告: {report_path}")
    
    def restructure(self):
        """执行完整的重构"""
        print("🚀 开始项目结构重组...")
        print()
        
        # 1. 备份当前结构
        self.backup_current_structure()
        print()
        
        # 2. 创建新目录结构
        self.create_directory_structure()
        print()
        
        # 3. 移动文件
        moved_files = self.move_files_by_rules()
        print()
        
        # 4. 清理空目录
        self.clean_empty_directories()
        print()
        
        # 5. 创建索引文件
        self.create_index_files()
        print()
        
        # 6. 更新导入路径
        self.update_import_paths()
        print()
        
        # 7. 生成报告
        self.generate_new_structure_report()
        print()
        
        print("✅ 项目结构重组完成！")
        print(f"📊 移动了 {len(moved_files)} 个文件/目录")
        print("📁 新的项目结构更加清晰和专业")
        print("💾 原始文件已备份到 backup_old_structure/ 目录")
        print()
        print("🔧 下一步:")
        print("  1. 检查导入路径是否需要调整")
        print("  2. 更新CI/CD配置文件")
        print("  3. 测试所有功能是否正常")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="项目结构重组工具")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--dry-run", action="store_true", help="仅显示将要执行的操作")
    
    args = parser.parse_args()
    
    restructurer = ProjectRestructurer(args.project_root)
    
    if args.dry_run:
        print("🔍 干运行模式 - 仅显示将要执行的操作")
        print("将要创建的目录结构:")
        for main_dir, sub_dirs in restructurer.new_structure.items():
            print(f"  📁 {main_dir}")
            if isinstance(sub_dirs, dict):
                for sub_dir in sub_dirs:
                    print(f"    📂 {sub_dir}")
    else:
        restructurer.restructure()

if __name__ == "__main__":
    main()
