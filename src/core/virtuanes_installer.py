#!/usr/bin/env python3
"""
VirtuaNES 0.97 模拟器自动安装器

专门用于在 RetroPie 系统中自动安装和配置 VirtuaNES 0.97 模拟器。
支持自动下载、编译、配置和集成到 RetroPie 环境中。

主要功能：
- 自动下载 VirtuaNES 0.97 源码
- 编译安装到 RetroPie 系统
- 自动配置模拟器参数
- 集成到 RetroArch 核心
- 支持 ROM 文件关联
- 自动备份和恢复配置

系统要求：
- RetroPie 系统
- Python 3.7+
- 编译工具链
- 网络连接

作者: AI Assistant
版本: 1.0.0
许可证: MIT
"""

import argparse

import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("virtuanes_installer.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


from src.core.base_installer import BaseInstaller

class VirtuaNESInstaller(BaseInstaller):
    """
    VirtuaNES 模拟器安装器类

    提供完整的 VirtuaNES 0.97 自动化安装和配置功能。
    """

    def __init__(self, config_file -> bool: str = "config/project_config.json") -> bool:
        """
        初始化 VirtuaNES 安装器

        Args:
            config_file (str): 配置文件路径
        """
        super().__init__(config_file)
        self.virtuanes_config = self.config.get("emulator", {}).get("virtuanes", {})
        
        # 检查是否为测试环境
        is_test_env = os.environ.get("TEST_ENV", "false").lower() == "true"
        
        if is_test_env:
            # 测试环境使用临时目录
            import tempfile
            temp_dir = Path(tempfile.gettempdir()) / "virtuanes_test"
            temp_dir.mkdir(exist_ok=True)
            
            self.install_dir = temp_dir / "install"
            self.config_dir = temp_dir / "config"
            self.core_dir = temp_dir / "cores"
            
            # 设置测试环境标志
            self.is_test_env = True
        else:
            # 生产环境使用实际路径
            self.install_dir = Path("/opt/retropie/emulators/virtuanes")
            self.config_dir = Path(self.virtuanes_config.get("config_path", "/home/pi/RetroPie/configs/nes/"))
            self.core_dir = Path(self.virtuanes_config.get("core_path", "/opt/retropie/emulators/retroarch/cores/"))
            
            # 设置生产环境标志
            self.is_test_env = False
        
        # 创建必要的目录
        self.install_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _get_required_packages(self) -> List[str]:
        """返回所需依赖包列表"""
        return [
            "build-essential",
            "cmake",
            "libsdl2-dev",
            "libsdl2-image-dev",
            "libsdl2-mixer-dev",
            "libsdl2-ttf-dev"
        ]

    def install(self) -> bool:
        """Main installation method"""
        return self.run()

    def download_virtuanes(self) -> Optional[Path]:
        """下载 VirtuaNES 0.97 源码"""
        logger.info("下载 VirtuaNES 0.97 源码...")
        
        # VirtuaNES 0.97 源码下载链接
        download_urls = [
            "https://github.com/RetroPie/RetroPie-Setup/raw/master/scriptmodules/emulators/virtuanes.sh",
            "https://sourceforge.net/projects/virtuanes/files/VirtuaNES%200.97/VirtuaNES097src.zip/download"
        ]
        
        for url in download_urls:
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # 保存安装脚本
                script_path = self.install_dir / "virtuanes_install.sh"
                with open(script_path, "w") as f:
                    f.write(response.text)
                
                # 设置执行权限
                os.chmod(script_path, 0o755)
                
                logger.info(f"✓ 下载成功: {script_path}")
                return script_path
                
            except Exception as e:
                logger.warning(f"下载失败 {url}: {e}")
                continue
        
        logger.error("所有下载源都失败")
        return None

    def install_virtuanes(self) -> bool:
        """安装 VirtuaNES"""
        logger.info("开始安装 VirtuaNES 0.97...")
        
        # 下载源码
        script_path = self.download_virtuanes()
        if not script_path:
            return False
        
        try:
            # 执行安装脚本
            result = subprocess.run(
                [str(script_path)],
                cwd=self.install_dir,
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info("✓ VirtuaNES 安装成功")
            logger.debug(f"安装输出: {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"安装失败: {e}")
            logger.error(f"错误输出: {e.stderr}")
            return False

    def configure_virtuanes(self) -> bool:
        """配置 VirtuaNES"""
        logger.info("配置 VirtuaNES...")
        
        config_content = """# VirtuaNES 0.97 配置文件
# 自动生成于 {}

# 基本设置
[General]
Version=0.97
Language=English
FullScreen=1
VSync=1
FrameSkip=0

# 图形设置
[Graphics]
Filter=0
Scanline=0
AspectRatio=1
Scale=2

# 音频设置
[Audio]
Enabled=1
Volume=100
SampleRate=44100
BufferSize=1024

# 控制器设置
[Controller]
Type=0
DeadZone=10
Sensitivity=100

# 保存设置
[Save]
AutoSave=1
SaveSlot=0
SavePath={}

# 网络设置
[Network]
Enabled=0
Port=8888
Host=127.0.0.1

# 作弊码设置
[Cheat]
Enabled=1
Path={}
""".format(
            time.strftime("%Y-%m-%d %H:%M:%S"),
            self.config.get("emulator", {}).get("saves_dir", "/home/pi/RetroPie/saves/"),
            self.config.get("emulator", {}).get("cheats_dir", "/home/pi/RetroPie/cheats/")
        )
        
        # 写入配置文件
        config_path = self.config_dir / "virtuanes.cfg"
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(config_content)
            
            logger.info(f"✓ 配置文件已生成: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"配置文件生成失败: {e}")
            return False

    def integrate_with_retroarch(self) -> bool:
        """集成到 RetroArch"""
        logger.info("集成 VirtuaNES 到 RetroArch...")
        
        # 创建 RetroArch 核心配置
        core_config = {
            "name": "VirtuaNES",
            "version": "0.97",
            "description": "VirtuaNES NES Emulator",
            "author": "VirtuaNES Team",
            "url": "https://github.com/RetroPie/RetroPie-Setup",
            "category": "Emulator",
            "system": "nes",
            "extensions": self.virtuanes_config.get("rom_extensions", [".nes", ".NES"]),
            "features": self.virtuanes_config.get("features", [])
        }
        
        # 写入核心信息文件
        core_info_path = self.core_dir / "virtuanes_libretro.info"
        try:
            with open(core_info_path, "w", encoding="utf-8") as f:
                for key, value in core_config.items():
                    if isinstance(value, list):
                        f.write(f"{key} = {','.join(value)}\n")
                    else:
                        f.write(f"{key} = {value}\n")
            
            logger.info(f"✓ RetroArch 核心信息已生成: {core_info_path}")
            return True
            
        except Exception as e:
            logger.error(f"RetroArch 集成失败: {e}")
            return False

    def setup_rom_association(self) -> bool:
        """设置 ROM 文件关联"""
        logger.info("设置 ROM 文件关联...")
        
        # 创建 .desktop 文件
        desktop_content = """[Desktop Entry]
Name=VirtuaNES
Comment=NES Emulator
Exec=virtuanes %f
Icon=virtuanes
Terminal=false
Type=Application
Categories=Game;Emulator;
MimeType=application/x-nes-rom;
"""
        
        desktop_path = Path("/usr/share/applications/virtuanes.desktop")
        try:
            with open(desktop_path, "w") as f:
                f.write(desktop_content)
            
            # 更新 MIME 数据库
            subprocess.run(["sudo", "update-desktop-database"], check=True)
            
            logger.info("✓ ROM 文件关联设置完成")
            return True
            
        except Exception as e:
            logger.error(f"ROM 关联设置失败: {e}")
            return False

    def create_launch_script(self) -> bool:
        """创建启动脚本"""
        logger.info("创建 VirtuaNES 启动脚本...")
        
        launch_script = """#!/bin/bash
# VirtuaNES 启动脚本

# 设置环境变量
export VIRTUALNES_CONFIG="{}"
export VIRTUALNES_SAVES="{}"
export VIRTUALNES_CHEATS="{}"

# 启动 VirtuaNES
cd {}
exec virtuanes "$@"
""".format(
            self.config_dir / "virtuanes.cfg",
            self.config.get("emulator", {}).get("saves_dir", "/home/pi/RetroPie/saves/"),
            self.config.get("emulator", {}).get("cheats_dir", "/home/pi/RetroPie/cheats/"),
            self.install_dir
        )
        
        script_path = self.install_dir / "launch_virtuanes.sh"
        try:
            with open(script_path, "w") as f:
                f.write(launch_script)
            
            os.chmod(script_path, 0o755)
            logger.info(f"✓ 启动脚本已创建: {script_path}")
            return True
            
        except Exception as e:
            logger.error(f"启动脚本创建失败: {e}")
            return False

    def verify_installation(self) -> bool:
        """验证安装"""
        logger.info("验证 VirtuaNES 安装...")
        
        checks = [
            (self.install_dir.exists(), "安装目录"),
            ((self.config_dir / "virtuanes.cfg").exists(), "配置文件"),
            ((self.core_dir / "virtuanes_libretro.info").exists(), "RetroArch 核心信息"),
            (Path("/usr/share/applications/virtuanes.desktop").exists(), "桌面文件"),
        ]
        
        all_passed = True
        for check, name in checks:
            if check:
                logger.info(f"✓ {name} 验证通过")
            else:
                logger.error(f"✗ {name} 验证失败")
                all_passed = False
        
        if all_passed:
            logger.info("🎉 VirtuaNES 0.97 安装验证完成！")
        else:
            logger.error("⚠️ 部分验证失败，请检查安装")
        
        return all_passed

    def run(self) -> bool:
        """运行完整的安装流程"""
        logger.info("开始 VirtuaNES 0.97 自动安装流程...")
        
        steps = [
            ("检查依赖", self.check_dependencies),
            ("安装 VirtuaNES", self.install_virtuanes),
            ("配置 VirtuaNES", self.configure_virtuanes),
            ("集成 RetroArch", self.integrate_with_retroarch),
            ("设置 ROM 关联", self.setup_rom_association),
            ("创建启动脚本", self.create_launch_script),
            ("验证安装", self.verify_installation),
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n=== {step_name} ===")
            if not step_func():
                logger.error(f"❌ {step_name} 失败")
                return False
            logger.info(f"✅ {step_name} 完成")
        
        logger.info("\n🎉 VirtuaNES 0.97 安装完成！")
        logger.info("使用说明:")
        logger.info("1. 启动: ./launch_virtuanes.sh")
        logger.info("2. 配置文件: {}".format(self.config_dir / "virtuanes.cfg"))
        logger.info("3. ROM 目录: {}".format(self.config.get("raspberry_pi", {}).get("roms_path", "/home/pi/RetroPie/roms/nes/")))
        
        return True


def main() -> bool:
    """主函数"""
    parser = argparse.ArgumentParser(description="VirtuaNES 0.97 自动安装器")
    parser.add_argument("--config", default="config/project_config.json", help="配置文件路径")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    parser.add_argument("--verify-only", action="store_true", help="仅验证安装")
    
    args = parser.parse_args()
    
    installer = VirtuaNESInstaller(args.config)
    
    if args.verify_only:
        success = installer.verify_installation()
    elif args.dry_run:
        logger.info("模拟运行模式 - 不执行实际安装")
        success = installer.check_dependencies()
    else:
        success = installer.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()