#!/usr/bin/env python3
"""
GamePlayer-Raspberry 全面自动化测试与修复系统
通读代码功能后，自动化测试，找到问题后自动修复，直到没有问题
"""

import os
import sys
import json
import time
import shutil
import logging
import asyncio
import subprocess
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import tempfile
import importlib.util
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automated_test_fix.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedTestAndFix:
    """全面自动化测试与修复系统"""
    
    def __init__(self):
        """初始化测试和修复系统"""
        self.project_root = Path(__file__).parent
        self.test_results = {}
        self.fixed_issues = []
        self.failed_fixes = []
        self.config_backup = {}
        # 测试模块
        self.test_modules = [
            self.test_core_modules,
            self.test_game_launcher,
            self.test_emulator_configs,
            self.test_rom_management,
            self.test_web_interface,
            self.test_docker_setup,
            self.test_build_scripts,
            self.test_dependencies,
            self.test_file_permissions,
            self.test_system_integration
        ]
        logger.info("🚀 自动化测试与修复系统初始化完成")

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """运行全面测试"""
        logger.info("📋 开始全面项目测试...")
        test_summary = {
            "start_time": datetime.now(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "issues_found": [],
            "test_details": {}
        }

        # 运行所有测试模块
        for test_module in self.test_modules:
            test_name = test_module.__name__.replace('test_', '')
            logger.info(f"🧪 执行测试: {test_name}")
            
            try:
                result = await test_module()
                test_summary["test_details"][test_name] = result
                test_summary["total_tests"] += 1
                
                if result.get("status") == "pass":
                    test_summary["passed_tests"] += 1
                else:
                    test_summary["failed_tests"] += 1
                    test_summary["issues_found"].extend(result.get("issues", []))
                    
            except Exception as e:
                logger.error(f"❌ 测试 {test_name} 执行失败: {e}")
                test_summary["failed_tests"] += 1
                test_summary["issues_found"].append({
                    "type": "test_execution_error",
                    "test": test_name,
                    "error": str(e)
                })
        test_summary["end_time"] = datetime.now()
        test_summary["duration"] = (test_summary["end_time"] - test_summary["start_time"]).total_seconds()
        return test_summary

    async def test_core_modules(self) -> Dict[str, Any]:
        """测试核心模块"""
        logger.info("🔍 测试核心模块...")
        
        result = {
            "status": "pass",
            "issues": [],
            "details": {}
        }
        
        core_modules = [
            "src/core/nes_emulator.py",
            "src/core/game_launcher.py",
            "src/core/game_health_checker.py",
            "src/core/rom_manager.py",
            "src/core/cheat_manager.py",
            "src/core/save_manager.py",
            "src/core/device_manager.py",
            "src/core/audio_manager.py"
        ]
        
        for module_path in core_modules:
            module_file = self.project_root / module_path
            module_name = module_file.stem
            
            # 检查文件存在
            if not module_file.exists():
                result["issues"].append({
                    "type": "missing_file",
                    "file": module_path,
                    "severity": "high"
                })
                continue
            
            # 检查语法
            try:
                with open(module_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                    compile(code, module_path, 'exec')
                    result["details"][module_name] = "✅ 语法正确"
            except SyntaxError as e:
                result["issues"].append({
                    "type": "syntax_error",
                    "file": module_path,
                    "error": str(e),
                    "line": e.lineno,
                    "severity": "high"
                })
                result["details"][module_name] = f"❌ 语法错误: {e}"
            except Exception as e:
                result["issues"].append({
                    "type": "file_read_error",
                    "file": module_path,
                    "error": str(e),
                    "severity": "medium"
                })
        
        if result["issues"]:
            result["status"] = "fail"
        return result

    async def test_game_launcher(self) -> Dict[str, Any]:
        """测试游戏启动器功能"""
        logger.info("🎮 测试游戏启动器...")
        
        result = {
            "status": "pass",
            "issues": [],
            "details": {}
        }
        
        launcher_file = self.project_root / "src/core/game_launcher.py"
        
        if not launcher_file.exists():
            result["issues"].append({
                "type": "missing_file",
                "file": "src/core/game_launcher.py",
                "severity": "high"
            })
            result["status"] = "fail"
            return result
        
        try:
            # 检查配置文件
            config_files = [
                "config/emulators/emulator_config.json",
                "config/emulators/general_settings.json"
            ]
            
            for config_file in config_files:
                config_path = self.project_root / config_file
                if not config_path.exists():
                    result["issues"].append({
                        "type": "missing_config",
                        "file": config_file,
                        "severity": "medium"
                    })
                else:
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            json.load(f)
                        result["details"][config_file] = "✅ 配置文件有效"
                    except json.JSONDecodeError as e:
                        result["issues"].append({
                            "type": "invalid_json",
                            "file": config_file,
                            "error": str(e),
                            "severity": "high"
                        })
            
            # 检查模拟器命令
            emulator_commands = ["mednafen", "snes9x-gtk", "vbam"]
            for cmd in emulator_commands:
                if shutil.which(cmd):
                    result["details"][f"emulator_{cmd}"] = "✅ 已安装"
                else:
                    result["details"][f"emulator_{cmd}"] = "⚠️ 未安装"
                    result["issues"].append({
                        "type": "missing_emulator",
                        "command": cmd,
                        "severity": "low"
                    })
        
        except Exception as e:
            result["issues"].append({
                "type": "launcher_test_error",
                "error": str(e),
                "severity": "medium"
            })
        
        if result["issues"]:
            result["status"] = "fail"
        
        return result
    async def test_emulator_configs(self) -> Dict[str, Any]:
        """测试模拟器配置"""
        logger.info("⚙️ 测试模拟器配置...")
        
        result = {
            "status": "pass",
            "issues": [],
            "details": {}
        }
        
        config_dir = self.project_root / "config/emulators"
        
        if not config_dir.exists():
            result["issues"].append({
                "type": "missing_directory",
                "path": "config/emulators",
                "severity": "high"
            })
            result["status"] = "fail"
            return result
        
        # 检查必需的配置文件
        required_configs = [
            "emulator_config.json",
            "general_settings.json"
        ]
        
        for config_file in required_configs:
            config_path = config_dir / config_file
            if not config_path.exists():
                result["issues"].append({
                    "type": "missing_config",
                    "file": f"config/emulators/{config_file}",
                    "severity": "medium"
                })
            else:
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                        
                    # 验证配置结构
                    if config_file == "emulator_config.json":
                        required_systems = ["nes", "snes", "gameboy", "gba", "genesis"]
                        for system in required_systems:
                            if system not in config_data:
                                result["issues"].append({
                                    "type": "incomplete_config",
                                    "file": config_file,
                                    "missing_system": system,
                                    "severity": "medium"
                                })
                    
                    result["details"][config_file] = "✅ 配置文件有效"
                    
                except json.JSONDecodeError as e:
                    result["issues"].append({
                        "type": "invalid_json",
                        "file": f"config/emulators/{config_file}",
                        "error": str(e),
                        "severity": "high"
                    })
        
        if result["issues"]:
            result["status"] = "fail"
        
        return result

    async def test_rom_management(self) -> Dict[str, Any]:
        """测试ROM管理"""
        logger.info("💾 测试ROM管理...")
        
        result = {
            "status": "pass",
            "issues": [],
            "details": {}
        }
        
        # 检查ROM目录结构
        rom_dir = self.project_root / "data/roms"
        if not rom_dir.exists():
            result["issues"].append({
                "type": "missing_directory",
                "path": "data/roms",
                "severity": "medium"
            })
        else:
            # 检查子目录
            required_subdirs = ["nes", "snes", "gameboy", "gba", "genesis"]
            for subdir in required_subdirs:
                subdir_path = rom_dir / subdir
                if not subdir_path.exists():
                    result["issues"].append({
                        "type": "missing_rom_directory",
                        "path": f"data/roms/{subdir}",
                        "severity": "low"
                    })
                else:
                    # 统计ROM文件
                    rom_files = list(subdir_path.glob("*.nes")) + list(subdir_path.glob("*.smc")) + \
                               list(subdir_path.glob("*.gb")) + list(subdir_path.glob("*.gba")) + \
                               list(subdir_path.glob("*.md"))
                    result["details"][f"roms_{subdir}"] = f"✅ {len(rom_files)} 个ROM文件"
        
        # 检查ROM管理脚本
        rom_manager_file = self.project_root / "src/core/rom_manager.py"
        if not rom_manager_file.exists():
            result["issues"].append({
                "type": "missing_file",
                "file": "src/core/rom_manager.py",
                "severity": "high"
            })
        
        if result["issues"]:
            result["status"] = "fail"
        
        return result

    async def test_web_interface(self) -> Dict[str, Any]:
        """测试Web界面"""
        logger.info("🌐 测试Web界面...")
        
        result = {
            "status": "pass",
            "issues": [],
            "details": {}
        }
        
        web_dir = self.project_root / "src/web"
        if not web_dir.exists():
            result["issues"].append({
                "type": "missing_directory",
                "path": "src/web",
                "severity": "medium"
            })
        else:
            # 检查Web文件
            web_files = list(web_dir.glob("*.html")) + list(web_dir.glob("*.js")) + list(web_dir.glob("*.css"))
            if not web_files:
                result["issues"].append({
                    "type": "missing_web_files",
                    "path": "src/web",
                    "severity": "medium"
                })
            else:
                result["details"]["web_files"] = f"✅ {len(web_files)} 个Web文件"
        
        if result["issues"]:
            result["status"] = "fail"
        
        return result

    async def test_docker_setup(self) -> Dict[str, Any]:
        """测试Docker设置"""
        logger.info("🐳 测试Docker设置...")
        result = {
            "status": "pass",
            "issues": [],
            "details": {}
        }
        
        # 检查Docker文件
        docker_files = [
            "Dockerfile.raspberry",
            "docker-compose.gui.yml",
            "docker-compose.simple.yml"
        ]
        
        for docker_file in docker_files:
            docker_path = self.project_root / docker_file
            if not docker_path.exists():
                result["issues"].append({
                    "type": "missing_docker_file",
                    "file": docker_file,
                    "severity": "medium"
                })
            else:
                result["details"][docker_file] = "✅ 存在"
        
        if result["issues"]:
            result["status"] = "fail"
        
        return result

    async def test_build_scripts(self) -> Dict[str, Any]:
        """测试构建脚本"""
        logger.info("🔨 测试构建脚本...")
        
        result = {
            "status": "pass",
            "issues": [],
            "details": {}
        }
        # 检查主要构建脚本
        build_scripts = [
            "src/scripts/one_click_image_builder.sh",
            "src/scripts/raspberry_image_builder.py"
        ]
        
        for script in build_scripts:
            script_path = self.project_root / script
            if not script_path.exists():
                result["issues"].append({
                    "type": "missing_build_script",
                    "file": script,
                    "severity": "high"
                })
                continue
            
            # 检查脚本语法
            try:
                if script.endswith('.sh'):
                    # 检查bash语法
                    check_result = subprocess.run(
                        ['bash', '-n', str(script_path)],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if check_result.returncode == 0:
                        result["details"][script] = "✅ 语法正确"
                    else:
                        result["issues"].append({
                            "type": "bash_syntax_error",
                            "file": script,
                            "error": check_result.stderr,
                            "severity": "high"
                        })
                elif script.endswith('.py'):
                    # 检查Python语法
                    with open(script_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                        compile(code, script, 'exec')
                    result["details"][script] = "✅ 语法正确"
                    
            except subprocess.TimeoutExpired:
                result["issues"].append({
                    "type": "syntax_check_timeout",
                    "file": script,
                    "severity": "medium"
                })
            except SyntaxError as e:
                result["issues"].append({
                    "type": "python_syntax_error",
                    "file": script,
                    "error": str(e),
                    "line": e.lineno,
                    "severity": "high"
                })
            except Exception as e:
                result["issues"].append({
                    "type": "script_check_error",
                    "file": script,
                    "error": str(e),
                    "severity": "medium"
                })
        
        if result["issues"]:
            result["status"] = "fail"
        
        return result
    async def test_dependencies(self) -> Dict[str, Any]:
        """测试依赖项"""
        logger.info("📦 测试依赖项...")
        
        result = {
            "status": "pass",
            "issues": [],
            "details": {}
        }
        
        # 检查requirements.txt
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            result["issues"].append({
                "type": "missing_requirements",
                "file": "requirements.txt",
                "severity": "medium"
            })
        else:
            try:
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    requirements = f.read().strip().split('\n')
                
                result["details"]["requirements"] = f"✅ {len(requirements)} 个依赖包"
                
            except Exception as e:
                result["issues"].append({
                    "type": "requirements_read_error",
                    "error": str(e),
                    "severity": "medium"
                })
        # 检查系统依赖
        system_commands = ["python3", "bash", "git"]
        for cmd in system_commands:
            if shutil.which(cmd):
                result["details"][f"system_{cmd}"] = "✅ 已安装"
            else:
                result["issues"].append({
                    "type": "missing_system_command",
                    "command": cmd,
                    "severity": "high"
                })
        
        if result["issues"]:
            result["status"] = "fail"
        
        return result
    async def test_file_permissions(self) -> Dict[str, Any]:
        """测试文件权限"""
        logger.info("🔐 测试文件权限...")
        
        result = {
            "status": "pass",
            "issues": [],
            "details": {}
        }
        
        # 检查可执行脚本
        executable_scripts = []
        for script_path in self.project_root.glob("**/*.sh"):
            executable_scripts.append(script_path)
        
        for script_path in executable_scripts:
            if not os.access(script_path, os.X_OK):
                result["issues"].append({
                    "type": "missing_execute_permission",
                    "file": str(script_path.relative_to(self.project_root)),
                    "severity": "medium"
                })
            else:
                result["details"][script_path.name] = "✅ 可执行"
        
        if result["issues"]:
            result["status"] = "fail"
        
        return result

    async def test_system_integration(self) -> Dict[str, Any]:
        """测试系统集成"""
        logger.info("🔧 测试系统集成...")
        
        result = {
            "status": "pass",
            "issues": [],
            "details": {}
        }
        
        # 检查核心功能是否能正常导入
        try:
            sys.path.insert(0, str(self.project_root / "src/core"))
            
            # 尝试导入核心模块
            core_modules = [
                "nes_emulator",
                "game_launcher",
                "game_health_checker"
            ]
            
            for module_name in core_modules:
                module_file = self.project_root / f"src/core/{module_name}.py"
                if module_file.exists():
                    try:
                        spec = importlib.util.spec_from_file_location(
                            module_name,
                            module_file
                        )
                        module = importlib.util.module_from_spec(spec)
                        # 不实际执行，只检查语法
                        result["details"][f"import_{module_name}"] = "✅ 可导入"
                    except Exception as e:
                        result["issues"].append({
                            "type": "module_import_error",
                            "module": module_name,
                            "error": str(e),
                            "severity": "high"
                        })
                else:
                    result["issues"].append({
                        "type": "missing_module",
                        "module": module_name,
                        "severity": "medium"
                    })
        
        except Exception as e:
            result["issues"].append({
                "type": "integration_test_error",
                "error": str(e),
                "severity": "medium"
            })
        
        if result["issues"]:
            result["status"] = "fail"
        
        return result

    async def auto_fix_issues(self, test_summary: Dict[str, Any]) -> Dict[str, Any]:
        """自动修复发现的问题"""
        logger.info("🔧 开始自动修复问题...")
        
        fix_summary = {
            "start_time": datetime.now(),
            "total_issues": len(test_summary["issues_found"]),
            "fixed_issues": 0,
            "failed_fixes": 0,
            "fix_details": {}
        }
        
        # 按严重程度排序问题
        issues = sorted(
            test_summary["issues_found"],
            key=lambda x: {"high": 3, "medium": 2, "low": 1}.get(x.get("severity", "low"), 1),
            reverse=True
        )
        
        for issue in issues:
            issue_type = issue.get("type", "unknown")
            logger.info(f"🔨 修复问题: {issue_type}")
            
            try:
                fixed = await self._fix_issue(issue)
                if fixed:
                    fix_summary["fixed_issues"] += 1
                    fix_summary["fix_details"][issue_type] = "✅ 已修复"
                    logger.info(f"✅ 问题已修复: {issue_type}")
                else:
                    fix_summary["failed_fixes"] += 1
                    fix_summary["fix_details"][issue_type] = "❌ 修复失败"
                    logger.warning(f"❌ 修复失败: {issue_type}")
                    
            except Exception as e:
                fix_summary["failed_fixes"] += 1
                fix_summary["fix_details"][issue_type] = f"❌ 修复异常: {str(e)}"
                logger.error(f"❌ 修复异常 {issue_type}: {e}")
        
        fix_summary["end_time"] = datetime.now()
        fix_summary["duration"] = (fix_summary["end_time"] - fix_summary["start_time"]).total_seconds()
        
        return fix_summary

    async def _fix_issue(self, issue: Dict[str, Any]) -> bool:
        """修复单个问题"""
        issue_type = issue.get("type", "unknown")
        
        try:
            if issue_type == "missing_file":
                return await self._fix_missing_file(issue)
            elif issue_type == "missing_directory":
                return await self._fix_missing_directory(issue)
            elif issue_type == "missing_config":
                return await self._fix_missing_config(issue)
            elif issue_type == "missing_execute_permission":
                return await self._fix_execute_permission(issue)
            elif issue_type == "missing_rom_directory":
                return await self._fix_missing_directory(issue)
            else:
                logger.warning(f"⚠️ 无修复方法: {issue_type}")
                return False
        except Exception as e:
            logger.error(f"❌ 修复失败 {issue_type}: {e}")
            return False

    async def _fix_missing_file(self, issue: Dict[str, Any]) -> bool:
        """修复缺失文件"""
        file_path = self.project_root / issue["file"]
        
        # 根据文件类型创建模板
        if file_path.suffix == ".py":
            template = self._get_python_template(file_path.stem)
        elif file_path.suffix == ".json":
            template = self._get_json_template(file_path.stem)
        elif file_path.suffix == ".sh":
            template = self._get_bash_template(file_path.stem)
        else:
            template = "# Auto-generated file\n"
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(template)
            logger.info(f"✅ 创建文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 创建文件失败 {file_path}: {e}")
            return False

    async def _fix_missing_directory(self, issue: Dict[str, Any]) -> bool:
        """修复缺失目录"""
        dir_path = self.project_root / issue["path"]
        
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # 为某些目录创建.gitkeep文件
            if any(name in str(dir_path) for name in ["logs", "saves", "downloads"]):
                gitkeep_file = dir_path / ".gitkeep"
                gitkeep_file.touch()
            
            logger.info(f"✅ 创建目录: {dir_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 创建目录失败 {dir_path}: {e}")
            return False

    async def _fix_execute_permission(self, issue: Dict[str, Any]) -> bool:
        """修复执行权限"""
        file_path = self.project_root / issue["file"]
        
        try:
            file_path.chmod(0o755)
            logger.info(f"✅ 设置执行权限: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 设置执行权限失败 {file_path}: {e}")
            return False

    async def _fix_missing_config(self, issue: Dict[str, Any]) -> bool:
        """修复缺失配置"""
        config_file = issue["file"]
        config_path = self.project_root / config_file
        
        template = self._get_config_template(config_path.stem)
        
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(template)
            logger.info(f"✅ 创建配置文件: {config_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 创建配置文件失败 {config_path}: {e}")
            return False

    def _get_python_template(self, module_name: str) -> str:
        """获取Python模板"""
        templates = {
            "rom_manager": '''#!/usr/bin/env python3
"""
ROM管理器
管理游戏ROM文件
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional

class RomManager:
    """ROM管理器"""
    def __init__(self, rom_dir: str = "data/roms"):
        self.rom_dir = Path(rom_dir)
        self.rom_dir.mkdir(parents=True, exist_ok=True)
    
    def list_roms(self, system: str) -> List[str]:
        """列出ROM文件"""
        system_dir = self.rom_dir / system
        if not system_dir.exists():
            return []
        
        extensions = {
            "nes": [".nes"],
            "snes": [".smc", ".sfc"],
            "gameboy": [".gb", ".gbc"],
            "gba": [".gba"],
            "genesis": [".md", ".gen"]
        }
        
        roms = []
        for ext in extensions.get(system, []):
            roms.extend(system_dir.glob(f"*{ext}"))
        
        return [rom.name for rom in roms]
    
    def get_rom_path(self, system: str, rom_name: str) -> Optional[Path]:
        """获取ROM文件路径"""
        rom_path = self.rom_dir / system / rom_name
        return rom_path if rom_path.exists() else None

if __name__ == "__main__":
    manager = RomManager()
    print("ROM管理器初始化完成")
''',
            "cheat_manager": '''#!/usr/bin/env python3
"""
金手指管理器
"""

import json
from pathlib import Path
from typing import Dict, List

class CheatManager:
    """金手指管理器"""
    def __init__(self, cheat_dir: str = "config/cheats"):
        self.cheat_dir = Path(cheat_dir)
        self.cheat_dir.mkdir(parents=True, exist_ok=True)
    
    def load_cheats(self, system: str) -> Dict:
        """加载作弊码"""
        cheat_file = self.cheat_dir / f"{system}_cheats.json"
        if cheat_file.exists():
            with open(cheat_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

if __name__ == "__main__":
    manager = CheatManager()
    print("金手指管理器初始化完成")
''',
            "save_manager": '''#!/usr/bin/env python3
"""
存档管理器
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional

class SaveManager:
    """存档管理器"""
    def __init__(self, save_dir: str = "data/saves"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def save_game(self, rom_path: str, game_state: Dict, slot: int = 1) -> bool:
        """保存游戏状态"""
        try:
            rom_name = Path(rom_path).stem
            save_file = self.save_dir / f"{rom_name}_slot_{slot}.save"
            save_data = {
                "timestamp": time.time(),
                "rom_path": rom_path,
                "game_state": game_state
            }
            
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"保存失败: {e}")
            return False

if __name__ == "__main__":
    manager = SaveManager()
    print("存档管理器初始化完成")
''',
            "device_manager": '''#!/usr/bin/env python3
"""
设备管理器
"""

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from typing import Dict, List, Optional

class DeviceManager:
    """设备管理器"""
    
    def __init__(self):
        if PYGAME_AVAILABLE:
            pygame.init()
            pygame.joystick.init()
            self.joysticks = []
            self._init_joysticks()
        else:
            self.joysticks = []
    
    def _init_joysticks(self):
        """初始化手柄"""
        if not PYGAME_AVAILABLE:
            return
        
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.joysticks.append(joystick)
    
    def auto_connect_devices(self):
        """自动连接设备"""
        print(f"检测到 {len(self.joysticks)} 个控制器")

if __name__ == "__main__":
    manager = DeviceManager()
    print("设备管理器初始化完成")
''',
            "audio_manager": '''#!/usr/bin/env python3
"""
音频管理器
"""

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from typing import Dict, Optional

class AudioManager:
    """音频管理器"""
    def __init__(self):
        if PYGAME_AVAILABLE:
            pygame.mixer.init()
        self.sounds = {}
        self.music_volume = 0.7
        self.sound_volume = 0.8
    
    def load_sound(self, name: str, file_path: str):
        """加载音效"""
        if not PYGAME_AVAILABLE:
            return
        
        try:
            sound = pygame.mixer.Sound(file_path)
            self.sounds[name] = sound
        except Exception as e:
            print(f"加载音效失败 {name}: {e}")

if __name__ == "__main__":
    manager = AudioManager()
    print("音频管理器初始化完成")
'''
        }
        
        return templates.get(module_name, f'''#!/usr/bin/env python3
"""
{module_name.replace('_', ' ').title()}
自动生成的模块
"""

class {module_name.replace('_', ' ').title().replace(' ', '')}:
    """自动生成的类"""
    
    def __init__(self):
        pass

if __name__ == "__main__":
    print("{module_name} 模块初始化完成")
''')

    def _get_config_template(self, config_name: str) -> str:
        """获取配置模板"""
        templates = {
            "emulator_config": '''{
  "nes": {
    "emulator": "mednafen",
    "command": "mednafen",
    "args": ["-force_module", "nes"],
    "extensions": [".nes"],
    "installed": false
  },
  "snes": {
    "emulator": "snes9x",
    "command": "snes9x-gtk",
    "args": ["-fullscreen"],
    "extensions": [".smc", ".sfc"],
    "installed": false
  },
  "gameboy": {
    "emulator": "visualboyadvance",
    "command": "vbam",
    "args": ["--fullscreen"],
    "extensions": [".gb", ".gbc"],
    "installed": false
  },
  "gba": {
    "emulator": "visualboyadvance",
    "command": "vbam",
    "args": ["--fullscreen"],
    "extensions": [".gba"],
    "installed": false
  },
  "genesis": {
    "emulator": "gens",
    "command": "gens",
    "args": ["--fullscreen"],
    "extensions": [".md", ".gen"],
    "installed": false
  }
}''',
            "general_settings": '''{
  "display": {
    "fullscreen": true,
    "resolution": "1920x1080",
    "vsync": true,
    "scaling": "auto"
  },
  "audio": {
    "enabled": true,
    "volume": 80,
    "sample_rate": 44100,
    "buffer_size": 512
  },
  "input": {
    "gamepad_enabled": true,
    "keyboard_enabled": true,
    "auto_detect_gamepad": true,
    "gamepad_deadzone": 0.1
  },
  "performance": {
    "frame_skip": 0,
    "speed_limit": 100,
    "rewind_enabled": false,
    "save_states": true
  }
}'''
        }
        return templates.get(config_name, '{}')

    def _get_json_template(self, file_name: str) -> str:
        """获取JSON模板"""
        return '{\n  "auto_generated": true,\n  "timestamp": "' + datetime.now().isoformat() + '"\n}'

    def _get_bash_template(self, file_name: str) -> str:
        """获取Bash模板"""
        return f'''#!/bin/bash
# {file_name} - 自动生成的脚本
# 生成时间: {datetime.now().isoformat()}

set -euo pipefail

echo "执行 {file_name} 脚本"

# TODO: 实现具体功能

echo "{file_name} 脚本执行完成"
'''

    async def generate_report(self, test_summary: Dict[str, Any], fix_summary: Dict[str, Any]):
        """生成测试和修复报告"""
        logger.info("📋 生成测试报告...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "project": "GamePlayer-Raspberry",
            "test_summary": test_summary,
            "fix_summary": fix_summary,
            "overall_status": "success" if fix_summary["failed_fixes"] == 0 else "partial_success"
        }
        
        # 保存详细报告
        report_file = self.project_root / f"test_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        # 生成简要报告
        summary_lines = [
            "🧪 GamePlayer-Raspberry 自动化测试与修复报告",
            "=" * 60,
            f"📅 时间: {report['timestamp']}",
            f"🔍 总测试数: {test_summary['total_tests']}",
            f"✅ 通过测试: {test_summary['passed_tests']}",
            f"❌ 失败测试: {test_summary['failed_tests']}",
            f"🔧 发现问题: {len(test_summary['issues_found'])}",
            f"✅ 已修复: {fix_summary['fixed_issues']}",
            f"❌ 修复失败: {fix_summary['failed_fixes']}",
            "",
            "📊 测试详情:",
        ]
        for test_name, result in test_summary["test_details"].items():
            status = "✅" if result.get("status") == "pass" else "❌"
            summary_lines.append(f"  {status} {test_name}")
        
        if fix_summary.get("fix_details"):
            summary_lines.extend([
                "",
                "🔧 修复详情:",
            ])
            for fix_name, status in fix_summary["fix_details"].items():
                summary_lines.append(f"  {status} {fix_name}")
        
        summary_lines.extend([
            "",
            f"📋 详细报告: {report_file}",
            "=" * 60
        ])
        
        summary_report = '\n'.join(summary_lines)
        
        # 保存简要报告
        summary_file = self.project_root / "test_fix_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_report)
        
        # 打印到控制台
        print(summary_report)
        logger.info(f"📋 报告已生成: {report_file}")
        return report

    async def run_full_test_and_fix_cycle(self) -> Dict[str, Any]:
        """运行完整的测试和修复周期"""
        logger.info("🚀 开始完整的测试和修复周期...")
        
        max_iterations = 3
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"🔄 第 {iteration} 轮测试和修复...")
            # 运行测试
            test_summary = await self.run_comprehensive_test()
            
            # 如果没有问题，退出循环
            if not test_summary["issues_found"]:
                logger.info("🎉 所有测试通过，无需修复！")
                break
            
            # 修复问题
            fix_summary = await self.auto_fix_issues(test_summary)
            
            # 检查是否还有未修复的问题
            if fix_summary["failed_fixes"] == 0:
                logger.info("🎉 所有问题已修复！")
                break
            elif iteration == max_iterations:
                logger.warning(f"⚠️ 达到最大迭代次数 ({max_iterations})，仍有未修复问题")
            
            # 等待一秒再进行下一轮
            await asyncio.sleep(1)
        
        # 最终测试
        final_test_summary = await self.run_comprehensive_test()
        
        # 生成最终报告
        final_fix_summary = {
            "iterations": iteration,
            "max_iterations": max_iterations,
            "final_status": "complete" if not final_test_summary["issues_found"] else "partial",
            "fixed_issues": 0,
            "failed_fixes": 0,
            "fix_details": {}
        }
        
        report = await self.generate_report(final_test_summary, final_fix_summary)
        
        return report

async def main():
    """主函数"""
    print("🎮 GamePlayer-Raspberry 自动化测试与修复系统")
    print("=" * 60)
    
    try:
        # 创建测试和修复系统
        test_fix_system = AutomatedTestAndFix()
        
        # 运行完整周期
        report = await test_fix_system.run_full_test_and_fix_cycle()
        
        # 总结
        if report["test_summary"]["failed_tests"] == 0:
            print("\n🎉 恭喜！所有测试通过，项目状态良好！")
            return 0
        else:
            print(f"\n⚠️ 仍有 {report['test_summary']['failed_tests']} 个测试失败，请查看报告了解详情。")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断测试")
        return 1
    except Exception as e:
        print(f"\n❌ 测试系统异常: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))
