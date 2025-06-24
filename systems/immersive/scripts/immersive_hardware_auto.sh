#!/bin/bash

# immersive_hardware_auto.sh
# 一键自动化配置沉浸式物理外设与环境交互（RetroPie/树莓派）
# 包含：街机控制器校准、Sinden光枪/Wii体感、灯光同步、震动反馈
# 日志：immersive_hardware_auto.log

LOGFILE="immersive_hardware_auto.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOGFILE"
}

set -e

log "=== 沉浸式外设与环境交互自动化配置开始 ==="

# 1. 街机控制器校准
log "[1/4] 街机控制器校准与映射"
sudo apt update
sudo apt install -y joystick jstest-gtk
for DEV in /dev/input/js*; do
    if [ -e "$DEV" ]; then
        log "正在校准 $DEV"
        jstest-gtk "$DEV" &
    fi
done
log "请在弹出的jstest-gtk窗口中完成校准，校准后关闭窗口。"

# 2. Sinden光枪与Wii体感自动配对
log "[2/4] Sinden光枪与Wii体感自动配对"
# Sinden Lightgun
if lsusb | grep -i 'Sinden'; then
    log "检测到Sinden Lightgun，自动下载并安装配置工具。"
    wget -O SindenLightgunSoftware.zip https://www.sindenlightgun.com/software/SindenLightgunSoftware.zip
    unzip -o SindenLightgunSoftware.zip -d sinden
    cd sinden
    sudo ./install.sh || true
    ./SindenLightgunConfigTool &
    cd ..
    log "Sinden Lightgun配置工具已启动，请根据界面完成摄像头校准。"
else
    log "未检测到Sinden Lightgun，跳过光枪配置。"
fi
# Wii体感
sudo apt install -y wminput
sudo systemctl enable bluetooth
sudo systemctl start bluetooth
if hcitool dev | grep -q hci; then
    log "蓝牙适配器已就绪，自动启动Wii手柄配对。"
    sudo pkill wminput || true
    sudo wminput &
    log "请按住Wii手柄1+2键进入配对模式。"
else
    log "未检测到蓝牙适配器，跳过Wii体感。"
fi

# 3. 灯光同步系统（GPIO控制WS2812B）
log "[3/4] 灯光同步系统自动配置"
sudo apt install -y python3-pip
pip3 install --upgrade rpi_ws281x adafruit-circuitpython-neopixel
cat > game_lights.py <<'EOF'
import board
import neopixel
import time

pixels = neopixel.NeoPixel(board.D18, 30)  # 30灯，GPIO18

def flash_red(times=3):
    for _ in range(times):
        pixels.fill((255, 0, 0))
        time.sleep(0.2)
        pixels.fill((0, 0, 0))
        time.sleep(0.2)

# 示例：受伤事件
flash_red()
EOF
log "已生成灯光控制脚本 game_lights.py，可通过 'python3 game_lights.py' 触发红光闪烁。"

# 4. 震动反馈引擎（外接震动电机）
log "[4/4] 震动反馈引擎自动配置"
pip3 install --upgrade numpy sounddevice RPi.GPIO
cat > vibration_engine.py <<'EOF'
import sounddevice as sd
import numpy as np
import RPi.GPIO as GPIO
import time

VIB_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(VIB_PIN, GPIO.OUT)

def trigger_vibration(duration=0.3):
    GPIO.output(VIB_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(VIB_PIN, GPIO.LOW)

def audio_callback(indata, frames, time_info, status):
    volume_norm = np.linalg.norm(indata) * 10
    if volume_norm > 2.5:  # 爆炸等大音量阈值
        trigger_vibration()

with sd.InputStream(callback=audio_callback):
    while True:
        time.sleep(0.1)
EOF
log "已生成震动反馈脚本 vibration_engine.py，可通过 'python3 vibration_engine.py &' 后台运行。"

log "=== 沉浸式外设与环境交互自动化配置完成 ==="
echo "如遇异常，日志见 $LOGFILE"
echo "如需自定义灯光/震动事件，请编辑 game_lights.py 和 vibration_engine.py" 