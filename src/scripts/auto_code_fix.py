#!/usr/bin/env python3
"""
自动代码修复工具
检查并自动修复代码中的问题
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class AutoCodeFixer:
    """自动代码修复器"""
    
    def __init__(self):
        self.project_root = project_root
        self.issues_found = []
        self.fixes_applied = []
    
    def check_syntax_errors(self) -> List[Dict]:
        """检查Python语法错误"""
        print("🔍 检查Python语法错误...")
        
        syntax_errors = []
        
        # 查找所有Python文件
        for py_file in self.project_root.rglob("*.py"):
            try:
                result = subprocess.run(
                    ["python3", "-m", "py_compile", str(py_file)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode != 0:
                    syntax_errors.append({
                        "file": str(py_file),
                        "error": result.stderr,
                        "type": "syntax_error"
                    })
                    
            except Exception as e:
                syntax_errors.append({
                    "file": str(py_file),
                    "error": str(e),
                    "type": "check_error"
                })
        
        if syntax_errors:
            print(f"❌ 发现 {len(syntax_errors)} 个语法错误")
            for error in syntax_errors:
                print(f"  📁 {error['file']}")
                print(f"  ❌ {error['error']}")
        else:
            print("✅ 没有发现语法错误")
        
        return syntax_errors
    
    def check_duplicate_directories(self) -> List[Dict]:
        """检查重复目录"""
        print("🔍 检查重复目录...")
        
        duplicates = []
        
        # 检查ROM目录重复
        root_roms = self.project_root / "roms"
        data_roms = self.project_root / "data" / "roms"
        
        if root_roms.exists() and data_roms.exists():
            duplicates.append({
                "type": "duplicate_directory",
                "directories": [str(root_roms), str(data_roms)],
                "description": "ROM目录重复"
            })
        
        if duplicates:
            print(f"❌ 发现 {len(duplicates)} 个重复目录")
            for dup in duplicates:
                print(f"  📁 {dup['description']}: {dup['directories']}")
        else:
            print("✅ 没有发现重复目录")
        
        return duplicates
    
    def check_empty_files(self) -> List[Dict]:
        """检查空文件"""
        print("🔍 检查空文件...")
        
        empty_files = []
        
        # 检查ROM文件
        for rom_file in (self.project_root / "data" / "roms").rglob("*.nes"):
            if rom_file.stat().st_size == 0:
                empty_files.append({
                    "file": str(rom_file),
                    "type": "empty_rom",
                    "description": "空ROM文件"
                })
        
        # 检查重要的配置文件
        important_files = [
            "config/emulators/emulator_config.json",
            "config/covers/cover_sources.json",
            "data/web/games.json"
        ]
        
        for file_path in important_files:
            full_path = self.project_root / file_path
            if full_path.exists() and full_path.stat().st_size == 0:
                empty_files.append({
                    "file": str(full_path),
                    "type": "empty_config",
                    "description": "空配置文件"
                })
        
        if empty_files:
            print(f"❌ 发现 {len(empty_files)} 个空文件")
            for empty in empty_files:
                print(f"  📁 {empty['description']}: {empty['file']}")
        else:
            print("✅ 没有发现空文件")
        
        return empty_files
    
    def check_import_errors(self) -> List[Dict]:
        """检查导入错误"""
        print("🔍 检查模块导入...")
        
        import_errors = []
        
        # 测试主要模块
        test_modules = [
            "src.core.bing_cover_downloader",
            "src.core.game_health_checker", 
            "src.core.game_launcher",
            "src.scripts.simple_demo_server"
        ]
        
        for module in test_modules:
            try:
                __import__(module)
                print(f"  ✅ {module}")
            except Exception as e:
                import_errors.append({
                    "module": module,
                    "error": str(e),
                    "type": "import_error"
                })
                print(f"  ❌ {module}: {e}")
        
        return import_errors
    
    def fix_syntax_errors(self, syntax_errors: List[Dict]) -> int:
        """修复语法错误"""
        print("🔧 修复语法错误...")
        
        fixed_count = 0
        
        for error in syntax_errors:
            file_path = Path(error["file"])
            error_msg = error["error"]
            
            # 修复常见的语法错误
            if "invalid syntax. Perhaps you forgot a comma?" in error_msg:
                try:
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 查找并修复docstring位置错误
                    if '"""TODO: Add docstring"""' in content:
                        # 移除错误位置的docstring
                        content = content.replace('"""TODO: Add docstring"""', '')
                        
                        # 写回文件
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"  ✅ 修复语法错误: {file_path}")
                        fixed_count += 1
                        
                except Exception as e:
                    print(f"  ❌ 修复失败 {file_path}: {e}")
        
        return fixed_count
    
    def fix_duplicate_directories(self, duplicates: List[Dict]) -> int:
        """修复重复目录"""
        print("🔧 修复重复目录...")
        
        fixed_count = 0
        
        for dup in duplicates:
            if dup["type"] == "duplicate_directory":
                directories = dup["directories"]
                
                # 删除根目录下的roms文件夹，保留data/roms
                root_roms = Path(directories[0])
                if root_roms.name == "roms" and root_roms.parent == self.project_root:
                    try:
                        subprocess.run(["rm", "-rf", str(root_roms)], check=True)
                        print(f"  ✅ 删除重复目录: {root_roms}")
                        fixed_count += 1
                    except Exception as e:
                        print(f"  ❌ 删除失败 {root_roms}: {e}")
        
        return fixed_count
    
    def fix_empty_files(self, empty_files: List[Dict]) -> int:
        """修复空文件"""
        print("🔧 修复空文件...")
        
        fixed_count = 0
        
        for empty in empty_files:
            file_path = Path(empty["file"])
            file_type = empty["type"]
            
            try:
                if file_type == "empty_rom":
                    # 创建标准NES ROM文件
                    self._create_nes_rom(file_path)
                    print(f"  ✅ 修复空ROM: {file_path}")
                    fixed_count += 1
                    
                elif file_type == "empty_config":
                    # 创建基本配置文件
                    self._create_basic_config(file_path)
                    print(f"  ✅ 修复空配置: {file_path}")
                    fixed_count += 1
                    
            except Exception as e:
                print(f"  ❌ 修复失败 {file_path}: {e}")
        
        return fixed_count
    
    def _create_nes_rom(self, file_path: Path):
        """创建标准NES ROM文件"""
        # iNES头部格式
        ines_header = bytearray([
            0x4E, 0x45, 0x53, 0x1A,  # "NES" + MS-DOS EOF
            0x01,  # PRG ROM size (16KB units)
            0x01,  # CHR ROM size (8KB units)
            0x00,  # Flags 6
            0x00,  # Flags 7
            0x00,  # PRG RAM size
            0x00,  # Flags 9
            0x00,  # Flags 10
            0x00, 0x00, 0x00, 0x00, 0x00  # Padding
        ])
        
        # 创建16KB的PRG ROM数据
        prg_rom = bytearray(16384)
        
        # 创建8KB的CHR ROM数据
        chr_rom = bytearray(8192)
        
        # 组合完整的ROM
        rom_data = ines_header + prg_rom + chr_rom
        
        with open(file_path, 'wb') as f:
            f.write(rom_data)
    
    def _create_basic_config(self, file_path: Path):
        """创建基本配置文件"""
        if file_path.name == "emulator_config.json":
            config = {
                "emulators": {
                    "nes": {"command": "mednafen", "args": ["-force_module", "nes"]},
                    "snes": {"command": "mednafen", "args": ["-force_module", "snes"]},
                    "gameboy": {"command": "mednafen", "args": ["-force_module", "gb"]}
                }
            }
        elif file_path.name == "cover_sources.json":
            config = {
                "image_sources": [],
                "game_covers": {},
                "download_settings": {"timeout": 15, "max_retries": 3}
            }
        elif file_path.name == "games.json":
            config = {
                "nes": [],
                "snes": [],
                "gameboy": []
            }
        else:
            config = {}
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def run_full_check_and_fix(self):
        """运行完整的检查和修复"""
        print("🎮 自动代码修复工具")
        print("=" * 50)
        
        total_issues = 0
        total_fixes = 0
        
        # 1. 检查语法错误
        syntax_errors = self.check_syntax_errors()
        total_issues += len(syntax_errors)
        if syntax_errors:
            total_fixes += self.fix_syntax_errors(syntax_errors)
        
        # 2. 检查重复目录
        duplicates = self.check_duplicate_directories()
        total_issues += len(duplicates)
        if duplicates:
            total_fixes += self.fix_duplicate_directories(duplicates)
        
        # 3. 检查空文件
        empty_files = self.check_empty_files()
        total_issues += len(empty_files)
        if empty_files:
            total_fixes += self.fix_empty_files(empty_files)
        
        # 4. 检查导入错误
        import_errors = self.check_import_errors()
        total_issues += len(import_errors)
        
        # 5. 最终验证
        print("\n🔍 最终验证...")
        final_syntax_errors = self.check_syntax_errors()
        final_import_errors = self.check_import_errors()
        
        print(f"\n{'='*50}")
        print(f"📊 修复结果:")
        print(f"  发现问题: {total_issues} 个")
        print(f"  修复成功: {total_fixes} 个")
        print(f"  剩余问题: {len(final_syntax_errors) + len(final_import_errors)} 个")
        
        if len(final_syntax_errors) + len(final_import_errors) == 0:
            print("🎉 所有问题已修复！代码状态良好。")
            return True
        else:
            print("⚠️ 仍有部分问题需要手动处理。")
            return False

def main():
    """主函数"""
    fixer = AutoCodeFixer()
    success = fixer.run_full_check_and_fix()
    
    if success:
        print("\n✅ 自动修复完成，代码已准备就绪！")
    else:
        print("\n⚠️ 自动修复部分完成，请检查剩余问题。")

if __name__ == "__main__":
    main()
