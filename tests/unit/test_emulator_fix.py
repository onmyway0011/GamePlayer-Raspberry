#!/usr/bin/env python3
"""
模拟器修复工具的单元测试
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加src目录到路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.emulator_fix.config_manager import ConfigManager
from core.emulator_fix.rom_manager import RomManager
from core.emulator_fix.emulator_installer import EmulatorInstaller
from core.emulator_fix.state_manager import StateManager, FixType, FixStatus
from core.emulator_fix.transaction_manager import TransactionManager
from core.emulator_fix.security_validator import SecurityValidator


class TestConfigManager(unittest.TestCase):
    """配置管理器测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name) / "config"
        self.config_dir.mkdir(parents=True)

        # 创建测试配置文件
        self._create_test_configs()

    def tearDown(self):
        """清理测试环境"""
        self.temp_dir.cleanup()

    def _create_test_configs(self):
        """创建测试配置文件"""
        # 标准ROM配置
        standard_roms = {
            "nes": {
                "test_game.nes": "测试游戏"
            }
        }
        with open(self.config_dir / "standard_roms.json", 'w') as f:
            json.dump(standard_roms, f)

        # 模拟器命令配置
        emulator_commands = {
            "emulators": {
                "mednafen": {
                    "command": "mednafen",
                    "systems": {"nes": ["-force_module", "nes"]}
                }
            }
        }
        with open(self.config_dir / "emulator_commands.json", 'w') as f:
            json.dump(emulator_commands, f)

        # 修复设置
        fix_settings = {
            "general": {"max_retries": 3},
            "rom_settings": {"min_size_bytes": 1024},
            "emulator_settings": {"auto_install": True},
            "logging": {"level": "INFO"},
            "security": {"safe_mode": True},
            "ui": {"show_progress": True}
        }
        with open(self.config_dir / "fix_settings.json", 'w') as f:
            json.dump(fix_settings, f)

    def test_config_loading(self):
        """测试配置加载"""
        config = ConfigManager(self.config_dir)

        # 验证标准ROM配置
        self.assertIn("nes", config.standard_roms)
        self.assertIn("test_game.nes", config.standard_roms["nes"])

        # 验证模拟器配置
        self.assertIn("mednafen", config.emulator_commands["emulators"])

        # 验证设置对象
        self.assertIsNotNone(config.general)
        self.assertEqual(config.general.max_retries, 3)

    def test_config_validation(self):
        """测试配置验证"""
        config = ConfigManager(self.config_dir)
        issues = config.validate_config()

        # 应该没有验证问题
        self.assertEqual(len(issues), 0)


