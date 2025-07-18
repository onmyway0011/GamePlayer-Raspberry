#!/bin/bash
# GamePlayer-Raspberry 自动启动脚本

# 错误处理
set -e

# 等待系统完全启动
sleep 10

# 设置环境变量
export HOME=/home/pi
export USER=pi
export DISPLAY=:0

# 创建日志目录
mkdir -p /home/pi/logs

# 启动前检查
if [ ! -d "/home/pi/GamePlayer-Raspberry" ]; then
    echo "$(date): GamePlayer-Raspberry 目录不存在" >> /home/pi/logs/gameplayer.log
    exit 1
fi

# 启动X服务器（如果未运行）
if ! pgrep -x "X" > /dev/null; then
    startx &
    sleep 5
fi

# 启动游戏管理器
cd /home/pi/GamePlayer-Raspberry
if [ -f "src/scripts/nes_game_launcher.py" ]; then
    python3 src/scripts/nes_game_launcher.py --autostart &
else
    echo "$(date): 找不到游戏启动器" >> /home/pi/logs/gameplayer.log
fi

# 启动Web服务器
if [ -d "/home/pi/GamePlayer-Raspberry/data/web" ]; then
    python3 -m http.server 8080 --directory /home/pi/GamePlayer-Raspberry/data/web &
else
    echo "$(date): Web目录不存在，创建基本Web界面" >> /home/pi/logs/gameplayer.log
    mkdir -p /home/pi/GamePlayer-Raspberry/data/web
    echo "<h1>GamePlayer-Raspberry</h1>" > /home/pi/GamePlayer-Raspberry/data/web/index.html
    python3 -m http.server 8080 --directory /home/pi/GamePlayer-Raspberry/data/web &
fi

# 记录启动日志
echo "$(date): GamePlayer-Raspberry 自动启动完成" >> /home/pi/logs/gameplayer.log
