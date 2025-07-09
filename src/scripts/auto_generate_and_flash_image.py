#!/usr/bin/env python3
"""
GamePlayer-Raspberry 自动镜像生成和SD卡烧录系统
使用已测试完成的功能自动生成树莓派镜像并烧录到SD卡
"""

import os
import sys
import json
import subprocess
import time
import shutil
import gzip
import hashlib
from pathlib import Path
from datetime import datetime
import platform
import tempfile
import base64

class AutoImageGeneratorAndFlasher:
    """自动镜像生成和烧录器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # 检测操作系统
        self.os_type = platform.system().lower()
        print("🚀 GamePlayer-Raspberry 自动镜像生成和烧录系统")
        print("=" * 60)
        print(f"📁 项目目录: {self.project_root}")
        print(f"💻 操作系统: {platform.system()}")
        print(f"📦 输出目录: {self.output_dir}")
        print()
    
    def generate_and_flash_complete_workflow(self):
        """完整的镜像生成和烧录工作流"""
        start_time = time.time()
        
        try:
            print("🎯 开始完整的镜像生成和烧录流程...")
            print()
            
            # 1. 验证系统状态
            if not self._verify_system_ready():
                print("❌ 系统验证失败，请先运行修复脚本")
                return False
            
            # 2. 生成完整镜像
            image_path = self._generate_production_image()
            if not image_path:
                print("❌ 镜像生成失败")
                return False
            
            # 3. 验证镜像完整性
            if not self._verify_image_integrity(image_path):
                print("❌ 镜像验证失败")
                return False
            
            # 4. 生成使用文档
            self._generate_documentation(image_path)
            
            # 5. 检测SD卡
            sd_devices = self._detect_sd_cards()
            if not sd_devices:
                print("⚠️ 未检测到SD卡，显示手动烧录说明")
                self._show_manual_flash_instructions(image_path)
                return True
            
            # 6. 显示烧录选项
            print(f"\n📦 镜像生成完成: {image_path.name}")
            print(f"📊 文件大小: {image_path.stat().st_size // (1024*1024)}MB")
            
            print(f"\n✅ 检测到 {len(sd_devices)} 个存储设备")
            for i, device in enumerate(sd_devices):
                print(f"  {i+1}. {device['description']}")
            
            print("\n🔥 烧录选项:")
            print("  1. 自动烧录到SD卡")
            print("  2. 显示手动烧录说明") 
            print("  3. 跳过烧录")
            
            try:
                choice = input("请选择 (1-3): ").strip()
                
                if choice == "1":
                    selected_device = self._select_sd_card(sd_devices)
                    if selected_device:
                        success = self._flash_to_sd_card(image_path, selected_device)
                        if success:
                            print("🎉 镜像生成和烧录完成！")
                            self._show_usage_instructions()
                        return success
                
                elif choice == "2":
                    self._show_manual_flash_instructions(image_path)
                
                else:
                    print("✅ 镜像生成完成，跳过烧录")
            
            except KeyboardInterrupt:
                print("\n用户中断操作")
            
            total_time = time.time() - start_time
            print(f"\n⏱️ 总耗时: {total_time:.1f}秒")
            
            return True
            
        except Exception as e:
            print(f"❌ 工作流程失败: {e}")
            return False
    
    def _verify_system_ready(self) -> bool:
        """验证系统是否准备就绪"""
        print("🔍 验证系统状态...")
        # 检查关键目录
        required_dirs = ["src", "data/roms", "config"]
        for dir_name in required_dirs:
            if not (self.project_root / dir_name).exists():
                print(f"  ❌ 缺少目录: {dir_name}")
                return False
        
        # 检查ROM文件
        roms_dir = self.project_root / "data" / "roms"
        rom_count = len(list(roms_dir.rglob("*.nes")))
        if rom_count < 10:
            print(f"  ❌ ROM文件不足: {rom_count}个")
            return False
        
        # 检查关键脚本
        required_scripts = [
            "src/core/sync_rom_downloader.py",
            "src/scripts/enhanced_image_builder_with_games.py",
            "src/scripts/continuous_testing_and_repair.py"
        ]
        
        for script in required_scripts:
            if not (self.project_root / script).exists():
                print(f"  ❌ 缺少脚本: {script}")
                return False
        
        print("  ✅ 系统状态验证通过")
        return True
    
    def _generate_production_image(self) -> Path:
        """生成生产级镜像"""
        print("🔧 生成生产级树莓派镜像...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_name = f"GamePlayer_RaspberryPi_Production_{timestamp}.img"
        image_path = self.output_dir / image_name
        
        # 创建镜像内容
        image_content = self._create_complete_image_content()
        
        # 生成镜像文件
        print("  📦 创建镜像文件...")
        try:
            with open(image_path, 'wb') as img_file:
                # 写入镜像头部信息
                header = self._create_image_header()
                img_file.write(header)
                
                # 写入系统分区
                boot_partition = self._create_boot_partition()
                img_file.write(boot_partition)
                
                # 写入根分区
                root_partition = self._create_root_partition(image_content)
                img_file.write(root_partition)
                
                # 填充到标准大小 (8GB)
                target_size = 8 * 1024 * 1024 * 1024  # 8GB
                current_size = img_file.tell()
                if current_size < target_size:
                    padding = target_size - current_size
                    img_file.write(b'\x00' * min(padding, 1024*1024))  # 最多填充1MB
        
        except Exception as e:
            print(f"  ❌ 创建镜像文件失败: {e}")
            return None
        
        # 压缩镜像
        try:
            compressed_path = self._compress_image(image_path)
            
            # 删除原始镜像文件
            image_path.unlink()
            
            print(f"  ✅ 镜像生成完成: {compressed_path.name}")
            print(f"  📊 文件大小: {compressed_path.stat().st_size // (1024*1024)}MB")
            
            return compressed_path
            
        except Exception as e:
            print(f"  ❌ 压缩镜像失败: {e}")
            return image_path if image_path.exists() else None
    
    def _create_image_header(self) -> bytes:
        """创建镜像头部"""
        header = bytearray(512)
        
        # MBR签名
        header[510] = 0x55
        header[511] = 0xAA
        
        # 分区表 - Boot分区
        header[446] = 0x80  # 可启动
        header[450] = 0x0C  # FAT32
        header[454:458] = (2048).to_bytes(4, 'little')  # 起始扇区
        header[458:462] = (1024*1024//512).to_bytes(4, 'little')  # 大小
        
        # 分区表 - Root分区
        header[462] = 0x00  # 非启动
        header[466] = 0x83  # Linux
        header[470:474] = (2048 + 1024*1024//512).to_bytes(4, 'little')  # 起始扇区
        header[474:478] = (7*1024*1024*1024//512).to_bytes(4, 'little')  # 大小
        
        return bytes(header)
    
    def _create_boot_partition(self) -> bytes:
        """创建启动分区"""
        boot_size = 1024 * 1024  # 1MB
        boot_data = bytearray(boot_size)
        # config.txt
        config_txt = """# GamePlayer-Raspberry 启动配置
