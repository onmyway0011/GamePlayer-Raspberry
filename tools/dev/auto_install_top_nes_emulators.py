#!/usr/bin/env python3
import os
import sys
import platform
import requests
import shutil
import tarfile
import zipfile
from pathlib import Path

EMUDIR = Path.home() / "emulators"
EMUDIR.mkdir(parents=True, exist_ok=True)

BIN_DIR = Path.home() / "bin"
BIN_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"Accept": "application/vnd.github.v3+json"}

# 检测平台


def get_platform():
    """TODO: Add docstring"""
    sys_os = platform.system().lower()
    arch = platform.machine().lower()
    if sys_os == "darwin":
        return "macos"
    elif sys_os == "linux":
        return "linux"
    else:
        print(f"不支持的系统: {sys_os}")
        sys.exit(1)

PLATFORM = get_platform()

# 下载文件


def download_file(url, out_path):
    """TODO: Add docstring"""
    print(f"下载: {url}")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(out_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"已保存: {out_path}")

# 解压文件


def extract_file(file_path, dest_dir):
    """TODO: Add docstring"""
    if file_path.suffix in ['.gz', '.tar']:
        with tarfile.open(file_path, 'r:*') as tar:
            tar.extractall(dest_dir)
    elif file_path.suffix == '.zip':
        with zipfile.ZipFile(file_path, 'r') as zipf:
            zipf.extractall(dest_dir)
    else:
        print(f"未知压缩格式: {file_path}")
    print(f"已解压到: {dest_dir}")

# 获取GitHub最新release下载链接


def get_latest_github_asset(repo, keyword):
    """TODO: Add docstring"""
    api = f"https://api.github.com/repos/{repo}/releases/latest"
    r = requests.get(api, headers=HEADERS)
    r.raise_for_status()
    data = r.json()
    for asset in data.get('assets', []):
        name = asset['name'].lower()
        if keyword in name:
            return asset['browser_download_url'], name
    # fallback: 尝试第一个asset
    if data.get('assets'):
        asset = data['assets'][0]
        return asset['browser_download_url'], asset['name']
    return None, None

# 集成Mesen


def install_mesen():
    """TODO: Add docstring"""
    print("\n==== 集成 Mesen ====")
    repo = "SourMesen/Mesen"
    if PLATFORM == "macos":
        keyword = "macos"
    else:
        keyword = "linux"
    url, fname = get_latest_github_asset(repo, keyword)
    if not url:
        print("未找到Mesen下载链接")
        return
    out_path = EMUDIR / fname
    download_file(url, out_path)
    extract_file(out_path, EMUDIR)
    # 查找主程序
    mesen_bin = None
    for p in EMUDIR.rglob('Mesen*'):
        if p.is_file() and os.access(p, os.X_OK):
            mesen_bin = p
            break
    if mesen_bin:
        mesen_link = BIN_DIR / 'mesen'
        mesen_link.symlink_to(mesen_bin)
        print(f"已软链: {mesen_link} -> {mesen_bin}")
    else:
        print("未找到Mesen主程序")

# 集成puNES


def install_punes():
    """TODO: Add docstring"""
    print("\n==== 集成 puNES ====")
    repo = "punesemu/puNES"
    if PLATFORM == "macos":
        keyword = "macos"
    else:
        keyword = "appimage"
    url, fname = get_latest_github_asset(repo, keyword)
    if not url:
        print("未找到puNES下载链接")
        return
    out_path = EMUDIR / fname
    download_file(url, out_path)
    if out_path.suffix == '.zip':
        extract_file(out_path, EMUDIR)
        punes_bin = None
        for p in EMUDIR.rglob('puNES*'):
            if p.is_file() and os.access(p, os.X_OK):
                punes_bin = p
                break
        if punes_bin:
            punes_link = BIN_DIR / 'punes'
            punes_link.symlink_to(punes_bin)
            print(f"已软链: {punes_link} -> {punes_bin}")
        else:
            print("未找到puNES主程序")
    else:
        out_path.chmod(0o755)
        punes_link = BIN_DIR / 'punes'
        punes_link.symlink_to(out_path)
        print(f"已软链: {punes_link} -> {out_path}")

# 集成Nestopia UE


def install_nestopia():
    """TODO: Add docstring"""
    print("\n==== 集成 Nestopia UE ====")
    repo = "0ldsk00l/nestopia"
    if PLATFORM == "macos":
        keyword = "macos"
    else:
        keyword = "linux"
    url, fname = get_latest_github_asset(repo, keyword)
    if not url:
        print("未找到Nestopia下载链接")
        return
    out_path = EMUDIR / fname
    download_file(url, out_path)
    if out_path.suffix in ['.gz', '.tar', '.zip']:
        extract_file(out_path, EMUDIR)
        nestopia_bin = None
        for p in EMUDIR.rglob('nestopia*'):
            if p.is_file() and os.access(p, os.X_OK):
                nestopia_bin = p
                break
        if nestopia_bin:
            nestopia_link = BIN_DIR / 'nestopia'
            nestopia_link.symlink_to(nestopia_bin)
            print(f"已软链: {nestopia_link} -> {nestopia_bin}")
        else:
            print("未找到Nestopia主程序")
    else:
        out_path.chmod(0o755)
        nestopia_link = BIN_DIR / 'nestopia'
        nestopia_link.symlink_to(out_path)
        print(f"已软链: {nestopia_link} -> {out_path}")

if __name__ == "__main__":
    install_mesen()
    install_punes()
    install_nestopia()
    print(f"\n✅ Mesen、puNES、Nestopia UE 已自动集成到{EMUDIR}，并软链到{BIN_DIR}。\n")
