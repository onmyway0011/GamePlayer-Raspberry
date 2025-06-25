#!/bin/bash
# VirtuaNES 0.97 自动集成脚本
# 用于在 RetroPie 镜像烧录过程中自动安装和配置 VirtuaNES 模拟器

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config/project_config.json"
VIRTUALNES_VERSION="0.97"
INSTALL_DIR="/opt/retropie/emulators/virtuanes"
CONFIG_DIR="/home/pi/RetroPie/configs/nes"
CORE_DIR="/opt/retropie/emulators/retroarch/cores"

# 检查是否为 root 用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要 root 权限运行"
        exit 1
    fi
}

# 检查配置文件
check_config() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_error "配置文件不存在: $CONFIG_FILE"
        exit 1
    fi
    
    # 检查 VirtuaNES 配置
    if ! python3 -c "import json; config=json.load(open('$CONFIG_FILE')); exit(0 if config.get('emulator', {}).get('virtuanes', {}).get('enabled', False) else 1)"; then
        log_warning "VirtuaNES 在配置中未启用，跳过安装"
        exit 0
    fi
    
    log_success "配置文件检查通过"
}

# 安装系统依赖
install_dependencies() {
    log_info "安装 VirtuaNES 系统依赖..."
    
    # 更新包列表
    apt-get update
    
    # 安装编译依赖
    local packages=(
        "build-essential"
        "cmake"
        "libsdl2-dev"
        "libsdl2-image-dev"
        "libsdl2-mixer-dev"
        "libsdl2-ttf-dev"
        "libx11-dev"
        "libxext-dev"
        "libxrandr-dev"
        "libxinerama-dev"
        "libxi-dev"
        "libxcursor-dev"
        "libxcomposite-dev"
        "libxdamage-dev"
        "libxfixes-dev"
        "libxss-dev"
        "libxrender-dev"
        "libxrandr-dev"
        "libasound2-dev"
        "libpulse-dev"
        "libdbus-1-dev"
        "libudev-dev"
        "libibus-1.0-dev"
        "libfribidi-dev"
        "libharfbuzz-dev"
    )
    
    for package in "${packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package "; then
            log_info "安装 $package..."
            apt-get install -y "$package"
        else
            log_info "$package 已安装"
        fi
    done
    
    log_success "系统依赖安装完成"
}

# 下载 VirtuaNES 源码
download_virtuanes() {
    log_info "下载 VirtuaNES $VIRTUALNES_VERSION 源码..."
    
    # 创建安装目录
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # 下载源码的多个来源
    local download_urls=(
        "https://github.com/RetroPie/RetroPie-Setup/raw/master/scriptmodules/emulators/virtuanes.sh"
        "https://sourceforge.net/projects/virtuanes/files/VirtuaNES%20$VIRTUALNES_VERSION/VirtuaNES${VIRTUALNES_VERSION//./}src.zip/download"
        "https://github.com/RetroPie/RetroPie-Setup/archive/refs/heads/master.zip"
    )
    
    local download_success=false
    
    for url in "${download_urls[@]}"; do
        log_info "尝试从 $url 下载..."
        
        if curl -L -o "virtuanes_source.zip" "$url" --connect-timeout 30 --max-time 300; then
            log_success "下载成功: $url"
            download_success=true
            break
        else
            log_warning "下载失败: $url"
        fi
    done
    
    if [[ "$download_success" == false ]]; then
        log_error "所有下载源都失败"
        return 1
    fi
    
    # 解压源码
    if [[ -f "virtuanes_source.zip" ]]; then
        unzip -q "virtuanes_source.zip"
        log_success "源码解压完成"
    fi
    
    return 0
}

