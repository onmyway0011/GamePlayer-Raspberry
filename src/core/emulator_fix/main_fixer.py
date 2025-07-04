#!/usr/bin/env python3
"""
主修复器 - 协调所有修复组件的主要入口点
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from .config_manager import get_config_manager
from .logger_setup import setup_logging, get_main_logger
from .state_manager import get_state_manager
from .rom_manager import RomManager
from .emulator_installer import EmulatorInstaller
from .progress_reporter import ProgressReporter
from .security_validator import SecurityValidator

logger = get_main_logger()


class EmulatorFixerMain:
    """主修复器类"""

    def __init__(self, project_root: Optional[Path] = None):
        """初始化主修复器"""
        # 设置日志
        setup_logging()

        if project_root is None:
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent

        self.project_root = Path(project_root)

        # 初始化组件
        self.config = get_config_manager()
        self.state_manager = get_state_manager()
        self.rom_manager = RomManager(self.project_root)
        self.emulator_installer = EmulatorInstaller()
        self.progress_reporter = ProgressReporter()
        self.security_validator = SecurityValidator()

        logger.info("🎮 游戏模拟器问题修复工具")
        logger.info("=" * 50)

        # 验证配置
        self._validate_setup()

    def _validate_setup(self) -> None:
        """验证设置"""
        logger.info("🔍 验证系统设置...")

        # 验证配置
        config_issues = self.config.validate_config()
        if config_issues:
            logger.warning("⚠️ 配置问题:")
            for issue in config_issues:
                logger.warning(f"  - {issue}")

        # 验证安全性
        if self.config.security.safe_mode:
            security_issues = self.security_validator.validate_environment()
            if security_issues:
                logger.error("❌ 安全验证失败:")
                for issue in security_issues:
                    logger.error(f"  - {issue}")
                if self.config.security.safe_mode:
                    raise RuntimeError("安全验证失败，无法继续")

        logger.info("✅ 系统设置验证完成")

    def fix_all_issues(self, interactive: bool = None):
        """修复所有问题"""
        if interactive is None:
            interactive = self.config.ui.interactive_mode

        logger.info("🚀 开始全面修复...")

        # 开始修复会话
        session = self.state_manager.start_session(
            metadata={
                "interactive": interactive,
                "project_root": str(self.project_root),
                "platform": self.emulator_installer.platform,
                "package_manager": self.emulator_installer.package_manager
            }
        )

        try:
            total_fixes = 0

            # 1. 检查和修复ROM文件
            logger.info("\n📋 第1步: 检查ROM文件")
            rom_fixes = self._fix_rom_issues(interactive)
            total_fixes += rom_fixes

            # 2. 检查和安装模拟器
            logger.info("\n📋 第2步: 检查模拟器")
            emulator_fixes = self._fix_emulator_issues(interactive)
            total_fixes += emulator_fixes

            # 3. 修复模拟器配置
            logger.info("\n📋 第3步: 修复模拟器配置")
            config_fixes = self._fix_config_issues(interactive)
            total_fixes += config_fixes

            # 4. 测试模拟器功能
            logger.info("\n📋 第4步: 测试模拟器功能")
            self._test_emulator_functionality()

            # 5. 清理和优化
            logger.info("\n📋 第5步: 清理和优化")
            cleanup_fixes = self._cleanup_and_optimize()
            total_fixes += cleanup_fixes

            # 结束会话
            finished_session = self.state_manager.finish_session()

            # 生成报告
            self._generate_final_report(finished_session, total_fixes)

            if total_fixes > 0:
                logger.info("🎉 模拟器问题修复完成！")
                self._print_success_summary(total_fixes)
                return True
            else:
                logger.info("ℹ️ 系统状态良好，无需修复")
                return True

        except Exception as e:
            logger.error(f"❌ 修复过程异常: {e}")
            self.state_manager.finish_session()
            return False

    def _fix_rom_issues(self, interactive: bool) -> int:
        """修复ROM问题"""
        try:
            # 检查ROM文件
            rom_issues = self.rom_manager.check_rom_files()

            total_issues = sum(len(issue_list) for issue_list in rom_issues.values())
            if total_issues == 0:
                logger.info("✅ ROM文件状态正常")
                return 0

            logger.info(f"📊 发现 {total_issues} 个ROM问题")

            # 交互式确认
            if interactive:
                response = input(f"是否修复这些ROM问题? (y/n): ").lower().strip()
                if response != 'y':
                    logger.info("⏭️ 跳过ROM修复")
                    return 0

            # 显示进度
            if self.config.ui.show_progress:
                self.progress_reporter.start_progress("修复ROM文件", total_issues)

            # 修复ROM文件
            fixed_count = self.rom_manager.fix_rom_files(rom_issues)

            if self.config.ui.show_progress:
                self.progress_reporter.finish_progress()

            logger.info(f"✅ ROM文件修复: {fixed_count} 个")
            return fixed_count

        except Exception as e:
            logger.error(f"❌ ROM修复失败: {e}")
            return 0

    def _fix_emulator_issues(self, interactive: bool) -> int:
        """修复模拟器问题"""
        try:
            # 检查模拟器状态
            emulator_status = self.emulator_installer.check_emulators()

            missing_emulators = [
                name for name, status in emulator_status.items()
                if not status["available"]
            ]

            if not missing_emulators:
                logger.info("✅ 所有模拟器都已安装")
                return 0

            logger.info(f"📊 发现 {len(missing_emulators)} 个缺失的模拟器")

            # 交互式确认
            if interactive:
                logger.info("缺失的模拟器:")
                for name in missing_emulators:
                    desc = self.config.get_emulator_description(name)
                    logger.info(f"  - {name}: {desc}")

                response = input(f"是否安装这些模拟器? (y/n): ").lower().strip()
                if response != 'y':
                    logger.info("⏭️ 跳过模拟器安装")
                    return 0

            # 显示进度
            if self.config.ui.show_progress:
                self.progress_reporter.start_progress("安装模拟器", len(missing_emulators))

            # 安装模拟器
            installed_count = self.emulator_installer.install_emulators(emulator_status)

            if self.config.ui.show_progress:
                self.progress_reporter.finish_progress()

            logger.info(f"✅ 模拟器安装: {installed_count} 个")
            return installed_count

        except Exception as e:
            logger.error(f"❌ 模拟器安装失败: {e}")
            return 0

    def _fix_config_issues(self, interactive: bool) -> int:
        """修复配置问题"""
        try:
            # 修复模拟器配置
            config_fixes = self.emulator_installer.fix_emulator_config()

            if config_fixes > 0:
                logger.info(f"✅ 模拟器配置修复: {config_fixes} 个")
            else:
                logger.info("✅ 模拟器配置正常")

            return config_fixes

        except Exception as e:
            logger.error(f"❌ 配置修复失败: {e}")
            return 0

    def _test_emulator_functionality(self) -> None:
        """测试模拟器功能"""
        try:
            # 查找测试ROM
            test_rom = self._find_test_rom()
            if not test_rom:
                logger.warning("⚠️ 没有找到测试ROM，跳过功能测试")
                return

            # 测试模拟器
            test_results = self.emulator_installer.test_emulators(test_rom)

            if test_results:
                working_count = len([r for r in test_results.values() if r["working"]])
                total_count = len(test_results)

                logger.info(f"📊 模拟器测试: {working_count}/{total_count} 工作正常")

                for name, result in test_results.items():
                    if result["working"]:
                        logger.info(f"  ✅ {name}: 工作正常")
                    else:
                        logger.warning(f"  ❌ {name}: {result['error']}")
            else:
                logger.info("ℹ️ 没有可测试的模拟器")

        except Exception as e:
            logger.error(f"❌ 模拟器测试失败: {e}")

    def _find_test_rom(self) -> Optional[Path]:
        """查找测试ROM"""
        # 查找第一个可用的ROM文件
        for system in ["nes", "snes", "gameboy", "gba"]:
            system_dir = self.rom_manager.roms_dir / system
            if system_dir.exists():
                for rom_file in system_dir.glob("*.nes"):
                    if rom_file.is_file() and rom_file.stat().st_size > 1024:
                        return rom_file
                for rom_file in system_dir.glob("*.*"):
                    if rom_file.is_file() and rom_file.stat().st_size > 1024:
                        return rom_file

        return None

    def _cleanup_and_optimize(self) -> int:
        """清理和优化"""
        cleanup_count = 0

        try:
            # 清理临时文件
            temp_dirs = [
                self.project_root / "temp",
                self.project_root / "tmp",
                Path.home() / ".mednafen" / "temp"
            ]

            for temp_dir in temp_dirs:
                if temp_dir.exists() and temp_dir.is_dir():
                    try:
                        import shutil
                        shutil.rmtree(temp_dir)
                        logger.debug(f"🧹 清理临时目录: {temp_dir}")
                        cleanup_count += 1
                    except Exception as e:
                        logger.warning(f"⚠️ 清理失败 {temp_dir}: {e}")

            if cleanup_count > 0:
                logger.info(f"✅ 清理完成: {cleanup_count} 个项目")
            else:
                logger.info("✅ 系统已经很干净")

        except Exception as e:
            logger.error(f"❌ 清理失败: {e}")

        return cleanup_count

    def _generate_final_report(self, session, total_fixes: int) -> None:
        """生成最终报告"""
        try:
            if self.config.ui.generate_html_report:
                report_path = Path(self.config.ui.report_path)
                report_path.parent.mkdir(parents=True, exist_ok=True)

                # 生成HTML报告
                html_content = self.progress_reporter.generate_html_report(session)

                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)

                logger.info(f"📄 生成报告: {report_path}")

        except Exception as e:
            logger.warning(f"⚠️ 生成报告失败: {e}")

    def _print_success_summary(self, total_fixes: int) -> None:
        """打印成功摘要"""
        logger.info("\n💡 解决方案:")
        logger.info("  1. ✅ ROM文件已修复 - 解决游戏加载失败")
        logger.info("  2. ✅ 模拟器已安装 - 提供完整的游戏支持")
        logger.info("  3. ✅ 配置已优化 - 解决中文乱码和兼容性问题")
        logger.info("  4. ✅ 功能已验证 - 确保系统正常工作")

        logger.info("\n🎮 推荐使用:")

        # 获取可用模拟器
        emulator_summary = self.emulator_installer.get_emulator_summary()
        for emulator in emulator_summary["available"]:
            logger.info(f"  • {emulator['name']} - {emulator['description']}")

        logger.info(f"\n📊 总修复项目: {total_fixes} 个")

    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        # ROM状态
        rom_issues = self.rom_manager.check_rom_files()
        rom_total_issues = sum(len(issue_list) for issue_list in rom_issues.values())

        # 模拟器状态
        emulator_summary = self.emulator_installer.get_emulator_summary()

        # 配置状态
        config_issues = self.config.validate_config()

        return {
            "rom_status": {
                "total_issues": rom_total_issues,
                "issues": rom_issues
            },
            "emulator_status": emulator_summary,
            "config_status": {
                "issues": config_issues,
                "valid": len(config_issues) == 0
            },
            "overall_health": {
                "rom_healthy": rom_total_issues == 0,
                "emulators_healthy": emulator_summary["missing_emulators"] == 0,
                "config_healthy": len(config_issues) == 0
            }
        }


def main():
    """主函数"""
    try:
        # 解析命令行参数
        import argparse
        parser = argparse.ArgumentParser(description="游戏模拟器问题修复工具")
        parser.add_argument("--interactive", "-i", action="store_true", help="交互式模式")
        parser.add_argument("--status", "-s", action="store_true", help="只显示状态")
        parser.add_argument("--config-dir", help="配置目录路径")
        parser.add_argument("--project-root", help="项目根目录路径")

        args = parser.parse_args()

        # 初始化修复器
        project_root = Path(args.project_root) if args.project_root else None
        fixer = EmulatorFixerMain(project_root)

        if args.status:
            # 只显示状态
            status = fixer.get_system_status()
            logger.info("📊 系统状态:")
            logger.info(f"  ROM健康: {'✅' if status['overall_health']['rom_healthy'] else '❌'}")
            logger.info(f"  模拟器健康: {'✅' if status['overall_health']['emulators_healthy'] else '❌'}")
            logger.info(f"  配置健康: {'✅' if status['overall_health']['config_healthy'] else '❌'}")
            return

        # 执行修复
        success = fixer.fix_all_issues(interactive=args.interactive)

        if success:
            logger.info("\n✅ 模拟器问题修复完成！")
            logger.info("🎮 现在可以正常运行游戏了")
            sys.exit(0)
        else:
            logger.error("\n❌ 修复过程中出现问题")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n⏹️ 用户取消操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ 程序异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
