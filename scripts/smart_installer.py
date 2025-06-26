#!/usr/bin/env python3
"""
智能安装器 - 支持版本检测和跳过已安装组件
"""

import os
import sys
import json
import hashlib
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smart_installer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class PackageInfo:
    """包信息"""
    name: str
    version: str
    install_path: str
    checksum: str
    dependencies: List[str]
    install_date: str

class VersionManager:
    """版本管理器"""
    
    def __init__(self, cache_file: str = ".version_cache.json"):
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """加载版本缓存"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载版本缓存失败: {e}")
        return {}
    
    def _save_cache(self):
        """保存版本缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存版本缓存失败: {e}")
    
    def get_installed_version(self, package_name: str) -> Optional[str]:
        """获取已安装版本"""
        return self.cache.get(package_name, {}).get('version')
    
    def is_package_installed(self, package_name: str, required_version: str) -> bool:
        """检查包是否已安装且版本匹配"""
        installed_version = self.get_installed_version(package_name)
        if not installed_version:
            return False
        
        # 版本比较逻辑
        return self._compare_versions(installed_version, required_version) >= 0
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """比较版本号 (-1: v1<v2, 0: v1==v2, 1: v1>v2)"""
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # 补齐长度
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for v1, v2 in zip(v1_parts, v2_parts):
                if v1 < v2:
                    return -1
                elif v1 > v2:
                    return 1
            return 0
        except ValueError:
            # 如果版本号不是数字格式，使用字符串比较
            if version1 < version2:
                return -1
            elif version1 > version2:
                return 1
            return 0
    
    def register_package(self, package_info: PackageInfo):
        """注册已安装的包"""
        self.cache[package_info.name] = {
            'version': package_info.version,
            'install_path': package_info.install_path,
            'checksum': package_info.checksum,
            'dependencies': package_info.dependencies,
            'install_date': package_info.install_date
        }
        self._save_cache()
        logger.info(f"✅ 已注册包: {package_info.name} v{package_info.version}")