class TestRomManager(unittest.TestCase):
    """ROM管理器测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)

        # 创建配置目录和文件
        config_dir = self.project_root / "config" / "emulator_fix"
        config_dir.mkdir(parents=True)

        standard_roms = {
            "nes": {
                "test_game.nes": "测试游戏"
            }
        }
        with open(config_dir / "standard_roms.json", 'w') as f:
            json.dump(standard_roms, f)

        # 创建空的其他配置文件
        with open(config_dir / "emulator_commands.json", 'w') as f:
            json.dump({"emulators": {}}, f)

        with open(config_dir / "fix_settings.json", 'w') as f:
            json.dump({
                "general": {},
                "rom_settings": {},
                "emulator_settings": {},
                "logging": {},
                "security": {},
                "ui": {}
            }, f)

    def tearDown(self):
        """清理测试环境"""
        self.temp_dir.cleanup()

    def test_rom_creation(self):
        """测试ROM创建"""
        rom_manager = RomManager(self.project_root)

        # 检查ROM文件（应该发现缺失）
        issues = rom_manager.check_rom_files()
        self.assertIn("missing", issues)
        self.assertTrue(len(issues["missing"]) > 0)

        # 修复ROM文件
        with patch.object(rom_manager.state_manager, 'add_fix_item') as mock_add_item:
            mock_fix_item = MagicMock()
            mock_add_item.return_value = mock_fix_item

            fixed_count = rom_manager.fix_rom_files(issues)
            self.assertGreater(fixed_count, 0)

    def test_nes_rom_creation(self):
        """测试NES ROM创建"""
        rom_manager = RomManager(self.project_root)

        # 创建NES ROM
        nes_rom = rom_manager._create_nes_rom()

        # 验证ROM结构
        self.assertGreater(len(nes_rom), 16)  # 至少有头部
        self.assertEqual(nes_rom[:4], b'NES\x1a')  # iNES头部


class TestStateManager(unittest.TestCase):
    """状态管理器测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_file = Path(self.temp_dir.name) / "test_state.json"

    def tearDown(self):
        """清理测试环境"""
        self.temp_dir.cleanup()

    def test_session_management(self):
        """测试会话管理"""
        manager = StateManager(self.state_file)

        # 开始会话
        session = manager.start_session("test_session")
        self.assertEqual(session.session_id, "test_session")
        self.assertIsNotNone(session.start_time)

        # 添加修复项目
        item = manager.add_fix_item(
            "test_item",
            FixType.ROM_CREATION,
            "测试项目",
            "测试描述"
        )
        self.assertEqual(item.id, "test_item")
        self.assertEqual(item.status, FixStatus.NOT_STARTED)

        # 执行项目
        item.start()
        self.assertEqual(item.status, FixStatus.IN_PROGRESS)

        item.complete()
        self.assertEqual(item.status, FixStatus.COMPLETED)

        # 结束会话
        finished_session = manager.finish_session()
        self.assertIsNotNone(finished_session.end_time)
        self.assertEqual(finished_session.completed_items, 1)


