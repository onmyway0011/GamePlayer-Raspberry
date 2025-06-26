#!/bin/bash
set -e

# 镜像文件名（可根据实际情况自动查找或传参）
IMG_FILE=${1:-downloads/retropie-buster-4.8-rpi4_400.img}

# 1. 自动清理镜像内容
log() { echo -e "\033[0;32m[shrink]\033[0m $1"; }

log "挂载镜像..."
LOOPDEV=$(sudo losetup --show -Pf $IMG_FILE)
MNTDIR=/mnt/shrink_img
sudo mkdir -p $MNTDIR
sudo mount ${LOOPDEV}p2 $MNTDIR

log "清理APT缓存、日志、文档、临时文件..."
sudo rm -rf $MNTDIR/var/cache/apt/archives/*
sudo rm -rf $MNTDIR/var/lib/apt/lists/*
sudo find $MNTDIR/var/log -type f -exec truncate -s 0 {} \;
sudo rm -rf $MNTDIR/tmp/*
sudo rm -rf $MNTDIR/var/tmp/*
sudo rm -rf $MNTDIR/usr/share/doc/*
sudo rm -rf $MNTDIR/usr/share/man/*
sudo rm -rf $MNTDIR/usr/share/info/*
sudo rm -rf $MNTDIR/usr/share/locale/*

log "可选：移除不必要的包（如需可解注释）"
# sudo chroot $MNTDIR apt-get remove --purge -y libreoffice* wolfram-engine sonic-pi scratch* minecraft-pi dillo gpicview penguinspuzzle python-games
# sudo chroot $MNTDIR apt-get autoremove -y
# sudo chroot $MNTDIR apt-get clean

log "清理演示ROM和样例文件..."
sudo rm -rf $MNTDIR/home/pi/RetroPie/roms/demo*
sudo rm -rf $MNTDIR/home/pi/RetroPie/roms/sample*

log "卸载镜像..."
sudo umount $MNTDIR
sudo losetup -d $LOOPDEV
sudo rmdir $MNTDIR

# 2. 用pishrink收缩镜像
if [ ! -f pishrink.sh ]; then
  wget -q https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
  chmod +x pishrink.sh
fi

log "收缩镜像..."
sudo ./pishrink.sh -a $IMG_FILE

log "镜像清理与收缩完成！"

# 依赖检查函数
check_apt_pkg() { dpkg -s "$1" &>/dev/null; }
check_pip_pkg() {
  local pkg=$1
  local ver=$2
  if python3 -c "import pkg_resources; pkg_resources.require('${pkg}${ver:+>='}${ver}')" 2>/dev/null; then
    return 0
  else
    return 1
  fi
}

# 系统依赖
APT_PKGS=(python3 python3-pip python3-dev git wget curl build-essential losetup)
for pkg in "${APT_PKGS[@]}"; do
  if ! check_apt_pkg "$pkg"; then
    apt-get update && apt-get install -y "$pkg"
  fi
done

# Python依赖
PIP_PKGS=(numpy:1.21.6 requests tqdm)
for item in "${PIP_PKGS[@]}"; do
  pkg=${item%%:*}
  ver=${item#*:}
  if [[ "$pkg" == "$ver" ]]; then ver=""; fi
  if ! check_pip_pkg "$pkg" "$ver"; then
    pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple "$pkg${ver:+==$ver}"
  fi
done 