#!/bin/bash
# 自动定时更新ROM源脚本
# 可添加到crontab或后台守护进程

WORKDIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$WORKDIR"

LOGDIR="$WORKDIR/logs"
mkdir -p "$LOGDIR"
LOGFILE="$LOGDIR/auto_update_rom_sources.log"

# 每次运行都记录日志
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] 开始自动更新ROM源..." >> "$LOGFILE"

# 执行自动更新脚本
python3 src/scripts/auto_update_rom_sources.py >> "$LOGFILE" 2>&1

RET=$?
if [ $RET -eq 0 ]; then
  echo "[$TIMESTAMP] ROM源自动更新完成" >> "$LOGFILE"
else
  echo "[$TIMESTAMP] ROM源自动更新失败，错误码 $RET" >> "$LOGFILE"
fi 