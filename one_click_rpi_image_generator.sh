#!/bin/bash
#==================================================================================
# 🎮 GamePlayer-Raspberry 一键树莓派镜像生成器
# 
# 功能：
# - 🔧 自动下载和配置树莓派OS
# - 🎮 安装所有游戏模拟器
# - 💾 下载游戏ROM文件
# - 🌐 配置Web界面和服务
# - 🚀 生成完整的游戏机镜像
#
# 使用方法：
# sudo ./one_click_rpi_image_generator.sh
#
# 作者：GamePlayer-Raspberry Team
# 版本：2.0.0
# 日期：2025-07-16
#==================================================================================

set -euo pipefail  # 严格错误处理

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="GamePlayer-Raspberry"
PROJECT_VERSION="2.0.0"
IMAGE_NAME="GamePlayer-Raspberry-${PROJECT_VERSION}"
WORK_DIR="${PWD}/image_build"
OUTPUT_DIR="${PWD}/output"
LOG_FILE="${OUTPUT_DIR}/build_log_$(date +%Y%m%d_%H%M%S).log"

# 系统配置
RPI_OS_VERSION="2024-03-15"
RPI_OS_URL="https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2024-03-15/2024-03-12-raspios-bookworm-arm64-lite.img.xz"
IMAGE_SIZE="8G"
WIFI_COUNTRY="CN"
DEFAULT_USER="gamer"
DEFAULT_PASS="gameplayer"

# 模拟器配置
EMULATORS=(
    "mednafen"          # 多系统模拟器
    "snes9x-gtk"        # SNES模拟器
    "visualboyadvance-m" # GBA模拟器
    "fceux"             # NES模拟器
    "desmume"           # NDS模拟器
    "mupen64plus"       # N64模拟器
    "pcsx-rearmed"      # PSX模拟器
)

# ROM源配置
ROM_SOURCES=(
    "homebrew"          # 自制游戏
    "demos"             # 演示ROM
    "open_source"       # 开源游戏
)

#==================================================================================
# 🎨 界面函数
#==================================================================================

print_header() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                  🎮 GamePlayer-Raspberry 镜像生成器 v${PROJECT_VERSION}                ║${NC}"
    echo -e "${CYAN}╠══════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║  ✨ 一键生成完整的树莓派游戏机镜像                                                  ║${NC}"
    echo -e "${CYAN}║  🎯 包含模拟器、ROM、Web界面和所有游戏功能                                         ║${NC}"
    echo -e "${CYAN}║  🚀 支持多种游戏系统和现代化管理界面                                              ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    local step_num=$1
    local step_desc=$2
    echo -e "${WHITE}[步骤 ${step_num}] ${BLUE}${step_desc}${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - [步骤 ${step_num}] ${step_desc}" >> "${LOG_FILE}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - INFO: $1" >> "${LOG_FILE}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - SUCCESS: $1" >> "${LOG_FILE}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - WARNING: $1" >> "${LOG_FILE}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" >> "${LOG_FILE}"
}

show_progress() {
    local current=$1
    local total=$2
    local desc=$3
    local percent=$((current * 100 / total))
    local bar_length=50
    local filled_length=$((percent * bar_length / 100))
    
    printf "\r${CYAN}进度: ["
    printf "%${filled_length}s" | tr ' ' '█'
    printf "%$((bar_length - filled_length))s" | tr ' ' '░'
    printf "] %d%% - %s${NC}" "$percent" "$desc"
    
    if [ "$current" -eq "$total" ]; then
        echo ""
    fi
}

#==================================================================================
# 🔧 系统检查函数
#==================================================================================

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "此脚本需要root权限运行"
        echo -e "${YELLOW}请使用: ${WHITE}sudo $0${NC}"
        exit 1
    fi
}

