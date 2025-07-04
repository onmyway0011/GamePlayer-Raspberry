#!/bin/bash

# GamePlayer-Raspberry 纯净树莓派镜像构建器
# 专门用于生成不包含Docker的纯净树莓派系统镜像
# 全流程自动化，无需人工确认或交互，遇到可跳过的错误自动跳过，致命错误自动退出

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_DIR="${BUILD_DIR:-$PROJECT_ROOT/output}"
TEMP_DIR="$BUILD_DIR/temp"
LOG_FILE="$BUILD_DIR/pure_build.log"

# 镜像配置
BASE_IMAGE_URL="https://github.com/RetroPie/RetroPie-Setup/releases/download/4.8/retropie-buster-4.8-rpi4_400.img.gz"
BASE_IMAGE_NAME="retropie-buster-4.8-rpi4_400.img.gz"
OUTPUT_IMAGE_NAME="retropie_gameplayer_pure.img"
OUTPUT_IMAGE_GZ="$OUTPUT_IMAGE_NAME.gz"

# 显示标题
show_header() {
    echo -e "${PURPLE}"
    echo "🍓 GamePlayer-Raspberry 纯净树莓派镜像构建器"
    echo "=============================================="
    echo "专注于树莓派原生系统 + 游戏组件"
    echo "不包含Docker相关组件"
    echo "版本: v4.7.0"
    echo "构建日期: $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${NC}"
}

# 日志函数
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log_step() {
    echo -e "${BLUE}[STEP] $1${NC}" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${CYAN}[INFO] $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR] $1${NC}" | tee -a "$LOG_FILE"
}

# 检查系统要求
check_requirements() {
    log_step "1. 检查系统要求..."
    
    # 检测操作系统
    local os_type=$(uname -s)
    log_info "检测到操作系统: $os_type"
    
    if [ "$os_type" != "Linux" ]; then
        log_error "❌ 纯净树莓派镜像构建需要Linux系统"
        log_info "在macOS上请使用Docker测试环境: ./start_docker_gui.sh"
        exit 1
    fi
    
    # 检查必要工具
    local required_tools=("sudo" "losetup" "kpartx" "chroot" "wget" "gzip" "python3")
    local missing_tools=()
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "❌ 缺少必需工具: ${missing_tools[*]}"
        log_info "请安装: sudo apt-get install ${missing_tools[*]}"
        exit 1
    fi
    
    # 检查磁盘空间 (需要至少8GB)
    local available_space=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    local required_space=$((8 * 1024 * 1024)) # 8GB in KB
    
    if [[ $available_space -lt $required_space ]]; then
        log_error "❌ 磁盘空间不足，需要至少8GB可用空间"
        exit 1
    fi
    
    log_success "✅ 系统要求检查通过"
}

# 准备构建环境
setup_build_environment() {
    log_step "2. 准备构建环境..."
    
    # 创建工作目录
    mkdir -p "$BUILD_DIR"
    mkdir -p "$TEMP_DIR"
    mkdir -p "$BUILD_DIR/mount"
    
    # 创建日志文件
    echo "GamePlayer-Raspberry 纯净镜像构建日志" > "$LOG_FILE"
    echo "构建开始时间: $(date)" >> "$LOG_FILE"
    echo "======================================" >> "$LOG_FILE"
    
    log_success "✅ 构建环境准备完成"
}

# 下载基础镜像
download_base_image() {
    log_step "3. 下载RetroPie基础镜像..."
    
    cd "$TEMP_DIR"
    
    if [[ -f "$BASE_IMAGE_NAME" ]]; then
        log_warning "⚠️ 基础镜像已存在，跳过下载"
        return
    fi
    
    log_info "下载 RetroPie 4.8 基础镜像..."
    wget -c "$BASE_IMAGE_URL" -O "$BASE_IMAGE_NAME" || {
        log_error "❌ 基础镜像下载失败"
        exit 1
    }
    
    log_success "✅ 基础镜像下载完成"
}

# 解压基础镜像
extract_base_image() {
    log_step "4. 解压基础镜像..."
    
    cd "$TEMP_DIR"
    
    if [[ -f "retropie-base.img" ]]; then
        log_warning "⚠️ 基础镜像已解压，跳过解压"
        return
    fi
    
    log_info "解压镜像文件..."
    gunzip -c "$BASE_IMAGE_NAME" > retropie-base.img || {
        log_error "❌ 镜像解压失败"
        exit 1
    }
    
    log_success "✅ 基础镜像解压完成"
}

