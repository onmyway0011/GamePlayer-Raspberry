#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化本地存档同步与云端同步脚本
- 支持腾讯云COS和自定义API
- 支持多模拟器（通过配置文件选择）
- 启动模拟器前自动拉取云端存档，退出后自动上传
- 存档和金手指目录均可配置
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

try:
    import boto3
    import paramiko
    import requests
    import tqdm
    from botocore.client import Config
except ImportError:
    print("请先安装 requests tqdm paramiko boto3")
    sys.exit(1)

CONFIG_PATH = Path(__file__).parent / "project_config.json"

# 读取配置
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

EMULATOR_TYPE = config["emulator"]["type"]
CHEATS_DIR = Path(config["emulator"]["cheats_dir"])
SAVES_DIR = Path(config["emulator"]["saves_dir"])
CLOUD_PROVIDER = config["cloud_save"]["provider"]

# 云端存储相关
COS_CONF = config["cloud_save"].get("cos", {})
API_CONF = config["cloud_save"].get("custom_api", {})


# ========== 云端存档操作 ==========
def cos_client():
    return boto3.client(
        "s3",
        aws_access_key_id=COS_CONF["secret_id"],
        aws_secret_access_key=COS_CONF["secret_key"],
        endpoint_url=COS_CONF.get("base_url"),
        region_name=COS_CONF["region"],
        config=Config(signature_version="s3v4"),
    )


def upload_to_cos(local_path, remote_key):
    client = cos_client()
    bucket = COS_CONF["bucket"]
    client.upload_file(str(local_path), bucket, remote_key)
    print(f"已上传到COS: {remote_key}")


def download_from_cos(remote_key, local_path):
    client = cos_client()
    bucket = COS_CONF["bucket"]
    try:
        client.download_file(bucket, remote_key, str(local_path))
        print(f"已从COS下载: {remote_key}")
        return True
    except Exception as e:
        print(f"云端无存档: {remote_key}")
        return False


def upload_to_api(local_path, remote_key):
    url = API_CONF["api_url"]
    api_key = API_CONF["api_key"]
    files = {"file": open(local_path, "rb")}
    data = {"key": remote_key, "api_key": api_key}
    resp = requests.post(url, files=files, data=data)
    print(f"API上传结果: {resp.status_code}")


def download_from_api(remote_key, local_path):
    url = API_CONF["api_url"]
    api_key = API_CONF["api_key"]
    params = {"key": remote_key, "api_key": api_key}
    resp = requests.get(url, params=params, stream=True)
    if resp.status_code == 200:
        with open(local_path, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        print(f"已从API下载: {remote_key}")
        return True
    print(f"API无存档: {remote_key}")
    return False


def upload_save(local_path, remote_key):
    if CLOUD_PROVIDER == "cos":
        upload_to_cos(local_path, remote_key)
    else:
        upload_to_api(local_path, remote_key)


def download_save(remote_key, local_path):
    if CLOUD_PROVIDER == "cos":
        return download_from_cos(remote_key, local_path)
    else:
        return download_from_api(remote_key, local_path)


# ========== 存档同步主流程 ==========
def get_latest_save(game_name):
    """获取本地最新存档文件"""
    game_save_dir = SAVES_DIR / game_name
    if not game_save_dir.exists():
        return None
    saves = sorted(game_save_dir.glob("*.sav"),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    return saves[0] if saves else None


def sync_save_from_cloud(game_name):
    """启动游戏前拉取云端存档"""
    game_save_dir = SAVES_DIR / game_name
    game_save_dir.mkdir(parents=True, exist_ok=True)
    remote_key = f"{game_name}/latest.sav"
    local_path = game_save_dir / "latest.sav"
    found = download_save(remote_key, local_path)
    if found:
        print(f"已同步云端存档: {local_path}")
    else:
        print(f"无云端存档，首次游玩: {game_name}")


def sync_save_to_cloud(game_name):
    """退出游戏后上传最新存档"""
    latest_save = get_latest_save(game_name)
    if latest_save:
        remote_key = f"{game_name}/latest.sav"
        upload_save(latest_save, remote_key)
    else:
        print(f"未找到本地存档: {game_name}")


# ========== 金手指自动加载 ==========
def enable_cheat(game_name):
    """启动模拟器时自动加载金手指"""
    cheat_file = CHEATS_DIR / f"{game_name}.cht"
    if cheat_file.exists():
        print(f"检测到金手指: {cheat_file}")
        return cheat_file
    print(f"未检测到金手指: {cheat_file}")
    return None


# ========== 启动模拟器 ==========
def launch_emulator(game_name, rom_path):
    cheat_file = enable_cheat(game_name)
    if EMULATOR_TYPE == "retroarch":
        cmd = [
            "retroarch",
            "-L",
            "/opt/retropie/libretro/nestopia_libretro.so",  # 可配置
            "--config",
            "/opt/retropie/configs/all/retroarch.cfg",
            rom_path,
        ]
        if cheat_file:
            cmd += ["--cheat", str(cheat_file)]
    elif EMULATOR_TYPE == "snes9x":
        cmd = ["snes9x", rom_path]
        if cheat_file:
            cmd += ["--cheat", str(cheat_file)]
    else:
        print(f"暂不支持的模拟器类型: {EMULATOR_TYPE}")
        return
    print(f"启动模拟器: {' '.join(cmd)}")
    subprocess.run(cmd)


# ========== 主流程入口 ==========
def main():
    if len(sys.argv) < 3:
        print("用法: python auto_save_sync.py <game_name> <rom_path>")
        sys.exit(1)
    game_name = sys.argv[1]
    rom_path = sys.argv[2]
    # 1. 启动前拉取云端存档
    sync_save_from_cloud(game_name)
    # 2. 启动模拟器（自动加载金手指）
    launch_emulator(game_name, rom_path)
    # 3. 退出后上传最新存档
    sync_save_to_cloud(game_name)


if __name__ == "__main__":
    main()