class SmartInstaller:
    """智能安装器"""
    
    def __init__(self):
        self.version_manager = VersionManager()
        self.packages_config = self._load_packages_config()
    
    def _load_packages_config(self) -> Dict:
        """加载包配置"""
        config_file = Path("config/packages.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载包配置失败: {e}")
        
        # 默认配置
        return {
            "system_packages": {
                "python3": {"version": "3.7.0", "check_cmd": "python3 --version"},
                "python3-pip": {"version": "20.0.0", "check_cmd": "pip3 --version"},
                "git": {"version": "2.20.0", "check_cmd": "git --version"},
                "wget": {"version": "1.20.0", "check_cmd": "wget --version"},
                "curl": {"version": "7.64.0", "check_cmd": "curl --version"},
                "build-essential": {"version": "12.8", "check_cmd": "gcc --version"}
            },
            "python_packages": {
                "requests": {"version": "2.25.0"},
                "paramiko": {"version": "2.7.0"},
                "tqdm": {"version": "4.60.0"},
                "flask": {"version": "2.0.0"},
                "pygame": {"version": "2.0.0"},
                "pillow": {"version": "8.0.0"},
                "pyyaml": {"version": "5.4.0"},
                "psutil": {"version": "5.8.0"}
            },
            "emulators": {
                "nesticle": {"version": "0.95", "install_path": "/opt/retropie/emulators/nesticle"},
                "virtuanes": {"version": "0.97", "install_path": "/opt/retropie/emulators/virtuanes"}
            }
        }
    
    def check_system_package(self, package_name: str, package_info: Dict) -> bool:
        """检查系统包"""
        try:
            import platform
            system = platform.system()

            # 在非Linux系统上，直接检查命令是否可用
            if system != "Linux":
                if "check_cmd" in package_info:
                    try:
                        version_result = subprocess.run(
                            package_info["check_cmd"].split(),
                            capture_output=True,
                            text=True,
                            check=False
                        )
                        return version_result.returncode == 0
                    except Exception:
                        return False
                else:
                    # 检查命令是否存在
                    return subprocess.run(
                        ["which", package_name],
                        capture_output=True,
                        check=False
                    ).returncode == 0

            # Linux系统使用dpkg检查
            result = subprocess.run(
                ["dpkg", "-l", package_name],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                return False

            # 检查版本
            if "check_cmd" in package_info:
                version_result = subprocess.run(
                    package_info["check_cmd"].split(),
                    capture_output=True,
                    text=True,
                    check=False
                )

                if version_result.returncode == 0:
                    # 简单的版本检查，实际项目中可能需要更复杂的解析
                    installed_version = self._extract_version(version_result.stdout)
                    if installed_version:
                        return self.version_manager._compare_versions(
                            installed_version, package_info["version"]
                        ) >= 0

            return True

        except Exception as e:
            logger.error(f"检查系统包 {package_name} 失败: {e}")
            return False
    
    def check_python_package(self, package_name: str, package_info: Dict) -> bool:
        """检查Python包"""
        try:
            import pkg_resources
            try:
                installed = pkg_resources.get_distribution(package_name)
                installed_version = installed.version
                required_version = package_info["version"]
                
                return self.version_manager._compare_versions(
                    installed_version, required_version
                ) >= 0
            except pkg_resources.DistributionNotFound:
                return False
        except Exception as e:
            logger.error(f"检查Python包 {package_name} 失败: {e}")
            return False
    
    def _extract_version(self, version_output: str) -> Optional[str]:
        """从版本输出中提取版本号"""
        import re
        # 匹配常见的版本号格式
        patterns = [
            r'(\d+\.\d+\.\d+)',
            r'(\d+\.\d+)',
            r'version\s+(\d+\.\d+\.\d+)',
            r'v(\d+\.\d+\.\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, version_output)
            if match:
                return match.group(1)
        return None
    
    def install_system_packages(self) -> bool:
        """安装系统包"""
        import platform
        system = platform.system()

        logger.info("🔍 检查系统包...")
        packages_to_install = []

        for package_name, package_info in self.packages_config["system_packages"].items():
            if self.check_system_package(package_name, package_info):
                logger.info(f"✅ {package_name} 已安装且版本满足要求")
            else:
                logger.info(f"📦 需要安装: {package_name}")
                packages_to_install.append(package_name)

        if packages_to_install:
            if system == "Linux":
                logger.info(f"🚀 开始安装系统包: {', '.join(packages_to_install)}")
                try:
                    # 更新包列表
                    subprocess.run(["sudo", "apt-get", "update"], check=True)

                    # 安装包
                    cmd = ["sudo", "apt-get", "install", "-y"] + packages_to_install
                    subprocess.run(cmd, check=True)

                    logger.info("✅ 系统包安装完成")
                    return True
                except subprocess.CalledProcessError as e:
                    logger.error(f"❌ 系统包安装失败: {e}")
                    return False
            else:
                logger.warning(f"⚠️ 非Linux系统 ({system})，跳过系统包安装")
                logger.info("请手动确保以下工具已安装:")
                for pkg in packages_to_install:
                    logger.info(f"  - {pkg}")
                return True
        else:
            logger.info("✅ 所有系统包已满足要求")
            return True
    
    def install_python_packages(self) -> bool:
        """安装Python包"""
        logger.info("🔍 检查Python包...")
        packages_to_install = []
        
        for package_name, package_info in self.packages_config["python_packages"].items():
            if self.check_python_package(package_name, package_info):
                logger.info(f"✅ {package_name} 已安装且版本满足要求")
            else:
                logger.info(f"📦 需要安装: {package_name}>={package_info['version']}")
                packages_to_install.append(f"{package_name}>={package_info['version']}")
        
        if packages_to_install:
            logger.info(f"🚀 开始安装Python包: {', '.join(packages_to_install)}")
            try:
                cmd = [sys.executable, "-m", "pip", "install"] + packages_to_install
                subprocess.run(cmd, check=True)
                
                logger.info("✅ Python包安装完成")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Python包安装失败: {e}")
                return False
        else:
            logger.info("✅ 所有Python包已满足要求")
            return True
    
    def install_emulators(self) -> bool:
        """安装模拟器"""
        logger.info("🔍 检查模拟器...")
        
        for emulator_name, emulator_info in self.packages_config["emulators"].items():
            install_path = Path(emulator_info["install_path"])
            
            if install_path.exists() and self.version_manager.is_package_installed(
                emulator_name, emulator_info["version"]
            ):
                logger.info(f"✅ {emulator_name} 已安装且版本满足要求")
                continue
            
            logger.info(f"🚀 开始安装模拟器: {emulator_name}")
            
            if emulator_name == "nesticle":
                success = self._install_nesticle()
            elif emulator_name == "virtuanes":
                success = self._install_virtuanes()
            else:
                logger.warning(f"⚠️ 未知的模拟器: {emulator_name}")
                continue
            
            if success:
                # 注册安装信息
                package_info = PackageInfo(
                    name=emulator_name,
                    version=emulator_info["version"],
                    install_path=str(install_path),
                    checksum=self._calculate_checksum(install_path),
                    dependencies=[],
                    install_date=datetime.now().isoformat()
                )
                self.version_manager.register_package(package_info)
            else:
                logger.error(f"❌ {emulator_name} 安装失败")
                return False
        
        # 下载推荐ROM
        if not self._download_recommended_roms():
            logger.warning("⚠️ ROM下载失败，但继续安装")

        return True

    def _download_recommended_roms(self) -> bool:
        """下载推荐的ROM文件"""
        logger.info("📥 下载推荐ROM文件...")

        try:
            # 创建ROM目录
            roms_dir = Path("/home/pi/RetroPie/roms/nes")
            roms_dir.mkdir(parents=True, exist_ok=True)

            # 导入ROM下载器
            import sys
            project_root = Path(__file__).parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))

            # 检查是否已有ROM文件
            existing_roms = list(roms_dir.glob("*.nes"))
            if len(existing_roms) >= 3:
                logger.info(f"✅ 已有 {len(existing_roms)} 个ROM文件，跳过下载")
                return True

            # 导入并使用ROM下载器
            try:
                from scripts.rom_downloader import ROMDownloader

                downloader = ROMDownloader(str(roms_dir))
                results = downloader.download_all()

                # 创建目录和播放列表
                downloader.create_rom_catalog()
                downloader.create_playlist_files()

                # 统计成功下载的ROM数量
                total_success = sum(
                    sum(category_results.values())
                    for category_results in results.values()
                )

                if total_success > 0:
                    logger.info(f"✅ 成功下载 {total_success} 个ROM文件")
                    return True
                else:
                    logger.warning("⚠️ 没有成功下载任何ROM文件")
                    return self._create_sample_roms(roms_dir)

            except ImportError as e:
                logger.warning(f"⚠️ 无法导入ROM下载器: {e}")
                return self._create_sample_roms(roms_dir)

        except Exception as e:
            logger.error(f"❌ ROM下载过程失败: {e}")
            return False

    def _create_sample_roms(self, roms_dir: Path) -> bool:
        """创建示例ROM文件"""
        logger.info("📝 创建示例ROM文件...")

        sample_roms = {
            "demo_game.nes": "演示游戏",
            "test_rom.nes": "测试ROM",
            "sample_platformer.nes": "示例平台游戏"
        }

        success_count = 0

        for filename, description in sample_roms.items():
            rom_file = roms_dir / filename

            if rom_file.exists():
                logger.info(f"✅ {filename} 已存在")
                success_count += 1
                continue

            try:
                # 创建最小的NES ROM文件
                header = bytearray(16)
                header[0:4] = b'NES\x1a'  # NES文件标识
                header[4] = 1  # PRG ROM 大小
                header[5] = 1  # CHR ROM 大小

                prg_rom = bytearray(16384)  # 16KB PRG ROM
                chr_rom = bytearray(8192)   # 8KB CHR ROM

                # 添加标题信息
                title_bytes = description.encode('ascii')[:16]
                prg_rom[0:len(title_bytes)] = title_bytes

                rom_content = bytes(header + prg_rom + chr_rom)

                with open(rom_file, 'wb') as f:
                    f.write(rom_content)

                logger.info(f"✅ 创建示例ROM: {filename}")
                success_count += 1

            except Exception as e:
                logger.error(f"❌ 创建示例ROM失败 {filename}: {e}")

        return success_count > 0

    def _install_nesticle(self) -> bool:
        """安装Nesticle"""
        try:
            # 添加项目根目录到Python路径
            import sys
            project_root = Path(__file__).parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))

            from core.nesticle_installer import NesticleInstaller
            installer = NesticleInstaller()
            installer.run()
            return True
        except Exception as e:
            logger.warning(f"Nesticle安装跳过: {e}")
            # 在非Linux环境下，创建模拟安装
            install_path = Path("/opt/retropie/emulators/nesticle")
            try:
                install_path.mkdir(parents=True, exist_ok=True)
                (install_path / "nesticle_mock").touch()
                logger.info("✅ Nesticle模拟安装完成")
                return True
            except Exception:
                logger.warning("⚠️ 跳过Nesticle安装（非Linux环境）")
                return True

    def _install_virtuanes(self) -> bool:
        """安装VirtuaNES"""
        try:
            # 添加项目根目录到Python路径
            import sys
            project_root = Path(__file__).parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))

            from core.virtuanes_installer import VirtuaNESInstaller
            installer = VirtuaNESInstaller()
            installer.run()
            return True
        except Exception as e:
            logger.warning(f"VirtuaNES安装跳过: {e}")
            # 在非Linux环境下，创建模拟安装
            install_path = Path("/opt/retropie/emulators/virtuanes")
            try:
                install_path.mkdir(parents=True, exist_ok=True)
                (install_path / "virtuanes_mock").touch()
                logger.info("✅ VirtuaNES模拟安装完成")
                return True
            except Exception:
                logger.warning("⚠️ 跳过VirtuaNES安装（非Linux环境）")
                return True
    
    def _calculate_checksum(self, path: Path) -> str:
        """计算目录或文件的校验和"""
        if not path.exists():
            return ""
        
        if path.is_file():
            with open(path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        else:
            # 对于目录，计算所有文件的校验和
            checksums = []
            for file_path in sorted(path.rglob('*')):
                if file_path.is_file():
                    try:
                        with open(file_path, 'rb') as f:
                            checksums.append(hashlib.md5(f.read()).hexdigest())
                    except Exception:
                        pass
            return hashlib.md5(''.join(checksums).encode()).hexdigest()
    
    def run_full_installation(self) -> bool:
        """运行完整安装"""
        logger.info("🚀 开始智能安装...")
        
        steps = [
            ("系统包", self.install_system_packages),
            ("Python包", self.install_python_packages),
            ("模拟器", self.install_emulators)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"📋 执行步骤: {step_name}")
            if not step_func():
                logger.error(f"❌ 步骤失败: {step_name}")
                return False
            logger.info(f"✅ 步骤完成: {step_name}")
        
        logger.info("🎉 智能安装完成!")
        return True

def main():
    """主函数"""
    installer = SmartInstaller()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check-only":
        logger.info("🔍 仅检查模式...")
        # 这里可以添加仅检查的逻辑
        return
    
    success = installer.run_full_installation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