# 挂载镜像
mount_image() {
    log_step "5. 挂载镜像文件系统..."
    
    cd "$TEMP_DIR"
    
    # 设置loop设备
    LOOP_DEVICE=$(sudo losetup -f --show retropie-base.img)
    echo "$LOOP_DEVICE" > loop_device.txt
    
    # 创建设备映射
    sudo kpartx -av "$LOOP_DEVICE"
    
    # 挂载根分区
    MOUNT_POINT="$BUILD_DIR/mount"
    sudo mkdir -p "$MOUNT_POINT"
    sudo mount "/dev/mapper/$(basename $LOOP_DEVICE)p2" "$MOUNT_POINT"
    
    # 挂载boot分区
    sudo mkdir -p "$MOUNT_POINT/boot"
    sudo mount "/dev/mapper/$(basename $LOOP_DEVICE)p1" "$MOUNT_POINT/boot"
    
    log_success "✅ 镜像挂载完成"
}

# 安装游戏组件
install_game_components() {
    log_step "6. 安装游戏组件..."
    
    MOUNT_POINT="$BUILD_DIR/mount"
    
    # 复制项目文件（排除Docker相关）
    log_info "复制游戏相关文件..."
    sudo mkdir -p "$MOUNT_POINT/home/pi/GamePlayer-Raspberry"
    
    # 复制核心游戏文件
    sudo cp -r "$PROJECT_ROOT/src" "$MOUNT_POINT/home/pi/GamePlayer-Raspberry/"
    sudo cp -r "$PROJECT_ROOT/data" "$MOUNT_POINT/home/pi/GamePlayer-Raspberry/"
    sudo cp -r "$PROJECT_ROOT/config" "$MOUNT_POINT/home/pi/GamePlayer-Raspberry/"
    sudo cp "$PROJECT_ROOT/requirements.txt" "$MOUNT_POINT/home/pi/GamePlayer-Raspberry/"
    
    # 排除Docker相关文件和脚本（增强覆盖）
    sudo rm -rf "$MOUNT_POINT/home/pi/GamePlayer-Raspberry/src/docker" 2>/dev/null || true
    sudo rm -f "$MOUNT_POINT/home/pi/GamePlayer-Raspberry/Dockerfile"* 2>/dev/null || true
    sudo rm -f "$MOUNT_POINT/home/pi/GamePlayer-Raspberry/docker-compose"* 2>/dev/null || true
    sudo rm -f "$MOUNT_POINT/home/pi/GamePlayer-Raspberry/start_docker"* 2>/dev/null || true
    sudo rm -f "$MOUNT_POINT/home/pi/GamePlayer-Raspberry/.dockerignore" 2>/dev/null || true
    sudo rm -f "$MOUNT_POINT/home/pi/GamePlayer-Raspberry/verify_docker_integration.py" 2>/dev/null || true
    
    sudo chown -R 1000:1000 "$MOUNT_POINT/home/pi/GamePlayer-Raspberry/"
    
    log_success "✅ 游戏文件复制完成"
}

# 配置系统
configure_system() {
    log_step "7. 配置系统..."
    
    MOUNT_POINT="$BUILD_DIR/mount"
    
    # 设置chroot环境
    sudo mount --bind /dev "$MOUNT_POINT/dev"
    sudo mount --bind /proc "$MOUNT_POINT/proc"
    sudo mount --bind /sys "$MOUNT_POINT/sys"
    
    # 在chroot环境中配置
    sudo chroot "$MOUNT_POINT" /bin/bash << 'EOF'
set -e

# 更新包列表
apt-get update

# 安装Python依赖
apt-get install -y python3-pip python3-venv

# 安装游戏模拟器
apt-get install -y mednafen fceux snes9x-gtk visualboyadvance-m

# 安装Web服务器依赖
pip3 install flask requests beautifulsoup4 pillow

# 创建游戏目录
mkdir -p /home/pi/RetroPie/roms/{nes,snes,gameboy,gba}
mkdir -p /home/pi/RetroPie/saves
chown -R pi:pi /home/pi/RetroPie/

# 设置开机自启动游戏服务
cat > /etc/systemd/system/gameplayer.service << 'SERVICE_EOF'
[Unit]
Description=GamePlayer-Raspberry Game Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/GamePlayer-Raspberry
ExecStart=/usr/bin/python3 /home/pi/GamePlayer-Raspberry/src/scripts/simple_demo_server.py
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE_EOF

systemctl enable gameplayer.service

# 配置自动登录
systemctl set-default multi-user.target

# 可选：安装更多模拟器（如需）
# apt-get install -y lr-fceumm lr-snes9x ...

EOF
    
    log_success "✅ 系统配置完成"
}