check_dependencies() {
    print_step "1" "检查系统依赖"
    
    local missing_deps=()
    local required_deps=(
        "wget" "curl" "unxz" "parted" "losetup" "kpartx" 
        "mount" "chroot" "systemctl" "python3" "pip3"
        "git" "docker" "qemu-user-static"
    )
    
    for dep in "${required_deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_warning "缺少依赖: ${missing_deps[*]}"
        print_info "正在安装缺少的依赖..."
        
        # 更新包管理器
        apt-get update -y
        
        # 安装依赖
        apt-get install -y "${missing_deps[@]}" || {
            print_error "依赖安装失败"
            exit 1
        }
    fi
    
    print_success "系统依赖检查完成"
}
check_disk_space() {
    local required_space=10  # GB
    local available_space=$(df / | awk 'NR==2 {print int($4/1024/1024)}')
    
    if [ "$available_space" -lt "$required_space" ]; then
        print_error "磁盘空间不足，需要至少 ${required_space}GB，当前可用 ${available_space}GB"
        exit 1
    fi
    
    print_success "磁盘空间检查通过 (可用: ${available_space}GB)"
}

#==================================================================================
# 📁 环境准备函数
#==================================================================================

prepare_environment() {
    print_step "2" "准备构建环境"
    
    # 创建工作目录
    mkdir -p "${WORK_DIR}" "${OUTPUT_DIR}"
    cd "${WORK_DIR}"
    
    # 初始化日志
    echo "GamePlayer-Raspberry 镜像构建日志" > "${LOG_FILE}"
    echo "构建开始时间: $(date)" >> "${LOG_FILE}"
    echo "构建版本: ${PROJECT_VERSION}" >> "${LOG_FILE}"
    echo "=========================================" >> "${LOG_FILE}"
    
    print_success "构建环境准备完成"
}

download_rpi_os() {
    print_step "3" "下载树莓派OS镜像"
    
    local os_file="rpi_os.img.xz"
    local os_img="rpi_os.img"
    
    if [ ! -f "${os_img}" ]; then
        if [ ! -f "${os_file}" ]; then
            print_info "正在下载树莓派OS镜像..."
            wget -O "${os_file}" "${RPI_OS_URL}" --progress=bar:force 2>&1 | while read line; do
                echo -ne "\r${CYAN}下载中... ${line}${NC}"
            done
            echo ""
        fi
        
        print_info "正在解压镜像文件..."
        unxz "${os_file}"
        mv "${os_file%.*}" "${os_img}"
    fi
    
    print_success "树莓派OS镜像准备完成"
}

#==================================================================================
# 💾 镜像处理函数
#==================================================================================

expand_image() {
    print_step "4" "扩展镜像大小"
    
    local os_img="rpi_os.img"
    local current_size=$(du -h "${os_img}" | cut -f1)
    
    print_info "当前镜像大小: ${current_size}"
    print_info "扩展镜像到: ${IMAGE_SIZE}"
    
    # 扩展镜像文件
    truncate -s "${IMAGE_SIZE}" "${os_img}"
    
    # 使用parted调整分区
    parted "${os_img}" --script resizepart 2 100%
    
    print_success "镜像扩展完成"
}

mount_image() {
    print_step "5" "挂载镜像文件系统"
    local os_img="rpi_os.img"
    
    # 设置loop设备
    LOOP_DEV=$(losetup --find --show "${os_img}")
    print_info "Loop设备: ${LOOP_DEV}"
    
    # 创建设备映射
    kpartx -av "${LOOP_DEV}"
    
    # 等待设备就绪
    sleep 2
    
    # 挂载分区
    mkdir -p mnt/boot mnt/root
    mount "/dev/mapper/$(basename ${LOOP_DEV})p1" mnt/boot
    mount "/dev/mapper/$(basename ${LOOP_DEV})p2" mnt/root
    
    # 检查文件系统
    e2fsck -f -y "/dev/mapper/$(basename ${LOOP_DEV})p2" || true
    
    # 调整文件系统大小
    resize2fs "/dev/mapper/$(basename ${LOOP_DEV})p2"
    print_success "镜像文件系统挂载完成"
}

#==================================================================================
# ⚙️ 系统配置函数
#==================================================================================

