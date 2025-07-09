#!/bin/bash
set -euo pipefail  # 增强错误处理

# 🍓 GamePlayer-Raspberry 纯净树莓派镜像构建器
# ===============================================
# 专注于树莓派原生系统 + 游戏组件
# 不包含Docker相关组件
# 版本: v4.7.0
# 构建日期: $(date '+%Y-%m-%d %H:%M:%S')

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
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# 全局变量
LOOPDEV=""
MNT_BOOT=""
MNT_ROOT=""
CLEANUP_DONE=false

# 错误处理和清理函数
cleanup() {
    if [ "$CLEANUP_DONE" = true ]; then
        return 0
    fi
    
    log_info "正在清理挂载点和循环设备..."
    
    # 卸载绑定挂载
    for mount_point in "/dev" "/proc" "/sys"; do
        if [ -n "$MNT_ROOT" ] && mountpoint -q "$MNT_ROOT$mount_point" 2>/dev/null; then
            umount "$MNT_ROOT$mount_point" 2>/dev/null || true
        fi
    done
    
    # 卸载分区
    if [ -n "$MNT_BOOT" ] && mountpoint -q "$MNT_BOOT" 2>/dev/null; then
        umount "$MNT_BOOT" 2>/dev/null || true
    fi
    
    if [ -n "$MNT_ROOT" ] && mountpoint -q "$MNT_ROOT" 2>/dev/null; then
        umount "$MNT_ROOT" 2>/dev/null || true
    fi
    
    # 删除设备映射
    if [ -n "$LOOPDEV" ]; then
        kpartx -dv "$LOOPDEV" 2>/dev/null || true
        losetup -d "$LOOPDEV" 2>/dev/null || true
    fi
    
    # 清理临时挂载点
    if [ -n "$MNT_BOOT" ] && [ -d "$MNT_BOOT" ]; then
        rmdir "$MNT_BOOT" 2>/dev/null || true
    fi
    
    if [ -n "$MNT_ROOT" ] && [ -d "$MNT_ROOT" ]; then
        rmdir "$MNT_ROOT" 2>/dev/null || true
    fi
    
    CLEANUP_DONE=true
}

# 设置错误处理
trap cleanup EXIT
trap 'log_error "脚本在第 $LINENO 行失败"; exit 1' ERR

# 检查权限
check_permissions() {
    if [ "$EUID" -ne 0 ]; then
        log_error "需要root权限运行此脚本"
        log_info "请使用: sudo $0"
        exit 1
    fi
}

# 创建输出目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUTDIR="$PROJECT_ROOT/output"

log_info "脚本目录: $SCRIPT_DIR"
log_info "项目根目录: $PROJECT_ROOT"
log_info "输出目录: $OUTDIR"

if ! mkdir -p "$OUTDIR"; then
    log_error "无法创建输出目录: $OUTDIR"
    exit 1
fi

