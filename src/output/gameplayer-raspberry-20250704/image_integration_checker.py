#!/usr/bin/env python3
"""
镜像集成检查器
检查树莓派镜像中集成的所有功能和组件
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ImageIntegrationChecker:
    """镜像集成检查器"""

    def __init__(self, project_root: str = None):
        """TODO: 添加文档字符串"""
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.check_results = {}

    def check_all_components(self) -> Dict[str, Dict]:
        """检查所有组件"""
        print("🔍 开始检查镜像集成组件...")
        print("=" * 50)

        checks = [
            ("核心脚本", self.check_core_scripts),
            ("ROM文件", self.check_rom_files),
            ("存档系统", self.check_save_system),
            ("金手指系统", self.check_cheat_system),
            ("Web界面", self.check_web_interface),
            ("Docker配置", self.check_docker_config),
            ("自动启动", self.check_autostart_config),
            ("设备管理", self.check_device_management),
            ("配置文件", self.check_config_files),
            ("文档和说明", self.check_documentation)
        ]

        for check_name, check_func in checks:
            print(f"\n📋 检查 {check_name}...")
            try:
                result = check_func()
                self.check_results[check_name] = result
                self._print_check_result(check_name, result)
            except Exception as e:
                self.check_results[check_name] = {
                    "status": "error",
                    "message": f"检查失败: {e}",
                    "items": []
                }
                print(f"❌ {check_name}: 检查失败 - {e}")

        return self.check_results

    def check_core_scripts(self) -> Dict:
        """检查核心脚本"""
        scripts_dir = self.project_root / "src" / "scripts"
        required_scripts = [
            "enhanced_game_launcher.py",
            "nes_game_launcher.py",
            "run_nes_game.py",
            "rom_downloader.py",
            "rom_manager.py",
            "raspberry_image_builder.py",
            "one_click_image_builder.sh",
            "smart_installer.py"
        ]

        found_scripts = []
        missing_scripts = []

        for script in required_scripts:
            script_path = scripts_dir / script
            if script_path.exists():
                found_scripts.append({
                    "name": script,
                    "path": str(script_path),
                    "size": script_path.stat().st_size,
                    "executable": os.access(script_path, os.X_OK)
                })
            else:
                missing_scripts.append(script)

        return {
            "status": "success" if not missing_scripts else "warning",
            "message": f"找到 {len(found_scripts)}/{len(required_scripts)} 个核心脚本",
            "items": found_scripts,
            "missing": missing_scripts
        }

    def check_rom_files(self) -> Dict:
        """检查ROM文件"""
        roms_dir = self.project_root / "data" / "roms" / "nes"

        if not roms_dir.exists():
            return {
                "status": "warning",
                "message": "ROM目录不存在",
                "items": []
            }

        rom_files = list(roms_dir.glob("*.nes"))
        catalog_file = roms_dir / "rom_catalog.json"
        playlists_dir = roms_dir / "playlists"

        catalog_exists = catalog_file.exists()
        playlists_exist = playlists_dir.exists()

        return {
            "status": "success" if rom_files else "warning",
            "message": f"找到 {len(rom_files)} 个ROM文件",
            "items": [
                {
                    "name": rom.name,
                    "size": rom.stat().st_size,
                    "path": str(rom)
                } for rom in rom_files
            ],
            "catalog": catalog_exists,
            "playlists": playlists_exist
        }

    def check_save_system(self) -> Dict:
        """检查存档系统"""
        saves_dir = self.project_root / "data" / "saves"
        core_dir = self.project_root / "src" / "core"

        save_manager_exists = (core_dir / "save_manager.py").exists()
        saves_dir_exists = saves_dir.exists()

        save_files = []
        if saves_dir_exists:
            save_files = list(saves_dir.glob("*.sav")) + list(saves_dir.glob("*_info.json"))

        return {
            "status": "success" if save_manager_exists else "warning",
            "message": f"存档系统 {'已集成' if save_manager_exists else '未集成'}",
            "items": [
                {"component": "SaveManager", "exists": save_manager_exists},
                {"component": "存档目录", "exists": saves_dir_exists},
                {"component": "存档文件", "count": len(save_files)}
            ]
        }

    def check_cheat_system(self) -> Dict:
        """检查金手指系统"""
        core_dir = self.project_root / "src" / "core"
        cheats_dir = self.project_root / "data" / "cheats"

        cheat_manager_exists = (core_dir / "cheat_manager.py").exists()
        cheats_dir_exists = cheats_dir.exists()

        cheat_files = []
        if cheats_dir_exists:
            cheat_files = list(cheats_dir.glob("*.cht")) + list(cheats_dir.glob("*.json"))

        return {
            "status": "success" if cheat_manager_exists else "warning",
            "message": f"金手指系统 {'已集成' if cheat_manager_exists else '未集成'}",
            "items": [
                {"component": "CheatManager", "exists": cheat_manager_exists},
                {"component": "金手指目录", "exists": cheats_dir_exists},
                {"component": "金手指文件", "count": len(cheat_files)}
            ]
        }

    def check_web_interface(self) -> Dict:
        """检查Web界面"""
        web_dir = self.project_root / "data" / "web"

        required_files = [
            "game_switcher/index.html",
            "index.html"
        ]

        found_files = []
        missing_files = []

        for file_path in required_files:
            full_path = web_dir / file_path
            if full_path.exists():
                found_files.append({
                    "name": file_path,
                    "size": full_path.stat().st_size
                })
            else:
                missing_files.append(file_path)

        return {
            "status": "success" if not missing_files else "warning",
            "message": f"Web界面文件 {len(found_files)}/{len(required_files)} 个",
            "items": found_files,
            "missing": missing_files
        }

    def check_docker_config(self) -> Dict:
        """检查Docker配置"""
        docker_dir = self.project_root / "build" / "docker"

        required_files = [
            "Dockerfile.raspberry-sim",
            "Dockerfile.gui",
            "Dockerfile.web-manager",
            "docker-compose.yml"
        ]

        found_files = []
        missing_files = []

        for file_name in required_files:
            file_path = docker_dir / file_name
            if file_path.exists():
                found_files.append({
                    "name": file_name,
                    "size": file_path.stat().st_size
                })
            else:
                missing_files.append(file_name)

        return {
            "status": "success" if not missing_files else "warning",
            "message": f"Docker配置文件 {len(found_files)}/{len(required_files)} 个",
            "items": found_files,
            "missing": missing_files
        }

    def check_autostart_config(self) -> Dict:
        """检查自动启动配置"""
        # 检查是否有自动启动相关的配置
        autostart_files = [
            "quick_start.sh",
            "src/scripts/enhanced_game_launcher.py"
        ]

        found_files = []
        for file_path in autostart_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                found_files.append({
                    "name": file_path,
                    "exists": True
                })

        return {
            "status": "success" if found_files else "warning",
            "message": f"自动启动配置 {len(found_files)} 个文件",
            "items": found_files
        }

    def check_device_management(self) -> Dict:
        """检查设备管理"""
        core_dir = self.project_root / "src" / "core"
        device_manager_exists = (core_dir / "device_manager.py").exists()

        return {
            "status": "success" if device_manager_exists else "warning",
            "message": f"设备管理器 {'已集成' if device_manager_exists else '未集成'}",
            "items": [
                {"component": "DeviceManager", "exists": device_manager_exists}
            ]
        }

    def check_config_files(self) -> Dict:
        """检查配置文件"""
        config_dir = self.project_root / "config"

        config_files = [
            "system/gameplayer_config.json",
            "docker/docker-compose.yml"
        ]

        found_files = []
        missing_files = []

        for file_path in config_files:
            full_path = config_dir / file_path
            if full_path.exists():
                found_files.append({
                    "name": file_path,
                    "size": full_path.stat().st_size
                })
            else:
                missing_files.append(file_path)

        return {
            "status": "success" if found_files else "warning",
            "message": f"配置文件 {len(found_files)} 个",
            "items": found_files,
            "missing": missing_files
        }

    def check_documentation(self) -> Dict:
        """检查文档和说明"""
        docs_dir = self.project_root / "docs"

        doc_files = [
            "README.md",
            "docs/guides/",
            "docs/reports/"
        ]

        found_docs = []
        for doc_path in doc_files:
            full_path = self.project_root / doc_path if not doc_path.startswith("docs/") else self.project_root / doc_path
            if full_path.exists():
                found_docs.append({
                    "name": doc_path,
                    "type": "directory" if full_path.is_dir() else "file"
                })

        return {
            "status": "success" if found_docs else "warning",
            "message": f"文档文件 {len(found_docs)} 个",
            "items": found_docs
        }

    def _print_check_result(self, check_name: str, result: Dict):
        """打印检查结果"""
        status = result["status"]
        message = result["message"]

        if status == "success":
            print(f"✅ {check_name}: {message}")
        elif status == "warning":
            print(f"⚠️ {check_name}: {message}")
        else:
            print(f"❌ {check_name}: {message}")

        # 显示详细信息
        if "missing" in result and result["missing"]:
            print(f"   缺失: {', '.join(result['missing'])}")

    def generate_report(self) -> str:
        """生成检查报告"""
        report = []
        report.append("# 🎮 GamePlayer-Raspberry 镜像集成检查报告")
        report.append("")
        report.append(f"**检查时间**: {self._get_current_time()}")
        report.append("")

        # 统计
        total_checks = len(self.check_results)
        success_count = sum(1 for r in self.check_results.values() if r["status"] == "success")
        warning_count = sum(1 for r in self.check_results.values() if r["status"] == "warning")
        error_count = sum(1 for r in self.check_results.values() if r["status"] == "error")

        report.append("## 📊 检查统计")
        report.append("")
        report.append(f"- **总检查项**: {total_checks}")
        report.append(f"- **✅ 成功**: {success_count}")
        report.append(f"- **⚠️ 警告**: {warning_count}")
        report.append(f"- **❌ 错误**: {error_count}")
        report.append("")

        # 详细结果
        report.append("## 📋 详细检查结果")
        report.append("")

        for check_name, result in self.check_results.items():
            status_icon = {"success": "✅", "warning": "⚠️", "error": "❌"}[result["status"]]
            report.append(f"### {status_icon} {check_name}")
            report.append("")
            report.append(f"**状态**: {result['message']}")
            report.append("")

            if "items" in result and result["items"]:
                report.append("**详细信息**:")
                for item in result["items"][:5]:  # 只显示前5个
                    if isinstance(item, dict):
                        if "name" in item:
                            report.append(f"- {item['name']}")
                        elif "component" in item:
                            status = "✅" if item.get("exists", True) else "❌"
                            report.append(f"- {status} {item['component']}")
                    else:
                        report.append(f"- {item}")

                if len(result["items"]) > 5:
                    report.append(f"- ... 还有 {len(result['items']) - 5} 个项目")
                report.append("")

            if "missing" in result and result["missing"]:
                report.append("**缺失项目**:")
                for missing in result["missing"]:
                    report.append(f"- ❌ {missing}")
                report.append("")

        return "\n".join(report)

    def _get_current_time(self) -> str:
        """获取当前时间"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="镜像集成检查器")
    parser.add_argument("--project-root", help="项目根目录")
    parser.add_argument("--output", help="输出报告文件")

    args = parser.parse_args()

    # 创建检查器
    checker = ImageIntegrationChecker(args.project_root)

    # 执行检查
    results = checker.check_all_components()

    # 生成报告
    report = checker.generate_report()

    # 输出报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 报告已保存到: {args.output}")
    else:
        print("\n" + "=" * 50)
        print(report)

    # 返回状态码
    error_count = sum(1 for r in results.values() if r["status"] == "error")
    sys.exit(1 if error_count > 0 else 0)

if __name__ == "__main__":
    main()
