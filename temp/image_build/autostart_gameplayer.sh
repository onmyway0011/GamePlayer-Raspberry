#!/bin/bash
# GamePlayer-Raspberry 自动启动脚本

# 等待系统完全启动
sleep 10

# 设置环境变量
export HOME=/home/pi
export USER=pi
export DISPLAY=:0

# 启动X服务器（如果未运行）
if ! pgrep -x "X" > /dev/null; then
    startx &
    sleep 5
fi

# 启动游戏管理器
cd /home/pi/GamePlayer-Raspberry
python3 src/scripts/nes_game_launcher.py --autostart &

# 启动Web服务器
python3 -m http.server 8080 --directory /home/pi/GamePlayer-Raspberry/data/web &

# 记录启动日志
echo "$(date): GamePlayer-Raspberry 自动启动完成" >> /home/pi/gameplayer.log
