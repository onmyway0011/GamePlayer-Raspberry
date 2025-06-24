#!/bin/bash
set -e

TARGET_DIR="/home/pi/GamePlayer-Raspberry"
SERVICE_FILE="firstboot_setup.service"
REQUIREMENTS="requirements.txt"
WEB_PORT=5000
LOG_DIR="$TARGET_DIR/logs"
VENV_DIR="$TARGET_DIR/.venv"
PYTHON_MIN_VERSION=3.7
ROM_DIR="$TARGET_DIR/systems/retropie/roms"
CHEAT_DIR="$TARGET_DIR/systems/retropie/cheats"
SAVE_DIR="$TARGET_DIR/systems/retropie/saves"
MAX_REBOOT=2
REBOOT_COUNT_FILE="$LOG_DIR/reboot_count.flag"

log() { echo -e "[\033[32mINFO\033[0m] $1"; }
warn() { echo -e "[\033[33mWARN\033[0m] $1"; }
err() { echo -e "[\033[31mERR \033[0m] $1"; }

# 0. 日志目录
mkdir -p "$LOG_DIR"

# 1. 剩余空间检测
SPACE=$(df -h / | awk 'NR==2{print $4}')
if [ "$(df / | awk 'NR==2{print $4}')" -lt 512000 ]; then
  err "SD卡空间不足 (<500MB)，请更换更大容量卡或清理空间。"
  exit 1
fi

# 2. 网络连通性自愈+源自适应
try_count=0
while true; do
  ping -c 1 www.baidu.com >/dev/null 2>&1 && log "网络正常" && break
  warn "网络不可用，切换国内源..."
  if [ $try_count -eq 0 ]; then
    sudo sed -i 's|http://raspbian.raspberrypi.org|http://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list || true
    sudo sed -i 's|http://archive.raspberrypi.org|http://mirrors.tuna.tsinghua.edu.cn/raspberrypi|g' /etc/apt/sources.list.d/raspi.list || true
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple || true
  fi
  try_count=$((try_count+1))
  sleep 2
done

# 3. systemd 目录自愈
while true; do
  [ -d "/etc/systemd/system" ] && log "systemd 目录已存在" && break
  warn "systemd 目录缺失，自动修复..."
  sudo mkdir -p /etc/systemd/system || true
  sleep 2
done

# 4. 目标目录自愈
while true; do
  [ -d "$TARGET_DIR" ] && log "目标目录已存在" && break
  warn "目标目录缺失，自动修复..."
  sudo mkdir -p "$TARGET_DIR" || true
  sleep 2
done

