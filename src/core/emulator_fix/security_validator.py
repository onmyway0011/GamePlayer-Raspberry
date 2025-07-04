#!/usr/bin/env python3
"""
安全验证器 - 验证文件路径和命令执行的安全性
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from .config_manager import get_config_manager
from .logger_setup import get_logger

logger = get_logger("security")


class SecurityValidator:
    """安全验证器"""

    def __init__(self):
        """初始化安全验证器"""
        self.config = get_config_manager()

        # 危险路径模式
        self.dangerous_path_patterns = [
            r'\.\./',  # 目录遍历
            r'\.\.\.',  # 目录遍历
            r'/etc/',  # 系统配置
            r'/bin/',  # 系统二进制
            r'/sbin/',  # 系统二进制
            r'/usr/bin/',  # 用户二进制
            r'/usr/sbin/',  # 用户二进制
            r'/root/',  # root目录
            r'/home/[^/]+/\.',  # 隐藏文件
            r'~/',  # 用户主目录
        ]

        # 允许的命令
        self.allowed_commands = {
            'brew', 'apt', 'yum', 'dnf', 'pacman',  # 包管理器
            'mednafen', 'fceux', 'nestopia', 'snes9x', 'visualboyadvance-m',  # 模拟器
            'which', 'whereis', 'ls', 'cat', 'mkdir', 'rm', 'cp', 'mv'  # 基本命令
        }

        # 危险命令模式
        self.dangerous_command_patterns = [
            r'rm\s+-rf\s+/',  # 删除根目录
            r'sudo\s+rm',  # sudo删除
            r'chmod\s+777',  # 危险权限
            r'curl.*\|\s*sh',  # 管道执行
            r'wget.*\|\s*sh',  # 管道执行
            r'eval\s*\(',  # eval执行
            r'exec\s*\(',  # exec执行
        ]

    def validate_environment(self) -> List[str]:
        """验证环境安全性"""
        issues = []

        try:
            # 检查当前用户权限
            if os.geteuid() == 0:  # root用户
                issues.append("不建议以root用户运行此程序")

            # 检查写入权限
            current_dir = Path.cwd()
            if not os.access(current_dir, os.W_OK):
                issues.append(f"当前目录没有写入权限: {current_dir}")

            # 检查必要的命令
            required_commands = ['python3', 'which']
            for cmd in required_commands:
                if not shutil.which(cmd):
                    issues.append(f"缺少必要命令: {cmd}")

            # 检查磁盘空间
            disk_usage = shutil.disk_usage(current_dir)
            free_space_mb = disk_usage.free / (1024 * 1024)
            if free_space_mb < 100:  # 少于100MB
                issues.append(f"磁盘空间不足: {free_space_mb:.1f}MB")

            logger.debug(f"🔒 环境安全检查完成，发现 {len(issues)} 个问题")

        except Exception as e:
            issues.append(f"环境检查异常: {e}")
            logger.error(f"❌ 环境安全检查失败: {e}")

        return issues

    def validate_path(self, path: Path, operation: str = "access"):
        """验证路径安全性"""
        if not self.config.security.validate_paths:
            return True

        try:
            # 转换为绝对路径
            abs_path = path.resolve()
            path_str = str(abs_path)

            # 检查危险路径模式
            for pattern in self.dangerous_path_patterns:
                if re.search(pattern, path_str, re.IGNORECASE):
                    logger.warning(f"⚠️ 危险路径模式: {path_str} 匹配 {pattern}")
                    return False

            # 检查路径是否在项目目录内
            project_root = Path.cwd().resolve()
            try:
                abs_path.relative_to(project_root)
            except ValueError:
                # 路径不在项目目录内
                if operation in ["write", "delete"]:
                    logger.warning(f"⚠️ 路径超出项目范围: {path_str}")
                    return False

            # 检查特殊操作
            if operation == "delete":
                # 不允许删除重要文件
                important_files = ['.git', 'README.md', 'requirements.txt', 'setup.py']
                if path.name in important_files:
                    logger.warning(f"⚠️ 不允许删除重要文件: {path.name}")
                    return False

            logger.debug(f"✅ 路径安全验证通过: {path_str}")
            return True

        except Exception as e:
            logger.error(f"❌ 路径验证异常: {e}")
            return False

    def validate_command(self, command: List[str]):
        """验证命令安全性"""
        if not self.config.security.restrict_commands:
            return True

        if not command:
            return False

        try:
            cmd_name = command[0]
            cmd_line = ' '.join(command)

            # 检查命令是否在允许列表中
            if cmd_name not in self.allowed_commands:
                logger.warning(f"⚠️ 不允许的命令: {cmd_name}")
                return False

            # 检查危险命令模式
            for pattern in self.dangerous_command_patterns:
                if re.search(pattern, cmd_line, re.IGNORECASE):
                    logger.warning(f"⚠️ 危险命令模式: {cmd_line} 匹配 {pattern}")
                    return False

            # 检查sudo使用
            if 'sudo' in command:
                # 只允许特定的sudo命令
                allowed_sudo_commands = ['apt', 'yum', 'dnf', 'pacman']
                if len(command) < 2 or command[1] not in allowed_sudo_commands:
                    logger.warning(f"⚠️ 不允许的sudo命令: {cmd_line}")
                    return False

            logger.debug(f"✅ 命令安全验证通过: {cmd_line}")
            return True

        except Exception as e:
            logger.error(f"❌ 命令验证异常: {e}")
            return False

    def validate_file_content(self, content: bytes, file_type: str = "unknown"):
        """验证文件内容安全性"""
        if not self.config.security.safe_mode:
            return True

        try:
            # 检查文件大小
            max_size = 100 * 1024 * 1024  # 100MB
            if len(content) > max_size:
                logger.warning(f"⚠️ 文件过大: {len(content)} bytes")
                return False

            # 检查二进制文件的魔数
            if file_type in ["rom", "binary"]:
                # ROM文件的基本检查
                if len(content) < 16:
                    logger.warning("⚠️ ROM文件过小")
                    return False

                # 检查是否包含可执行代码标识
                executable_signatures = [
                    b'\x7fELF',  # ELF
                    b'MZ',       # PE
                    b'\xca\xfe\xba\xbe',  # Mach-O
                ]

                for sig in executable_signatures:
                    if content.startswith(sig):
                        logger.warning(f"⚠️ 检测到可执行文件签名: {sig}")
                        return False

            # 检查文本文件
            elif file_type in ["config", "text"]:
                try:
                    text_content = content.decode('utf-8', errors='ignore')

                    # 检查危险脚本内容
                    dangerous_patterns = [
                        r'eval\s*\(',
                        r'exec\s*\(',
                        r'system\s*\(',
                        r'subprocess\.',
                        r'os\.system',
                        r'__import__',
                    ]

                    for pattern in dangerous_patterns:
                        if re.search(pattern, text_content, re.IGNORECASE):
                            logger.warning(f"⚠️ 检测到危险脚本模式: {pattern}")
                            return False

                except UnicodeDecodeError:
                    # 无法解码为文本，可能是二进制文件
                    pass

            logger.debug(f"✅ 文件内容安全验证通过: {file_type}")
            return True

        except Exception as e:
            logger.error(f"❌ 文件内容验证异常: {e}")
            return False

    def check_permissions(self, path: Path, required_permissions: str):
        """检查文件权限"""
        if not self.config.security.check_permissions:
            return True

        try:
            if not path.exists():
                # 检查父目录权限
                parent = path.parent
                if not parent.exists():
                    return False
                path = parent

            # 检查读权限
            if 'r' in required_permissions and not os.access(path, os.R_OK):
                logger.warning(f"⚠️ 缺少读权限: {path}")
                return False

            # 检查写权限
            if 'w' in required_permissions and not os.access(path, os.W_OK):
                logger.warning(f"⚠️ 缺少写权限: {path}")
                return False

            # 检查执行权限
            if 'x' in required_permissions and not os.access(path, os.X_OK):
                logger.warning(f"⚠️ 缺少执行权限: {path}")
                return False

            logger.debug(f"✅ 权限检查通过: {path} ({required_permissions})")
            return True

        except Exception as e:
            logger.error(f"❌ 权限检查异常: {e}")
            return False

    def safe_execute_command(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """安全执行命令"""
        # 验证命令安全性
        if not self.validate_command(command):
            raise SecurityError(f"命令安全验证失败: {' '.join(command)}")

        # 设置安全的执行环境
        safe_kwargs = {
            'capture_output': True,
            'text': True,
            'timeout': 300,  # 5分钟超时
            'check': False,  # 不自动抛出异常
        }
        safe_kwargs.update(kwargs)

        # 清理环境变量
        if 'env' not in safe_kwargs:
            safe_env = {
                'PATH': os.environ.get('PATH', ''),
                'HOME': os.environ.get('HOME', ''),
                'USER': os.environ.get('USER', ''),
                'LANG': os.environ.get('LANG', 'en_US.UTF-8'),
            }
            safe_kwargs['env'] = safe_env

        try:
            logger.debug(f"🔒 安全执行命令: {' '.join(command)}")
            result = subprocess.run(command, **safe_kwargs)
            logger.debug(f"✅ 命令执行完成，返回码: {result.returncode}")
            return result

        except subprocess.TimeoutExpired as e:
            logger.error(f"❌ 命令执行超时: {' '.join(command)}")
            raise
        except Exception as e:
            logger.error(f"❌ 命令执行异常: {e}")
            raise

    def get_security_summary(self) -> Dict[str, Any]:
        """获取安全状态摘要"""
        env_issues = self.validate_environment()

        return {
            "safe_mode": self.config.security.safe_mode,
            "validate_paths": self.config.security.validate_paths,
            "restrict_commands": self.config.security.restrict_commands,
            "check_permissions": self.config.security.check_permissions,
            "environment_issues": env_issues,
            "environment_healthy": len(env_issues) == 0,
            "allowed_commands": list(self.allowed_commands),
            "security_level": "high" if self.config.security.safe_mode else "normal"
        }


class SecurityError(Exception):
    """安全错误"""
    pass

if __name__ == "__main__":
    # 测试安全验证器
    validator = SecurityValidator()

    # 测试环境验证
    env_issues = validator.validate_environment()
    print(f"📊 环境问题: {len(env_issues)}")
    for issue in env_issues:
        print(f"  - {issue}")

    # 测试路径验证
    safe_path = Path("./test.txt")
    dangerous_path = Path("../../../etc/passwd")

    print(f"✅ 安全路径: {validator.validate_path(safe_path)}")
    print(f"❌ 危险路径: {validator.validate_path(dangerous_path)}")

    # 测试命令验证
    safe_command = ["brew", "install", "mednafen"]
    dangerous_command = ["rm", "-rf", "/"]

    print(f"✅ 安全命令: {validator.validate_command(safe_command)}")
    print(f"❌ 危险命令: {validator.validate_command(dangerous_command)}")

    # 获取安全摘要
    summary = validator.get_security_summary()
    print(f"🔒 安全级别: {summary['security_level']}")
    print(f"🌍 环境健康: {summary['environment_healthy']}")

    print("✅ 安全验证器测试完成")
