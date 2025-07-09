#!/usr/bin/env python3
"""
树莓派镜像一键生成器
支持自动下载、定制、优化和压缩镜像
"""

import os
import sys
import json
import shutil
import subprocess
import logging
import hashlib
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import tempfile
import zipfile
import gzip
import signal
import time

# 配置日志
def setup_logging():
    """设置日志配置"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"image_builder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

@dataclass
class ImageConfig:
    """镜像配置"""
    name: str
    version: str
    url: str
    checksum: str
    size_mb: int
    description: str

class RaspberryImageBuilder:
    """树莓派镜像构建器"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(exist_ok=True)
        self.downloads_dir = Path("downloads").resolve()
        self.downloads_dir.mkdir(exist_ok=True)
        
        # 临时目录使用更安全的路径
        self.temp_dir = Path(tempfile.mkdtemp(prefix="pi_builder_", dir="/tmp"))
        
        # 挂载点和循环设备跟踪
        self.mounted_points = []
        self.loop_devices = []
        
        # 注册清理函数
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # 镜像配置 - 使用更稳定的镜像源
        self.image_configs = {
            "retropie_4.8": ImageConfig(
                name="RetroPie 4.8",
                version="4.8",
                url="https://github.com/RetroPie/RetroPie-Setup/releases/download/4.8/retropie-buster-4.8-rpi4_400.img.gz",
                checksum="",  # 将在运行时跳过校验
                size_mb=3500,
                description="RetroPie 4.8 for Raspberry Pi 4/400"
            ),
            "raspios_lite": ImageConfig(
                name="Raspberry Pi OS Lite",
                version="2023-12-05",
                url="https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2023-12-06/2023-12-05-raspios-bookworm-armhf-lite.img.xz",
                checksum="",  # 将在运行时跳过校验
                size_mb=2000,
                description="Raspberry Pi OS Lite (32-bit)"
            )
        }
        
        # 定制配置
        self.customizations = {
            "enable_ssh": True,
            "wifi_config": True,
            "auto_expand_filesystem": True,
            "install_gameplayer": True,
            "optimize_performance": True,
            "cleanup_unnecessary": True
        }
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.warning(f"接收到信号 {signum}，开始清理...")
        self.cleanup()
        sys.exit(1)
    
    def cleanup(self):
        """清理资源"""
        logger.info("🧹 开始清理资源...")
        
        # 卸载所有挂载点
        for mount_point in reversed(self.mounted_points):
            if mount_point and Path(mount_point).exists():
                try:
                    subprocess.run(['sudo', 'umount', '-f', mount_point], 
                                 check=False, capture_output=True)
                    logger.info(f"已卸载: {mount_point}")
                except Exception as e:
                    logger.warning(f"卸载失败 {mount_point}: {e}")
        
        # 分离所有循环设备
        for loop_device in self.loop_devices:
            try:
                subprocess.run(['sudo', 'losetup', '-d', loop_device], 
                             check=False, capture_output=True)
                logger.info(f"已分离循环设备: {loop_device}")
            except Exception as e:
                logger.warning(f"分离循环设备失败 {loop_device}: {e}")
        
        # 清理临时目录
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                logger.info(f"已清理临时目录: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"清理临时目录失败: {e}")
        
        # 清空跟踪列表
        self.mounted_points.clear()
        self.loop_devices.clear()
    
    def __del__(self):
        """析构函数"""
        self.cleanup()
    
    def check_system_requirements(self) -> bool:
        """检查系统要求"""
        logger.info("🔍 检查系统要求...")
        
        # 检查是否为root权限
        if os.geteuid() != 0:
            logger.error("❌ 需要root权限运行此脚本")
            logger.info("请使用: sudo python3 raspberry_image_builder.py")
            return False
        
        # 检查必需命令
        required_commands = ['losetup', 'mount', 'umount', 'kpartx', 'chroot', 'wget', 'gzip', 'xz']
        missing_commands = []
        
        for cmd in required_commands:
            if not shutil.which(cmd):
                missing_commands.append(cmd)
        
        if missing_commands:
            logger.error(f"❌ 缺少必需命令: {', '.join(missing_commands)}")
            logger.info("请安装缺少的软件包")
            return False
        
        # 检查磁盘空间 (至少需要10GB)
        try:
            stat = shutil.disk_usage(self.output_dir)
            free_gb = stat.free / (1024**3)
            if free_gb < 10:
                logger.warning(f"⚠️ 磁盘空间不足: {free_gb:.1f}GB，建议至少10GB")
        except Exception as e:
            logger.warning(f"⚠️ 无法检查磁盘空间: {e}")
        
        logger.info("✅ 系统要求检查通过")
        return True
    
    def download_image(self, image_key: str) -> Optional[Path]:
        """下载镜像文件"""
        if image_key not in self.image_configs:
            logger.error(f"❌ 未知的镜像类型: {image_key}")
            return None
        
        config = self.image_configs[image_key]
        filename = Path(config.url).name
        local_path = self.downloads_dir / filename
        
        # 检查是否已下载
        if local_path.exists() and local_path.stat().st_size > 0:
            logger.info(f"✅ 镜像已存在: {filename}")
            return local_path
        
        logger.info(f"📥 开始下载镜像: {config.name}")
        logger.info(f"🔗 URL: {config.url}")
        
        try:
            # 使用更健壮的下载方式
            temp_path = local_path.with_suffix(local_path.suffix + '.tmp')
            
            response = requests.get(config.url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            mb_downloaded = downloaded // (1024 * 1024)
                            mb_total = total_size // (1024 * 1024)
                            print(f"\r📥 下载进度: {progress:.1f}% ({mb_downloaded}MB/{mb_total}MB)", end='', flush=True)
            
            print()  # 换行
            
            # 原子性重命名
            temp_path.rename(local_path)
            logger.info(f"✅ 下载完成: {filename}")
            return local_path
                
        except Exception as e:
            logger.error(f"❌ 下载失败: {e}")
            # 清理临时文件
            if 'temp_path' in locals() and temp_path.exists():
                temp_path.unlink()
            if local_path.exists():
                local_path.unlink()
            return None
    
    def extract_image(self, compressed_path: Path) -> Optional[Path]:
        """解压镜像文件"""
        logger.info(f"📦 解压镜像: {compressed_path.name}")
        
        # 确定解压后的文件名
        if compressed_path.suffix == '.gz':
            extracted_name = compressed_path.stem
        elif compressed_path.suffix == '.xz':
            extracted_name = compressed_path.stem
        elif compressed_path.suffix == '.zip':
            extracted_name = compressed_path.stem + '.img'
        else:
            extracted_name = compressed_path.name + '.img'
        
        extracted_path = self.temp_dir / extracted_name
        
        try:
            if compressed_path.suffix == '.gz':
                with gzip.open(compressed_path, 'rb') as f_in:
                    with open(extracted_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out, length=1024*1024)  # 1MB chunks
            elif compressed_path.suffix == '.xz':
                result = subprocess.run(['xz', '-d', '-c', str(compressed_path)], 
                                     stdout=open(extracted_path, 'wb'), 
                                     stderr=subprocess.PIPE, check=True)
            elif compressed_path.suffix == '.zip':
                with zipfile.ZipFile(compressed_path, 'r') as zip_ref:
                    zip_ref.extractall(self.temp_dir)
                    # 找到.img文件
                    for file_path in self.temp_dir.glob('*.img'):
                        extracted_path = file_path
                        break
            else:
                # 假设已经是.img文件
                shutil.copy2(compressed_path, extracted_path)
            
            if not extracted_path.exists():
                raise FileNotFoundError("解压后的镜像文件不存在")
            
            logger.info(f"✅ 解压完成: {extracted_path.name}")
            return extracted_path
            
        except Exception as e:
            logger.error(f"❌ 解压失败: {e}")
            return None
    
    def mount_image(self, image_path: Path) -> Optional[Tuple[Path, Path]]:
        """挂载镜像文件，返回(根分区挂载点, boot分区挂载点)"""
        logger.info(f"🔧 挂载镜像: {image_path.name}")
        
        try:
            # 创建loop设备
            result = subprocess.run(
                ['losetup', '--show', '-Pf', str(image_path)],
                capture_output=True, text=True, check=True
            )
            loop_device = result.stdout.strip()
            self.loop_devices.append(loop_device)
            logger.info(f"📎 Loop设备: {loop_device}")
            
            # 等待分区设备创建
            time.sleep(2)
            
            # 使用kpartx创建分区映射
            subprocess.run(['kpartx', '-av', loop_device], check=True, capture_output=True)
            time.sleep(1)
            
            # 创建挂载点
            root_mount = self.temp_dir / "root_mount"
            boot_mount = self.temp_dir / "boot_mount"
            root_mount.mkdir(exist_ok=True)
            boot_mount.mkdir(exist_ok=True)
            
            # 确定分区设备路径
            root_partition = f"{loop_device}p2"
            boot_partition = f"{loop_device}p1"
            
            # 如果直接分区不存在，尝试映射设备
            if not Path(root_partition).exists():
                mapper_base = f"/dev/mapper/{Path(loop_device).name}"
                root_partition = f"{mapper_base}p2"
                boot_partition = f"{mapper_base}p1"
            
            # 验证分区设备存在
            if not Path(root_partition).exists() or not Path(boot_partition).exists():
                raise FileNotFoundError(f"找不到分区设备: {root_partition}, {boot_partition}")
            
            # 挂载根分区
            subprocess.run(['mount', root_partition, str(root_mount)], check=True)
            self.mounted_points.append(str(root_mount))
            
            # 挂载boot分区到根分区的boot目录
            boot_in_root = root_mount / "boot"
            if boot_in_root.exists():
                subprocess.run(['mount', boot_partition, str(boot_in_root)], check=True)
                self.mounted_points.append(str(boot_in_root))
                boot_mount_point = boot_in_root
            else:
                # 如果根分区中没有boot目录，单独挂载
                subprocess.run(['mount', boot_partition, str(boot_mount)], check=True)
                self.mounted_points.append(str(boot_mount))
                boot_mount_point = boot_mount
            
            logger.info(f"✅ 镜像已挂载 - 根: {root_mount}, Boot: {boot_mount_point}")
            return root_mount, boot_mount_point
            
        except Exception as e:
            logger.error(f"❌ 挂载失败: {e}")
            return None
    
    def customize_image(self, root_mount: Path, boot_mount: Path) -> bool:
        """定制镜像"""
        logger.info("🎨 开始定制镜像...")
        
        try:
            # 启用SSH
            if self.customizations["enable_ssh"]:
                self._enable_ssh(boot_mount)
            
            # 配置WiFi
            if self.customizations["wifi_config"]:
                self._setup_wifi_config(boot_mount)
            
            # 自动扩展文件系统
            if self.customizations["auto_expand_filesystem"]:
                self._enable_auto_expand(boot_mount)
            
            # 安装GamePlayer
            if self.customizations["install_gameplayer"]:
                self._install_gameplayer(root_mount)
            
            # 性能优化
            if self.customizations["optimize_performance"]:
                self._optimize_performance(boot_mount)
            
            # 清理不必要文件
            if self.customizations["cleanup_unnecessary"]:
                self._cleanup_image(root_mount)
            
            logger.info("✅ 镜像定制完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 镜像定制失败: {e}")
            return False
    
    def _enable_ssh(self, boot_mount: Path):
        """启用SSH"""
        logger.info("🔐 启用SSH...")
        
        ssh_file = boot_mount / "ssh"
        ssh_file.touch()
        logger.info("✅ SSH已启用")
    
    def _setup_wifi_config(self, boot_mount: Path):
        """设置WiFi配置模板"""
        logger.info("📶 配置WiFi模板...")
        
        wpa_config = boot_mount / "wpa_supplicant.conf"
        config_content = '''country=CN
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

# 配置你的WiFi网络
# network={
#     ssid="YOUR_WIFI_SSID"
#     psk="YOUR_WIFI_PASSWORD"
#     key_mgmt=WPA-PSK
# }
'''
        
        try:
            with open(wpa_config, 'w') as f:
                f.write(config_content)
            logger.info("✅ WiFi配置模板已创建")
        except Exception as e:
            logger.warning(f"⚠️ WiFi配置创建失败: {e}")
    
    def _enable_auto_expand(self, boot_mount: Path):
        """启用自动扩展文件系统"""
        logger.info("💾 启用自动扩展文件系统...")
        
        try:
            cmdline_file = boot_mount / "cmdline.txt"
            if cmdline_file.exists():
                with open(cmdline_file, 'r') as f:
                    cmdline = f.read().strip()
                
                if 'init=/usr/lib/raspi-config/init_resize.sh' not in cmdline:
                    cmdline += ' init=/usr/lib/raspi-config/init_resize.sh'
                    
                    with open(cmdline_file, 'w') as f:
                        f.write(cmdline)
                    
                    logger.info("✅ 自动扩展文件系统已启用")
                else:
                    logger.info("✅ 自动扩展文件系统已经启用")
            else:
                logger.warning("⚠️ 找不到cmdline.txt文件")
        except Exception as e:
            logger.warning(f"⚠️ 启用自动扩展失败: {e}")
    
    def _install_gameplayer(self, root_mount: Path):
        """安装GamePlayer到镜像"""
        logger.info("🎮 安装GamePlayer...")

        try:
            # 创建目标目录
            target_dir = root_mount / "home" / "pi" / "GamePlayer-Raspberry"
            target_dir.mkdir(parents=True, exist_ok=True)

            # 复制项目文件
            project_root = Path(__file__).parent.parent.parent
            source_dirs = ["src", "config", "data"]
            source_files = ["requirements.txt", "README.md"]

            for source_dir in source_dirs:
                source_path = project_root / source_dir
                if source_path.exists():
                    target_path = target_dir / source_dir
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.copytree(source_path, target_path, ignore_dangling_symlinks=True)
                    logger.info(f"✅ 已复制目录: {source_dir}")
                else:
                    logger.warning(f"⚠️ 源目录不存在: {source_dir}")

            for source_file in source_files:
                source_path = project_root / source_file
                if source_path.exists():
                    target_path = target_dir / source_file
                    shutil.copy2(source_path, target_path)
                    logger.info(f"✅ 已复制文件: {source_file}")

            # 创建ROM目录
            roms_dir = root_mount / "home" / "pi" / "RetroPie" / "roms" / "nes"
            roms_dir.mkdir(parents=True, exist_ok=True)

            # 创建示例ROM
            self._create_sample_roms(roms_dir)

            # 设置正确的所有权
            try:
                subprocess.run(['chown', '-R', '1000:1000', str(target_dir)], check=False)
                subprocess.run(['chown', '-R', '1000:1000', str(roms_dir.parent.parent)], check=False)
            except Exception as e:
                logger.warning(f"⚠️ 设置文件所有权失败: {e}")

            # 创建自启动脚本
            self._create_startup_script(root_mount)

            logger.info("✅ GamePlayer安装完成")

        except Exception as e:
            logger.error(f"❌ GamePlayer安装失败: {e}")
            raise

    def _create_sample_roms(self, roms_dir: Path):
        """创建示例ROM文件"""
        logger.info("📝 创建示例ROM文件...")

        sample_roms = {
            "demo_game.nes": "Demo Game - Test ROM",
            "sample_platformer.nes": "Sample Platformer",
            "test_shooter.nes": "Test Shooter Game",
            "puzzle_demo.nes": "Puzzle Game Demo",
            "racing_demo.nes": "Racing Game Demo"
        }

        rom_catalog = {
            "roms": [],
            "categories": ["demo", "test", "sample"],
            "total_count": len(sample_roms),
            "created_date": datetime.now().isoformat()
        }

        for filename, description in sample_roms.items():
            rom_file = roms_dir / filename
            try:
                # 创建最小的NES ROM文件
                header = bytearray(16)
                header[0:4] = b'NES\x1a'  # NES文件标识
                header[4] = 1  # PRG ROM 大小 (16KB)
                header[5] = 1  # CHR ROM 大小 (8KB)

                prg_rom = bytearray(16384)  # 16KB PRG ROM
                chr_rom = bytearray(8192)   # 8KB CHR ROM

                # 在PRG ROM中添加标题信息
                title_bytes = description.encode('ascii', errors='ignore')[:16]
                prg_rom[0:len(title_bytes)] = title_bytes

                # 添加一些测试代码（NOP指令）
                for i in range(len(title_bytes), min(100, len(prg_rom))):
                    prg_rom[i] = 0xEA  # NOP instruction

                rom_content = bytes(header + prg_rom + chr_rom)

                with open(rom_file, 'wb') as f:
                    f.write(rom_content)
                # 添加到目录
                rom_catalog["roms"].append({
                    "filename": filename,
                    "title": description,
                    "size": len(rom_content),
                    "category": "demo",
                    "playable": True
                })

                logger.info(f"✅ 创建示例ROM: {filename}")

            except Exception as e:
                logger.error(f"❌ 创建示例ROM失败 {filename}: {e}")

        # 保存ROM目录
        try:
            catalog_file = roms_dir / "rom_catalog.json"
            with open(catalog_file, 'w', encoding='utf-8') as f:
                json.dump(rom_catalog, f, indent=2, ensure_ascii=False)
            logger.info("✅ ROM目录已创建")
        except Exception as e:
            logger.warning(f"⚠️ ROM目录创建失败: {e}")

    def _create_startup_script(self, root_mount: Path):
        """创建启动脚本"""
        logger.info("🚀 创建启动脚本...")

        try:
            # 创建启动脚本
            startup_script = root_mount / "home" / "pi" / "start_gameplayer.sh"
            script_content = '''#!/bin/bash
# GamePlayer-Raspberry 自动启动脚本

export HOME=/home/pi
export USER=pi
export DISPLAY=:0

# 创建日志目录
mkdir -p /home/pi/logs

# 等待网络就绪
sleep 10

cd /home/pi/GamePlayer-Raspberry

# 检查并启动Web服务器
if [ -d "data/web" ]; then
    echo "$(date): 启动Web服务器..." >> /home/pi/logs/startup.log
    python3 -m http.server 8080 --directory data/web >> /home/pi/logs/web_server.log 2>&1 &
else
    echo "$(date): Web目录不存在，创建基本Web界面..." >> /home/pi/logs/startup.log
    mkdir -p data/web
    echo "<h1>🎮 GamePlayer-Raspberry</h1><p>游戏系统启动中...</p>" > data/web/index.html
    python3 -m http.server 8080 --directory data/web >> /home/pi/logs/web_server.log 2>&1 &
fi

# 检查并启动游戏系统
if [ -f "src/core/nes_emulator.py" ]; then
    echo "$(date): 启动游戏系统..." >> /home/pi/logs/startup.log
    cd src && python3 -c "
try:
    from core.nes_emulator import NESEmulator
    print('GamePlayer系统就绪')
except Exception as e:
    print(f'GamePlayer启动失败: {e}')
" >> /home/pi/logs/startup.log 2>&1
fi

echo "$(date): GamePlayer-Raspberry 启动完成" >> /home/pi/logs/startup.log
'''

            with open(startup_script, 'w') as f:
                f.write(script_content)
            
            # 设置执行权限
            os.chmod(startup_script, 0o755)

            # 创建systemd服务文件
            service_file = root_mount / "etc" / "systemd" / "system" / "gameplayer.service"
            service_content = '''[Unit]
Description=GamePlayer-Raspberry Auto Start
After=multi-user.target network.target
Wants=network.target

[Service]
Type=forking
User=pi
Group=pi
WorkingDirectory=/home/pi
ExecStart=/home/pi/start_gameplayer.sh
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
'''

            with open(service_file, 'w') as f:
                f.write(service_content)

            # 启用服务（在chroot环境中）
            try:
                # 创建符号链接来启用服务
                service_link = root_mount / "etc" / "systemd" / "system" / "multi-user.target.wants" / "gameplayer.service"
                service_link.parent.mkdir(parents=True, exist_ok=True)
                if service_link.exists():
                    service_link.unlink()
                service_link.symlink_to("../gameplayer.service")
                logger.info("✅ 自启动服务已启用")
            except Exception as e:
                logger.warning(f"⚠️ 启用自启动服务失败: {e}")

        except Exception as e:
            logger.error(f"❌ 创建启动脚本失败: {e}")
            raise
    
    def _optimize_performance(self, boot_mount: Path):
        """性能优化"""
        logger.info("⚡ 性能优化...")
        
        try:
            config_file = boot_mount / "config.txt"
            if config_file.exists():
                with open(config_file, 'a') as f:
                    f.write('\n# GamePlayer Performance Optimizations\n')
                    f.write('gpu_mem=128\n')
                    f.write('disable_splash=1\n')
                    f.write('boot_delay=0\n')
                    f.write('disable_overscan=1\n')
                    f.write('hdmi_force_hotplug=1\n')
                
                logger.info("✅ 性能优化完成")
            else:
                logger.warning("⚠️ 找不到config.txt文件")
        except Exception as e:
            logger.warning(f"⚠️ 性能优化失败: {e}")
    
    def _cleanup_image(self, root_mount: Path):
        """清理镜像"""
        logger.info("🧹 清理镜像...")
        
        cleanup_paths = [
            "var/cache/apt/archives/*.deb",
            "var/lib/apt/lists/*",
            "tmp/*",
            "var/tmp/*",
            "var/log/*.log",
            "var/log/*/*.log"
        ]
        
        for path_pattern in cleanup_paths:
            full_pattern = root_mount / path_pattern
            try:
                # 使用shell展开来处理通配符
                subprocess.run(f'rm -rf {full_pattern}', shell=True, check=False)
            except Exception as e:
                logger.debug(f"清理 {path_pattern} 失败: {e}")
        
        logger.info("✅ 镜像清理完成")
    
    def unmount_image(self):
        """卸载镜像"""
        logger.info("📤 卸载镜像...")
        
        # 使用cleanup方法来卸载所有资源
        self.cleanup()
        logger.info("✅ 镜像已卸载")
    
    def compress_image(self, image_path: Path) -> Path:
        """压缩镜像"""
        logger.info(f"🗜️ 压缩镜像: {image_path.name}")
        
        compressed_path = self.output_dir / f"{image_path.stem}_gameplayer.img.gz"
        
        try:
            # 使用较小的缓冲区以减少内存使用
            with open(image_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb', compresslevel=6) as f_out:
                    chunk_size = 1024 * 1024  # 1MB chunks
                    while True:
                        chunk = f_in.read(chunk_size)
                        if not chunk:
                            break
                        f_out.write(chunk)
            
            # 计算压缩比
            original_size = image_path.stat().st_size
            compressed_size = compressed_path.stat().st_size
            ratio = (1 - compressed_size / original_size) * 100
            
            logger.info(f"✅ 压缩完成: {compressed_path.name}")
            logger.info(f"📊 压缩比: {ratio:.1f}% (原始: {original_size//1024//1024}MB, 压缩后: {compressed_size//1024//1024}MB)")
            
            return compressed_path
            
        except Exception as e:
            logger.error(f"❌ 压缩失败: {e}")
            raise
    
    def build_image(self, image_key: str = "retropie_4.8") -> Optional[Path]:
        """构建完整镜像"""
        logger.info(f"🚀 开始构建镜像: {image_key}")
        
        try:
            # 检查系统要求
            if not self.check_system_requirements():
                return None
            
            # 1. 下载镜像
            compressed_image = self.download_image(image_key)
            if not compressed_image:
                return None
            
            # 2. 解压镜像
            image_path = self.extract_image(compressed_image)
            if not image_path:
                return None
            
            # 3. 挂载镜像
            mount_result = self.mount_image(image_path)
            if not mount_result:
                return None
            
            root_mount, boot_mount = mount_result
            
            # 4. 定制镜像
            if not self.customize_image(root_mount, boot_mount):
                self.unmount_image()
                return None
            
            # 5. 卸载镜像
            self.unmount_image()
            
            # 6. 压缩镜像
            final_image = self.compress_image(image_path)
            
            # 7. 生成信息文件
            self._generate_image_info(final_image, image_key)
            
            logger.info(f"🎉 镜像构建完成: {final_image}")
            return final_image
            
        except Exception as e:
            logger.error(f"❌ 镜像构建失败: {e}")
            return None
        finally:
            # 确保清理资源
            self.cleanup()
    
    def _generate_image_info(self, image_path: Path, image_key: str):
        """生成镜像信息文件"""
        try:
            # 计算校验和
            checksum = self._calculate_file_checksum(image_path)
            
            info = {
                "name": f"GamePlayer-Raspberry {self.image_configs[image_key].name}",
                "version": "1.0.0",
                "base_image": self.image_configs[image_key].name,
                "build_date": datetime.now().isoformat(),
                "file_size_mb": image_path.stat().st_size // 1024 // 1024,
                "checksum_sha256": checksum,
                "features": [k for k, v in self.customizations.items() if v],
                "installation_guide": {
                    "method1": "使用 Raspberry Pi Imager 烧录到SD卡",
                    "method2": f"使用 dd 命令: sudo dd if={image_path.name} of=/dev/sdX bs=4M status=progress",
                    "first_boot": "首次启动会自动扩展文件系统并启动GamePlayer系统",
                    "web_access": "访问 http://树莓派IP:8080 进入游戏界面"
                },
                "default_credentials": {
                    "username": "pi",
                    "password": "raspberry"
                }
            }
            
            # 保存为JSON
            info_file = image_path.with_suffix('.json')
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(info, f, indent=2, ensure_ascii=False)
            
            # 保存为文本格式
            text_info_file = image_path.with_suffix('.info')
            with open(text_info_file, 'w', encoding='utf-8') as f:
                f.write(f"# GamePlayer-Raspberry 镜像信息\n\n")
                f.write(f"镜像名称: {info['name']}\n")
                f.write(f"构建时间: {info['build_date']}\n")
                f.write(f"文件大小: {info['file_size_mb']} MB\n")
                f.write(f"SHA256: {checksum}\n\n")
                f.write(f"功能特性:\n")
                for feature in info['features']:
                    f.write(f"  ✅ {feature}\n")
                f.write(f"\n使用说明:\n")
                f.write(f"  1. {info['installation_guide']['method1']}\n")
                f.write(f"  2. 或者 {info['installation_guide']['method2']}\n")
                f.write(f"  3. {info['installation_guide']['first_boot']}\n")
                f.write(f"  4. {info['installation_guide']['web_access']}\n")
            
            # 生成校验和文件
            checksum_file = image_path.with_suffix('.sha256')
            with open(checksum_file, 'w') as f:
                f.write(f"{checksum}  {image_path.name}\n")
            
            logger.info(f"📋 镜像信息已保存: {info_file.name}")
            
        except Exception as e:
            logger.warning(f"⚠️ 生成镜像信息失败: {e}")
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """计算文件SHA256校验和"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

def main():
    """主函数"""
    try:
        builder = RaspberryImageBuilder()
        
        # 构建镜像
        image_type = sys.argv[1] if len(sys.argv) > 1 else "raspios_lite"
        result = builder.build_image(image_type)
        
        if result:
            logger.info(f"🎉 镜像构建成功: {result}")
            logger.info("📝 使用说明:")
            logger.info("  1. 使用 Raspberry Pi Imager 烧录镜像")
            logger.info("  2. 或使用命令: sudo dd if=镜像文件 of=/dev/sdX bs=4M status=progress")
            logger.info("  3. 首次启动会自动扩展文件系统")
            logger.info("  4. 访问 http://树莓派IP:8080 进入游戏界面")
            logger.info("  5. 默认用户: pi, 密码: raspberry")
            sys.exit(0)
        else:
            logger.error("❌ 镜像构建失败")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("🛑 用户中断构建过程")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 构建过程发生意外错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
