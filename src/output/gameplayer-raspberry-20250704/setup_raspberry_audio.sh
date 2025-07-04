#!/bin/bash
# 树莓派音频配置脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "🔊 树莓派音频系统配置"
echo "======================"

# 检查是否为树莓派
check_raspberry_pi() {
    log_info "检查设备类型..."
    
    if [ -f /proc/device-tree/model ]; then
        MODEL=$(cat /proc/device-tree/model)
        if [[ $MODEL == *"Raspberry Pi"* ]]; then
            log_success "✅ 检测到树莓派设备: $MODEL"
            return 0
        fi
    fi
    
    log_warning "⚠️ 未检测到树莓派设备，将使用通用配置"
    return 1
}

# 更新系统
update_system() {
    log_info "更新系统包..."
    
    sudo apt-get update >/dev/null 2>&1
    sudo apt-get upgrade -y >/dev/null 2>&1
    
    log_success "✅ 系统更新完成"
}

# 安装音频相关包
install_audio_packages() {
    log_info "安装音频相关包..."
    
    local packages=(
        "alsa-utils"
        "pulseaudio"
        "pulseaudio-module-bluetooth"
        "bluez"
        "bluez-tools"
        "sox"
        "libsox-fmt-all"
        "mpg123"
        "vorbis-tools"
        "python3-pygame"
        "python3-pyaudio"
    )
    
    for package in "${packages[@]}"; do
        log_info "安装 $package..."
        sudo apt-get install -y "$package" >/dev/null 2>&1 || {
            log_warning "⚠️ 安装 $package 失败，跳过"
        }
    done
    
    log_success "✅ 音频包安装完成"
}

# 配置ALSA
configure_alsa() {
    log_info "配置ALSA音频系统..."
    
    # 创建ALSA配置文件
    sudo tee /etc/asound.conf > /dev/null << 'EOF'
# ALSA configuration for GamePlayer-Raspberry

pcm.!default {
    type pulse
    fallback "sysdefault"
    hint {
        show on
        description "Default ALSA Output (currently PulseAudio Sound Server)"
    }
}

ctl.!default {
    type pulse
    fallback "sysdefault"
}

# Hardware specific configuration
pcm.hw0 {
    type hw
    card 0
    device 0
}

pcm.hdmi {
    type hw
    card 0
    device 1
}

# Software mixing
pcm.dmixer {
    type dmix
    ipc_key 1024
    slave {
        pcm "hw:0,0"
        period_time 0
        period_size 1024
        buffer_size 4096
        rate 44100
    }
    bindings {
        0 0
        1 1
    }
}
EOF
    
    log_success "✅ ALSA配置完成"
}

# 配置PulseAudio
configure_pulseaudio() {
    log_info "配置PulseAudio..."
    
    # 创建PulseAudio配置目录
    mkdir -p ~/.config/pulse
    
    # 配置PulseAudio
    cat > ~/.config/pulse/default.pa << 'EOF'
#!/usr/bin/pulseaudio -nF

# Load audio drivers
load-module module-alsa-sink device=hw:0,0
load-module module-alsa-sink device=hw:0,1
load-module module-alsa-source device=hw:0,0

# Load bluetooth modules
load-module module-bluetooth-policy
load-module module-bluetooth-discover

# Load other modules
load-module module-native-protocol-unix
load-module module-default-device-restore
load-module module-rescue-streams
load-module module-always-sink
load-module module-intended-roles
load-module module-suspend-on-idle

# Set default sink
set-default-sink alsa_output.0.analog-stereo
EOF
    
    # 重启PulseAudio
    pulseaudio -k 2>/dev/null || true
    sleep 2
    pulseaudio --start 2>/dev/null || true
    
    log_success "✅ PulseAudio配置完成"
}

# 配置树莓派音频输出
configure_raspberry_audio() {
    log_info "配置树莓派音频输出..."
    
    # 强制HDMI音频输出
    if [ -f /boot/config.txt ]; then
        sudo cp /boot/config.txt /boot/config.txt.backup
        
        # 添加音频配置
        sudo tee -a /boot/config.txt > /dev/null << 'EOF'

# Audio configuration for GamePlayer-Raspberry
hdmi_drive=2
hdmi_force_hotplug=1
config_hdmi_boost=4

# Force audio output
dtparam=audio=on
audio_pwm_mode=2
EOF
        
        log_success "✅ 树莓派音频配置完成"
    else
        log_warning "⚠️ 未找到 /boot/config.txt，跳过树莓派特定配置"
    fi
}

