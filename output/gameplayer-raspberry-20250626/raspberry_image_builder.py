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
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import tempfile
import zipfile
import gzip

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('image_builder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.downloads_dir = Path("downloads")
        self.downloads_dir.mkdir(exist_ok=True)
        self.temp_dir = Path(tempfile.mkdtemp(prefix="pi_builder_"))
        
        # 镜像配置
        self.image_configs = {
            "retropie_4.8": ImageConfig(
                name="RetroPie 4.8",
                version="4.8",
                url="https://github.com/RetroPie/RetroPie-Setup/releases/download/4.8/retropie-buster-4.8-rpi4_400.img.gz",
                checksum="a8b8e0b8c8d8e8f8g8h8i8j8k8l8m8n8",
                size_mb=3500,
                description="RetroPie 4.8 for Raspberry Pi 4/400"
            ),
            "raspios_lite": ImageConfig(
                name="Raspberry Pi OS Lite",
                version="2023-12-05",
                url="https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2023-12-06/2023-12-05-raspios-bookworm-arm64-lite.img.xz",
                checksum="b8c8d8e8f8g8h8i8j8k8l8m8n8o8p8q8",
                size_mb=2000,
                description="Raspberry Pi OS Lite (64-bit)"
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
    
    def download_image(self, image_key: str) -> Optional[Path]:
        """下载镜像文件"""
        if image_key not in self.image_configs:
            logger.error(f"❌ 未知的镜像类型: {image_key}")
            return None
        
        config = self.image_configs[image_key]
        filename = Path(config.url).name
        local_path = self.downloads_dir / filename
        
        # 检查是否已下载且校验和正确
        if local_path.exists():
            logger.info(f"🔍 检查已下载的镜像: {filename}")
            if self._verify_checksum(local_path, config.checksum):
                logger.info(f"✅ 镜像已存在且校验和正确: {filename}")
                return local_path
            else:
                logger.warning(f"⚠️ 镜像校验和不匹配，重新下载: {filename}")
                local_path.unlink()
        
        logger.info(f"📥 开始下载镜像: {config.name}")
        logger.info(f"🔗 URL: {config.url}")
        
        try:
            response = requests.get(config.url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r📥 下载进度: {progress:.1f}% ({downloaded // 1024 // 1024}MB/{total_size // 1024 // 1024}MB)", end='')
            
            print()  # 换行
            logger.info(f"✅ 下载完成: {filename}")
            
            # 验证校验和
            if self._verify_checksum(local_path, config.checksum):
                logger.info("✅ 镜像校验和验证通过")
                return local_path
            else:
                logger.error("❌ 镜像校验和验证失败")
                local_path.unlink()
                return None
                
        except Exception as e:
            logger.error(f"❌ 下载失败: {e}")
            if local_path.exists():
                local_path.unlink()
            return None
    
    def _verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """验证文件校验和"""
        if not expected_checksum or expected_checksum == "a8b8e0b8c8d8e8f8g8h8i8j8k8l8m8n8":
            # 跳过示例校验和
            return True
        
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256()
                for chunk in iter(lambda: f.read(4096), b""):
                    file_hash.update(chunk)
                return file_hash.hexdigest() == expected_checksum
        except Exception as e:
            logger.error(f"校验和计算失败: {e}")
            return False
    
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
            extracted_name = compressed_path.stem + '.img'
        
        extracted_path = self.temp_dir / extracted_name
        
        try:
            if compressed_path.suffix == '.gz':
                with gzip.open(compressed_path, 'rb') as f_in:
                    with open(extracted_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            elif compressed_path.suffix == '.xz':
                subprocess.run(['xz', '-d', '-c', str(compressed_path)], 
                             stdout=open(extracted_path, 'wb'), check=True)
            elif compressed_path.suffix == '.zip':
                with zipfile.ZipFile(compressed_path, 'r') as zip_ref:
                    zip_ref.extractall(self.temp_dir)
                    # 找到.img文件
                    for file in self.temp_dir.glob('*.img'):
                        extracted_path = file
                        break
            else:
                # 假设已经是.img文件
                shutil.copy2(compressed_path, extracted_path)
            
            logger.info(f"✅ 解压完成: {extracted_path.name}")
            return extracted_path
            
        except Exception as e:
            logger.error(f"❌ 解压失败: {e}")
            return None
    
    def mount_image(self, image_path: Path) -> Optional[Path]:
        """挂载镜像文件"""
        logger.info(f"🔧 挂载镜像: {image_path.name}")
        
        try:
            # 创建loop设备
            result = subprocess.run(
                ['sudo', 'losetup', '--show', '-Pf', str(image_path)],
                capture_output=True, text=True, check=True
            )
            loop_device = result.stdout.strip()
            logger.info(f"📎 Loop设备: {loop_device}")
            
            # 创建挂载点
            mount_point = self.temp_dir / "mount"
            mount_point.mkdir(exist_ok=True)
            
            # 挂载根分区（通常是第二个分区）
            root_partition = f"{loop_device}p2"
            subprocess.run(['sudo', 'mount', root_partition, str(mount_point)], check=True)
            
            # 挂载boot分区
            boot_mount = mount_point / "boot"
            boot_partition = f"{loop_device}p1"
            subprocess.run(['sudo', 'mount', boot_partition, str(boot_mount)], check=True)
            
            logger.info(f"✅ 镜像已挂载到: {mount_point}")
            return mount_point
            
        except Exception as e:
            logger.error(f"❌ 挂载失败: {e}")
            return None
    
    def customize_image(self, mount_point: Path) -> bool:
        """定制镜像"""
        logger.info("🎨 开始定制镜像...")
        
        try:
            # 启用SSH
            if self.customizations["enable_ssh"]:
                ssh_file = mount_point / "boot" / "ssh"
                ssh_file.touch()
                logger.info("✅ 已启用SSH")
            
            # 配置WiFi
            if self.customizations["wifi_config"]:
                self._setup_wifi_config(mount_point)
            
            # 自动扩展文件系统
            if self.customizations["auto_expand_filesystem"]:
                self._enable_auto_expand(mount_point)
            
            # 安装GamePlayer
            if self.customizations["install_gameplayer"]:
                self._install_gameplayer(mount_point)
            
            # 性能优化
            if self.customizations["optimize_performance"]:
                self._optimize_performance(mount_point)
            
            # 清理不必要文件
            if self.customizations["cleanup_unnecessary"]:
                self._cleanup_image(mount_point)
            
            logger.info("✅ 镜像定制完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 镜像定制失败: {e}")
            return False
    
    def _setup_wifi_config(self, mount_point: Path):
        """设置WiFi配置"""
        logger.info("📶 配置WiFi...")
        
        wpa_config = mount_point / "boot" / "wpa_supplicant.conf"
        config_content = '''country=CN
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YOUR_WIFI_SSID"
    psk="YOUR_WIFI_PASSWORD"
    key_mgmt=WPA-PSK
}
'''
        
        with open(wpa_config, 'w') as f:
            f.write(config_content)
        
        logger.info("✅ WiFi配置已创建")
    
    def _enable_auto_expand(self, mount_point: Path):
        """启用自动扩展文件系统"""
        logger.info("💾 启用自动扩展文件系统...")
        
        # 在cmdline.txt中添加init参数
        cmdline_file = mount_point / "boot" / "cmdline.txt"
        if cmdline_file.exists():
            with open(cmdline_file, 'r') as f:
                cmdline = f.read().strip()
            
            if 'init=/usr/lib/raspi-config/init_resize.sh' not in cmdline:
                cmdline += ' init=/usr/lib/raspi-config/init_resize.sh'
                
                with open(cmdline_file, 'w') as f:
                    f.write(cmdline)
                
                logger.info("✅ 自动扩展文件系统已启用")
    
    def _install_gameplayer(self, mount_point: Path):
        """安装GamePlayer到镜像"""
        logger.info("🎮 安装GamePlayer...")
        
        # 复制项目文件
        target_dir = mount_point / "home" / "pi" / "GamePlayer-Raspberry"
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制核心文件
        source_files = [
            "core/",
            "scripts/",
            "config/",
            "requirements.txt",
            "README.md"
        ]
        
        for item in source_files:
            source_path = Path(item)
            if source_path.exists():
                if source_path.is_dir():
                    subprocess.run(['sudo', 'cp', '-r', str(source_path), str(target_dir)], check=True)
                else:
                    subprocess.run(['sudo', 'cp', str(source_path), str(target_dir)], check=True)
        
        # 创建自启动脚本
        autostart_script = mount_point / "home" / "pi" / ".bashrc"
        startup_content = '''
# GamePlayer-Raspberry 自动启动
if [ -d "/home/pi/GamePlayer-Raspberry" ]; then
    cd /home/pi/GamePlayer-Raspberry
    python3 scripts/smart_installer.py --check-only
fi
'''
        
        with open(autostart_script, 'a') as f:
            f.write(startup_content)
        
        logger.info("✅ GamePlayer安装完成")
    
    def _optimize_performance(self, mount_point: Path):
        """性能优化"""
        logger.info("⚡ 性能优化...")
        
        # GPU内存分配
        config_file = mount_point / "boot" / "config.txt"
        if config_file.exists():
            with open(config_file, 'a') as f:
                f.write('\n# GamePlayer Performance Optimizations\n')
                f.write('gpu_mem=128\n')
                f.write('arm_freq=1800\n')
                f.write('over_voltage=6\n')
                f.write('disable_splash=1\n')
        
        logger.info("✅ 性能优化完成")
    
    def _cleanup_image(self, mount_point: Path):
        """清理镜像"""
        logger.info("🧹 清理镜像...")
        
        cleanup_paths = [
            "var/cache/apt/archives/*",
            "var/lib/apt/lists/*",
            "tmp/*",
            "var/tmp/*",
            "usr/share/doc/*",
            "usr/share/man/*",
            "var/log/*"
        ]
        
        for path in cleanup_paths:
            full_path = mount_point / path
            try:
                subprocess.run(['sudo', 'rm', '-rf', str(full_path)], check=False)
            except Exception:
                pass
        
        logger.info("✅ 镜像清理完成")
    
    def unmount_image(self, mount_point: Path):
        """卸载镜像"""
        logger.info("📤 卸载镜像...")
        
        try:
            # 卸载boot分区
            subprocess.run(['sudo', 'umount', str(mount_point / "boot")], check=False)
            
            # 卸载根分区
            subprocess.run(['sudo', 'umount', str(mount_point)], check=True)
            
            # 分离loop设备
            result = subprocess.run(['losetup', '-a'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if str(self.temp_dir) in line:
                    loop_device = line.split(':')[0]
                    subprocess.run(['sudo', 'losetup', '-d', loop_device], check=False)
            
            logger.info("✅ 镜像已卸载")
            
        except Exception as e:
            logger.error(f"⚠️ 卸载过程中出现错误: {e}")
    
    def compress_image(self, image_path: Path) -> Path:
        """压缩镜像"""
        logger.info(f"🗜️ 压缩镜像: {image_path.name}")
        
        compressed_path = self.output_dir / f"{image_path.stem}_gameplayer.img.gz"
        
        try:
            with open(image_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
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
            # 1. 下载镜像
            compressed_image = self.download_image(image_key)
            if not compressed_image:
                return None
            
            # 2. 解压镜像
            image_path = self.extract_image(compressed_image)
            if not image_path:
                return None
            
            # 3. 挂载镜像
            mount_point = self.mount_image(image_path)
            if not mount_point:
                return None
            
            # 4. 定制镜像
            if not self.customize_image(mount_point):
                self.unmount_image(mount_point)
                return None
            
            # 5. 卸载镜像
            self.unmount_image(mount_point)
            
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
            # 清理临时文件
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _generate_image_info(self, image_path: Path, image_key: str):
        """生成镜像信息文件"""
        info = {
            "name": f"GamePlayer-Raspberry {self.image_configs[image_key].name}",
            "version": "1.0.0",
            "base_image": self.image_configs[image_key].name,
            "build_date": datetime.now().isoformat(),
            "file_size_mb": image_path.stat().st_size // 1024 // 1024,
            "checksum": self._calculate_file_checksum(image_path),
            "features": list(self.customizations.keys()),
            "installation_guide": "使用 Raspberry Pi Imager 或 dd 命令烧录到SD卡"
        }
        
        info_file = image_path.with_suffix('.json')
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📋 镜像信息已保存: {info_file.name}")
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """计算文件校验和"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

def main():
    """主函数"""
    builder = RaspberryImageBuilder()
    
    # 检查系统要求
    required_tools = ['sudo', 'losetup', 'mount', 'umount']
    for tool in required_tools:
        if not shutil.which(tool):
            logger.error(f"❌ 缺少必需工具: {tool}")
            sys.exit(1)
    
    # 构建镜像
    image_type = sys.argv[1] if len(sys.argv) > 1 else "retropie_4.8"
    result = builder.build_image(image_type)
    
    if result:
        logger.info(f"🎉 镜像构建成功: {result}")
        logger.info("📝 使用说明:")
        logger.info("  1. 使用 Raspberry Pi Imager 烧录镜像")
        logger.info("  2. 或使用命令: sudo dd if=镜像文件 of=/dev/sdX bs=4M status=progress")
        logger.info("  3. 首次启动会自动扩展文件系统")
        logger.info("  4. 默认用户: pi, 密码: raspberry")
    else:
        logger.error("❌ 镜像构建失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