# 5. 拷贝项目文件自愈
while true; do
  sudo cp -r ./* "$TARGET_DIR" 2>/dev/null || true
  sudo chown -R pi:pi "$TARGET_DIR" || true
  [ -f "$TARGET_DIR/$SERVICE_FILE" ] && log "项目文件已拷贝" && break
  warn "项目文件拷贝失败，重试..."
  sleep 2
done

# 6. apt/pip 损坏修复
sudo dpkg --configure -a || true
sudo apt --fix-broken install -y || true

# 7. Python3 版本自愈
while true; do
  if command -v python3 >/dev/null; then
    PYV=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    awk "BEGIN{exit !($PYV >= $PYTHON_MIN_VERSION)}" && log "python3 版本满足要求 ($PYV)" && break
    warn "python3 版本过低，自动升级..."
    sudo apt update && sudo apt install -y python3 || true
  else
    warn "python3 缺失，自动安装..."
    sudo apt update && sudo apt install -y python3 || true
  fi
  sleep 2
done

# 8. pip3 自愈
while true; do
  command -v pip3 >/dev/null && log "pip3 已安装" && break
  warn "pip3 缺失，自动安装..."
  sudo apt install -y python3-pip || true
  sleep 2
done

# 9. 虚拟环境自愈
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR" || true
fi
source "$VENV_DIR/bin/activate" || true

# 10. requirements.txt 依赖完整性自愈
if [ ! -s "$TARGET_DIR/$REQUIREMENTS" ]; then
  warn "requirements.txt 缺失或为空，自动生成..."
  echo -e "flask\nrequests" > "$TARGET_DIR/$REQUIREMENTS"
fi

# 11. 依赖安装自愈
while true; do
  pip install --upgrade pip setuptools wheel || true
  pip install -r "$TARGET_DIR/$REQUIREMENTS" && log "依赖安装成功" && break
  warn "依赖安装失败，重试..."
  sleep 2
done

# 12. 端口占用检测自愈
if lsof -i:$WEB_PORT | grep LISTEN; then
  warn "端口 $WEB_PORT 被占用，自动释放..."
  fuser -k $WEB_PORT/tcp || true
fi

# 13. 关键目录自愈
for d in "$ROM_DIR" "$CHEAT_DIR" "$SAVE_DIR"; do
  [ -d "$d" ] || sudo mkdir -p "$d"
  sudo chown -R pi:pi "$d"
  sudo chmod -R 755 "$d"
done

# 14. systemd 服务自愈+健康检测
while true; do
  sudo cp "$TARGET_DIR/$SERVICE_FILE" /etc/systemd/system/ || true
  sudo systemctl daemon-reload || true
  sudo systemctl enable $SERVICE_FILE || true
  sudo systemctl restart $SERVICE_FILE || true
  sleep 2
  sudo systemctl is-active --quiet $SERVICE_FILE && log "systemd 服务已部署并运行" && break
  warn "systemd 服务启动失败，输出日志快照..."
  sudo journalctl -u $SERVICE_FILE --no-pager | tail -20 > "$LOG_DIR/${SERVICE_FILE}.err.log"
  sleep 2
done

# 15. 关键文件/目录权限自愈
sudo chown -R pi:pi "$TARGET_DIR" || true
sudo chmod -R 755 "$TARGET_DIR" || true

# 16. 关键脚本/服务自启动校验
for script in auto_save_sync.py web_config.py; do
  if [ -f "$TARGET_DIR/$script" ]; then
    grep -q "$script" /etc/rc.local 2>/dev/null || sudo bash -c "echo 'python3 $TARGET_DIR/$script &' >> /etc/rc.local"
  fi
done

# 17. 模拟器健康检测与自愈
if ! command -v emulationstation >/dev/null; then
  warn "EmulationStation 未安装，自动安装..."
  sudo apt update && sudo apt install -y emulationstation || true
fi
if ! emulationstation --version >/dev/null 2>&1; then
  warn "EmulationStation 启动异常，自动重装..."
  sudo apt install --reinstall -y emulationstation || true
fi

# 18. 日志上传/本地Web展示（本地方案）
# 可选：将 $LOG_DIR/*.log 通过 web_config.py 提供下载/查看接口

# 19. Web 配置引导二维码
if command -v qrencode >/dev/null; then
  IP=$(hostname -I | awk '{print $1}')
  URL="http://$IP:$WEB_PORT"
  qrencode -o "$LOG_DIR/web_config_qr.png" "$URL"
  log "Web 配置二维码已生成: $LOG_DIR/web_config_qr.png"
fi

# 20. 自动重启机制（多次自愈失败自动重启）
if [ ! -f "$REBOOT_COUNT_FILE" ]; then echo 0 > "$REBOOT_COUNT_FILE"; fi
REBOOT_COUNT=$(cat "$REBOOT_COUNT_FILE")
if [ "$REBOOT_COUNT" -lt "$MAX_REBOOT" ]; then
  if grep -q "ERR" "$LOG_DIR/${SERVICE_FILE}.err.log" 2>/dev/null; then
    warn "多次自愈失败，自动重启树莓派..."
    echo $((REBOOT_COUNT+1)) > "$REBOOT_COUNT_FILE"
    sudo reboot
  fi
fi

log "全部自动化步骤已完成，系统极致稳健、零人工干预，已准备就绪。" 