# 1. 检查系统要求
check_requirements() {
    log_step "1. 检查系统要求..."
    
    # 检查权限
    check_permissions
    
    # 检查必需命令
    local required_commands=("wget" "kpartx" "losetup" "chroot" "gzip" "xz" "mount" "umount")
    local missing_commands=()
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_commands+=("$cmd")
        fi
    done
    
    if [ ${#missing_commands[@]} -ne 0 ]; then
        log_error "缺少必需命令: ${missing_commands[*]}"
        log_info "请安装缺少的工具包"
        exit 1
    fi
    
    # 检查磁盘空间 (至少需要8GB)
    local available_space
    available_space=$(df "$OUTDIR" 2>/dev/null | awk 'NR==2 {print $4}' || echo "0")
    if [ "${available_space:-0}" -lt 8388608 ]; then  # 8GB in KB
        log_warning "磁盘空间可能不足，建议至少8GB可用空间"
    fi
    
    log_success "系统要求检查通过"
}

# 2. 下载基础镜像（带缓存）
download_base_image() {
    log_step "2. 准备基础镜像..."
    
    # 使用更稳定的镜像源
    local BASE_IMG_URL="https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2023-05-03/2023-05-03-raspios-bullseye-armhf-lite.img.xz"
    local BASE_IMG_XZ="$OUTDIR/raspios_lite_base.img.xz"
    local BASE_IMG="$OUTDIR/raspios_lite_base.img"
    
    # 设置全局变量供后续使用
    BASE_IMAGE_PATH="$BASE_IMG"
    
    # 检查是否已存在完整的 .img 文件
    if [ -f "$BASE_IMG" ]; then
        log_info "检测到本地已存在解压后的基础镜像，跳过下载与解压"
        ls -lh "$BASE_IMG"
        return 0
    fi
    
    # 检查是否已存在完整的 .img.xz 文件
    if [ -f "$BASE_IMG_XZ" ]; then
        log_info "检测到本地已存在基础镜像压缩包，跳过下载"
        ls -lh "$BASE_IMG_XZ"
    else
        log_step "下载官方基础镜像..."
        if ! wget -O "$BASE_IMG_XZ.tmp" "$BASE_IMG_URL"; then
            log_error "基础镜像下载失败"
            rm -f "$BASE_IMG_XZ.tmp"
            exit 1
        fi
        
        # 原子性重命名
        mv "$BASE_IMG_XZ.tmp" "$BASE_IMG_XZ"
        log_success "基础镜像下载完成"
        ls -lh "$BASE_IMG_XZ"
    fi
    
    # 解压 .img.xz 文件
    if [ ! -f "$BASE_IMG" ]; then
        log_step "解压基础镜像..."
        if ! xz -dk "$BASE_IMG_XZ"; then
            log_error "基础镜像解压失败"
            exit 1
        fi
        log_success "基础镜像解压完成"
        ls -lh "$BASE_IMG"
    else
        log_info "解压后的镜像已存在，跳过解压"
    fi
}

# 3. 挂载镜像分区
mount_image() {
    log_step "3. 挂载镜像分区..."
    
    # 创建循环设备
    LOOPDEV=$(losetup --show -fP "$BASE_IMAGE_PATH")
    if [ -z "$LOOPDEV" ]; then
        log_error "无法创建循环设备"
        exit 1
    fi
    log_info "循环设备: $LOOPDEV"
    
    # 创建设备映射
    if ! kpartx -av "$LOOPDEV"; then
        log_error "无法创建设备映射"
        exit 1
    fi
    
    # 等待设备文件创建
    sleep 3
    
    # 创建挂载点
    MNT_BOOT="/tmp/rpi_boot_$$"
    MNT_ROOT="/tmp/rpi_root_$$"
    
    if ! mkdir -p "$MNT_BOOT" "$MNT_ROOT"; then
        log_error "无法创建挂载点"
        exit 1
    fi
    
    # 确定分区设备路径
    local BOOT_PART="${LOOPDEV}p1"
    local ROOT_PART="${LOOPDEV}p2"
    
    # 检查分区是否存在，如果不存在尝试映射路径
    if [ ! -b "$BOOT_PART" ]; then
        BOOT_PART="/dev/mapper/$(basename "$LOOPDEV")p1"
        ROOT_PART="/dev/mapper/$(basename "$LOOPDEV")p2"
    fi
    
    # 验证分区设备存在
    if [ ! -b "$ROOT_PART" ] || [ ! -b "$BOOT_PART" ]; then
        log_error "找不到分区设备: $BOOT_PART, $ROOT_PART"
        exit 1
    fi
    
    log_info "分区设备: BOOT=$BOOT_PART, ROOT=$ROOT_PART"
    
    # 挂载分区
    if ! mount "$ROOT_PART" "$MNT_ROOT"; then
        log_error "无法挂载根分区"
        exit 1
    fi
    
    if ! mount "$BOOT_PART" "$MNT_BOOT"; then
        log_error "无法挂载boot分区"
        exit 1
    fi
    
    log_success "镜像分区挂载完成"
}

# 4. 集成ROM和模拟器
integrate_game_components() {
    log_step "4. 集成游戏组件..."
    
    # 创建目标目录
    local target_home="$MNT_ROOT/home/pi"
    if ! mkdir -p "$target_home"; then
        log_error "无法创建目标目录"
        exit 1
    fi
    
    # 复制ROM文件
    if [ -d "$PROJECT_ROOT/data/roms" ]; then
        log_info "复制ROM文件..."
        if ! cp -r "$PROJECT_ROOT/data/roms" "$target_home/"; then
            log_warning "ROM文件复制失败"
        else
            log_success "ROM文件复制完成"
        fi
    else
        log_warning "找不到ROM目录，创建空目录"
        mkdir -p "$target_home/roms"
    fi
    
    # 复制配置文件
    if [ -d "$PROJECT_ROOT/config" ]; then
        log_info "复制配置文件..."
        if ! cp -r "$PROJECT_ROOT/config" "$target_home/"; then
            log_warning "配置文件复制失败"
        else
            log_success "配置文件复制完成"
        fi
    else
        log_warning "找不到配置目录，创建空目录"
        mkdir -p "$target_home/config"
    fi
    
    # 复制源代码
    if [ -d "$PROJECT_ROOT/src" ]; then
        log_info "复制GamePlayer源代码..."
        if ! cp -r "$PROJECT_ROOT/src" "$target_home/GamePlayer-Raspberry/"; then
            log_warning "源代码复制失败"
        else
            log_success "源代码复制完成"
        fi
    fi
    
    # 设置正确的所有权
    if ! chown -R 1000:1000 "$target_home" 2>/dev/null; then
        log_warning "无法设置文件所有权"
    fi
    
    log_success "游戏组件集成完成"
}

# 5. 系统配置和软件安装
configure_system() {
    log_step "5. 配置系统和安装软件..."
    
    # 绑定挂载系统目录
    local bind_mounts=("/dev" "/proc" "/sys")
    for mount_point in "${bind_mounts[@]}"; do
        if ! mount --bind "$mount_point" "$MNT_ROOT$mount_point"; then
            log_error "无法绑定挂载 $mount_point"
            exit 1
        fi
    done
    
    # 复制DNS配置
    if [ -f "/etc/resolv.conf" ]; then
        cp /etc/resolv.conf "$MNT_ROOT/etc/resolv.conf" || true
    fi
    
    # 在chroot环境中执行配置
    local chroot_script="$MNT_ROOT/tmp/setup_gameplayer.sh"
    
    cat > "$chroot_script" << 'CHROOT_SCRIPT'
#!/bin/bash
set -e

echo "[CHROOT] 更新软件包列表..."
apt-get update || exit 1

echo "[CHROOT] 安装基础软件包..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-pygame \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    cmake \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libasound2-dev \
    || exit 1

echo "[CHROOT] 启用SSH服务..."
systemctl enable ssh || true

echo "[CHROOT] 配置用户权限..."
usermod -a -G audio,video,input,gpio pi || true

echo "[CHROOT] 安装Python依赖..."
if [ -f "/home/pi/GamePlayer-Raspberry/requirements.txt" ]; then
    pip3 install -r /home/pi/GamePlayer-Raspberry/requirements.txt || true
fi

echo "[CHROOT] 系统配置完成"
CHROOT_SCRIPT
    
    chmod +x "$chroot_script"
    
    # 执行chroot脚本
    if ! chroot "$MNT_ROOT" /tmp/setup_gameplayer.sh; then
        log_warning "chroot配置脚本执行失败，继续构建"
    else
        log_success "系统配置完成"
    fi
    
    # 清理临时脚本
    rm -f "$chroot_script"
    
    # 创建自动启动服务
    create_autostart_service
}

# 创建自动启动服务
create_autostart_service() {
    log_info "创建自动启动服务..."
    
    # 创建启动脚本
    cat > "$MNT_ROOT/home/pi/start_gameplayer.sh" << 'STARTUP_SCRIPT'
#!/bin/bash
# GamePlayer自动启动脚本
export HOME=/home/pi
export USER=pi
export DISPLAY=:0

cd /home/pi/GamePlayer-Raspberry

# 启动Web服务器
if [ -d "data/web" ]; then
    python3 -m http.server 8080 --directory data/web &
fi

# 启动游戏启动器
if [ -f "src/scripts/nes_game_launcher.py" ]; then
    python3 src/scripts/nes_game_launcher.py &
fi

# 记录启动日志
echo "$(date): GamePlayer-Raspberry 自动启动完成" >> /home/pi/logs/startup.log
STARTUP_SCRIPT
    
    chmod +x "$MNT_ROOT/home/pi/start_gameplayer.sh"
    
    # 创建systemd服务文件
    cat > "$MNT_ROOT/etc/systemd/system/gameplayer.service" << 'SERVICE_FILE'
[Unit]
Description=GamePlayer-Raspberry Auto Start
After=multi-user.target
Wants=network.target

[Service]
Type=forking
User=pi
Group=pi
WorkingDirectory=/home/pi
ExecStart=/home/pi/start_gameplayer.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_FILE
    
    # 在chroot中启用服务
    chroot "$MNT_ROOT" systemctl enable gameplayer.service 2>/dev/null || true
    
    log_success "自动启动服务创建完成"
}

# 6. 清理和卸载
unmount_and_cleanup() {
    log_step "6. 清理和卸载分区..."
    
    # 清理chroot环境
    if [ -f "$MNT_ROOT/etc/resolv.conf.backup" ]; then
        mv "$MNT_ROOT/etc/resolv.conf.backup" "$MNT_ROOT/etc/resolv.conf" 2>/dev/null || true
    fi
    
    # 手动调用cleanup函数
    cleanup
    log_success "分区卸载和清理完成"
}

# 7. 压缩镜像
compress_image() {
    log_step "7. 压缩最终镜像..."
    
    local FINAL_IMG="$OUTDIR/retropie_gameplayer_complete.img"
    local FINAL_IMG_GZ="$OUTDIR/retropie_gameplayer_complete.img.gz"
    
    # 复制基础镜像到最终镜像
    if ! cp "$BASE_IMAGE_PATH" "$FINAL_IMG"; then
        log_error "无法复制基础镜像"
        exit 1
    fi
    
    # 压缩镜像
    log_info "正在压缩镜像（这可能需要几分钟）..."
    if ! gzip -c "$FINAL_IMG" > "$FINAL_IMG_GZ"; then
        log_error "镜像压缩失败"
        exit 1
    fi
    
    # 删除未压缩的镜像以节省空间
    rm -f "$FINAL_IMG"
    
    # 生成校验和
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$FINAL_IMG_GZ" > "$FINAL_IMG_GZ.sha256"
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$FINAL_IMG_GZ" > "$FINAL_IMG_GZ.sha256"
    fi
    
    # 生成镜像信息
    cat > "$OUTDIR/retropie_gameplayer_complete.img.info" << EOF
# GamePlayer-Raspberry 镜像信息

构建时间: $(date)
镜像大小: $(du -h "$FINAL_IMG_GZ" | cut -f1)
基础系统: Raspberry Pi OS Lite
包含组件:
- GamePlayer-Raspberry 游戏系统
- Python3 运行环境
- 自动启动服务
- Web管理界面

烧录命令:
sudo dd if=retropie_gameplayer_complete.img.gz of=/dev/sdX bs=4M status=progress

使用说明:
1. 烧录镜像到SD卡
2. 插入树莓派启动
3. 访问 http://树莓派IP:8080 进入游戏界面
EOF
    
    log_success "镜像压缩完成: $FINAL_IMG_GZ"
    ls -lh "$FINAL_IMG_GZ"
}

# 主函数
main() {
    echo "🍓 GamePlayer-Raspberry 纯净树莓派镜像构建器"
    echo "=============================================="
    echo "版本: v4.7.0"
    echo "构建时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    check_requirements
    download_base_image
    mount_image
    integrate_game_components
    configure_system
    unmount_and_cleanup
    compress_image
    
    echo ""
    log_success "✅ 树莓派镜像构建完成！"
    echo "==============================="
    echo ""
    echo "📁 输出文件:"
    echo "  镜像文件: $OUTDIR/retropie_gameplayer_complete.img.gz"
    echo "  校验文件: $OUTDIR/retropie_gameplayer_complete.img.gz.sha256"
    echo "  信息文件: $OUTDIR/retropie_gameplayer_complete.img.info"
    echo ""
    echo "🚀 下一步:"
    echo "  1. 使用 Raspberry Pi Imager 烧录镜像"
    echo "  2. 插入树莓派并启动"
    echo "  3. 访问 http://树莓派IP:8080 开始游戏"
    echo ""
    echo "🎮 享受游戏时光！"
}
# 执行主函数
main "$@"
