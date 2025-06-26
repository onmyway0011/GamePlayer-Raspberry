#!/bin/bash
set -e

IMG="downloads/retropie-buster-4.8-rpi4_400.img"
LOG="logs/batch_burn.log"

if [ ! -f "$IMG" ]; then
  echo "[ERR] 镜像文件不存在: $IMG"
  exit 1
fi

mkdir -p logs

echo "=== 一键批量烧录脚本启动 ===" | tee -a "$LOG"

echo "请插入SD卡（仅插一张），按回车开始烧录，Ctrl+C退出..."

while true; do
  read -p "插入SD卡后按回车继续..."
  # 自动检测新插入的SD卡（排除系统盘）
  BEFORE=$(lsblk -dn -o NAME)
  sleep 2
  AFTER=$(lsblk -dn -o NAME)
  NEW=$(comm -13 <(echo "$BEFORE") <(echo "$AFTER"))
  if [ -z "$NEW" ]; then
    echo "[WARN] 未检测到新SD卡，请重新插拔。"
    continue
  fi
  DEV="/dev/${NEW}"
  echo "[INFO] 检测到SD卡: $DEV"
  read -p "确认烧录到 $DEV ? (y/n): " yn
  if [[ "$yn" != "y" ]]; then
    echo "[INFO] 跳过本次烧录。"
    continue
  fi
  echo "[INFO] 开始烧录 $IMG 到 $DEV ..." | tee -a "$LOG"
  sudo dd if="$IMG" of="$DEV" bs=4M status=progress conv=fsync
  sync
  echo "[OK] 烧录完成: $DEV" | tee -a "$LOG"
  # 自动弹出SD卡
  sudo eject "$DEV" || true
  echo "[INFO] $DEV 已弹出，请更换下一张卡。"
  echo "--------------------------------------" | tee -a "$LOG"
done 