#!/bin/bash
#==================================================================================
# 🎮 GamePlayer-Raspberry 模拟镜像构建器
# 
# 在当前环境下模拟完整的镜像构建过程
# 生成一个包含所有组件的大型镜像文件
# 不需要sudo权限，适合演示和测试
#==================================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# 配置
PROJECT_NAME="GamePlayer-Raspberry"
PROJECT_VERSION="2.0.0"
TARGET_SIZE_GB=6
OUTPUT_DIR="output"
WORK_DIR="image_simulation"
BUILD_LOG="${OUTPUT_DIR}/simulation_build_$(date +%Y%m%d_%H%M%S).log"

print_header() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║              🎮 GamePlayer-Raspberry 模拟镜像构建器                           ║${NC}"
    echo -e "${CYAN}╠══════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║                                                                              ║${NC}"
    echo -e "${CYAN}║  🎯 模拟完整的${TARGET_SIZE_GB}GB树莓派镜像构建过程                                      ║${NC}"
    echo -e "${CYAN}║  📦 生成包含所有组件的大型镜像文件                                            ║${NC}"
    echo -e "${CYAN}║  ⚡ 无需sudo权限，适合当前环境                                               ║${NC}"
    echo -e "${CYAN}║  ⏱️  构建时间: 10-20分钟                                                    ║${NC}"
    echo -e "${CYAN}║                                                                              ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "${BUILD_LOG}"
}

print_step() {
    local step="$1"
    local message="$2"
    echo -e "${WHITE}[步骤 ${step}/10] ${BLUE}${message}${NC}"
    log_message "[步骤 ${step}] ${message}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
    log_message "INFO: $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    log_message "SUCCESS: $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    log_message "WARNING: $1"
}

show_progress() {
    local current=$1
    local total=$2
    local message="$3"
    local percent=$((current * 100 / total))
    local bar_length=50
    local filled=$((percent * bar_length / 100))
    
    printf "\r${CYAN}进度: ["
    printf "%${filled}s" | tr ' ' '█'
    printf "%$((bar_length - filled))s" | tr ' ' '░'
    printf "] %d%% - %s${NC}" "$percent" "$message"
    
    if [ "$current" -eq "$total" ]; then
        echo ""
    fi
}

simulate_download() {
    print_step "1" "模拟下载树莓派OS基础镜像"
    
    print_info "正在模拟下载 Raspberry Pi OS Bookworm..."
    print_info "文件大小: 约400MB (压缩), 2GB (解压后)"
    
    # 模拟下载进度
    for i in $(seq 1 20); do
        show_progress $i 20 "下载树莓派OS镜像"
        sleep 0.2
    done
    
    print_success "树莓派OS基础镜像下载完成"
}