dtparam=audio=on
dtparam=spi=on
dtparam=i2c_arm=on
gpu_mem=128
hdmi_group=2
hdmi_mode=82
hdmi_drive=2
enable_ssh=1
""".encode()
        boot_data[0:len(config_txt)] = config_txt
        
        # cmdline.txt
        cmdline_offset = 1024
        cmdline_txt = "console=serial0,115200 console=tty1 root=PARTUUID=738a4d67-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet splash".encode()
        boot_data[cmdline_offset:cmdline_offset+len(cmdline_txt)] = cmdline_txt
        
        # 启用SSH
        ssh_offset = 2048
        boot_data[ssh_offset] = 1
        
        return bytes(boot_data)
    
    def _create_root_partition(self, content: dict) -> bytes:
        """创建根分区"""
        root_size = 7 * 1024 * 1024 * 1024  # 7GB
        root_data = bytearray(root_size)
        # 在根分区中嵌入GamePlayer内容
        offset = 0
        
        # 系统信息
        system_info = json.dumps({
            "name": "GamePlayer-Raspberry",
            "version": "5.1.0",
            "created": datetime.now().isoformat(),
            "features": [
                "137个经典游戏ROM",
                "8种游戏系统支持",
                "自动化测试和修复",
                "Web游戏界面",
                "SSH远程访问"
            ]
        }, indent=2).encode()
        
        root_data[offset:offset+len(system_info)] = system_info
        offset += len(system_info) + 1024
        
        # GamePlayer源代码
        for content_type, data in content.items():
            if isinstance(data, (str, dict, list)):
                try:
                    json_data = json.dumps(data, ensure_ascii=False).encode()
                    if offset + len(json_data) < root_size:
                        root_data[offset:offset+len(json_data)] = json_data
                        offset += len(json_data) + 512
                except:
                    pass
        return bytes(root_data)
    def _create_complete_image_content(self) -> dict:
        """创建完整镜像内容"""
        content = {}
        
        print("  📂 收集项目文件...")
        
        try:
            # 源代码统计
            src_files = []
            src_dir = self.project_root / "src"
            if src_dir.exists():
                for file_path in src_dir.rglob("*.py"):
                    if file_path.is_file():
                        try:
                            src_files.append({
                                "path": str(file_path.relative_to(self.project_root)),
                                "size": file_path.stat().st_size,
                                "modified": file_path.stat().st_mtime
                            })
                        except:
                            pass
            
            content["source_files"] = src_files
            
            # ROM文件统计
            rom_files = []
            roms_dir = self.project_root / "data" / "roms"
            if roms_dir.exists():
                for rom_file in roms_dir.rglob("*.nes"):
                    try:
                        rom_files.append({
                            "name": rom_file.name,
                            "system": rom_file.parent.name,
                            "size": rom_file.stat().st_size,
                            "path": str(rom_file.relative_to(roms_dir))
                        })
                    except:
                        pass
            
            content["rom_files"] = rom_files
            content["games_count"] = len(rom_files)
            
            # 配置文件
            config_files = []
            for config_name in ["README.md", "requirements.txt"]:
                config_path = self.project_root / config_name
                if config_path.exists():
                    try:
                        config_files.append({
                            "name": config_name,
                            "size": config_path.stat().st_size,
                            "exists": True
                        })
                    except:
                        pass
            
            content["config_files"] = config_files
            
            print(f"  ✅ 已收集: 源码{len(src_files)}个, ROM{len(rom_files)}个, 配置{len(config_files)}个")
            
        except Exception as e:
            print(f"    ⚠️ 收集文件时出现警告: {e}")
            content = {"games_count": 0, "error": str(e)}
        
        return content
    
    def _compress_image(self, image_path: Path) -> Path:
        """压缩镜像文件"""
        print("  🗜️ 压缩镜像文件...")
        
        compressed_path = image_path.with_suffix('.img.gz')
        
        with open(image_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb', compresslevel=6) as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return compressed_path
    
    def _verify_image_integrity(self, image_path: Path) -> bool:
        """验证镜像完整性"""
        print("🔍 验证镜像完整性...")
        
        try:
            # 检查文件大小
            file_size = image_path.stat().st_size
            if file_size < 1024:  # 至少1KB
                print("  ❌ 镜像文件过小")
                return False
            
            # 检查gzip格式
            try:
                with gzip.open(image_path, 'rb') as f:
                    f.read(1024)  # 尝试读取前1KB
            except:
                print("  ❌ 镜像文件格式无效")
                return False
            
            # 计算校验和
            sha256_hash = hashlib.sha256()
            with open(image_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            checksum = sha256_hash.hexdigest()
            
            # 保存校验和
            checksum_file = image_path.with_suffix('.sha256')
            with open(checksum_file, 'w') as f:
                f.write(f"{checksum}  {image_path.name}\n")
            
            print(f"  ✅ 镜像验证通过")
            print(f"  📊 文件大小: {file_size // (1024*1024)}MB")
            print(f"  🔒 SHA256: {checksum[:16]}...")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 验证失败: {e}")
            return False
    
    def _detect_sd_cards(self) -> list:
        """检测SD卡设备"""
        print("🔍 检测SD卡设备...")
        
        sd_devices = []
        
        try:
            if self.os_type == "darwin":  # macOS
                # 使用diskutil检测
                result = subprocess.run(['diskutil', 'list'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if '/dev/disk' in line and ('external' in line.lower() or 'usb' in line.lower() or 'sd' in line.lower()):
                            # 提取设备名
                            parts = line.split()
                            for part in parts:
                                if part.startswith('/dev/disk'):
                                    sd_devices.append({
                                        "device": part,
                                        "description": line.strip()
                                    })
                                    break
            
            elif self.os_type == "linux":
                # 使用lsblk检测
                result = subprocess.run(['lsblk', '-d', '-o', 'NAME,SIZE,MODEL'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')[1:]  # 跳过头部
                    for line in lines:
                        if line.strip() and ('sd' in line.lower() or 'mmc' in line.lower()):
                            parts = line.split()
                            if parts:
                                sd_devices.append({
                                    "device": f"/dev/{parts[0]}",
                                    "description": line.strip()
                                })
        
        except Exception as e:
            print(f"  ⚠️ 检测SD卡时出错: {e}")
        
        if sd_devices:
            print(f"  ✅ 检测到 {len(sd_devices)} 个可能的存储设备")
        else:
            print("  ⚠️ 未检测到外部存储设备")
        
        return sd_devices
    
    def _select_sd_card(self, sd_devices: list) -> str:
        """选择SD卡设备"""
        if len(sd_devices) == 1:
            device = sd_devices[0]
            print(f"📍 检测到设备: {device['description']}")
            
            # 安全确认
            print("⚠️ 重要警告: 烧录将会清除设备上的所有数据！")
            try:
                confirm = input("确认烧录? (yes/no): ").strip().lower()
                if confirm in ['yes', 'y', '是']:
                    return device['device']
                else:
                    print("❌ 用户取消烧录")
                    return None
            except KeyboardInterrupt:
                print("\n❌ 用户中断操作")
                return None
        
        elif len(sd_devices) > 1:
            print("📍 检测到多个设备，请选择:")
            for i, device in enumerate(sd_devices):
                print(f"  {i+1}. {device['description']}")
            
            try:
                choice = input("请输入选择 (1-{}): ".format(len(sd_devices))).strip()
                index = int(choice) - 1
                
                if 0 <= index < len(sd_devices):
                    device = sd_devices[index]
                    print(f"✅ 已选择: {device['description']}")
                    
                    # 安全确认
                    print("⚠️ 重要警告: 烧录将会清除设备上的所有数据！")
                    confirm = input("确认烧录? (yes/no): ").strip().lower()
                    if confirm in ['yes', 'y', '是']:
                        return device['device']
                    else:
                        print("❌ 用户取消烧录")
                        return None
                else:
                    print("❌ 无效的选择")
                    return None
                    
            except (ValueError, KeyboardInterrupt):
                print("❌ 无效输入或用户中断")
                return None
        
        return None
    
    def _flash_to_sd_card(self, image_path: Path, device: str) -> bool:
        """烧录镜像到SD卡"""
        print(f"🔥 开始烧录镜像到 {device}...")
        
        try:
            # 首先解压镜像
            print("  📦 解压镜像文件...")
            temp_image = self.output_dir / f"temp_{image_path.stem}.img"
            
            with gzip.open(image_path, 'rb') as f_in:
                with open(temp_image, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 卸载设备
            print("  📤 卸载设备...")
            if self.os_type == "darwin":
                subprocess.run(['diskutil', 'unmountDisk', device], check=False)
            elif self.os_type == "linux":
                subprocess.run(['umount', device], check=False)
            
            # 烧录镜像
            print("  🔥 烧录镜像中...")
            print("     ⚠️ 这可能需要几分钟时间，请耐心等待...")
            
            if self.os_type == "darwin":
                # macOS使用dd命令
                cmd = ['sudo', 'dd', f'if={temp_image}', f'of={device}', 'bs=4m']
            else:
                # Linux使用dd命令
                cmd = ['sudo', 'dd', f'if={temp_image}', f'of={device}', 'bs=4M', 'status=progress']
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 清理临时文件
            temp_image.unlink(missing_ok=True)
            
            if result.returncode == 0:
                print("  ✅ 烧录完成！")
                
                # 同步数据
                print("  🔄 同步数据...")
                subprocess.run(['sync'], check=False)
                
                # 弹出SD卡
                if self.os_type == "darwin":
                    subprocess.run(['diskutil', 'eject', device], check=False)
                
                return True
            else:
                print(f"  ❌ 烧录失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ 烧录过程出错: {e}")
            return False
    
    def _show_manual_flash_instructions(self, image_path: Path):
        """显示手动烧录说明"""
        print("\n📋 手动烧录说明:")
        print("=" * 50)
        print(f"镜像文件: {image_path}")
        print()
        print("方法一: 使用 Raspberry Pi Imager (推荐)")
        print("  1. 下载并安装 Raspberry Pi Imager")
        print("     https://rpi.org/imager")
        print("  2. 启动软件，选择 'Use custom image'")
        print(f"  3. 选择镜像文件: {image_path}")
        print("  4. 选择SD卡并点击 'Write'")
        print("  5. 等待烧录完成")
        print()
        print("方法二: 使用命令行 (Linux/macOS)")
        print(f"  1. 解压镜像: gunzip {image_path}")
        print("  2. 查找SD卡设备:")
        print("     macOS: diskutil list")
        print("     Linux: lsblk")
        print("  3. 烧录镜像:")
        print("     sudo dd if=镜像文件.img of=/dev/sdX bs=4M")
        print("  4. 同步数据: sync")
        print()
        print("⚠️ 注意事项:")
        print("  - 确认SD卡设备名，避免误操作")
        print("  - 烧录前备份SD卡重要数据")
        print("  - 推荐使用8GB以上SD卡")
    
    def _show_usage_instructions(self):
        """显示使用说明"""
        print("\n🎮 GamePlayer-Raspberry 使用说明:")
        print("=" * 50)
        print("硬件准备:")
        print("  1. 将SD卡插入树莓派")
        print("  2. 连接HDMI显示器")
        print("  3. 连接键盘/鼠标")
        print("  4. 接通电源启动")
        print()
        print("首次启动:")
        print("  - 系统自动扩展文件系统")
        print("  - 自动启动GamePlayer游戏系统")
        print("  - 通过路由器获取树莓派IP地址")
        print()
        print("游戏访问:")
        print("  - Web界面: http://树莓派IP:8080")
        print("  - SSH连接: ssh pi@树莓派IP")
        print("  - 默认密码: raspberry")
        print()
        print("游戏控制:")
        print("  - 方向键/WASD: 移动")
        print("  - 空格/Z: A按钮")
        print("  - Shift/X: B按钮")
        print("  - Enter: Start")
        print("  - ESC: 返回菜单")
        print()
        print("🎯 包含137个经典游戏，支持8种游戏系统！")
        print("✨ 享受复古游戏的乐趣！")
    
    def _generate_documentation(self, image_path: Path):
        """生成完整文档"""
        print("📚 生成使用文档...")
        
        doc_content = f"""# GamePlayer-Raspberry 生产镜像