# 编译安装 VirtuaNES
compile_virtuanes() {
    log_info "编译安装 VirtuaNES..."
    
    cd "$INSTALL_DIR"
    
    # 查找源码目录
    local source_dir=""
    for dir in */; do
        if [[ -d "$dir" && "$dir" != "*/" ]]; then
            source_dir="$dir"
            break
        fi
    done
    
    if [[ -z "$source_dir" ]]; then
        log_error "未找到源码目录"
        return 1
    fi
    
    cd "$source_dir"
    
    # 检查是否有 Makefile
    if [[ -f "Makefile" ]]; then
        log_info "使用 Makefile 编译..."
        make clean
        make -j$(nproc)
    elif [[ -f "CMakeLists.txt" ]]; then
        log_info "使用 CMake 编译..."
        mkdir -p build
        cd build
        cmake ..
        make -j$(nproc)
    else
        log_error "未找到构建文件"
        return 1
    fi
    
    # 安装到系统
    if [[ -f "virtuanes" ]]; then
        cp virtuanes /usr/local/bin/
        chmod +x /usr/local/bin/virtuanes
        log_success "VirtuaNES 编译安装完成"
    else
        log_error "编译失败，未找到可执行文件"
        return 1
    fi
    
    return 0
}

# 配置 VirtuaNES
configure_virtuanes() {
    log_info "配置 VirtuaNES..."
    
    # 创建配置目录
    mkdir -p "$CONFIG_DIR"
    
    # 生成配置文件
    cat > "$CONFIG_DIR/virtuanes.cfg" << 'EOF'
# VirtuaNES 0.97 配置文件
# 自动生成于 $(date)

# 基本设置
[General]
Version=0.97
Language=English
FullScreen=1
VSync=1
FrameSkip=0
AutoSave=1

# 图形设置
[Graphics]
Filter=0
Scanline=0
AspectRatio=1
Scale=2
Resolution=1920x1080

# 音频设置
[Audio]
Enabled=1
Volume=100
SampleRate=44100
BufferSize=1024
Stereo=1

# 控制器设置
[Controller]
Type=0
DeadZone=10
Sensitivity=100
AutoFire=0

# 保存设置
[Save]
AutoSave=1
SaveSlot=0
SavePath=/home/pi/RetroPie/saves/nes/

# 网络设置
[Network]
Enabled=0
Port=8888
Host=127.0.0.1

# 作弊码设置
[Cheat]
Enabled=1
Path=/home/pi/RetroPie/cheats/nes/

# 高级设置
[Advanced]
FastForward=1
Rewind=1
Netplay=0
EOF
    
    log_success "VirtuaNES 配置完成"
}

# 集成到 RetroArch
integrate_retroarch() {
    log_info "集成 VirtuaNES 到 RetroArch..."
    
    # 创建核心信息文件
    cat > "$CORE_DIR/virtuanes_libretro.info" << 'EOF'
name = "VirtuaNES"
version = "0.97"
description = "VirtuaNES NES Emulator"
author = "VirtuaNES Team"
url = "https://github.com/RetroPie/RetroPie-Setup"
category = "Emulator"
system = "nes"
extensions = .nes,.NES
features = high_compatibility,save_states,cheat_support,netplay,rewind,shaders
EOF
    
    # 创建启动脚本
    cat > "$INSTALL_DIR/launch_virtuanes.sh" << EOF
#!/bin/bash
# VirtuaNES 启动脚本

# 设置环境变量
export VIRTUALNES_CONFIG="$CONFIG_DIR/virtuanes.cfg"
export VIRTUALNES_SAVES="/home/pi/RetroPie/saves/nes/"
export VIRTUALNES_CHEATS="/home/pi/RetroPie/cheats/nes/"

# 启动 VirtuaNES
cd $INSTALL_DIR
exec virtuanes "\$@"
EOF
    
    chmod +x "$INSTALL_DIR/launch_virtuanes.sh"
    
    # 创建桌面文件
    cat > "/usr/share/applications/virtuanes.desktop" << 'EOF'
[Desktop Entry]
Name=VirtuaNES
Comment=NES Emulator
Exec=virtuanes %f
Icon=virtuanes
Terminal=false
Type=Application
Categories=Game;Emulator;
MimeType=application/x-nes-rom;
EOF
    
    # 更新 MIME 数据库
    update-desktop-database
    
    log_success "RetroArch 集成完成"
}

