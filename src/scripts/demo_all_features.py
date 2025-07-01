#!/usr/bin/env python3
"""
GamePlayer-Raspberry 完整功能演示
展示所有核心功能和特性
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class FeatureDemo:
    """功能演示类"""

    def __init__(self):
        """初始化演示环境"""
        self.project_root = project_root
        self.demo_results = {}
        
        # 颜色定义
        self.colors = {
            'red': '\033[0;31m',
            'green': '\033[0;32m',
            'yellow': '\033[1;33m',
            'blue': '\033[0;34m',
            'purple': '\033[0;35m',
            'cyan': '\033[0;36m',
            'white': '\033[1;37m',
            'reset': '\033[0m'
        }

    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{self.colors['cyan']}{'='*60}")
        print(f"🎮 {title}")
        print(f"{'='*60}{self.colors['reset']}")

    def print_step(self, step: str, status: str = "info"):
        """打印步骤"""
        color = self.colors.get(status, self.colors['white'])
        print(f"{color}▶ {step}{self.colors['reset']}")

    def print_success(self, message: str):
        """打印成功信息"""
        print(f"{self.colors['green']}✅ {message}{self.colors['reset']}")

    def print_warning(self, message: str):
        """打印警告信息"""
        print(f"{self.colors['yellow']}⚠️ {message}{self.colors['reset']}")

    def print_error(self, message: str):
        """打印错误信息"""
        print(f"{self.colors['red']}❌ {message}{self.colors['reset']}")

    def check_dependencies(self) -> bool:
        """检查依赖"""
        self.print_header("依赖检查")
        
        dependencies = {
            'pygame': '游戏界面和图形渲染',
            'requests': 'ROM下载和网络请求',
            'numpy': '数据处理和计算',
            'pathlib': '文件路径处理'
        }
        
        missing_deps = []
        
        for dep, description in dependencies.items():
            try:
                __import__(dep)
                self.print_success(f"{dep} - {description}")
            except ImportError:
                self.print_error(f"{dep} - {description}")
                missing_deps.append(dep)
        
        if missing_deps:
            self.print_warning(f"缺失依赖: {', '.join(missing_deps)}")
            self.print_warning("请运行: pip3 install " + " ".join(missing_deps))
            return False
        
        return True

    def check_project_structure(self) -> bool:
        """检查项目结构"""
        self.print_header("项目结构检查")
        
        required_dirs = [
            "src/core",
            "src/scripts", 
            "data/roms/nes",
            "data/saves",
            "config/system",
            "docs",
            "tests"
        ]
        
        missing_dirs = []
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                self.print_success(f"目录存在: {dir_path}")
            else:
                self.print_error(f"目录缺失: {dir_path}")
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            self.print_warning("创建缺失目录...")
            for dir_path in missing_dirs:
                full_path = self.project_root / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                self.print_success(f"已创建: {dir_path}")
        
        return True

    def demo_rom_management(self) -> bool:
        """演示ROM管理功能"""
        self.print_header("ROM管理演示")
        
        try:
            # 检查ROM下载器
            rom_downloader_path = self.project_root / "src/scripts/rom_downloader.py"
            if rom_downloader_path.exists():
                self.print_step("ROM下载器检查")
                self.print_success("ROM下载器可用")
                
                # 检查ROM目录
                roms_dir = self.project_root / "data/roms/nes"
                rom_count = len(list(roms_dir.glob("*.nes")))
                
                if rom_count > 0:
                    self.print_success(f"发现 {rom_count} 个ROM文件")
                else:
                    self.print_warning("未发现ROM文件，建议先下载")
                
                return True
            else:
                self.print_error("ROM下载器不存在")
                return False
                
        except Exception as e:
            self.print_error(f"ROM管理演示失败: {e}")
            return False

    def demo_game_launcher(self) -> bool:
        """演示游戏启动器"""
        self.print_header("游戏启动器演示")
        
        try:
            # 检查游戏启动器
            launcher_path = self.project_root / "src/scripts/nes_game_launcher.py"
            if launcher_path.exists():
                self.print_step("游戏启动器检查")
                self.print_success("游戏启动器可用")
                
                # 检查简单播放器
                player_path = self.project_root / "src/scripts/simple_nes_player.py"
                if player_path.exists():
                    self.print_success("简单NES播放器可用")
                
                # 检查游戏运行器
                runner_path = self.project_root / "src/scripts/run_nes_game.py"
                if runner_path.exists():
                    self.print_success("游戏运行器可用")
                
                return True
            else:
                self.print_error("游戏启动器不存在")
                return False
                
        except Exception as e:
            self.print_error(f"游戏启动器演示失败: {e}")
            return False

    def demo_emulator_integration(self) -> bool:
        """演示模拟器集成"""
        self.print_header("模拟器集成演示")
        
        try:
            # 检查Nesticle安装器
            nesticle_path = self.project_root / "src/core/nesticle_installer.py"
            if nesticle_path.exists():
                self.print_step("Nesticle安装器检查")
                self.print_success("Nesticle安装器可用")
            
            # 检查VirtuaNES安装器
            virtuanes_path = self.project_root / "src/core/virtuanes_installer.py"
            if virtuanes_path.exists():
                self.print_step("VirtuaNES安装器检查")
                self.print_success("VirtuaNES安装器可用")
            
            # 检查RetroPie安装器
            retropie_path = self.project_root / "src/core/retropie_installer.py"
            if retropie_path.exists():
                self.print_step("RetroPie安装器检查")
                self.print_success("RetroPie安装器可用")
            
            return True
            
        except Exception as e:
            self.print_error(f"模拟器集成演示失败: {e}")
            return False

    def demo_cheat_system(self) -> bool:
        """演示金手指系统"""
        self.print_header("金手指系统演示")
        
        try:
            # 检查金手指管理器
            cheat_manager_path = self.project_root / "src/core/cheat_manager.py"
            if cheat_manager_path.exists():
                self.print_step("金手指管理器检查")
                self.print_success("金手指管理器可用")
            
            # 检查金手指文件
            cheats_dir = self.project_root / "data/cheats"
            if cheats_dir.exists():
                cheat_files = list(cheats_dir.glob("*.cht"))
                if cheat_files:
                    self.print_success(f"发现 {len(cheat_files)} 个金手指文件")
                else:
                    self.print_warning("未发现金手指文件")
            
            return True
            
        except Exception as e:
            self.print_error(f"金手指系统演示失败: {e}")
            return False

    def demo_save_system(self) -> bool:
        """演示存档系统"""
        self.print_header("存档系统演示")
        
        try:
            # 检查存档管理器
            save_manager_path = self.project_root / "src/core/save_manager.py"
            if save_manager_path.exists():
                self.print_step("存档管理器检查")
                self.print_success("存档管理器可用")
            
            # 检查存档目录
            saves_dir = self.project_root / "data/saves"
            if saves_dir.exists():
                self.print_success("存档目录可用")
            else:
                saves_dir.mkdir(parents=True, exist_ok=True)
                self.print_success("已创建存档目录")
            
            return True
            
        except Exception as e:
            self.print_error(f"存档系统演示失败: {e}")
            return False

    def demo_config_management(self) -> bool:
        """演示配置管理"""
        self.print_header("配置管理演示")
        
        try:
            # 检查配置管理器
            config_manager_path = self.project_root / "src/core/config_manager.py"
            if config_manager_path.exists():
                self.print_step("配置管理器检查")
                self.print_success("配置管理器可用")
            
            # 检查配置文件
            config_dir = self.project_root / "config"
            if config_dir.exists():
                config_files = list(config_dir.rglob("*.json"))
                if config_files:
                    self.print_success(f"发现 {len(config_files)} 个配置文件")
                else:
                    self.print_warning("未发现配置文件")
            
            return True
            
        except Exception as e:
            self.print_error(f"配置管理演示失败: {e}")
            return False

    def demo_audio_system(self) -> bool:
        """演示音频系统"""
        self.print_header("音频系统演示")
        
        try:
            # 检查音频管理器
            audio_manager_path = self.project_root / "src/core/audio_manager.py"
            if audio_manager_path.exists():
                self.print_step("音频管理器检查")
                self.print_success("音频管理器可用")
            
            # 检查HDMI配置
            hdmi_config_path = self.project_root / "src/core/hdmi_config.py"
            if hdmi_config_path.exists():
                self.print_step("HDMI配置检查")
                self.print_success("HDMI配置可用")
            
            return True
            
        except Exception as e:
            self.print_error(f"音频系统演示失败: {e}")
            return False

    def demo_web_interface(self) -> bool:
        """演示Web界面"""
        self.print_header("Web界面演示")
        
        try:
            # 检查Web配置
            web_config_path = self.project_root / "src/web/web_config.py"
            if web_config_path.exists():
                self.print_step("Web配置检查")
                self.print_success("Web配置可用")
            
            # 检查Web文件
            web_dir = self.project_root / "data/web"
            if web_dir.exists():
                web_files = list(web_dir.glob("*.html"))
                if web_files:
                    self.print_success(f"发现 {len(web_files)} 个Web文件")
                else:
                    self.print_warning("未发现Web文件")
            
            return True
            
        except Exception as e:
            self.print_error(f"Web界面演示失败: {e}")
            return False

    def demo_docker_integration(self) -> bool:
        """演示Docker集成"""
        self.print_header("Docker集成演示")
        
        try:
            # 检查Docker脚本
            docker_scripts = [
                "src/scripts/raspberry_docker_sim.sh",
                "src/scripts/docker_gui_raspberry.sh",
                "src/scripts/docker_build_and_run.sh"
            ]
            
            available_scripts = []
            for script in docker_scripts:
                script_path = self.project_root / script
                if script_path.exists():
                    available_scripts.append(script)
                    self.print_success(f"Docker脚本可用: {script}")
            
            if available_scripts:
                self.print_success(f"发现 {len(available_scripts)} 个Docker脚本")
            else:
                self.print_warning("未发现Docker脚本")
            
            # 检查Dockerfile
            dockerfile_path = self.project_root / "Dockerfile.raspberry"
            if dockerfile_path.exists():
                self.print_success("Dockerfile可用")
            
            return True
            
        except Exception as e:
            self.print_error(f"Docker集成演示失败: {e}")
            return False

    def demo_testing_framework(self) -> bool:
        """演示测试框架"""
        self.print_header("测试框架演示")
        
        try:
            # 检查测试目录
            tests_dir = self.project_root / "tests"
            if tests_dir.exists():
                test_files = list(tests_dir.rglob("test_*.py"))
                if test_files:
                    self.print_success(f"发现 {len(test_files)} 个测试文件")
                    
                    # 显示测试文件
                    for test_file in test_files[:5]:  # 只显示前5个
                        relative_path = test_file.relative_to(self.project_root)
                        self.print_step(f"测试文件: {relative_path}")
                else:
                    self.print_warning("未发现测试文件")
            else:
                self.print_warning("测试目录不存在")
            
            return True
            
        except Exception as e:
            self.print_error(f"测试框架演示失败: {e}")
            return False

    def demo_development_tools(self) -> bool:
        """演示开发工具"""
        self.print_header("开发工具演示")
        
        try:
            # 检查开发工具
            dev_tools = [
                "tools/dev/code_analyzer.py",
                "tools/dev/code_optimizer.py",
                "tools/dev/auto_optimizer.py"
            ]
            
            available_tools = []
            for tool in dev_tools:
                tool_path = self.project_root / tool
                if tool_path.exists():
                    available_tools.append(tool)
                    self.print_success(f"开发工具可用: {tool}")
            
            if available_tools:
                self.print_success(f"发现 {len(available_tools)} 个开发工具")
            else:
                self.print_warning("未发现开发工具")
            
            return True
            
        except Exception as e:
            self.print_error(f"开发工具演示失败: {e}")
            return False

    def generate_demo_report(self) -> Dict[str, Any]:
        """生成演示报告"""
        self.print_header("生成演示报告")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project": "GamePlayer-Raspberry",
            "version": "3.0.0",
            "features": self.demo_results,
            "summary": {
                "total_features": len(self.demo_results),
                "successful_features": sum(1 for result in self.demo_results.values() if result),
                "failed_features": sum(1 for result in self.demo_results.values() if not result)
            }
        }
        
        # 保存报告
        report_path = self.project_root / "docs/reports/demo_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.print_success(f"演示报告已保存: {report_path}")
        return report

    def run_demo(self):
        """运行完整演示"""
        self.print_header("GamePlayer-Raspberry 完整功能演示")
        
        print(f"{self.colors['cyan']}🎮 欢迎使用 GamePlayer-Raspberry 3.0.0")
        print(f"📁 项目根目录: {self.project_root}")
        print(f"🕐 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}{self.colors['reset']}")
        
        # 运行各项演示
        demos = [
            ("依赖检查", self.check_dependencies),
            ("项目结构检查", self.check_project_structure),
            ("ROM管理演示", self.demo_rom_management),
            ("游戏启动器演示", self.demo_game_launcher),
            ("模拟器集成演示", self.demo_emulator_integration),
            ("金手指系统演示", self.demo_cheat_system),
            ("存档系统演示", self.demo_save_system),
            ("配置管理演示", self.demo_config_management),
            ("音频系统演示", self.demo_audio_system),
            ("Web界面演示", self.demo_web_interface),
            ("Docker集成演示", self.demo_docker_integration),
            ("测试框架演示", self.demo_testing_framework),
            ("开发工具演示", self.demo_development_tools)
        ]
        
        for demo_name, demo_func in demos:
            try:
                result = demo_func()
                self.demo_results[demo_name] = result
            except Exception as e:
                self.print_error(f"{demo_name} 执行异常: {e}")
                self.demo_results[demo_name] = False
        
        # 生成报告
        report = self.generate_demo_report()
        
        # 显示总结
        self.print_header("演示总结")
        
        summary = report["summary"]
        print(f"📊 总功能数: {summary['total_features']}")
        print(f"✅ 成功功能: {summary['successful_features']}")
        print(f"❌ 失败功能: {summary['failed_features']}")
        
        success_rate = (summary['successful_features'] / summary['total_features']) * 100
        print(f"📈 成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            self.print_success("🎉 系统状态良好！")
        elif success_rate >= 60:
            self.print_warning("⚠️ 系统状态一般，建议检查失败的功能")
        else:
            self.print_error("❌ 系统状态较差，需要修复多个功能")
        
        print(f"\n{self.colors['cyan']}📋 详细报告: docs/reports/demo_report.json")
        print(f"🎮 开始游戏: ./quick_start.sh{self.colors['reset']}")


def main():
    """主函数"""
    try:
        demo = FeatureDemo()
        demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️ 演示被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 演示执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