class TestTransactionManager(unittest.TestCase):
    """事务管理器测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

    def tearDown(self):
        """清理测试环境"""
        self.temp_dir.cleanup()

    def test_successful_transaction(self):
        """测试成功的事务"""
        manager = TransactionManager()
        manager.start_transaction()

        test_file = self.test_dir / "test.txt"

        # 添加文件操作
        manager.add_file_operation(
            "create_file",
            "file_creation",
            "创建测试文件",
            test_file,
            content=b"Hello, World!"
        )

        # 提交事务
        success = manager.commit()
        self.assertTrue(success)

        # 验证文件创建
        self.assertTrue(test_file.exists())
        self.assertEqual(test_file.read_bytes(), b"Hello, World!")

    def test_failed_transaction_rollback(self):
        """测试失败事务的回滚"""
        manager = TransactionManager()
        manager.start_transaction()

        test_file = self.test_dir / "test.txt"

        # 先创建文件
        test_file.write_text("Original content")

        # 添加修改操作
        manager.add_file_operation(
            "modify_file",
            "file_modification",
            "修改测试文件",
            test_file,
            content=b"Modified content"
        )

        # 添加一个会失败的操作
        manager.add_custom_operation(
            "fail_operation",
            "test_failure",
            "故意失败的操作",
            lambda: exec('raise Exception("故意失败")'),
            lambda: None
        )

        # 提交事务（应该失败并回滚）
        success = manager.commit()
        self.assertFalse(success)

        # 验证文件回滚到原始内容
        self.assertEqual(test_file.read_text(), "Original content")


class TestSecurityValidator(unittest.TestCase):
    """安全验证器测试"""

    def setUp(self):
        """设置测试环境"""
        self.validator = SecurityValidator()

    def test_path_validation(self):
        """测试路径验证"""
        # 安全路径
        safe_path = Path("./test.txt")
        self.assertTrue(self.validator.validate_path(safe_path))

        # 危险路径
        dangerous_path = Path("../../../etc/passwd")
        self.assertFalse(self.validator.validate_path(dangerous_path))

    def test_command_validation(self):
        """测试命令验证"""
        # 安全命令
        safe_command = ["brew", "install", "mednafen"]
        self.assertTrue(self.validator.validate_command(safe_command))

        # 危险命令
        dangerous_command = ["rm", "-rf", "/"]
        self.assertFalse(self.validator.validate_command(dangerous_command))

    def test_file_content_validation(self):
        """测试文件内容验证"""
        # 安全ROM内容
        safe_rom = b'NES\x1a' + b'\x00' * 1000
        self.assertTrue(self.validator.validate_file_content(safe_rom, "rom"))

        # 危险可执行文件
        dangerous_exe = b'\x7fELF' + b'\x00' * 100
        self.assertFalse(self.validator.validate_file_content(dangerous_exe, "rom"))


class TestEmulatorInstaller(unittest.TestCase):
    """模拟器安装器测试"""

    def setUp(self):
        """设置测试环境"""
        self.installer = EmulatorInstaller()

    @patch('shutil.which')
    def test_emulator_detection(self, mock_which):
        """测试模拟器检测"""
        # 模拟mednafen存在
        mock_which.return_value = "/usr/local/bin/mednafen"

        status = self.installer.check_emulators()

        # 验证检测结果
        self.assertIn("mednafen", status)
        if "mednafen" in status:
            self.assertTrue(status["mednafen"]["available"])

    @patch('subprocess.run')
    def test_emulator_version_detection(self, mock_run):
        """测试模拟器版本检测"""
        # 模拟版本输出
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Mednafen 1.29.0"

        version = self.installer._get_emulator_version("mednafen")
        self.assertEqual(version, "Mednafen 1.29.0")


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)

        # 创建完整的配置结构
        self._setup_complete_config()

    def tearDown(self):
        """清理测试环境"""
        self.temp_dir.cleanup()

    def _setup_complete_config(self):
        """设置完整配置"""
        config_dir = self.project_root / "config" / "emulator_fix"
        config_dir.mkdir(parents=True)

        # 创建所有必要的配置文件
        configs = {
            "standard_roms.json": {
                "nes": {"test_game.nes": "测试游戏"}
            },
            "emulator_commands.json": {
                "emulators": {
                    "mednafen": {
                        "command": "mednafen",
                        "systems": {"nes": ["-force_module", "nes"]}
                    }
                }
            },
            "fix_settings.json": {
                "general": {"max_retries": 3, "parallel_workers": 1},
                "rom_settings": {"min_size_bytes": 1024},
                "emulator_settings": {"auto_install": False},
                "logging": {"level": "INFO"},
                "security": {"safe_mode": False},
                "ui": {"show_progress": False}
            }
        }

        for filename, content in configs.items():
            with open(config_dir / filename, 'w') as f:
                json.dump(content, f)

    def test_full_workflow(self):
        """测试完整工作流程"""
        # 初始化组件
        config = ConfigManager(self.project_root / "config" / "emulator_fix")
        rom_manager = RomManager(self.project_root)

        # 检查ROM文件
        issues = rom_manager.check_rom_files()
        self.assertIn("missing", issues)

        # 修复ROM文件
        with patch.object(rom_manager.state_manager, 'add_fix_item') as mock_add_item:
            mock_fix_item = MagicMock()
            mock_add_item.return_value = mock_fix_item

            fixed_count = rom_manager.fix_rom_files(issues)
            self.assertGreaterEqual(fixed_count, 0)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_classes = [
        TestConfigManager,
        TestRomManager,
        TestStateManager,
        TestTransactionManager,
        TestSecurityValidator,
        TestEmulatorInstaller,
        TestIntegration
    ]

    suite = unittest.TestSuite()

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回测试结果
    return result.wasSuccessful()

if __name__ == "__main__":
    print("🧪 运行模拟器修复工具单元测试...")
    success = run_tests()

    if success:
        print("✅ 所有测试通过！")
        exit(0)
    else:
        print("❌ 部分测试失败！")
        exit(1)
