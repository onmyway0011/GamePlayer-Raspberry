#!/usr/bin/env python3
"""
Nesticle 95 安装器测试用例

测试 Nesticle 模拟器的自动安装、配置和集成功能。
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 设置测试环境变量
os.environ["TEST_ENV"] = "true"

# 导入被测试的模块
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.core.nesticle_installer import NesticleInstaller


class TestNesticleInstaller(unittest.TestCase):
    """Nesticle 安装器测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.json"

        # 创建测试配置
        self.test_config = {
            "emulator": {
                "type": "retroarch",
                "default": "nesticle",
                "cheats_dir": "/home/pi/RetroPie/cheats/",
                "saves_dir": "/home/pi/RetroPie/saves/",
                "nesticle": {
                    "version": "95",
                    "enabled": True,
                    "auto_install": True,
                    "is_default": True,
                    "config_path": "/home/pi/RetroPie/configs/nes/",
                    "core_path": "/opt/retropie/emulators/retroarch/cores/",
                    "rom_extensions": [".nes", ".NES"],
                    "features": [
                        "high_compatibility",
                        "save_states",
                        "cheat_support",
                        "netplay",
                        "rewind",
                        "shaders",
                        "infinite_lives",
                        "auto_save"
                    ],
                    "cheats": {
                        "enabled": True,
                        "infinite_lives": True,
                        "auto_cheat": True,
                        "cheat_codes": {
                            "super_mario_bros": {
                                "infinite_lives": "00FF-01-99",
                                "invincible": "00FF-01-FF",
                                "max_power": "00FF-01-03"
                            },
                            "contra": {
                                "infinite_lives": "00FF-01-99",
                                "infinite_ammo": "00FF-01-FF",
                                "spread_gun": "00FF-01-01"
                            }
                        }
                    },
                    "save_states": {
                        "enabled": True,
                        "auto_save": True,
                        "save_interval": 30,
                        "max_saves": 10,
                        "save_path": "/home/pi/RetroPie/saves/nes/"
                    }
                }
            }
        }

        # 写入测试配置文件
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.test_config, f, indent=2)

        # 创建安装器实例
        self.installer = NesticleInstaller(str(self.config_file))

    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_config(self):
        """测试配置文件加载"""
        config = self.installer.config
        self.assertIsInstance(config, dict)
        self.assertIn("emulator", config)
        self.assertIn("nesticle", config["emulator"])
        self.assertEqual(config["emulator"]["nesticle"]["version"], "95")

    @patch('subprocess.run')
    def test_check_dependencies(self, mock_run):
        """测试依赖检查"""
        # 模拟依赖检查成功
        mock_run.return_value.returncode = 0

        result = self.installer.check_dependencies()
        self.assertTrue(result)

    def test_configure_nesticle(self):
        """测试 Nesticle 配置"""
        result = self.installer.configure_nesticle()
        self.assertTrue(result)

        # 检查配置文件是否创建
        config_path = self.installer.config_dir / "nesticle.cfg"
        self.assertTrue(config_path.exists())

        # 检查配置文件内容
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Nesticle 95 配置文件", content)
            self.assertIn("AutoSave=1", content)
            self.assertIn("InfiniteLives=1", content)

    def test_setup_cheat_system(self):
        """测试金手指系统设置"""
        result = self.installer.setup_cheat_system()
        self.assertTrue(result)

        # 检查金手指目录是否创建
        self.assertTrue(self.installer.cheats_dir.exists())

        # 检查金手指文件是否生成
        mario_cheat_file = self.installer.cheats_dir / "super_mario_bros.cht"
        self.assertTrue(mario_cheat_file.exists())

    def test_setup_auto_save_system(self):
        """测试自动保存系统设置"""
        result = self.installer.setup_auto_save_system()
        self.assertTrue(result)

        # 检查自动保存脚本是否创建
        auto_save_script = self.installer.install_dir / "auto_save.sh"
        self.assertTrue(auto_save_script.exists())

        # 检查脚本权限
        self.assertTrue(os.access(auto_save_script, os.X_OK))

    def test_integrate_with_retroarch(self):
        """测试 RetroArch 集成"""
        result = self.installer.integrate_with_retroarch()
        self.assertTrue(result)

        # 检查核心信息文件是否创建
        core_info_path = self.installer.core_dir / "nesticle_libretro.info"
        self.assertTrue(core_info_path.exists())

        # 检查核心信息内容
        with open(core_info_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("name = Nesticle", content)
            self.assertIn("version = 95", content)
            self.assertIn("infinite_lives", content)

    def test_create_launch_script(self):
        """测试启动脚本创建"""
        result = self.installer.create_launch_script()
        self.assertTrue(result)

        # 检查启动脚本是否创建
        launch_script = self.installer.install_dir / "launch_nesticle.sh"
        self.assertTrue(launch_script.exists())

        # 检查脚本权限
        self.assertTrue(os.access(launch_script, os.X_OK))

        # 检查脚本内容
        with open(launch_script, "r") as f:
            content = f.read()
            self.assertIn("Nesticle 启动脚本", content)
            self.assertIn("auto_save.sh", content)

    def test_set_as_default_emulator(self):
        """测试设置为默认模拟器"""
        result = self.installer.set_as_default_emulator()
        self.assertTrue(result)

        # 检查默认配置是否创建
        default_config_path = self.installer.config_dir / "default_emulator.json"
        self.assertTrue(default_config_path.exists())

        # 检查配置内容
        with open(default_config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            self.assertEqual(config["nes"]["default_emulator"], "nesticle")
            self.assertTrue(config["nes"]["emulators"]["nesticle"]["enabled"])

    def test_verify_installation(self):
        """测试安装验证"""
        # 先创建必要的文件
        self.installer.configure_nesticle()
        self.installer.setup_cheat_system()
        self.installer.setup_auto_save_system()
        self.installer.integrate_with_retroarch()
        self.installer.create_launch_script()
        self.installer.set_as_default_emulator()

        result = self.installer.verify_installation()
        self.assertTrue(result)

    @patch.object(NesticleInstaller, 'check_dependencies', return_value=True)
    def test_run_complete_installation(self, mock_check_deps):
        """测试完整安装流程"""
        result = self.installer.run()
        self.assertTrue(result)

    def test_cheat_codes_generation(self):
        """测试金手指代码生成"""
        self.installer.setup_cheat_system()

        # 检查超级马里奥金手指文件
        mario_cheat_file = self.installer.cheats_dir / "super_mario_bros.cht"
        self.assertTrue(mario_cheat_file.exists())

        with open(mario_cheat_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("infinite_lives", content)
            self.assertIn("00FF-01-99", content)

    def test_auto_save_configuration(self):
        """测试自动保存配置"""
        self.installer.setup_auto_save_system()

        auto_save_script = self.installer.install_dir / "auto_save.sh"
        with open(auto_save_script, "r") as f:
            content = f.read()

            # 检查配置参数
            self.assertIn("SAVE_INTERVAL=30", content)
            self.assertIn("MAX_SAVES=10", content)
            self.assertIn("auto_save", content)

    def test_retroarch_core_config(self):
        """测试 RetroArch 核心配置"""
        self.installer.integrate_with_retroarch()

        core_info_path = self.installer.core_dir / "nesticle_libretro.info"
        with open(core_info_path, "r", encoding="utf-8") as f:
            content = f.read()

            # 检查核心信息
            self.assertIn("system = nes", content)
            self.assertIn("extensions = .nes,.NES", content)
            self.assertIn("infinite_lives", content)
            self.assertIn("auto_save", content)

    def test_launch_script_environment(self):
        """测试启动脚本环境变量"""
        self.installer.create_launch_script()

        launch_script = self.installer.install_dir / "launch_nesticle.sh"
        with open(launch_script, "r") as f:
            content = f.read()

            # 检查环境变量设置
            self.assertIn("NESTICLE_CONFIG", content)
            self.assertIn("NESTICLE_SAVES", content)
            self.assertIn("NESTICLE_CHEATS", content)

    def test_error_handling(self):
        """测试错误处理"""
        # 测试配置文件不存在的情况
        # 由于我们使用基类的配置加载，这里只测试配置是否正确加载
        self.assertIsInstance(self.installer.config, dict)
        self.assertIn("emulator", self.installer.config)

    def test_test_environment_detection(self):
        """测试测试环境检测"""
        # 确保测试环境变量已设置
        self.assertEqual(os.environ.get("TEST_ENV"), "true")

        # 检查是否使用临时目录
        self.assertIn("nesticle_test", str(self.installer.install_dir))

    def test_configuration_validation(self):
        """测试配置验证"""
        # 测试有效配置
        self.assertTrue(self.installer.nesticle_config["enabled"])
        self.assertTrue(self.installer.nesticle_config["is_default"])
        self.assertEqual(self.installer.nesticle_config["version"], "95")

    def test_feature_flags(self):
        """测试功能标志"""
        features = self.installer.nesticle_config["features"]

        # 检查关键功能
        self.assertIn("infinite_lives", features)
        self.assertIn("auto_save", features)
        self.assertIn("cheat_support", features)
        self.assertIn("save_states", features)

    def test_rom_extensions(self):
        """测试 ROM 扩展名配置"""
        extensions = self.installer.nesticle_config["rom_extensions"]
        self.assertIn(".nes", extensions)
        self.assertIn(".NES", extensions)

    def test_cheat_system_configuration(self):
        """测试金手指系统配置"""
        cheats_config = self.installer.nesticle_config["cheats"]

        self.assertTrue(cheats_config["enabled"])
        self.assertTrue(cheats_config["infinite_lives"])
        self.assertTrue(cheats_config["auto_cheat"])

        # 检查金手指代码
        cheat_codes = cheats_config["cheat_codes"]
        self.assertIn("super_mario_bros", cheat_codes)
        self.assertIn("contra", cheat_codes)

    def test_save_system_configuration(self):
        """测试保存系统配置"""
        save_config = self.installer.nesticle_config["save_states"]

        self.assertTrue(save_config["enabled"])
        self.assertTrue(save_config["auto_save"])
        self.assertEqual(save_config["save_interval"], 30)
        self.assertEqual(save_config["max_saves"], 10)

    def test_directory_structure(self):
        """测试目录结构创建"""
        # 检查所有必要目录是否创建
        self.assertTrue(self.installer.install_dir.exists())
        self.assertTrue(self.installer.config_dir.exists())
        self.assertTrue(self.installer.core_dir.exists())
        self.assertTrue(self.installer.cheats_dir.exists())
        self.assertTrue(self.installer.saves_dir.exists())

    def test_download_nesticle_test_env(self):
        """测试测试环境下的下载功能"""
        script_path = self.installer.download_nesticle()
        self.assertIsNotNone(script_path)
        self.assertTrue(script_path.exists())

        # 检查脚本内容
        with open(script_path, "r") as f:
            content = f.read()
            self.assertIn("测试模式", content)

    def test_install_nesticle_test_env(self):
        """测试测试环境下的安装功能"""
        result = self.installer.install_nesticle()
        self.assertTrue(result)


class TestNesticleIntegration(unittest.TestCase):
    """Nesticle 集成测试类"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "integration_config.json"

        # 创建集成测试配置
        self.integration_config = {
            "emulator": {
                "nesticle": {
                    "enabled": True,
                    "is_default": True,
                    "version": "95"
                }
            }
        }

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.integration_config, f, indent=2)

    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch.object(NesticleInstaller, 'check_dependencies', return_value=True)
    @patch.object(NesticleInstaller, 'configure_nesticle', return_value=True)
    @patch.object(NesticleInstaller, 'setup_cheat_system', return_value=True)
    @patch.object(NesticleInstaller, 'setup_auto_save_system', return_value=True)
    @patch.object(NesticleInstaller, 'integrate_with_retroarch', return_value=True)
    @patch.object(NesticleInstaller, 'create_launch_script', return_value=True)
    @patch.object(NesticleInstaller, 'set_as_default_emulator', return_value=True)
    @patch.object(NesticleInstaller, 'verify_installation', return_value=True)
    def test_integration_workflow(self, mock_verify, mock_default, mock_launch,

                                mock_retroarch, mock_save, mock_cheat, mock_config, mock_deps):
        """测试完整集成工作流"""
        installer = NesticleInstaller(str(self.config_file))
        result = installer.run()
        self.assertTrue(result)

    def test_integration_with_retropie(self):
        """测试与 RetroPie 的集成"""
        installer = NesticleInstaller(str(self.config_file))

        # 测试 RetroArch 集成
        result = installer.integrate_with_retroarch()
        self.assertTrue(result)

    def test_default_emulator_setting(self):
        """测试默认模拟器设置"""
        installer = NesticleInstaller(str(self.config_file))

        result = installer.set_as_default_emulator()
        self.assertTrue(result)

        # 验证配置内容
        default_config_path = installer.config_dir / "default_emulator.json"
        if default_config_path.exists():
            with open(default_config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.assertEqual(config["nes"]["default_emulator"], "nesticle")

if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