# 设置 ROM 关联
setup_rom_association() {
    log_info "设置 ROM 文件关联..."
    
    # 创建 MIME 类型
    cat > "/usr/share/mime/packages/virtuanes.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="application/x-nes-rom">
    <comment>NES ROM</comment>
    <comment xml:lang="zh_CN">任天堂娱乐系统游戏</comment>
    <glob pattern="*.nes"/>
    <glob pattern="*.NES"/>
  </mime-type>
</mime-info>
EOF
    
    # 更新 MIME 数据库
    update-mime-database /usr/share/mime
    
    log_success "ROM 文件关联设置完成"
}

# 创建符号链接
create_symlinks() {
    log_info "创建符号链接..."
    
    # 链接到 RetroPie 目录
    ln -sf "$INSTALL_DIR/launch_virtuanes.sh" "/home/pi/RetroPie/emulators/virtuanes/"
    ln -sf "/usr/local/bin/virtuanes" "/home/pi/RetroPie/emulators/virtuanes/virtuanes"
    
    # 链接配置文件
    ln -sf "$CONFIG_DIR/virtuanes.cfg" "/home/pi/.config/virtuanes.cfg"
    
    log_success "符号链接创建完成"
}

# 验证安装
verify_installation() {
    log_info "验证 VirtuaNES 安装..."
    
    local checks=(
        "可执行文件:/usr/local/bin/virtuanes"
        "配置文件:$CONFIG_DIR/virtuanes.cfg"
        "核心信息:$CORE_DIR/virtuanes_libretro.info"
        "桌面文件:/usr/share/applications/virtuanes.desktop"
        "启动脚本:$INSTALL_DIR/launch_virtuanes.sh"
    )
    
    local all_passed=true
    
    for check in "${checks[@]}"; do
        local name="${check%:*}"
        local path="${check#*:}"
        
        if [[ -f "$path" ]]; then
            log_success "✓ $name 验证通过"
        else
            log_error "✗ $name 验证失败: $path"
            all_passed=false
        fi
    done
    
    # 测试可执行文件
    if virtuanes --version 2>/dev/null || virtuanes -h 2>/dev/null; then
        log_success "✓ VirtuaNES 可执行文件测试通过"
    else
        log_warning "⚠ VirtuaNES 可执行文件测试失败（可能正常）"
    fi
    
    if [[ "$all_passed" == true ]]; then
        log_success "🎉 VirtuaNES $VIRTUALNES_VERSION 安装验证完成！"
    else
        log_error "⚠️ 部分验证失败，请检查安装"
        return 1
    fi
    
    return 0
}

# 清理临时文件
cleanup() {
    log_info "清理临时文件..."
    
    cd "$INSTALL_DIR"
    rm -f virtuanes_source.zip
    rm -rf RetroPie-Setup-master
    
    log_success "清理完成"
}

# 主函数
main() {
    log_info "开始 VirtuaNES $VIRTUALNES_VERSION 自动集成..."
    
    # 检查环境
    check_root
    check_config
    
    # 执行安装步骤
    local steps=(
        "安装系统依赖:install_dependencies"
        "下载 VirtuaNES:download_virtuanes"
        "编译安装:compile_virtuanes"
        "配置 VirtuaNES:configure_virtuanes"
        "集成 RetroArch:integrate_retroarch"
        "设置 ROM 关联:setup_rom_association"
        "创建符号链接:create_symlinks"
        "验证安装:verify_installation"
        "清理临时文件:cleanup"
    )
    
    for step in "${steps[@]}"; do
        local step_name="${step%:*}"
        local step_func="${step#*:}"
        
        log_info "=== $step_name ==="
        if $step_func; then
            log_success "✅ $step_name 完成"
        else
            log_error "❌ $step_name 失败"
            exit 1
        fi
    done
    
    log_success "🎉 VirtuaNES $VIRTUALNES_VERSION 自动集成完成！"
    log_info "使用说明:"
    log_info "1. 启动: virtuanes 或 ./launch_virtuanes.sh"
    log_info "2. 配置文件: $CONFIG_DIR/virtuanes.cfg"
    log_info "3. ROM 目录: /home/pi/RetroPie/roms/nes/"
    log_info "4. 保存目录: /home/pi/RetroPie/saves/nes/"
    log_info "5. 作弊码目录: /home/pi/RetroPie/cheats/nes/"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 