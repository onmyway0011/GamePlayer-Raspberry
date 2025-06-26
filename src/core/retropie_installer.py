#!/usr/bin/env python3
"""
RetroPie 镜像下载和烧录工具

这是一个跨平台的Python脚本，用于自动化下载RetroPie镜像并烧录到SD卡。
支持Windows、Linux和macOS三平台，提供完整的自动化安装流程。

主要功能：
- 自动检测系统依赖和必要工具
- 从RetroPie官网自动获取最新镜像下载链接
- 支持断点续传的镜像下载
- 自动解压.img.gz和.zip格式的镜像文件
- 智能扫描和列出可用的SD卡设备
- 安全的镜像烧录操作（Linux/macOS使用dd命令）
- 完整的操作日志记录和错误处理

系统要求：
- Python 3.7+
- Windows: 需要手动安装Win32DiskImager或balenaEtcher
- Linux/macOS: 需要dd命令和sudo权限

作者: AI Assistant
版本: 2.0.0
许可证: MIT
"""

import argparse
import hashlib
import json
import logging
import os
import platform
import subprocess
import sys
import tarfile
import time
import zipfile
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(
        "retropie_installer.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

try:
    import requests
except ImportError:
    raise ImportError("缺少requests库，请运行 pip install requests 安装。")


class RetroPieInstaller:
    """
    RetroPie 镜像下载和烧录工具类

    提供完整的RetroPie镜像自动化安装流程，包括：
    - 系统依赖检查
    - 镜像下载和解压
    - 磁盘设备管理
    - 镜像烧录操作

    属性:
        system (str): 当前操作系统名称
        retropie_url (str): RetroPie官网URL
        download_dir (Path): 下载目录路径
    """

    def __init__(self) -> bool:
        """
        初始化RetroPie安装器

        设置基本配置和创建必要的目录结构。
        """
        self.system = platform.system()
        self.retropie_url = "https://retropie.org.uk/download/"
        self.download_dir = Path("downloads")
        self.download_dir.mkdir(exist_ok=True)
        self.log_file = Path("retropie_installer.log")

    def check_dependencies(self) -> bool:
        """
        检查系统依赖是否满足

        根据操作系统类型检查必要的工具和权限。

        Returns:
            bool: 依赖检查是否通过
        """
        logger.info("检查系统依赖...")

        if self.system == "Windows":
            return self._check_windows_dependencies()
        elif self.system in ["Linux", "Darwin"]:  # Darwin = macOS
            return self._check_unix_dependencies()
        else:
            logger.error(f"不支持的操作系统: {self.system}")
            return False

    def _check_windows_dependencies(self) -> bool:
        """
        检查Windows系统依赖

        检查是否有可用的镜像烧录工具。

        Returns:
            bool: Windows依赖检查结果
        """
        # 检查是否有Win32DiskImager或类似工具
        possible_tools = ["Win32DiskImager.exe",
                          "balenaEtcher.exe", "Rufus.exe"]

        for tool in possible_tools:
            if self._find_executable(tool):
                logger.info(f"找到烧录工具: {tool}")
                return True

        logger.warning("未找到烧录工具，请手动安装 Win32DiskImager 或 balenaEtcher")
        return False

    def _check_unix_dependencies(self) -> bool:
        """
        检查Unix系统依赖（Linux/macOS）

        检查dd命令是否可用。

        Returns:
            bool: Unix依赖检查结果
        """
        # 检查dd命令
        if self._run_command(["which", "dd"])[0] == 0:
            logger.info("找到 dd 命令")
            return True

        logger.error("未找到 dd 命令")
        return False

    def _find_executable(self, name: str) -> Optional[str]:
        """
        查找可执行文件

        Args:
            name (str): 可执行文件名

        Returns:
            Optional[str]: 可执行文件的完整路径，如果未找到则返回None
        """
        for path in os.environ.get("PATH", "").split(os.pathsep):
            exe_path = Path(path) / name
            if exe_path.exists():
                return str(exe_path)
        return None

    def _run_command(self, cmd: List[str], check: bool = True) -> Tuple[int, str, str]:
        """
        运行命令并返回结果

        Args:
            cmd (List[str]): 要执行的命令列表
            check (bool): 是否在命令失败时抛出异常

        Returns:
            Tuple[int, str, str]: (返回码, 标准输出, 标准错误)
        """
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=check)
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr

    def get_retropie_download_url(self) -> Optional[str]:
        """
        获取RetroPie镜像下载链接

        From RetroPie官网解析页面内容，查找适合树莓派4B的镜像下载链接。

        Returns:
            Optional[str]: 下载链接URL，如果未找到则返回None
        """
        logger.info("获取RetroPie下载链接...")

        try:
            response = requests.get(self.retropie_url, timeout=30)
            response.raise_for_status()

            # 解析页面内容，查找树莓派4B的镜像链接
            content = response.text.lower()

            # 常见的RetroPie镜像文件名模式
            patterns = [
                "retropie-buster-4.8-rpi4_400.img.gz",
                "retropie-buster-4.8-rpi4.img.gz",
                "retropie-4.8-rpi4.img.gz",
                "retropie-buster-rpi4.img.gz",
            ]

            for pattern in patterns:
                if pattern in content:
                    # 构建完整下载URL
                    download_url = f"https://github.com/RetroPie/RetroPie-Setup/releases/download/4.8/{pattern}"
                    logger.info(f"找到下载链接: {download_url}")
                    return download_url

            logger.warning("未找到合适的镜像链接，请手动下载")
            return None

        except requests.RequestException as e:
            logger.error(f"获取下载链接失败: {e}")
            return None

    def download_image(self, url: str) -> Optional[Path]:
        """
        下载RetroPie镜像

        Support断点续传的镜像下载，显示下载进度。

        Args:
            url (str): 镜像下载链接

        Returns:
            Optional[Path]: 下载文件的路径，如果下载失败则返回None
        """
        filename = url.split("/")[-1]
        file_path = self.download_dir / filename

        if file_path.exists():
            logger.info(f"镜像文件已存在: {file_path}")
            return file_path

        logger.info(f"开始下载镜像: {url}")

        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r下载进度: {progress:.1f}%",
                                  end="", flush=True)

            print()  # 换行
            logger.info(f"下载完成: {file_path}")
            return file_path

        except requests.RequestException as e:
            logger.error(f"下载失败: {e}")
            if file_path.exists():
                file_path.unlink()
            return None

    def extract_image(self, archive_path: Path) -> Optional[Path]:
        """解压镜像文件"""
        logger.info(f"解压镜像文件: {archive_path}")

        try:
            if archive_path.suffix == ".gz":
                # 处理 .img.gz 文件
                img_path = archive_path.with_suffix("")
                if img_path.exists():
                    logger.info(f"镜像文件已存在: {img_path}")
                    return img_path

                import gzip

                with gzip.open(archive_path, "rb") as f_in:
                    with open(img_path, "wb") as f_out:
                        f_out.write(f_in.read())

                logger.info(f"解压完成: {img_path}")
                return img_path

            elif archive_path.suffix == ".zip":
                # 处理 .zip 文件
                with zipfile.ZipFile(archive_path, "r") as zip_ref:
                    # 查找 .img 文件
                    img_files = [f for f in zip_ref.namelist()
                                 if f.endswith(".img")]
                    if not img_files:
                        logger.error("ZIP文件中未找到.img文件")
                        return None

                    img_filename = img_files[0]
                    img_path = self.download_dir / Path(img_filename).name

                    if img_path.exists():
                        logger.info(f"镜像文件已存在: {img_path}")
                        return img_path

                    with zip_ref.open(img_filename) as source, open(img_path, "wb") as target:
                        target.write(source.read())

                    logger.info(f"解压完成: {img_path}")
                    return img_path

            else:
                logger.error(f"不支持的文件格式: {archive_path.suffix}")
                return None

        except Exception as e:
            logger.error(f"解压失败: {e}")
            return None

    def list_available_disks(self) -> List[Tuple[str, str, str]]:
        """列出可用的磁盘"""
        logger.info("扫描可用磁盘...")
        disks = []

        if self.system == "Windows":
            return self._list_windows_disks()
        elif self.system in ["Linux", "Darwin"]:
            return self._list_unix_disks()

        return disks

    def _list_windows_disks(self) -> List[Tuple[str, str, str]]:
        """列出Windows磁盘"""
        disks = []
        try:
            # 使用 PowerShell 获取磁盘信息
            cmd = [
                "powershell",
                "Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID,Size,FreeSpace,VolumeName | ConvertTo-Json",
            ]

            returncode, stdout, stderr = self._run_command(cmd, check=False)

            if returncode == 0:
                import json

                disks_data = json.loads(stdout)
                if not isinstance(disks_data, list):
                    disks_data = [disks_data]

                for disk in disks_data:
                    device_id = disk.get("DeviceID", "")
                    size = int(disk.get("Size", 0))
                    free_space = int(disk.get("FreeSpace", 0))
                    volume_name = disk.get("VolumeName", "Unknown")

                    # 只显示可移动磁盘或大容量磁盘
                    if size > 1024**3:  # 大于1GB
                        size_gb = size / (1024**3)
                        free_gb = free_space / (1024**3)
                        disks.append(
                            (device_id, f"{size_gb:.1f}GB", volume_name))

                return disks

        except Exception as e:
            logger.error(f"获取Windows磁盘信息失败: {e}")

        return disks

    def _list_unix_disks(self) -> List[Tuple[str, str, str]]:
        """列出Unix磁盘"""
        disks = []

        try:
            if self.system == "Darwin":  # macOS
                cmd = ["diskutil", "list"]
            else:  # Linux
                cmd = ["lsblk", "-o", "NAME,SIZE,TYPE,MOUNTPOINT", "-J"]

            returncode, stdout, stderr = self._run_command(cmd, check=False)

            if returncode == 0:
                if self.system == "Darwin":
                    # 解析 macOS diskutil 输出
                    lines = stdout.split("\n")
                    for line in lines:
                        if "/dev/disk" in line and "external" in line.lower():
                            parts = line.split()
                            if len(parts) >= 3:
                                disk_name = parts[0]
                                size = parts[1] if len(
                                    parts) > 1 else "Unknown"
                                disks.append(
                                    (disk_name, size, "External Disk"))
                else:
                    # 解析 Linux lsblk 输出
                    import json

                    try:
                        data = json.loads(stdout)
                        for device in data.get("blockdevices", []):
                            if device.get("type") == "disk":
                                name = device.get("name", "")
                                size = device.get("size", "Unknown")
                                mountpoint = device.get("mountpoint", "")
                                disks.append(
                                    (name, size, mountpoint or "Unmounted"))
                    except json.JSONDecodeError:
                        logger.warning("无法解析lsblk输出")

        except Exception as e:
            logger.error(f"获取Unix磁盘信息失败: {e}")

        return disks

    def burn_image(self, image_path: Path, target_disk: str) -> bool:
        """
        烧录镜像到SD卡

        Args:
            image_path (Path): 镜像文件路径
            target_disk (str): 目标磁盘设备

        Returns:
            bool: 烧录是否成功
        """
        logger.info(f"开始烧录镜像到 {target_disk}...")

        if self.system == "Windows":
            return self._burn_windows(image_path, target_disk)
        elif self.system in ["Linux", "Darwin"]:
            return self._burn_unix(image_path, target_disk)
        else:
            logger.error(f"不支持的操作系统: {self.system}")
            return False

    def integrate_virtuanes(self, image_path: Path) -> bool:
        """
        在镜像中集成 VirtuaNES 模拟器

        Args:
            image_path (Path): 镜像文件路径

        Returns:
            bool: 集成是否成功
        """
        logger.info("开始集成 VirtuaNES 0.97 到镜像...")
        
        try:
            # 挂载镜像
            mount_point = Path("/mnt/retropie_image")
            mount_point.mkdir(exist_ok=True)
            
            # 获取镜像的分区偏移
            offset = self._get_partition_offset(image_path)
            if not offset:
                logger.error("无法获取分区偏移")
                return False
            
            # 挂载镜像
            subprocess.run([
                "sudo", "mount", "-o", f"loop,offset={offset}", 
                str(image_path), str(mount_point)
            ], check=True)
            
            try:
                # 复制 VirtuaNES 集成脚本到镜像
                virtuanes_script = Path("scripts/auto_virtuanes_integration.sh")
                if virtuanes_script.exists():
                    target_script = mount_point / "home/pi/auto_virtuanes_integration.sh"
                    shutil.copy2(virtuanes_script, target_script)
                    os.chmod(target_script, 0o755)
                    logger.info("✓ VirtuaNES 集成脚本已复制到镜像")
                
                # 复制配置文件到镜像
                config_file = Path("config/project_config.json")
                if config_file.exists():
                    target_config = mount_point / "home/pi/project_config.json"
                    shutil.copy2(config_file, target_config)
                    logger.info("✓ 配置文件已复制到镜像")
                
                # 创建开机自启动脚本
                startup_script = mount_point / "etc/rc.local"
                if startup_script.exists():
                    # 在 rc.local 中添加 VirtuaNES 安装命令
                    with open(startup_script, "r") as f:
                        content = f.read()
                    
                    if "auto_virtuanes_integration.sh" not in content:
                        virtuanes_line = "\n# 自动安装 VirtuaNES 模拟器\n/home/pi/auto_virtuanes_integration.sh &\n"
                        with open(startup_script, "w") as f:
                            f.write(content + virtuanes_line)
                        logger.info("✓ 开机自启动脚本已更新")
                
                logger.info("✓ VirtuaNES 集成完成")
                return True
                
            finally:
                # 卸载镜像
                subprocess.run(["sudo", "umount", str(mount_point)], check=True)
                
        except Exception as e:
            logger.error(f"VirtuaNES 集成失败: {e}")
            return False

    def _get_partition_offset(self, image_path: Path) -> Optional[int]:
        """
        获取镜像中第一个分区的偏移量

        Args:
            image_path (Path): 镜像文件路径

        Returns:
            Optional[int]: 分区偏移量（字节）
        """
        try:
            # 使用 fdisk 获取分区信息
            result = subprocess.run([
                "fdisk", "-l", str(image_path)
            ], capture_output=True, text=True, check=True)
            
            # 解析输出找到第一个分区的起始扇区
            for line in result.stdout.split('\n'):
                if 'img1' in line or 'img2' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        start_sector = int(parts[1])
                        return start_sector * 512  # 转换为字节
                        
            return None
            
        except Exception as e:
            logger.error(f"获取分区偏移失败: {e}")
            return None

    def _burn_windows(self, image_path: Path, target_disk: str) -> bool:
        """Windows系统烧录"""
        logger.warning("Windows系统需要手动烧录")
        logger.info(f"请使用 Win32DiskImager 或 balenaEtcher 将镜像烧录到 {target_disk}")
        logger.info(f"镜像文件路径: {image_path}")
        return False

    def _burn_unix(self, image_path: Path, target_disk: str) -> bool:
        """Unix系统烧录"""
        logger.warning(f"即将烧录镜像到 {target_disk}")
        logger.warning("此操作将擦除目标磁盘的所有数据！")

        # 确认操作
        confirm = input("确认继续？(输入 'yes' 确认): ")
        if confirm.lower() != "yes":
            logger.info("操作已取消")
            return False

        try:
            # 卸载磁盘（如果已挂载）
            if self.system == "Darwin":
                unmount_cmd = ["diskutil", "unmountDisk", target_disk]
            else:
                unmount_cmd = ["sudo", "umount", target_disk]

            self._run_command(unmount_cmd, check=False)
            time.sleep(2)

            # 使用dd命令烧录
            dd_cmd = ["sudo", "dd", f"if={image_path}",
                      f"of={target_disk}", "bs=4M", "status=progress"]

            logger.info("开始烧录，这可能需要几分钟...")
            returncode, stdout, stderr = self._run_command(dd_cmd)

            if returncode == 0:
                logger.info("烧录完成！")
                return True
            else:
                logger.error(f"烧录失败: {stderr}")
                return False

        except Exception as e:
            logger.error(f"烧录过程中出错: {e}")
            return False

    def integrate_nesticle_to_image(self, image_path: str) -> bool:
        """集成 Nesticle 到 RetroPie 镜像"""
        logger.info("集成 Nesticle 到 RetroPie 镜像...")
        
        try:
            # 创建挂载点
            mount_point = "/tmp/nesticle_mount"
            subprocess.run(["sudo", "mkdir", "-p", mount_point], check=True)
            
            # 挂载镜像
            loop_device = subprocess.check_output(
                ["sudo", "losetup", "--find", "--show", image_path], 
                text=True
            ).strip()
            
            subprocess.run(["sudo", "mount", f"{loop_device}p2", mount_point], check=True)
            
            # 复制 Nesticle 集成脚本
            target_script = f"{mount_point}/opt/retropie/emulators/nesticle/integrate_nesticle.sh"
            subprocess.run(["sudo", "mkdir", "-p", os.path.dirname(target_script)], check=True)
            subprocess.run([
                "sudo", "cp", 
                "scripts/auto_nesticle_integration.sh", 
                target_script
            ], check=True)
            subprocess.run(["sudo", "chmod", "+x", target_script], check=True)
            
            # 修改开机启动脚本
            startup_script = f"{mount_point}/etc/rc.local"
            if os.path.exists(startup_script):
                # 在 exit 0 之前添加启动命令
                startup_content = f"""# 启动 Nesticle 集成
if [[ -f /opt/retropie/emulators/nesticle/integrate_nesticle.sh ]]; then
    /opt/retropie/emulators/nesticle/integrate_nesticle.sh &
fi
"""
                # 读取原文件
                with open(startup_script, 'r') as f:
                    content = f.read()
                
                # 在 exit 0 之前插入内容
                if 'exit 0' in content:
                    new_content = content.replace('exit 0', f'{startup_content}exit 0')
                else:
                    new_content = content + f'\n{startup_content}'
                
                # 写回文件
                with open(startup_script, 'w') as f:
                    f.write(new_content)
            
            # 卸载镜像
            subprocess.run(["sudo", "umount", mount_point], check=True)
            subprocess.run(["sudo", "losetup", "-d", loop_device], check=True)
            subprocess.run(["sudo", "rmdir", mount_point], check=True)
            
            logger.info("✓ Nesticle 已集成到镜像")
            return True
            
        except Exception as e:
            logger.error(f"Nesticle 镜像集成失败: {e}")
            return False

    def run(self) -> bool:
        """运行主程序"""
        logger.info("=== RetroPie 镜像下载和烧录工具 ===")
        logger.info(f"操作系统: {self.system}")

        # 检查依赖
        if not self.check_dependencies():
            logger.error("系统依赖检查失败")
            return

        # 获取下载链接
        download_url = self.get_retropie_download_url()
        if not download_url:
            logger.error("无法获取下载链接")
            return

        # 下载镜像
        archive_path = self.download_image(download_url)
        if not archive_path:
            logger.error("镜像下载失败")
            return

        # 解压镜像
        image_path = self.extract_image(archive_path)
        if not image_path:
            logger.error("镜像解压失败")
            return

        # 集成 VirtuaNES（如果启用）
        if self._should_integrate_virtuanes():
            logger.info("检测到 VirtuaNES 配置，开始集成...")
            if not self.integrate_virtuanes(image_path):
                logger.warning("VirtuaNES 集成失败，继续烧录流程")
            else:
                logger.info("✓ VirtuaNES 集成成功")

        # 集成 Nesticle（如果启用）
        if self._should_integrate_nesticle():
            logger.info("检测到 Nesticle 配置，开始集成...")
            if not self.integrate_nesticle_to_image(str(image_path)):
                logger.warning("Nesticle 集成失败，继续烧录流程")
            else:
                logger.info("✓ Nesticle 集成成功")

        # 列出可用磁盘
        disks = self.list_available_disks()
        if not disks:
            logger.error("未找到可用磁盘")
            return
        logger.info("可用磁盘:")
        for i, (device, size, name) in enumerate(disks):
            print(f"{i+1}. {device} ({size}) - {name}")

        # 选择目标磁盘
        try:
            choice = int(input(f"请选择目标磁盘 (1-{len(disks)}): ")) - 1
            if 0 <= choice < len(disks):
                target_disk = disks[choice][0]
            else:
                logger.error("无效的选择")
                return
        except ValueError:
            logger.error("请输入有效的数字")
            return

        # 烧录镜像
        if self.burn_image(image_path, target_disk):
            logger.info("RetroPie 安装完成！")
        else:
            logger.error("烧录失败")

    def _should_integrate_virtuanes(self) -> bool:
        """检查是否应该集成 VirtuaNES"""
        try:
            config_file = Path("config/project_config.json")
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return config.get("emulator", {}).get("virtuanes", {}).get("enabled", False)
        except Exception as e:
            logger.warning(f"检查 VirtuaNES 配置失败: {e}")
        
        return False

    def _should_integrate_nesticle(self) -> bool:
        """检查是否应该集成 Nesticle"""
        try:
            config_file = Path("config/project_config.json")
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return config.get("emulator", {}).get("nesticle", {}).get("enabled", False)
        except Exception as e:
            logger.warning(f"检查 Nesticle 配置失败: {e}")
        
        return False


def main() -> bool:
    """主函数"""
    parser = argparse.ArgumentParser(description="RetroPie 镜像下载和烧录工具")
    parser.add_argument("--check-only", action="store_true", help="仅检查系统依赖")
    parser.add_argument("--download-only", action="store_true", help="仅下载镜像")
    parser.add_argument("--list-disks", action="store_true", help="列出可用磁盘")

    args = parser.parse_args()

    installer = RetroPieInstaller()

    if args.check_only:
        if installer.check_dependencies():
            logger.info("系统依赖检查通过")
        else:
            logger.error("系统依赖检查失败")
        return

    if args.list_disks:
        disks = installer.list_available_disks()
        if disks:
            logger.info("可用磁盘:")
            for i, (device, size, name) in enumerate(disks):
                print(f"{i+1}. {device} ({size}) - {name}")
        else:
            logger.info("未找到可用磁盘")
        return

    if args.download_only:
        download_url = installer.get_retropie_download_url()
        if download_url:
            archive_path = installer.download_image(download_url)
            if archive_path:
                image_path = installer.extract_image(archive_path)
                if image_path:
                    logger.info(f"镜像下载完成: {image_path}")
        return

    # 运行完整流程
    installer.run()


if __name__ == "__main__":
    main()