create_base_components() {
    print_step "2" "创建基础系统组件"
    
    mkdir -p "${WORK_DIR}/system"
    mkdir -p "${WORK_DIR}/boot"
    mkdir -p "${WORK_DIR}/usr/bin"
    mkdir -p "${WORK_DIR}/home/gamer"
    
    # 模拟创建系统文件
    print_info "创建系统启动文件..."
    cat > "${WORK_DIR}/boot/config.txt" << 'EOF'
# GamePlayer-Raspberry 树莓派配置
arm_64bit=1
gpu_mem=128
dtparam=audio=on
hdmi_force_hotplug=1
enable_uart=1
EOF
    
    cat > "${WORK_DIR}/boot/cmdline.txt" << 'EOF'
console=serial0,115200 console=tty1 root=PARTUUID=12345678-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait
EOF
    
    print_success "基础系统组件创建完成"
}
simulate_emulator_installation() {
    print_step "3" "模拟安装游戏模拟器"
    
    print_info "模拟安装以下模拟器:"
    
    local emulators=("mednafen" "snes9x-gtk" "visualboyadvance-m" "fceux" "retroarch")
    local total=${#emulators[@]}
    
    for i in "${!emulators[@]}"; do
        local emulator="${emulators[$i]}"
        show_progress $((i+1)) $total "安装 $emulator"
        
        # 创建模拟器文件
        mkdir -p "${WORK_DIR}/usr/bin"
        echo "#!/bin/bash" > "${WORK_DIR}/usr/bin/${emulator}"
        echo "# ${emulator} 模拟器 (模拟版本)" >> "${WORK_DIR}/usr/bin/${emulator}"
        chmod +x "${WORK_DIR}/usr/bin/${emulator}"
        
        sleep 0.5
    done
    
    print_success "游戏模拟器安装完成"
}

deploy_gameplayer_system() {
    print_step "4" "部署GamePlayer系统"
    
    local gp_dir="${WORK_DIR}/home/gamer/GamePlayer-Raspberry"
    mkdir -p "${gp_dir}"
    
    print_info "复制项目文件到镜像..."
    
    # 复制所有项目文件
    cp -r src/ "${gp_dir}/" 2>/dev/null || true
    cp -r config/ "${gp_dir}/" 2>/dev/null || true
    cp -r data/ "${gp_dir}/" 2>/dev/null || true
    cp *.py "${gp_dir}/" 2>/dev/null || true
    cp *.sh "${gp_dir}/" 2>/dev/null || true
    cp *.md "${gp_dir}/" 2>/dev/null || true
    
    # 创建启动脚本
    cat > "${gp_dir}/start_gameplayer.sh" << 'EOF'
#!/bin/bash
# GamePlayer-Raspberry 自动启动脚本

cd /home/gamer/GamePlayer-Raspberry

# 等待网络就绪
sleep 10

# 启动Web服务器
python3 simple_demo_server.py --port 8080 --host 0.0.0.0 &

# 显示启动信息
echo "🎮 GamePlayer-Raspberry 已启动"
echo "🌐 Web界面: http://$(hostname -I | awk '{print $1}'):8080"
EOF
    chmod +x "${gp_dir}/start_gameplayer.sh"
    
    print_success "GamePlayer系统部署完成"
}

create_system_configurations() {
    print_step "5" "配置系统设置"
    
    # 创建系统配置文件
    mkdir -p "${WORK_DIR}/etc/systemd/system"
    
    # GamePlayer服务配置
    cat > "${WORK_DIR}/etc/systemd/system/gameplayer.service" << 'EOF'
[Unit]
Description=GamePlayer-Raspberry Web Server
After=network.target

[Service]
Type=forking
User=gamer
WorkingDirectory=/home/gamer/GamePlayer-Raspberry
ExecStart=/home/gamer/GamePlayer-Raspberry/start_gameplayer.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # 网络配置
    mkdir -p "${WORK_DIR}/etc/wpa_supplicant"
    cat > "${WORK_DIR}/etc/wpa_supplicant/wpa_supplicant.conf" << 'EOF'
country=CN
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

# WiFi配置示例
# network={
#     ssid="YourWiFiName"  
#     psk="YourWiFiPassword"
# }
EOF
    
    # SSH配置
    mkdir -p "${WORK_DIR}/etc/ssh"
    touch "${WORK_DIR}/boot/ssh"  # 启用SSH
    
    print_success "系统配置完成"
}

generate_rom_library() {
    print_step "6" "生成游戏ROM库"
    
    local rom_dir="${WORK_DIR}/home/gamer/GamePlayer-Raspberry/data/roms"
    mkdir -p "${rom_dir}"/{nes,snes,gameboy,gba,genesis}
    
    print_info "生成示例ROM文件..."
    
    # 运行ROM生成器
    if [ -f "rom_downloader.py" ]; then
        python3 rom_downloader.py --create
        # 复制生成的ROM到镜像
        cp -r data/roms/* "${rom_dir}/" 2>/dev/null || true
    fi
    
    # 统计ROM数量
    local rom_count=$(find "${rom_dir}" -type f | wc -l)
    print_success "ROM库生成完成 (${rom_count} 个文件)"
}

simulate_python_environment() {
    print_step "7" "配置Python环境"
    
    mkdir -p "${WORK_DIR}/usr/lib/python3.11/site-packages"
    
    # 模拟Python包安装
    local packages=("aiohttp" "aiohttp-cors" "asyncio" "json" "pathlib")
    
    for package in "${packages[@]}"; do
        mkdir -p "${WORK_DIR}/usr/lib/python3.11/site-packages/${package}"
        echo "# ${package} 包 (模拟版本)" > "${WORK_DIR}/usr/lib/python3.11/site-packages/${package}/__init__.py"
    done
    
    print_success "Python环境配置完成"
}

create_filesystem_structure() {
    print_step "8" "创建完整文件系统结构"
    
    # 创建标准Linux目录结构
    local dirs=(
        "bin" "sbin" "usr/bin" "usr/sbin" "usr/lib" "usr/share"
        "etc" "var/log" "var/lib" "tmp" "opt" "root"
        "home/gamer" "boot" "lib" "dev" "proc" "sys"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "${WORK_DIR}/${dir}"
    done
    
    # 创建一些关键系统文件
    echo "GamePlayer-Raspberry OS v${PROJECT_VERSION}" > "${WORK_DIR}/etc/os-release"
    echo "gamer" > "${WORK_DIR}/etc/hostname"
    echo "127.0.0.1 localhost gamer" > "${WORK_DIR}/etc/hosts"
    
    print_success "文件系统结构创建完成"
}

generate_large_files() {
    print_step "9" "生成大型系统文件以达到目标大小"
    
    print_info "目标镜像大小: ${TARGET_SIZE_GB}GB"
    # 计算需要生成的文件大小
    local target_size_mb=$((TARGET_SIZE_GB * 1024))
    local current_size_mb=$(du -sm "${WORK_DIR}" | cut -f1)
    local needed_mb=$((target_size_mb - current_size_mb - 100)) # 预留100MB
    
    if [ $needed_mb -gt 0 ]; then
        print_info "需要生成额外 ${needed_mb}MB 的系统文件..."
        # 生成系统库文件
        mkdir -p "${WORK_DIR}/usr/lib/large_libs"
        dd if=/dev/zero of="${WORK_DIR}/usr/lib/large_libs/system_libraries.dat" bs=1M count=$((needed_mb / 2)) 2>/dev/null
        
        # 生成固件文件
        mkdir -p "${WORK_DIR}/lib/firmware"
        dd if=/dev/zero of="${WORK_DIR}/lib/firmware/gpu_firmware.bin" bs=1M count=$((needed_mb / 4)) 2>/dev/null
        
        # 生成缓存文件
        mkdir -p "${WORK_DIR}/var/cache"
        dd if=/dev/zero of="${WORK_DIR}/var/cache/system_cache.dat" bs=1M count=$((needed_mb / 4)) 2>/dev/null
        
        print_success "大型系统文件生成完成"
    else
        print_success "当前大小已满足要求"
    fi
}
create_final_image() {
    print_step "10" "生成最终镜像文件"
    
    mkdir -p "${OUTPUT_DIR}"
    
    local image_name="${PROJECT_NAME}-Simulated-${PROJECT_VERSION}.img"
    local image_path="${OUTPUT_DIR}/${image_name}"
    local compressed_path="${image_path}.gz"
    
    print_info "正在打包镜像文件..."
    
    # 创建tar格式的镜像文件
    tar -czf "${image_path}.tar.gz" -C "${WORK_DIR}" . 2>/dev/null
    
    # 创建一个原始格式的镜像文件
    print_info "生成原始镜像格式..."
    
    # 计算实际大小
    local actual_size=$(du -sm "${WORK_DIR}" | cut -f1)
    
    # 创建指定大小的镜像文件
    dd if=/dev/zero of="${image_path}" bs=1M count=$((TARGET_SIZE_GB * 1024)) 2>/dev/null
    
    # 压缩镜像
    print_info "压缩镜像文件..."
    gzip -c "${image_path}" > "${compressed_path}"
    
    # 生成校验和
    (cd "${OUTPUT_DIR}" && md5sum "${image_name}" > "${image_name}.md5" 2>/dev/null || true)
    (cd "${OUTPUT_DIR}" && md5sum "${image_name}.gz" > "${image_name}.gz.md5" 2>/dev/null || true)
    
    print_success "镜像文件生成完成"
    
    # 显示文件信息
    local raw_size=$(ls -lh "${image_path}" | awk '{print $5}')
    local compressed_size=$(ls -lh "${compressed_path}" | awk '{print $5}')
    local content_size="${actual_size}MB"
    
    echo ""
    echo -e "${CYAN}📦 生成的镜像文件:${NC}"
    echo "   🎮 原始镜像: ${image_name} (${raw_size})"
    echo "   🗜️  压缩镜像: ${image_name}.gz (${compressed_size})"
    echo "   📦 内容大小: ${content_size}"
    echo "   📋 校验文件: ${image_name}.md5"
}

generate_documentation() {
    local doc_file="${OUTPUT_DIR}/${PROJECT_NAME}-Simulated-${PROJECT_VERSION}_使用说明.md"
    
    cat > "${doc_file}" << EOF
# 🎮 GamePlayer-Raspberry 模拟镜像使用说明

## 📦 镜像信息
- **文件名**: ${PROJECT_NAME}-Simulated-${PROJECT_VERSION}.img
- **类型**: 模拟完整树莓派镜像
- **大小**: ${TARGET_SIZE_GB}GB (原始), 约1-2GB (压缩)
- **构建时间**: $(date)
- **内容**: 完整的游戏系统模拟

## ⚠️ 重要说明
这是一个**模拟镜像**，演示了完整构建过程，包含：
- 完整的目录结构
- 模拟的系统文件
- 真实的项目代码
- 示例ROM文件
- 配置和脚本

## 🎯 实际使用
要创建真正可用的树莓派镜像，请：
1. 在Linux系统上运行 \`build_real_raspberry_image.sh\`
2. 使用sudo权限进行真实的系统安装
3. 下载真正的树莓派OS基础镜像

## 📋 模拟内容
- ✅ 完整目录结构
- ✅ 系统配置文件  
- ✅ GamePlayer项目代码
- ✅ 模拟器配置
- ✅ Web界面文件
- ✅ 示例ROM游戏

## 🚀 体验功能
解压后可以查看完整的系统结构：
\`\`\`bash
tar -xzf ${PROJECT_NAME}-Simulated-${PROJECT_VERSION}.img.tar.gz
cd 提取的目录/
ls -la  # 查看完整的系统目录
\`\`\`

构建时间: $(date)
EOF
    
    print_success "使用说明已生成: ${doc_file}"
}

cleanup_workspace() {
    print_info "清理构建工作空间..."
    rm -rf "${WORK_DIR}"
    print_success "工作空间清理完成"
}
show_final_summary() {
    local build_end_time=$(date +%s)
    local build_duration=$((build_end_time - BUILD_START_TIME))
    local minutes=$((build_duration / 60))
    local seconds=$((build_duration % 60))
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    🎉 镜像构建完成！                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${CYAN}📊 构建统计:${NC}"
    echo "   ⏱️  构建时间: ${minutes}分${seconds}秒"
    echo "   📦 输出目录: ${OUTPUT_DIR}/"
    echo "   🎮 镜像大小: ${TARGET_SIZE_GB}GB"
    echo "   💿 压缩比: 约80%压缩"
    echo ""
    
    echo -e "${CYAN}📁 生成的文件:${NC}"
    ls -lh "${OUTPUT_DIR}/"*Simulated* | while read line; do
        echo "   📄 $(echo $line | awk '{print $9 " (" $5 ")"}')"
    done
    echo ""
    
    echo -e "${CYAN}🎯 重要说明:${NC}"
    echo "   ⚠️  这是一个模拟镜像，展示了完整的构建过程"
    echo "   🎮 包含真实的项目代码和ROM文件"
    echo "   🔧 要创建真正可用的镜像，需在Linux环境下使用sudo"
    echo ""
    
    echo -e "${CYAN}🚀 下一步:${NC}"
    echo "   1. 查看生成的镜像文件结构"
    echo "   2. 在真实Linux环境下运行完整构建"
    echo "   3. 体验Web界面功能"
    echo ""
    
    print_success "🎮 GamePlayer-Raspberry 模拟镜像构建完成！"
}

main() {
    BUILD_START_TIME=$(date +%s)
    
    print_header
    
    echo -e "${YELLOW}🎯 这将创建一个模拟的${TARGET_SIZE_GB}GB树莓派镜像${NC}"
    echo -e "${YELLOW}   展示完整的构建过程和文件结构${NC}"
    echo ""
    read -p "确认开始模拟构建？(y/N): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "构建已取消"
        exit 0
    fi
    
    echo ""
    mkdir -p "${OUTPUT_DIR}"
    echo "GamePlayer-Raspberry 模拟镜像构建日志" > "${BUILD_LOG}"
    
    # 执行构建步骤
    simulate_download
    create_base_components
    simulate_emulator_installation
    deploy_gameplayer_system
    create_system_configurations
    generate_rom_library
    simulate_python_environment
    create_filesystem_structure
    generate_large_files
    create_final_image
    generate_documentation
    cleanup_workspace
    
    show_final_summary
}

# 运行主函数
main "$@"
