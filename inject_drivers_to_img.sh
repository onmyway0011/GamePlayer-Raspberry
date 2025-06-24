#!/bin/bash
set -e

IMG="retropie-buster-4.8-rpi4_400.img"
SCRIPT="auto_hardware_setup.sh"

# 检查依赖
command -v fdisk >/dev/null || { echo "请先安装fdisk"; exit 1; }
command -v mount >/dev/null || { echo "请先安装mount"; exit 1; }
command -v sudo >/dev/null || { echo "请先安装sudo"; exit 1; }

# 1. 计算分区偏移
echo "正在计算分区偏移..."
BOOT_START=$(fdisk -l $IMG | grep "FAT32" | awk '{print $2}')
ROOT_START=$(fdisk -l $IMG | grep "Linux" | awk '{print $2}' | head -n1)
SECTOR_SIZE=$(fdisk -l $IMG | grep "Units" | awk '{print $9}')

BOOT_OFFSET=$((BOOT_START * SECTOR_SIZE))
ROOT_OFFSET=$((ROOT_START * SECTOR_SIZE))

echo "BOOT分区偏移: $BOOT_OFFSET"
echo "ROOT分区偏移: $ROOT_OFFSET"

# 2. 挂载分区
sudo mkdir -p /mnt/rpi-boot /mnt/rpi-root
sudo mount -o loop,offset=$BOOT_OFFSET $IMG /mnt/rpi-boot
sudo mount -o loop,offset=$ROOT_OFFSET $IMG /mnt/rpi-root

# 3. 复制脚本到镜像
echo "复制自动化脚本到镜像..."
sudo cp $SCRIPT /mnt/rpi-root/home/pi/
sudo chmod +x /mnt/rpi-root/home/pi/$SCRIPT

# 4. 写入 systemd 服务
echo "写入 systemd 服务..."
sudo tee /mnt/rpi-root/etc/systemd/system/auto_hw.service >/dev/null <<EOF
[Unit]
Description=Auto Hardware Setup

[Service]
Type=oneshot
ExecStart=/bin/bash /home/pi/$SCRIPT
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

sudo ln -sf /etc/systemd/system/auto_hw.service /mnt/rpi-root/etc/systemd/system/multi-user.target.wants/auto_hw.service

# 5. 卸载分区
echo "卸载分区..."
sudo umount /mnt/rpi-boot
sudo umount /mnt/rpi-root
sudo rmdir /mnt/rpi-boot /mnt/rpi-root

echo "驱动和自动化脚本已集成到镜像！烧录后首次开机将自动完成驱动配置。"