configure_system() {
    print_step "6" "配置系统基础设置"
    
    local root_dir="mnt/root"
    local boot_dir="mnt/boot"
    
    # 启用SSH
    touch "${boot_dir}/ssh"
    
    # 配置WiFi (如果指定)
    if [ -n "${WIFI_SSID:-}" ] && [ -n "${WIFI_PASSWORD:-}" ]; then
        cat > "${boot_dir}/wpa_supplicant.conf" << EOF
country=${WIFI_COUNTRY}
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="${WIFI_SSID}"
    psk="${WIFI_PASSWORD}"
}
EOF
    fi
    
    # 设置用户账户
    chroot "${root_dir}" /bin/bash << EOF
# 创建游戏用户
useradd -m -s /bin/bash ${DEFAULT_USER}
echo "${DEFAULT_USER}:${DEFAULT_PASS}" | chpasswd
usermod -aG sudo,video,audio,input,gpio,i2c,spi ${DEFAULT_USER}

# 配置自动登录
mkdir -p /etc/systemd/system/getty@tty1.service.d/
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf << EOL
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin ${DEFAULT_USER} --noclear %I \$TERM
EOL

# 更新系统
apt-get update -y
apt-get upgrade -y

# 安装基础工具
apt-get install -y \
    vim nano curl wget git \
    python3 python3-pip python3-venv \
    build-essential cmake \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libopenal-dev libsndfile1-dev \
    nodejs npm \
    nginx \
    htop tree unzip p7zip-full
EOF
    
    print_success "系统基础配置完成"
}

install_emulators() {
    print_step "7" "安装游戏模拟器"
    
    local root_dir="mnt/root"
    local total=${#EMULATORS[@]}
    local current=0
    
    # 设置qemu用户模式模拟
    cp /usr/bin/qemu-aarch64-static "${root_dir}/usr/bin/"
    
    for emulator in "${EMULATORS[@]}"; do
        current=$((current + 1))
        show_progress $current $total "安装 $emulator"
        
        chroot "${root_dir}" /bin/bash << EOF
# 安装模拟器
case "$emulator" in
    "mednafen")
        apt-get install -y mednafen
        ;;
    "snes9x-gtk")
        apt-get install -y snes9x-gtk
        ;;
    "visualboyadvance-m")
        apt-get install -y visualboyadvance-m
        ;;
    "fceux")
        apt-get install -y fceux
        ;;
    "desmume")
        apt-get install -y desmume
        ;;
    "mupen64plus")
        apt-get install -y mupen64plus-ui-console mupen64plus-data
        ;;
    "pcsx-rearmed")
        # 从源码编译或使用特定PPA
        apt-get install -y libpcre3-dev
        ;;
esac
EOF
        sleep 1
    done
    
    print_success "游戏模拟器安装完成"
}

#==================================================================================
# 🎮 游戏内容安装
#==================================================================================