# 配置蓝牙音频
configure_bluetooth_audio() {
    log_info "配置蓝牙音频..."
    
    # 启用蓝牙服务
    sudo systemctl enable bluetooth
    sudo systemctl start bluetooth
    
    # 配置蓝牙音频
    sudo tee /etc/bluetooth/main.conf > /dev/null << 'EOF'
[General]
Class = 0x000100
DiscoverableTimeout = 0
PairableTimeout = 0
AutoConnectTimeout = 60

[Policy]
AutoEnable=true
EOF
    
    # 重启蓝牙服务
    sudo systemctl restart bluetooth
    
    log_success "✅ 蓝牙音频配置完成"
}

# 测试音频输出
test_audio() {
    log_info "测试音频输出..."
    
    # 测试ALSA
    if command -v speaker-test >/dev/null 2>&1; then
        log_info "测试ALSA音频输出..."
        timeout 3 speaker-test -t sine -f 1000 -l 1 >/dev/null 2>&1 && {
            log_success "✅ ALSA音频测试成功"
        } || {
            log_warning "⚠️ ALSA音频测试失败"
        }
    fi
    
    # 测试PulseAudio
    if command -v pactl >/dev/null 2>&1; then
        log_info "测试PulseAudio..."
        pactl info >/dev/null 2>&1 && {
            log_success "✅ PulseAudio运行正常"
        } || {
            log_warning "⚠️ PulseAudio未运行"
        }
    fi
    
    # 生成测试音频文件
    if command -v sox >/dev/null 2>&1; then
        log_info "生成测试音频..."
        sox -n -r 44100 -c 2 /tmp/test_audio.wav synth 1 sine 440 vol 0.5 2>/dev/null && {
            log_success "✅ 测试音频文件生成成功"
            
            # 播放测试音频
            if command -v aplay >/dev/null 2>&1; then
                log_info "播放测试音频..."
                aplay /tmp/test_audio.wav >/dev/null 2>&1 && {
                    log_success "✅ 音频播放测试成功"
                } || {
                    log_warning "⚠️ 音频播放测试失败"
                }
            fi
            
            # 清理测试文件
            rm -f /tmp/test_audio.wav
        }
    fi
}

# 创建音频管理脚本
create_audio_scripts() {
    log_info "创建音频管理脚本..."
    
    # 创建音频切换脚本
    sudo tee /usr/local/bin/audio-switch > /dev/null << 'EOF'
#!/bin/bash
# 音频输出切换脚本

case "$1" in
    hdmi)
        amixer cset numid=3 2
        echo "音频输出切换到HDMI"
        ;;
    headphone)
        amixer cset numid=3 1
        echo "音频输出切换到耳机"
        ;;
    auto)
        amixer cset numid=3 0
        echo "音频输出设置为自动"
        ;;
    *)
        echo "用法: $0 {hdmi|headphone|auto}"
        exit 1
        ;;
esac
EOF
    
    sudo chmod +x /usr/local/bin/audio-switch
    
    # 创建音频测试脚本
    sudo tee /usr/local/bin/audio-test > /dev/null << 'EOF'
#!/bin/bash
# 音频测试脚本

echo "🔊 音频系统测试"
echo "==============="

# 测试ALSA
echo "测试ALSA..."
speaker-test -t sine -f 1000 -l 1 -s 1

# 测试音量
echo "当前音量设置:"
amixer get PCM

# 测试音频设备
echo "可用音频设备:"
aplay -l

echo "测试完成"
EOF
    
    sudo chmod +x /usr/local/bin/audio-test
    
    log_success "✅ 音频管理脚本创建完成"
}

# 设置音频权限
setup_audio_permissions() {
    log_info "设置音频权限..."
    
    # 添加用户到音频组
    sudo usermod -a -G audio $USER
    sudo usermod -a -G pulse-access $USER
    
    # 设置设备权限
    sudo tee /etc/udev/rules.d/99-audio-permissions.rules > /dev/null << 'EOF'
# Audio device permissions for GamePlayer-Raspberry
SUBSYSTEM=="sound", GROUP="audio", MODE="0664"
KERNEL=="controlC[0-9]*", GROUP="audio", MODE="0664"
EOF
    
    # 重新加载udev规则
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    
    log_success "✅ 音频权限设置完成"
}

# 主函数
main() {
    log_info "开始配置树莓派音频系统..."
    
    check_raspberry_pi
    update_system
    install_audio_packages
    configure_alsa
    configure_pulseaudio
    configure_raspberry_audio
    configure_bluetooth_audio
    setup_audio_permissions
    create_audio_scripts
    test_audio
    
    echo ""
    log_success "🎉 树莓派音频系统配置完成！"
    echo ""
    echo "📋 使用说明:"
    echo "  • 切换音频输出: sudo audio-switch {hdmi|headphone|auto}"
    echo "  • 测试音频: sudo audio-test"
    echo "  • 调节音量: alsamixer"
    echo "  • 查看音频设备: aplay -l"
    echo ""
    echo "🔄 建议重启系统以确保所有配置生效"
}

# 执行主函数
main "$@"
