#!/usr/bin/env python3
"""
高级游戏模拟器问题修复工具 - 主入口脚本
基于企业级架构设计，提供完整的模拟器问题诊断和修复功能
"""

import sys
import argparse
from pathlib import Path

# 添加src目录到Python路径
current_file = Path(__file__)
src_dir = current_file.parent.parent
sys.path.insert(0, str(src_dir))

from core.emulator_fix.main_fixer import EmulatorFixerMain
from core.emulator_fix.logger_setup import setup_logging, get_main_logger


def create_argument_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="🎮 高级游戏模拟器问题修复工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s                          # 自动修复所有问题
  %(prog)s --interactive            # 交互式修复
  %(prog)s --status                 # 只显示系统状态
  %(prog)s --test                   # 运行测试套件
  %(prog)s --config-check           # 检查配置文件
  %(prog)s --project-root /path     # 指定项目根目录

功能特性:
  ✅ 自动检测和修复ROM文件问题
  ✅ 智能安装缺失的模拟器
  ✅ 修复模拟器配置和乱码问题
  ✅ 并行处理提高修复效率
  ✅ 事务性操作支持回滚
  ✅ 企业级安全验证
  ✅ 详细的HTML报告生成
  ✅ 实时进度显示
        """
    )

    # 主要操作选项
    action_group = parser.add_argument_group("操作选项")
    action_group.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="启用交互式模式，每个步骤都会询问确认"
    )
    action_group.add_argument(
        "--status", "-s",
        action="store_true",
        help="只显示系统状态，不执行修复操作"
    )
    action_group.add_argument(
        "--test", "-t",
        action="store_true",
        help="运行单元测试套件"
    )
    action_group.add_argument(
        "--config-check", "-c",
        action="store_true",
        help="检查配置文件完整性"
    )

    # 配置选项
    config_group = parser.add_argument_group("配置选项")
    config_group.add_argument(
        "--project-root",
        type=Path,
        help="指定项目根目录路径"
    )
    config_group.add_argument(
        "--config-dir",
        type=Path,
        help="指定配置文件目录路径"
    )
    config_group.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="设置日志级别"
    )

    # 修复选项
    fix_group = parser.add_argument_group("修复选项")
    fix_group.add_argument(
        "--skip-rom-fix",
        action="store_true",
        help="跳过ROM文件修复"
    )
    fix_group.add_argument(
        "--skip-emulator-install",
        action="store_true",
        help="跳过模拟器安装"
    )
    fix_group.add_argument(
        "--skip-config-fix",
        action="store_true",
        help="跳过配置文件修复"
    )
    fix_group.add_argument(
        "--parallel-workers",
        type=int,
        default=4,
        help="并行工作线程数 (默认: 4)"
    )

    # 输出选项
    output_group = parser.add_argument_group("输出选项")
    output_group.add_argument(
        "--no-progress",
        action="store_true",
        help="禁用进度显示"
    )
    output_group.add_argument(
        "--no-color",
        action="store_true",
        help="禁用彩色输出"
    )
    output_group.add_argument(
        "--report-path",
        type=Path,
        help="指定HTML报告输出路径"
    )
    output_group.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="静默模式，只输出错误信息"
    )
    output_group.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细模式，输出调试信息"
    )

    # 安全选项
    security_group = parser.add_argument_group("安全选项")
    security_group.add_argument(
        "--safe-mode",
        action="store_true",
        help="启用安全模式，进行额外的安全检查"
    )
    security_group.add_argument(
        "--no-backup",
        action="store_true",
        help="禁用备份功能"
    )

    return parser


def setup_logging_from_args(args) -> None:
    """根据命令行参数设置日志"""
    log_level = "ERROR" if args.quiet else "DEBUG" if args.verbose else args.log_level

    setup_logging(
        console_level=log_level,
        file_level="DEBUG"  # 文件总是记录详细日志
    )


def run_tests():
    """运行测试套件"""
    logger = get_main_logger()
    logger.info("🧪 运行单元测试套件...")

    try:
        # 添加项目根目录到路径
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))

        # 导入测试模块
        from tests.test_emulator_fix import run_tests

        # 运行测试
        success = run_tests()

        if success:
            logger.info("✅ 所有测试通过！")
        else:
            logger.error("❌ 部分测试失败！")

        return success

    except ImportError as e:
        logger.error(f"❌ 无法导入测试模块: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 测试运行异常: {e}")
        return False


def check_config(project_root: Path):
    """检查配置文件"""
    logger = get_main_logger()
    logger.info("🔍 检查配置文件...")

    try:
        from core.emulator_fix.config_manager import ConfigManager

        config = ConfigManager()
        issues = config.validate_config()

        if issues:
            logger.warning("⚠️ 配置问题:")
            for issue in issues:
                logger.warning(f"  - {issue}")
            return False
        else:
            logger.info("✅ 配置文件检查通过")

            # 显示配置摘要
            logger.info("📊 配置摘要:")
            logger.info(f"  ROM系统: {list(config.standard_roms.keys())}")
            logger.info(f"  模拟器: {list(config.emulator_commands.get('emulators', {}).keys())}")
            logger.info(f"  并行工作者: {config.general.parallel_workers}")
            logger.info(f"  安全模式: {config.security.safe_mode}")

            return True

    except Exception as e:
        logger.error(f"❌ 配置检查失败: {e}")
        return False


def show_system_status(fixer: EmulatorFixerMain) -> None:
    """显示系统状态"""
    logger = get_main_logger()
    logger.info("📊 系统状态检查...")

    try:
        status = fixer.get_system_status()

        # ROM状态
        rom_status = status["rom_status"]
        rom_icon = "✅" if status["overall_health"]["rom_healthy"] else "❌"
        logger.info(f"{rom_icon} ROM文件: {rom_status['total_issues']} 个问题")

        # 模拟器状态
        emu_status = status["emulator_status"]
        emu_icon = "✅" if status["overall_health"]["emulators_healthy"] else "❌"
        logger.info(f"{emu_icon} 模拟器: {emu_status['available_emulators']}/{emu_status['total_emulators']} 可用")

        # 配置状态
        config_icon = "✅" if status["overall_health"]["config_healthy"] else "❌"
        logger.info(f"{config_icon} 配置文件: {'正常' if status['overall_health']['config_healthy'] else '有问题'}")

        # 详细信息
        if not status["overall_health"]["rom_healthy"]:
            logger.info("📋 ROM问题详情:")
            for issue_type, issues in rom_status["issues"].items():
                if issues:
                    logger.info(f"  {issue_type}: {len(issues)} 个")

        if not status["overall_health"]["emulators_healthy"]:
            logger.info("📋 缺失的模拟器:")
            for emulator in emu_status["missing"]:
                logger.info(f"  - {emulator['name']}: {emulator['description']}")

        # 总体健康度
        all_healthy = all(status["overall_health"].values())
        overall_icon = "🎉" if all_healthy else "⚠️"
        overall_status = "完全健康" if all_healthy else "需要修复"
        logger.info(f"{overall_icon} 总体状态: {overall_status}")

    except Exception as e:
        logger.error(f"❌ 状态检查失败: {e}")


def main():
    """主函数"""
    # 解析命令行参数
    parser = create_argument_parser()
    args = parser.parse_args()

    # 设置日志
    setup_logging_from_args(args)
    logger = get_main_logger()

    try:
        # 显示欢迎信息
        logger.info("🎮 高级游戏模拟器问题修复工具 v4.6.0")
        logger.info("=" * 60)

        # 运行测试
        if args.test:
            success = run_tests()
            sys.exit(0 if success else 1)

        # 检查配置
        if args.config_check:
            success = check_config(args.project_root)
            sys.exit(0 if success else 1)

        # 初始化修复器
        logger.info("🚀 初始化修复器...")
        fixer = EmulatorFixerMain(args.project_root)

        # 只显示状态
        if args.status:
            show_system_status(fixer)
            sys.exit(0)

        # 应用命令行选项到配置
        if hasattr(fixer.config.general, 'parallel_workers'):
            fixer.config.general.parallel_workers = args.parallel_workers

        if args.no_progress:
            fixer.config.ui.show_progress = False

        if args.report_path:
            fixer.config.ui.report_path = str(args.report_path)

        if args.safe_mode:
            fixer.config.security.safe_mode = True

        if args.no_backup:
            fixer.config.general.backup_before_fix = False

        # 执行修复
        logger.info("🔧 开始修复过程...")
        success = fixer.fix_all_issues(interactive=args.interactive)

        if success:
            logger.info("🎉 修复完成！")
            logger.info("💡 建议:")
            logger.info("  1. 重启相关服务以确保更改生效")
            logger.info("  2. 测试游戏启动功能")
            logger.info("  3. 查看生成的HTML报告了解详情")
            sys.exit(0)
        else:
            logger.error("❌ 修复过程中出现问题")
            logger.error("💡 建议:")
            logger.error("  1. 检查日志文件获取详细错误信息")
            logger.error("  2. 确保有足够的权限执行操作")
            logger.error("  3. 尝试使用 --interactive 模式逐步修复")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("⏹️ 用户取消操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 程序异常: {e}")
        if args.verbose:
            import traceback
            logger.error(f"详细错误信息:\n{traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
