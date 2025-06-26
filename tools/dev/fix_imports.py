#!/usr/bin/env python3
"""
导入路径修复工具
自动修复重组后的导入路径
"""

import os
import re
from pathlib import Path
from typing import Dict, List

class ImportFixer:
    """导入路径修复器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        
        # 路径映射规则
        self.path_mappings = {
            # 核心模块
            "from src.core.": "from src.core.",
            "import src.core.": "import src.core.",
            
            # 脚本模块
            "from src.scripts.": "from src.scripts.",
            "import src.scripts.": "import src.scripts.",
            
            # 系统模块
            "from src.systems.": "from src.systems.",
            "import src.systems.": "import src.systems.",
            
            # Web模块
            "from src.web.web_config": "from src.web.web_config",
            "import src.web.web_config": "import src.web.web_config",
            
            # 工具模块
            "from tools.dev.": "from tools.dev.dev.",
            "import tools.dev.": "import tools.dev.dev.",
        }
        
        # 相对导入修复
        self.relative_imports = {
            "src/core/": {
                "from save_manager": "from .save_manager",
                "from cheat_manager": "from .cheat_manager", 
                "from device_manager": "from .device_manager",
                "from config_manager": "from .config_manager",
            },
            "src/scripts/": {
                "from src.core.": "from ..core.",
                "from src.scripts.": "from .",
            }
        }
    
    def find_python_files(self) -> List[Path]:
        """查找所有Python文件"""
        python_files = []
        
        # 扫描源码目录
        for pattern in ["src/**/*.py", "tests/**/*.py", "tools/**/*.py"]:
            python_files.extend(self.project_root.glob(pattern))
        
        # 添加根目录的Python文件
        python_files.extend(self.project_root.glob("*.py"))
        
        return python_files
    
    def fix_file_imports(self, file_path: Path) -> bool:
        """修复单个文件的导入"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 应用路径映射
            for old_import, new_import in self.path_mappings.items():
                content = content.replace(old_import, new_import)
            
            # 应用相对导入修复
            file_dir = str(file_path.parent.relative_to(self.project_root))
            if file_dir in self.relative_imports:
                for old_import, new_import in self.relative_imports[file_dir].items():
                    content = content.replace(old_import, new_import)
            
            # 如果内容有变化，写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ 修复文件失败 {file_path}: {e}")
            return False
    
    def fix_all_imports(self):
        """修复所有文件的导入"""
        print("🔧 开始修复导入路径...")
        
        python_files = self.find_python_files()
        fixed_count = 0
        
        for file_path in python_files:
            if self.fix_file_imports(file_path):
                print(f"  ✅ 修复: {file_path.relative_to(self.project_root)}")
                fixed_count += 1
        
        print(f"✅ 导入路径修复完成，共修复 {fixed_count} 个文件")
    
    def create_init_files(self):
        """创建__init__.py文件"""
        print("📝 创建__init__.py文件...")
        
        init_dirs = [
            "src",
            "src/core", 
            "src/scripts",
            "src/web",
            "src/systems",
            "tests",
            "tests/unit",
            "tests/fixtures",
            "tools",
            "tools/dev"
        ]
        
        for dir_path in init_dirs:
            init_file = self.project_root / dir_path / "__init__.py"
            if not init_file.exists():
                init_file.touch()
                print(f"  📝 创建: {init_file.relative_to(self.project_root)}")

def main():
    """主函数"""
    fixer = ImportFixer()
    fixer.create_init_files()
    fixer.fix_all_imports()

if __name__ == "__main__":
    main()