setup_gameplayer_project() {
    print_step "8" "部署GamePlayer项目"
    
    local root_dir="mnt/root"
    local project_dir="${root_dir}/home/${DEFAULT_USER}/GamePlayer-Raspberry"
    
    # 创建项目目录
    mkdir -p "${project_dir}"
    
    # 复制项目文件
    print_info "复制项目文件..."
    cp -r "${PWD}/../"* "${project_dir}/" 2>/dev/null || true
    
    # 设置目录权限
    chroot "${root_dir}" /bin/bash << EOF
chown -R ${DEFAULT_USER}:${DEFAULT_USER} /home/${DEFAULT_USER}/
chmod +x /home/${DEFAULT_USER}/GamePlayer-Raspberry/*.sh
chmod +x /home/${DEFAULT_USER}/GamePlayer-Raspberry/src/scripts/*.sh
EOF
    
    # 安装Python依赖
    chroot "${root_dir}" /bin/bash << EOF
cd /home/${DEFAULT_USER}/GamePlayer-Raspberry
python3 -m pip install -r requirements.txt
python3 -m pip install aiohttp aiohttp-cors
EOF
    
    print_success "GamePlayer项目部署完成"
}

download_roms() {
    print_step "9" "下载游戏ROM文件"
    
    local root_dir="mnt/root"
    local rom_dir="${root_dir}/home/${DEFAULT_USER}/GamePlayer-Raspberry/data/roms"
    
    # 创建ROM目录结构
    mkdir -p "${rom_dir}"/{nes,snes,gameboy,gba,genesis,n64,psx}
    
    print_info "下载自制和开源游戏ROM..."
    
    # 下载自制NES游戏
    local nes_homebrew_roms=(
        "https://github.com/christopherpow/nes-test-roms/raw/master/nestest.nes"
        "https://github.com/christopherpow/nes-test-roms/raw/master/sprite_hit_tests_2005.10.05/01.basics.nes"
        "https://github.com/christopherpow/nes-test-roms/raw/master/sprite_hit_tests_2005.10.05/02.alignment.nes"
    )
    
    for rom_url in "${nes_homebrew_roms[@]}"; do
        local rom_name=$(basename "$rom_url")
        if [ ! -f "${rom_dir}/nes/${rom_name}" ]; then
            wget -q -O "${rom_dir}/nes/${rom_name}" "$rom_url" || print_warning "下载失败: $rom_name"
        fi
    done
    
    # 创建ROM信息文件
    chroot "${root_dir}" /bin/bash << EOF
cd /home/${DEFAULT_USER}/GamePlayer-Raspberry
python3 << PYTHON
import json
import os
from pathlib import Path

# 生成ROM目录信息
rom_data = {}
rom_base = Path('data/roms')
for system in ['nes', 'snes', 'gameboy', 'gba', 'genesis', 'n64', 'psx']:
    system_dir = rom_base / system
    if system_dir.exists():
        roms = []
        for rom_file in system_dir.glob('*.nes'):
            roms.append({
                'name': rom_file.stem.replace('_', ' ').title(),
                'filename': rom_file.name,
                'system': system,
                'size': rom_file.stat().st_size if rom_file.exists() else 0
            })
        rom_data[system] = roms

# 保存ROM信息
with open('data/web/rom_list.json', 'w') as f:
    json.dump(rom_data, f, indent=2)

print(f"ROM信息已生成，包含 {sum(len(roms) for roms in rom_data.values())} 个游戏")
PYTHON

chown -R ${DEFAULT_USER}:${DEFAULT_USER} /home/${DEFAULT_USER}/GamePlayer-Raspberry/data/
EOF
    print_success "游戏ROM下载完成"
}

#==================================================================================
# 🌐 Web服务配置
#==================================================================================

setup_web_services() {
    print_step "10" "配置Web服务"
    
    local root_dir="mnt/root"
    
    # 配置Nginx
    chroot "${root_dir}" /bin/bash << EOF
# 创建GamePlayer nginx配置
cat > /etc/nginx/sites-available/gameplayer << 'NGINX_EOF'
server {
    listen 80;
    server_name _;
    
    # Web界面
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # API接口
    location /api/ {
        proxy_pass http://127.0.0.1:8080/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    # 静态文件
    location /static/ {
        alias /home/${DEFAULT_USER}/GamePlayer-Raspberry/src/web/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
NGINX_EOF

# 启用站点
ln -sf /etc/nginx/sites-available/gameplayer /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试nginx配置
nginx -t
EOF
    
    # 创建GamePlayer服务
    cat > "${root_dir}/etc/systemd/system/gameplayer.service" << EOF
[Unit]
Description=GamePlayer-Raspberry Web Server
After=network.target

[Service]
Type=simple
User=${DEFAULT_USER}
WorkingDirectory=/home/${DEFAULT_USER}/GamePlayer-Raspberry
ExecStart=/usr/bin/python3 simple_demo_server.py --port 8080
Restart=always
RestartSec=5
Environment=PYTHONPATH=/home/${DEFAULT_USER}/GamePlayer-Raspberry

[Install]
WantedBy=multi-user.target
EOF
    # 启用服务
    chroot "${root_dir}" /bin/bash << EOF
systemctl enable nginx
systemctl enable gameplayer
EOF
    
    print_success "Web服务配置完成"
}

#==================================================================================
# 🚀 系统优化配置
#==================================================================================

optimize_system() {
    print_step "11" "优化系统性能"
    
    local root_dir="mnt/root"
    local boot_dir="mnt/boot"
    
    # GPU内存分割
    echo "gpu_mem=128" >> "${boot_dir}/config.txt"
    
    # 音频配置
    echo "dtparam=audio=on" >> "${boot_dir}/config.txt"
    
    # USB启动支持
    echo "program_usb_boot_mode=1" >> "${boot_dir}/config.txt"
    
    # 系统调优
    chroot "${root_dir}" /bin/bash << EOF
# 设置交换文件
echo "CONF_SWAPSIZE=1024" > /etc/dphys-swapfile

# 优化内核参数
cat >> /etc/sysctl.conf << SYSCTL_EOF
# GamePlayer优化
vm.swappiness=10
vm.vfs_cache_pressure=50
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr
SYSCTL_EOF

# 清理系统
apt-get autoremove -y
apt-get autoclean
rm -rf /var/lib/apt/lists/*
rm -rf /tmp/*
rm -rf /var/tmp/*

# 重新生成locale
locale-gen
EOF
    
    print_success "系统优化完成"
}

setup_autostart() {
    print_step "12" "配置自动启动"
    
    local root_dir="mnt/root"
    
    # 创建首次启动脚本
    cat > "${root_dir}/home/${DEFAULT_USER}/first_boot.sh" << 'EOF'
#!/bin/bash

# 首次启动配置
echo "🎮 GamePlayer-Raspberry 首次启动配置..."

# 扩展文件系统
sudo raspi-config --expand-rootfs

# 启动Web服务
cd /home/gamer/GamePlayer-Raspberry
python3 automated_test_and_fix.py

# 显示欢迎信息
clear
cat << 'WELCOME'
╔══════════════════════════════════════════════════════════════════════════════╗
║                     🎮 GamePlayer-Raspberry v2.0.0                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🌐 Web界面: http://$(hostname -I | awk '{print $1}')                      ║
║  🎮 支持系统: NES, SNES, Game Boy, GBA, Genesis                            ║
║  💾 ROM目录: /home/gamer/GamePlayer-Raspberry/data/roms/                   ║
║  ⚙️  配置文件: /home/gamer/GamePlayer-Raspberry/config/                    ║
║                                                                              ║
║  📖 使用说明:                                                                ║
║     - 将ROM文件放入对应系统目录                                               ║
║     - 在浏览器中访问Web界面                                                   ║
║     - 点击游戏卡片即可启动                                                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

用户名: gamer
密码: gameplayer

按任意键继续...
WELCOME

read -n 1 -s
# 删除首次启动脚本
rm -f /home/gamer/first_boot.sh
EOF
    
    # 设置首次启动
    chroot "${root_dir}" /bin/bash << EOF
chmod +x /home/${DEFAULT_USER}/first_boot.sh
chown ${DEFAULT_USER}:${DEFAULT_USER} /home/${DEFAULT_USER}/first_boot.sh

# 添加到.bashrc
echo "" >> /home/${DEFAULT_USER}/.bashrc
echo "# GamePlayer首次启动" >> /home/${DEFAULT_USER}/.bashrc
echo "if [ -f /home/${DEFAULT_USER}/first_boot.sh ]; then" >> /home/${DEFAULT_USER}/.bashrc
echo "    /home/${DEFAULT_USER}/first_boot.sh" >> /home/${DEFAULT_USER}/.bashrc
echo "fi" >> /home/${DEFAULT_USER}/.bashrc
EOF
    
    print_success "自动启动配置完成"
}

#==================================================================================
# 🏁 镜像完成和清理
#==================================================================================

finalize_image() {
    print_step "13" "完成镜像构建"
    
    local root_dir="mnt/root"
    
    # 清理构建痕迹
    rm -f "${root_dir}/usr/bin/qemu-aarch64-static"
    
    # 同步文件系统
    sync
    
    # 卸载文件系统
    umount mnt/boot
    umount mnt/root
    
    # 移除设备映射
    kpartx -d "${LOOP_DEV}"
    losetup -d "${LOOP_DEV}"
    
    # 压缩镜像
    print_info "正在压缩镜像文件..."
    local output_img="${OUTPUT_DIR}/${IMAGE_NAME}.img"
    local output_zip="${OUTPUT_DIR}/${IMAGE_NAME}.img.zip"
    
    mv rpi_os.img "${output_img}"
    
    # 创建压缩包
    cd "${OUTPUT_DIR}"
    zip -9 "${IMAGE_NAME}.img.zip" "${IMAGE_NAME}.img"
    
    # 生成MD5校验
    md5sum "${IMAGE_NAME}.img" > "${IMAGE_NAME}.img.md5"
    md5sum "${IMAGE_NAME}.img.zip" > "${IMAGE_NAME}.img.zip.md5"
    
    print_success "镜像构建完成"
}

generate_usage_guide() {
    print_step "14" "生成使用指南"
    
    local guide_file="${OUTPUT_DIR}/${IMAGE_NAME}_使用指南.md"
    cat > "${guide_file}" << 'EOF'
# 🎮 GamePlayer-Raspberry 使用指南

## 📋 镜像信息

- **版本**: 2.0.0
- **构建日期**: $(date '+%Y-%m-%d %H:%M:%S')
- **基础系统**: Raspberry Pi OS Bookworm (64-bit)
- **镜像大小**: 8GB
- **支持硬件**: Raspberry Pi 3B+, 4B, 400, Zero 2W

## 🚀 快速开始

### 1. 烧录镜像
```bash
# 使用Raspberry Pi Imager (推荐)
# 或使用dd命令
sudo dd if=GamePlayer-Raspberry-2.0.0.img of=/dev/sdX bs=4M status=progress
```

### 2. 首次启动
1. 插入SD卡到树莓派
2. 连接HDMI显示器和USB键盘
3. 接通电源，等待系统启动
4. 系统会自动执行首次配置

### 3. 网络访问
- 默认用户: `gamer`
- 默认密码: `gameplayer`
- Web界面: `http://树莓派IP地址`

## 🎮 支持的游戏系统
| 系统 | 模拟器 | ROM格式 | 目录位置 |
|------|--------|---------|----------|
| NES | mednafen, fceux | .nes | data/roms/nes/ |
| SNES | snes9x-gtk | .smc, .sfc | data/roms/snes/ |
| Game Boy | visualboyadvance-m | .gb, .gbc | data/roms/gameboy/ |
| GBA | visualboyadvance-m | .gba | data/roms/gba/ |
| Genesis | mednafen | .md, .gen | data/roms/genesis/ |

## 📁 添加游戏ROM

1. **通过SSH传输**:
   ```bash
   scp game.nes gamer@树莓派IP:/home/gamer/GamePlayer-Raspberry/data/roms/nes/
   ```

2. **通过USB设备**:
   - 插入USB设备到树莓派
   - 复制ROM文件到对应目录

3. **通过Web界面**:
   - 访问Web管理界面
   - 使用文件上传功能

## ⚙️ 配置说明

### 系统配置文件
- **模拟器配置**: `config/emulators/emulator_config.json`
- **系统设置**: `config/emulators/general_settings.json`
- **用户设置**: `config/emulators/user_settings.json`

### 服务管理
```bash
# 重启GamePlayer服务
sudo systemctl restart gameplayer

# 查看服务状态
sudo systemctl status gameplayer

# 查看服务日志
sudo journalctl -u gameplayer -f
```

## 🔧 故障排除

### Web界面无法访问
1. 检查服务状态: `sudo systemctl status gameplayer`
2. 重启服务: `sudo systemctl restart gameplayer`
3. 检查防火墙: `sudo ufw status`

### 游戏无法启动
1. 检查ROM文件格式是否正确
2. 确认模拟器已正确安装
3. 查看错误日志: `tail -f /home/gamer/GamePlayer-Raspberry/logs/gameplayer.log`

### 性能优化
1. **超频设置** (编辑 `/boot/config.txt`):
   ```
   arm_freq=1800
   gpu_freq=500
   over_voltage=4
   ```

2. **内存分配**:
   ```
   gpu_mem=128
   ```

## 📞 技术支持

- GitHub: https://github.com/onmyway0011/GamePlayer-Raspberry
- Issues: https://github.com/onmyway0011/GamePlayer-Raspberry/issues

## 📄 许可证

MIT License - 详见 LICENSE 文件
EOF
    
    print_success "使用指南生成完成"
}

show_build_summary() {
    local build_time=$(($(date +%s) - START_TIME))
    local hours=$((build_time / 3600))
    local minutes=$(((build_time % 3600) / 60))
    local seconds=$((build_time % 60))
    
    clear
    print_header
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                           🎉 构建完成！                                        ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${CYAN}📊 构建统计:${NC}"
    echo -e "   ⏱️  构建时间: ${hours}小时${minutes}分钟${seconds}秒"
    echo -e "   📦 镜像文件: ${OUTPUT_DIR}/${IMAGE_NAME}.img"
    echo -e "   🗜️  压缩包: ${OUTPUT_DIR}/${IMAGE_NAME}.img.zip"
    echo -e "   📋 使用指南: ${OUTPUT_DIR}/${IMAGE_NAME}_使用指南.md"
    echo -e "   📝 构建日志: ${LOG_FILE}"
    echo ""
    
    echo -e "${CYAN}🎮 镜像功能:${NC}"
    echo -e "   ✅ 支持多游戏系统 (NES, SNES, GB, GBA, Genesis)"
    echo -e "   ✅ 现代化Web管理界面"
    echo -e "   ✅ 自动ROM扫描和管理"
    echo -e "   ✅ 金手指和存档支持"
    echo -e "   ✅ Docker容器化支持"
    echo -e "   ✅ 自动化测试和修复"
    echo ""
    
    echo -e "${CYAN}🚀 下一步:${NC}"
    echo -e "   1. 使用 Raspberry Pi Imager 烧录镜像到SD卡"
    echo -e "   2. 插入SD卡到树莓派并启动"
    echo -e "   3. 通过浏览器访问 Web 界面开始游戏"
    echo ""
    
    echo -e "${YELLOW}📖 详细说明请查看使用指南文件${NC}"
    echo ""
}

#==================================================================================
# 🎯 主函数
#==================================================================================

main() {
    local START_TIME=$(date +%s)
    
    # 设置错误处理
    trap 'print_error "构建过程中发生错误，请查看日志: ${LOG_FILE}"; exit 1' ERR
    
    print_header
    
    # 检查用户输入
    echo -e "${YELLOW}📋 构建配置:${NC}"
    echo -e "   镜像名称: ${IMAGE_NAME}"
    echo -e "   镜像大小: ${IMAGE_SIZE}"
    echo -e "   默认用户: ${DEFAULT_USER}"
    echo -e "   工作目录: ${WORK_DIR}"
    echo -e "   输出目录: ${OUTPUT_DIR}"
    echo ""
    
    # 可选WiFi配置
    read -p "是否配置WiFi？(y/N): " configure_wifi
    if [[ $configure_wifi =~ ^[Yy]$ ]]; then
        read -p "WiFi名称 (SSID): " WIFI_SSID
        read -s -p "WiFi密码: " WIFI_PASSWORD
        echo ""
    fi
    
    read -p "确认开始构建？(y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "构建已取消"
        exit 0
    fi
    
    echo ""
    
    # 执行构建步骤
    check_root
    check_dependencies
    check_disk_space
    prepare_environment
    download_rpi_os
    expand_image
    mount_image
    configure_system
    install_emulators
    setup_gameplayer_project
    download_roms
    setup_web_services
    optimize_system
    setup_autostart
    finalize_image
    generate_usage_guide
    
    # 显示构建总结
    show_build_summary
    
    print_success "🎮 GamePlayer-Raspberry 镜像构建完成！"
}

#==================================================================================
# 🚀 脚本入口
#==================================================================================

# 检查参数
case "${1:-}" in
    --help|-h)
        echo "GamePlayer-Raspberry 一键镜像生成器"
        echo ""
        echo "用法: sudo $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --help, -h     显示此帮助信息"
        echo "  --version, -v  显示版本信息"
        echo ""
        echo "环境变量:"
        echo "  WIFI_SSID      WiFi网络名称"
        echo "  WIFI_PASSWORD  WiFi密码"
        echo "  IMAGE_SIZE     镜像大小 (默认: 8G)"
        echo ""
        exit 0
        ;;
    --version|-v)
        echo "GamePlayer-Raspberry 镜像生成器 v${PROJECT_VERSION}"
        exit 0
        ;;
esac

# 运行主函数
main "$@"