# 清理和优化
cleanup_and_optimize() {
    log_step "8. 清理和优化镜像..."
    
    MOUNT_POINT="$BUILD_DIR/mount"
    
    # 在chroot环境中清理
    sudo chroot "$MOUNT_POINT" /bin/bash << 'EOF'
set -e

# 清理APT缓存
apt-get clean
apt-get autoremove -y

# 清理临时文件
rm -rf /tmp/*
rm -rf /var/tmp/*

# 清理日志文件
find /var/log -type f -name "*.log" -delete

# 清理bash历史
rm -f /home/pi/.bash_history
rm -f /root/.bash_history

EOF
    
    log_success "✅ 镜像清理完成"
}

# 卸载镜像
unmount_image() {
    log_step "9. 卸载镜像文件系统..."
    
    MOUNT_POINT="$BUILD_DIR/mount"
    
    # 卸载chroot绑定
    sudo umount "$MOUNT_POINT/dev" 2>/dev/null || true
    sudo umount "$MOUNT_POINT/proc" 2>/dev/null || true
    sudo umount "$MOUNT_POINT/sys" 2>/dev/null || true
    
    # 卸载分区
    sudo umount "$MOUNT_POINT/boot" 2>/dev/null || true
    sudo umount "$MOUNT_POINT" 2>/dev/null || true
    
    # 删除设备映射
    if [[ -f "$TEMP_DIR/loop_device.txt" ]]; then
        LOOP_DEVICE=$(cat "$TEMP_DIR/loop_device.txt")
        sudo kpartx -dv "$LOOP_DEVICE"
        sudo losetup -d "$LOOP_DEVICE"
        rm -f "$TEMP_DIR/loop_device.txt"
    fi
    
    log_success "✅ 镜像卸载完成"
}

# 生成最终镜像
generate_final_image() {
    log_step "10. 生成最终镜像..."
    
    cd "$TEMP_DIR"
    
    # 复制镜像到输出目录
    cp retropie-base.img "$BUILD_DIR/$OUTPUT_IMAGE_NAME"
    
    # 压缩镜像
    log_info "压缩镜像文件..."
    gzip -c "$BUILD_DIR/$OUTPUT_IMAGE_NAME" > "$BUILD_DIR/$OUTPUT_IMAGE_GZ"
    
    # 生成校验和
    cd "$BUILD_DIR"
    sha256sum "$OUTPUT_IMAGE_GZ" > "$OUTPUT_IMAGE_GZ.sha256"
    
    # 生成镜像信息
    cat > "$OUTPUT_IMAGE_NAME.info" << EOF
GamePlayer-Raspberry 纯净树莓派镜像
==================================

构建信息:
- 构建时间: $(date)
- 基础镜像: RetroPie 4.8
- 目标平台: Raspberry Pi 4/400
- 镜像类型: 纯净树莓派系统
- 镜像大小: $(du -h "$OUTPUT_IMAGE_GZ" | cut -f1)

包含组件:
- RetroPie 4.8 基础系统
- 4种游戏模拟器 (mednafen, fceux, snes9x, visualboyadvance-m)
- 游戏ROM文件
- 游戏封面图片
- 轻量级Web游戏选择器
- 自动存档系统
- 金手指配置
- USB手柄支持
- 音频系统支持

不包含:
- Docker相关组件
- 开发调试工具
- VNC远程桌面
- 系统监控工具

使用方法:
1. 使用Raspberry Pi Imager烧录到SD卡
2. 插入树莓派并启动
3. 系统自动启动游戏服务
4. 访问 http://树莓派IP:8080 进入游戏界面

更多信息请查看: README_纯净镜像使用说明.md
EOF
    
    log_success "✅ 最终镜像生成完成"
}

# 自动化测试入口（全自动自愈）
automated_test_image() {
    log_step "11. 自动化测试镜像（全自动自愈）..."
    local max_retry=5
    local retry_count=0
    local test_passed=false
    local image_path="$BUILD_DIR/$OUTPUT_IMAGE_NAME"
    local image_gz_path="$BUILD_DIR/$OUTPUT_IMAGE_GZ"

    # 检查QEMU是否可用
    if ! command -v qemu-system-arm >/dev/null 2>&1; then
        log_warning "未检测到QEMU，跳过自动化测试（如需测试请安装qemu-system-arm）"
        return 0
    fi

    # 解压镜像（如有必要）
    if [ -f "$image_gz_path" ] && [ ! -f "$image_path" ]; then
        log_info "解压镜像用于QEMU测试..."
        gunzip -c "$image_gz_path" > "$image_path"
    fi

    while [ $retry_count -lt $max_retry ]; do
        log_info "QEMU自动化测试第$((retry_count+1))次..."
        # 启动QEMU（以后台方式，模拟树莓派3B）
        qemu-system-arm -M raspi3b -m 1024 -drive file="$image_path",format=raw,if=sd -net nic -net user,hostfwd=tcp::18080-:8080 -nographic -serial null -append "rw console=ttyAMA0 root=/dev/mmcblk0p2 rootfstype=ext4 fsck.repair=yes rootwait" &
        QEMU_PID=$!
        sleep 60 # 等待系统和服务启动

        # 检查8080端口
        if curl -s http://localhost:18080 | grep -q "GamePlayer"; then
            log_success "8080端口Web服务检测通过"
        else
            log_warning "8080端口Web服务检测失败，尝试修复..."
            kill $QEMU_PID 2>/dev/null || true
            # 自动修复：重新集成Web服务/ROM/模拟器
            sudo chroot "$BUILD_DIR/mount" /bin/bash -c "pip3 install flask requests beautifulsoup4 pillow || true"
            sudo chroot "$BUILD_DIR/mount" /bin/bash -c "apt-get install -y mednafen fceux snes9x-gtk visualboyadvance-m || true"
            sudo chroot "$BUILD_DIR/mount" /bin/bash -c "cd /home/pi/GamePlayer-Raspberry && python3 src/scripts/rom_downloader.py --category homebrew_games --output data/roms/nes/ || true"
            retry_count=$((retry_count+1))
            continue
        fi

        # 检查关键文件
        for f in "/home/pi/GamePlayer-Raspberry/src/scripts/simple_demo_server.py" "/home/pi/GamePlayer-Raspberry/data/roms/nes"; do
            if ! sudo chroot "$BUILD_DIR/mount" test -e "$f"; then
                log_warning "$f 缺失，自动修复..."
                sudo chroot "$BUILD_DIR/mount" /bin/bash -c "cd /home/pi/GamePlayer-Raspberry && python3 src/scripts/rom_downloader.py --category homebrew_games --output data/roms/nes/ || true"
                retry_count=$((retry_count+1))
                kill $QEMU_PID 2>/dev/null || true
                continue 2
            fi
        done

        # 检查服务
        if ! sudo chroot "$BUILD_DIR/mount" systemctl status gameplayer.service | grep -q running; then
            log_warning "gameplayer.service 未正常运行，自动修复..."
            sudo chroot "$BUILD_DIR/mount" systemctl restart gameplayer.service || true
            retry_count=$((retry_count+1))
            kill $QEMU_PID 2>/dev/null || true
            continue
        fi

        # 所有检测通过
        test_passed=true
        kill $QEMU_PID 2>/dev/null || true
        break
    done

    if [ "$test_passed" = true ]; then
        log_success "🎉 镜像自动化测试全部通过！"
    else
        log_error "❌ 镜像自动化测试多次修复后仍未通过，请检查日志！"
        exit 1
    fi
}

# 主函数
main() {
    # 设置错误处理
    trap 'unmount_image 2>/dev/null || true' EXIT
    
    show_header
    
    # 执行构建流程
    check_requirements
    setup_build_environment
    download_base_image
    extract_base_image
    mount_image
    install_game_components
    configure_system
    cleanup_and_optimize
    unmount_image
    generate_final_image
    # 自动化测试入口（全自动自愈）
    automated_test_image
    
    echo ""
    echo -e "${GREEN}🎉 纯净树莓派镜像构建完成！${NC}"
    echo "================================"
    echo ""
    echo -e "${CYAN}📁 输出文件:${NC}"
    echo "  镜像文件: $BUILD_DIR/$OUTPUT_IMAGE_GZ"
    echo "  信息文件: $BUILD_DIR/$OUTPUT_IMAGE_NAME.info"
    echo "  校验文件: $BUILD_DIR/$OUTPUT_IMAGE_GZ.sha256"
    echo ""
    echo -e "${CYAN}📊 镜像统计:${NC}"
    if [ -f "$BUILD_DIR/$OUTPUT_IMAGE_GZ" ]; then
        echo "  文件大小: $(du -h "$BUILD_DIR/$OUTPUT_IMAGE_GZ" | cut -f1)"
        echo "  SHA256: $(cat "$BUILD_DIR/$OUTPUT_IMAGE_GZ.sha256" | cut -d' ' -f1)"
    fi
    echo ""
    echo -e "${CYAN}🚀 下一步:${NC}"
    echo "  1. 使用 Raspberry Pi Imager 烧录镜像"
    echo "  2. 插入树莓派并启动"
    echo "  3. 访问 http://树莓派IP:8080 开始游戏"
    echo ""
    echo -e "${GREEN}🎮 享受纯净的树莓派游戏体验！${NC}"
}

# 运行主函数
main "$@"
