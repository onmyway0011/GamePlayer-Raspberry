#!/usr/bin/env python3
"""
日志系统设置 - 统一的日志配置和管理
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from .config_manager import get_config_manager


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""

    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }

    def format(self, record):
        """TODO: Add docstring"""
        # 添加颜色
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"

        return super().format(record)


class LoggerSetup:
    """日志系统设置类"""

    def __init__(self):
        """TODO: Add docstring"""
        self.config = get_config_manager()
        self._setup_done = False

    def setup_logging(self,
        """TODO: Add docstring"""
                     logger_name: Optional[str] = None,
                     console_level: Optional[str] = None,
                     file_level: Optional[str] = None) -> logging.Logger:
        """设置日志系统"""

        if logger_name is None:
            logger_name = "emulator_fix"

        logger = logging.getLogger(logger_name)

        # 避免重复设置
        if self._setup_done and logger.handlers:
            return logger

        # 清除现有处理器
        logger.handlers.clear()

        # 设置日志级别
        log_level = getattr(logging, self.config.logging.level.upper(), logging.INFO)
        logger.setLevel(log_level)

        # 创建格式化器
        formatter = logging.Formatter(self.config.logging.format)
        colored_formatter = ColoredFormatter(self.config.logging.format)

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_level = console_level or self.config.logging.level
        console_handler.setLevel(getattr(logging, console_level.upper(), logging.INFO))
        console_handler.setFormatter(colored_formatter)
        logger.addHandler(console_handler)

        # 文件处理器
        if self.config.logging.file:
            try:
                log_file = Path(self.config.logging.file)
                log_file.parent.mkdir(parents=True, exist_ok=True)

                # 使用RotatingFileHandler进行日志轮转
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=self.config.logging.max_size_mb * 1024 * 1024,
                    backupCount=self.config.logging.backup_count,
                    encoding='utf-8'
                )

                file_level = file_level or self.config.logging.level
                file_handler.setLevel(getattr(logging, file_level.upper(), logging.INFO))
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

            except Exception as e:
                logger.warning(f"⚠️ 无法设置文件日志: {e}")

        self._setup_done = True
        return logger

    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的日志器"""
        return logging.getLogger(f"emulator_fix.{name}")

# 全局日志设置实例
_logger_setup = LoggerSetup()


def setup_logging(logger_name: Optional[str] = None,
    """TODO: Add docstring"""
                 console_level: Optional[str] = None,
                 file_level: Optional[str] = None) -> logging.Logger:
    """设置日志系统的便捷函数"""
    return _logger_setup.setup_logging(logger_name, console_level, file_level)


def get_logger(name: str) -> logging.Logger:
    """获取日志器的便捷函数"""
    return _logger_setup.get_logger(name)

# 预设的日志器

def get_main_logger() -> logging.Logger:
    """获取主日志器"""
    return get_logger("main")


def get_rom_logger() -> logging.Logger:
    """获取ROM管理日志器"""
    return get_logger("rom")


def get_emulator_logger() -> logging.Logger:
    """获取模拟器日志器"""
    return get_logger("emulator")


def get_config_logger() -> logging.Logger:
    """获取配置日志器"""
    return get_logger("config")


def get_test_logger() -> logging.Logger:
    """获取测试日志器"""
    return get_logger("test")

if __name__ == "__main__":
    # 测试日志系统
    logger = setup_logging()

    logger.debug("🔍 这是调试信息")
    logger.info("ℹ️ 这是信息")
    logger.warning("⚠️ 这是警告")
    logger.error("❌ 这是错误")
    logger.critical("🚨 这是严重错误")

    # 测试子日志器
    rom_logger = get_rom_logger()
    rom_logger.info("📁 ROM管理器日志测试")

    emulator_logger = get_emulator_logger()
    emulator_logger.info("🎮 模拟器日志测试")