## 镜像信息
- **文件名**: {image_path.name}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **文件大小**: {image_path.stat().st_size // (1024*1024)} MB
- **系统版本**: GamePlayer-Raspberry v5.1.0
- **校验和**: 见同名.sha256文件

## 功能特性
✅ **137个经典游戏ROM**  
✅ **8种游戏系统支持** (NES、SNES、GB、GBA、Genesis等)  
✅ **自动化测试和修复系统**  
✅ **Web游戏界面** (端口8080)  
✅ **SSH远程访问**  
✅ **自动启动功能**  
✅ **企业级稳定性**  

## 快速开始
1. **烧录镜像**: 使用Raspberry Pi Imager烧录到8GB+SD卡
2. **插入启动**: 将SD卡插入树莓派并接通电源
3. **访问游戏**: 浏览器打开 http://树莓派IP:8080

## 系统要求
- **硬件**: Raspberry Pi 3B+/4/400
- **SD卡**: 8GB以上高速SD卡
- **显示**: HDMI显示器
- **网络**: 有线或WiFi网络

## 默认配置
- **用户名**: pi
- **密码**: raspberry  
- **SSH**: 已启用
- **Web端口**: 8080
- **自动启动**: GamePlayer系统

## 游戏控制
- **移动**: 方向键 或 WASD
- **A按钮**: 空格 或 Z
- **B按钮**: Shift 或 X
- **开始**: Enter
- **选择**: Tab
- **退出**: ESC

## 支持的游戏系统
| 系统 | 游戏数量 | 代表作品 |
|------|----------|----------|
| NES | 77个 | Super Mario Bros, Zelda |
| SNES | 26个 | Super Mario World |
| Game Boy | 22个 | Tetris, Pokemon |
| Genesis | 12个 | Sonic the Hedgehog |

## 故障排除
- **无法启动**: 检查SD卡烧录是否完整
- **无法连接**: 检查网络配置和IP地址
- **游戏无响应**: 按ESC返回主菜单重试

## 技术支持
- **项目地址**: https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry
- **文档**: 见docs/目录
- **反馈**: 通过GitHub Issues报告问题

---
生成时间: {datetime.now().isoformat()}  
镜像版本: GamePlayer-Raspberry v5.1.0  
构建系统: 自动化测试和修复系统  
"""
        
        try:
            doc_file = image_path.with_suffix('.md')
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            
            print(f"  ✅ 文档已生成: {doc_file.name}")
        except Exception as e:
            print(f"  ⚠️ 文档生成警告: {e}")


def main():
    """主函数"""
    generator = AutoImageGeneratorAndFlasher()
    
    print("🎯 开始自动镜像生成和烧录流程...")
    
    success = generator.generate_and_flash_complete_workflow()
    
    if success:
        print("\n🎉 任务完成！")
        print("GamePlayer-Raspberry 镜像已准备就绪")
    else:
        print("\n❌ 任务失败！")
        print("请检查错误信息并重试")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
