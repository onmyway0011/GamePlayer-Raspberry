from abc import ABC, abstractmethod
from typing import List
import logging
import os
import subprocess


class BaseInstaller(ABC):
    """
    Abstract base class for emulator installers to reduce code duplication
    """

    def __init__(self, config_path=None):
        """TODO: Add docstring"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = self._load_config(config_path) if config_path else {}

    def check_dependencies(self):
        """检查系统依赖"""
        self.logger.info("检查依赖包...")

        required_packages = self._get_required_packages()

        for package in required_packages:
            if not self._check_package(package):
                self.logger.warning(f"缺少依赖包: {package}")
                if self._install_package(package):
                    self.logger.info(f"✓ 已安装: {package}")
                else:
                    self.logger.error(f"✗ 安装失败: {package}")
                    return False

        self.logger.info("✓ 所有依赖检查通过")
        return True

    @abstractmethod
    def _get_required_packages(self) -> List[str]:
        """返回所需依赖包列表"""
        pass

    @abstractmethod
    def install(self):
        """Main installation method"""
        pass

    def _load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path) as f:
                import json
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return {}

    def _check_package(self, package: str):
        """检查包是否已安装"""
        try:
            result = subprocess.run(
                ["dpkg", "-l", package],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False

    def _install_package(self, package: str):
        """安装系统包"""
        try:
            self._run_command(f"sudo apt-get install -y {package}")
            return True
        except Exception as e:
            self.logger.error(f"安装包失败 {package}: {e}")
            return False

    def _run_command(self, command):
        """Helper method to run shell commands"""
        import subprocess
        try:
            result = subprocess.run(command, shell=True, check=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout.decode('utf-8')
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {e.stderr.decode('utf-8')}")
            raise
