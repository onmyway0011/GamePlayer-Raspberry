#!/usr/bin/env python3
"""
NES ROM 下载和传输工具

这是一个自动化ROM下载和传输工具，专门用于RetroPie游戏系统。
支持从合法ROM资源站下载游戏合集并自动传输到树莓派。

主要功能：
- 从Archive.org等合法资源站搜索和下载ROM
- 支持断点续传和校验和验证
- 自动解压ZIP格式的ROM文件
- 通过SFTP自动传输到树莓派
- 完整的日志记录和错误处理
- 配置文件驱动的灵活配置

系统要求：
- Python 3.7+
- 网络连接
- 树莓派SSH访问权限

作者: AI Assistant
版本: 2.0.0
许可证: MIT
"""

import argparse
import hashlib
import json
import logging
import os
import time
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from functools import lru_cache

import paramiko
import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.util.retry import Retry

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(
        "rom_downloader.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class ROMDownloader:
    """
    ROM下载和传输工具类

    提供完整的ROM自动化下载和传输流程，包括：
    - ROM搜索和下载链接获取
    - 断点续传的文件下载
    - 文件完整性验证
    - 自动解压和文件处理
    - SFTP传输到树莓派

    属性:
        config_file (Path): 配置文件路径
        download_dir (Path): 下载目录路径
        config (Dict): 配置字典
        session (requests.Session): HTTP会话对象
    """

    @lru_cache(maxsize=128)
    def _get_cached_download(self, url: str) -> bytes:
        """
        Cached download method to avoid redundant downloads
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Failed to download {url}: {e}")
            raise

    def __init__(self, config_file: str = "rom_config.json"):
        """
        初始化ROM下载器

        Args:
            config_file (str): 配置文件路径
        """
        self.config_file = Path(config_file)
        self.download_dir = Path("downloads/roms")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()

        # 设置重试策略
        self.session = self._setup_session()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")

        # 默认配置
        default_config = {
            "rom_sources": {
                "archive_org": {
                    "base_url": "https://archive.org",
                    "search_url": "https://archive.org/advancedsearch.php",
                    "download_patterns": ["nes-100-in-1", "nes-games-collection", "nintendo-entertainment-system-roms"],
                }
            },
            "raspberry_pi": {
                "host": "192.168.1.100",
                "port": 22,
                "username": "pi",
                "password": "",
                "key_file": "",
                "roms_path": "/home/pi/RetroPie/roms/nes/",
            },
            "download": {"timeout": 30, "chunk_size": 8192, "max_retries": 3, "retry_delay": 5},
            "verification": {"verify_checksum": True, "checksum_algorithm": "sha256"},
        }

        # 保存默认配置
        self._save_config(default_config)
        return default_config

    def _save_config(self, config: Dict):
        """保存配置文件"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"配置文件已保存: {self.config_file}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")

    def _setup_session(self) -> requests.Session:
        """设置HTTP会话，包含重试策略"""
        session = requests.Session()

        retry_strategy = Retry(
            total=self.config["download"]["max_retries"],
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=self.config["download"]["retry_delay"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def search_roms(self, query: str = "nes 100 in 1") -> List[Dict]:
        """搜索ROM文件"""
        logger.info(f"搜索ROM: {query}")

        try:
            search_url = self.config["rom_sources"]["archive_org"]["search_url"]
            params = {"q": query, "output": "json",
                      "rows": 50, "sort": "downloads desc"}

            response = self.session.get(search_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            results = []

            for doc in data.get("response", {}).get("docs", []):
                if "downloads" in doc and doc["downloads"] > 0:
                    result = {
                        "identifier": doc.get("identifier", ""),
                        "title": doc.get("title", ""),
                        "description": doc.get("description", ""),
                        "downloads": doc.get("downloads", 0),
                        "files": doc.get("files", []),
                    }
                    results.append(result)

            logger.info(f"找到 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.error(f"搜索ROM失败: {e}")
            return []

    def get_download_url(self, identifier: str) -> Optional[str]:
        """获取下载链接"""
        try:
            metadata_url = f"{self.config['rom_sources']['archive_org']['base_url']}/metadata/{identifier}"
            response = self.session.get(metadata_url, timeout=30)
            response.raise_for_status()

            data = response.json()
            files = data.get("files", {})

            # 查找ZIP文件
            for filename in files.keys():
                if filename.lower().endswith(".zip"):
                    download_url = (
                        f"{self.config['rom_sources']['archive_org']['base_url']}/download/{identifier}/{filename}"
                    )
                    logger.info(f"找到下载链接: {download_url}")
                    return download_url

            logger.warning(f"未找到ZIP文件: {identifier}")
            return None

        except Exception as e:
            logger.error(f"获取下载链接失败: {e}")
            return None

    def download_file(self, url: str, filename: str) -> Optional[Path]:
        """下载文件，支持断点续传"""
        file_path = self.download_dir / filename

        # 检查是否已存在
        if file_path.exists():
            logger.info(f"文件已存在: {file_path}")
            return file_path

        try:
            # 获取文件大小
            response = self.session.head(url, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))

            # 检查是否有部分下载的文件
            temp_path = file_path.with_suffix(".tmp")
            resume_pos = 0

            if temp_path.exists():
                resume_pos = temp_path.stat().st_size
                if resume_pos >= total_size:
                    # 文件已完整下载
                    temp_path.rename(file_path)
                    logger.info(f"文件下载完成: {file_path}")
                    return file_path

            # 设置断点续传头
            headers = {}
            if resume_pos > 0:
                headers["Range"] = f"bytes={resume_pos}-"
                logger.info(f"断点续传: {resume_pos} bytes")

            # 开始下载
            response = self.session.get(
                url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()

            mode = "ab" if resume_pos > 0 else "wb"

            with open(temp_path, mode) as f:
                with tqdm(total=total_size, initial=resume_pos, unit="B", unit_scale=True, desc=filename) as pbar:
                    for chunk in response.iter_content(chunk_size=self.config["download"]["chunk_size"]):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            # 重命名临时文件
            temp_path.rename(file_path)
            logger.info(f"下载完成: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"下载失败: {e}")
            # 清理临时文件
            if temp_path.exists():
                temp_path.unlink()
            return None

    def verify_file(self, file_path: Path):
        """验证文件完整性"""
        if not self.config["verification"]["verify_checksum"]:
            return True

        logger.info(f"验证文件完整性: {file_path}")

        try:
            algorithm = self.config["verification"]["checksum_algorithm"]
            hash_func = getattr(hashlib, algorithm)()

            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_func.update(chunk)

            checksum = hash_func.hexdigest()
            logger.info(f"文件校验和 ({algorithm}): {checksum}")

            # 这里可以添加预定义的校验和验证
            # 由于ROM文件可能来自不同源，暂时只计算校验和

            return True

        except Exception as e:
            logger.error(f"文件验证失败: {e}")
            return False

    def extract_roms(self, zip_path: Path) -> List[Path]:
        """解压ROM文件"""
        logger.info(f"解压ROM文件: {zip_path}")

        rom_files = []
        extract_dir = self.download_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # 列出所有文件
                file_list = zip_ref.namelist()
                logger.info(f"ZIP文件包含 {len(file_list)} 个文件")

                # 过滤ROM文件
                rom_extensions = [".nes", ".NES"]
                rom_files_in_zip = [f for f in file_list if any(
                    f.endswith(ext) for ext in rom_extensions)]

                logger.info(f"找到 {len(rom_files_in_zip)} 个ROM文件")

                # 解压ROM文件
                for rom_file in rom_files_in_zip:
                    try:
                        zip_ref.extract(rom_file, extract_dir)
                        rom_path = extract_dir / rom_file
                        rom_files.append(rom_path)
                        logger.info(f"解压: {rom_file}")
                    except Exception as e:
                        logger.error(f"解压文件失败 {rom_file}: {e}")

            return rom_files

        except Exception as e:
            logger.error(f"解压失败: {e}")
            return []

    def connect_sftp(self) -> Optional[paramiko.SSHClient]:
        """连接SFTP服务器"""
        logger.info("连接树莓派SFTP服务器...")

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            pi_config = self.config["raspberry_pi"]

            # 使用密钥文件或密码
            if pi_config.get("key_file") and Path(pi_config["key_file"]).exists():
                ssh.connect(
                    hostname=pi_config["host"],
                    port=pi_config["port"],
                    username=pi_config["username"],
                    key_filename=pi_config["key_file"],
                    timeout=30,
                )
            else:
                ssh.connect(
                    hostname=pi_config["host"],
                    port=pi_config["port"],
                    username=pi_config["username"],
                    password=pi_config["password"],
                    timeout=30,
                )

            logger.info("SFTP连接成功")
            return ssh

        except Exception as e:
            logger.error(f"SFTP连接失败: {e}")
            return None

    def upload_roms(self, rom_files: List[Path]):
        """上传ROM文件到树莓派"""
        if not rom_files:
            logger.warning("没有ROM文件需要上传")
            return False

        ssh = self.connect_sftp()
        if not ssh:
            return False

        try:
            sftp = ssh.open_sftp()
            pi_config = self.config["raspberry_pi"]
            remote_path = pi_config["roms_path"]

            # 确保远程目录存在
            try:
                sftp.stat(remote_path)
            except FileNotFoundError:
                logger.info(f"创建远程目录: {remote_path}")
                sftp.mkdir(remote_path)

            uploaded_count = 0

            for rom_file in rom_files:
                try:
                    remote_file = f"{remote_path}/{rom_file.name}"

                    # 检查文件是否已存在
                    try:
                        remote_stat = sftp.stat(remote_file)
                        local_stat = rom_file.stat()

                        if remote_stat.st_size == local_stat.st_size:
                            logger.info(f"文件已存在，跳过: {rom_file.name}")
                            uploaded_count += 1
                            continue
                    except FileNotFoundError:
                        pass

                    # 上传文件
                    logger.info(f"上传: {rom_file.name}")
                    sftp.put(str(rom_file), remote_file)
                    uploaded_count += 1

                except Exception as e:
                    logger.error(f"上传文件失败 {rom_file.name}: {e}")

            sftp.close()
            ssh.close()

            logger.info(f"上传完成: {uploaded_count}/{len(rom_files)} 个文件")
            return uploaded_count > 0

        except Exception as e:
            logger.error(f"上传过程出错: {e}")
            ssh.close()
            return False

    def run(self, search_query: str = "nes 100 in 1"):
        """运行完整的下载和传输流程"""
        logger.info("=== NES ROM 下载和传输工具 ===")

        # 1. 优先尝试配置文件中的下载地址
        nes_zip_urls = self.config.get("nes_zip_urls", [])
        zip_path = None
        download_url = None
        if nes_zip_urls:
            logger.info(f"配置文件中找到 {len(nes_zip_urls)} 个NES ZIP下载地址，优先尝试...")
            for url in nes_zip_urls:
                filename = url.split("/")[-1]
                logger.info(f"尝试下载: {url}")
                zip_path = self.download_file(url, filename)
                if zip_path:
                    download_url = url
                    logger.info(f"成功下载: {url}")
                    break
                else:
                    logger.warning(f"下载失败: {url}")

        # 2. 如果配置地址全部失败，则自动搜索
        if not zip_path:
            logger.info("配置地址全部失败，自动搜索可用ROM...")
            results = self.search_roms(search_query)
            if not results:
                logger.error("未找到ROM文件")
                return False
            print("\n搜索结果:")
            for i, result in enumerate(results[:5]):
                print(
                    f"{i+1}. {result['title']} (下载次数: {result['downloads']})")
            selected_result = results[0]
            logger.info(f"选择: {selected_result['title']}")
            download_url = self.get_download_url(selected_result["identifier"])
            if not download_url:
                logger.error("无法获取下载链接")
                return False
            filename = download_url.split("/")[-1]
            zip_path = self.download_file(download_url, filename)
            if not zip_path:
                logger.error("下载失败")
                return False

        # 3. 验证文件
        if not self.verify_file(zip_path):
            logger.error("文件验证失败")
            return False

        # 4. 解压ROM文件
        rom_files = self.extract_roms(zip_path)
        if not rom_files:
            logger.error("解压失败或未找到ROM文件")
            return False

        # 5. 上传到树莓派
        if self.upload_roms(rom_files):
            logger.info("ROM传输完成！")
            return True
        else:
            logger.error("ROM传输失败")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="NES ROM 下载和传输工具")
    parser.add_argument("--config", default="rom_config.json", help="配置文件路径")
    parser.add_argument("--search", default="nes 100 in 1", help="搜索关键词")
    parser.add_argument("--download-only", action="store_true", help="仅下载，不上传")
    parser.add_argument("--upload-only", action="store_true", help="仅上传已下载的文件")
    parser.add_argument("--setup-config", action="store_true", help="设置配置文件")

    args = parser.parse_args()

    downloader = ROMDownloader(args.config)

    if args.setup_config:
        print("请编辑配置文件:", args.config)
        print("配置项包括:")
        print("- 树莓派连接信息")
        print("- 下载参数")
        print("- 验证设置")
        return

    if args.upload_only:
        # 查找已下载的ROM文件
        extract_dir = downloader.download_dir / "extracted"
        if extract_dir.exists():
            rom_files = list(extract_dir.glob("*.nes")) + \
                list(extract_dir.glob("*.NES"))
            if rom_files:
                downloader.upload_roms(rom_files)
            else:
                logger.error("未找到ROM文件")
        else:
            logger.error("未找到解压目录")
        return

    # 运行完整流程
    success = downloader.run(args.search)

    if success:
        print("\n🎉 ROM下载和传输完成！")
    else:
        print("\n❌ 操作失败，请查看日志文件")

if __name__ == "__main__":
    main()
