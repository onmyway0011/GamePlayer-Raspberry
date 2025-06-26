#!/bin/bash
# 树莓派Docker模拟环境启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${PURPLE}[STEP]${NC} $1"; }

# 全局变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONTAINER_NAME="gameplayer-raspberry-sim"
IMAGE_NAME="gameplayer-raspberry:raspberry-sim"

# 显示横幅
show_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              GamePlayer-Raspberry 树莓派模拟环境            ║"
    echo "║                                                              ║"
    echo "║  🍓 完整树莓派环境模拟                                      ║"
    echo "║  🎮 50款NES游戏                                             ║"
    echo "║  🖥️ VNC图形界面                                             ║"
    echo "║  🐳 Docker容器化                                            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 检查Docker
check_docker() {
    log_step "检查Docker环境..."
    
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker服务未运行，请启动Docker"
        exit 1
    fi
    
    log_success "✅ Docker环境正常"
}

# 构建Docker镜像
build_image() {
    log_step "构建树莓派模拟镜像..."
    
    cd "$PROJECT_ROOT"
    
    # 检查是否需要重新构建
    if docker images | grep -q "$IMAGE_NAME"; then
        log_info "镜像已存在，检查是否需要更新..."
        
        # 检查Dockerfile是否有更新
        if [ "Dockerfile.raspberry-sim" -nt "$(docker inspect --format='{{.Created}}' $IMAGE_NAME 2>/dev/null || echo '1970-01-01')" ]; then
            log_info "Dockerfile已更新，重新构建镜像..."
        else
            log_info "镜像是最新的，跳过构建"
            return 0
        fi
    fi
    
    log_info "开始构建镜像（这可能需要几分钟）..."
    
    # 构建镜像
    if docker build -f Dockerfile.raspberry-sim -t "$IMAGE_NAME" .; then
        log_success "✅ 镜像构建完成"
    else
        log_error "❌ 镜像构建失败"
        exit 1
    fi
}

# 停止现有容器
stop_existing_container() {
    log_step "检查现有容器..."
    
    if docker ps -a | grep -q "$CONTAINER_NAME"; then
        log_info "停止现有容器..."
        docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
        docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true
        log_success "✅ 现有容器已清理"
    fi
}

# 启动容器
start_container() {
    log_step "启动树莓派模拟容器..."
    
    # 启动容器
    docker run -d \
        --name "$CONTAINER_NAME" \
        --platform linux/arm64 \
        -p 5901:5901 \
        -p 6080:6080 \
        -p 8080:8080 \
        --shm-size=1g \
        --privileged \
        "$IMAGE_NAME"
    
    if [ $? -eq 0 ]; then
        log_success "✅ 容器启动成功"
    else
        log_error "❌ 容器启动失败"
        exit 1
    fi
}

# 等待服务就绪
wait_for_services() {
    log_step "等待服务启动..."
    
    local max_wait=60
    local wait_time=0
    
    while [ $wait_time -lt $max_wait ]; do
        if curl -s http://localhost:6080 >/dev/null 2>&1; then
            log_success "✅ VNC服务已就绪"
            break
        fi
        
        echo -n "."
        sleep 2
        wait_time=$((wait_time + 2))
    done
    
    if [ $wait_time -ge $max_wait ]; then
        log_warning "⚠️ VNC服务启动超时，但容器可能仍在初始化"
    fi
    
    echo ""
}

# 下载50款ROM文件
download_50_roms() {
    log_step "下载50款NES游戏..."

    log_info "在容器中执行ROM下载..."
    docker exec "$CONTAINER_NAME" bash -c "
        cd /home/pi/GamePlayer-Raspberry
        python3 scripts/rom_downloader.py --output /home/pi/RetroPie/roms/nes
        echo '✅ ROM下载完成'

        # 列出下载的游戏
        echo '📋 已下载的游戏:'
        python3 scripts/rom_manager.py --roms-dir /home/pi/RetroPie/roms/nes list | head -20

        # 统计游戏数量
        rom_count=\$(find /home/pi/RetroPie/roms/nes -name '*.nes' | wc -l)
        echo \"🎮 总计: \$rom_count 款游戏\"
    "
}

# 启动Web管理界面
start_web_manager() {
    log_step "启动Web管理界面..."

    # 检查是否已有Web管理容器
    if docker ps -a | grep -q "gameplayer-web-manager"; then
        log_info "停止现有Web管理容器..."
        docker stop gameplayer-web-manager >/dev/null 2>&1 || true
        docker rm gameplayer-web-manager >/dev/null 2>&1 || true
    fi

    # 构建Web管理镜像
    log_info "构建Web管理界面镜像..."
    cd "$PROJECT_ROOT"
    docker build -f Dockerfile.web-manager -t gameplayer-web:latest .

    # 启动Web管理容器
    log_info "启动Web管理容器..."
    docker run -d \
        --name gameplayer-web-manager \
        -p 3000:3000 \
        -v "$PROJECT_ROOT/test_50_roms:/app/roms:ro" \
        -v "$PROJECT_ROOT/saves:/app/saves:rw" \
        -v "$PROJECT_ROOT/configs:/app/configs:rw" \
        --link "$CONTAINER_NAME:raspberry-sim" \
        gameplayer-web:latest

    if [ $? -eq 0 ]; then
        log_success "✅ Web管理界面启动成功"
        log_info "📱 访问地址: http://localhost:3000"
    else
        log_error "❌ Web管理界面启动失败"
    fi
}

# 显示访问信息
show_access_info() {
    log_success "🎉 树莓派模拟环境启动完成！"
    echo ""
    echo -e "${CYAN}📱 访问方式:${NC}"
    echo -e "  🖥️  VNC Web界面: ${GREEN}http://localhost:6080/vnc.html${NC}"
    echo -e "  🌐  Web管理界面: ${GREEN}http://localhost:3000${NC}"
    echo -e "  📁  文件浏览器: ${GREEN}http://localhost:8080${NC}"
    echo -e "  🔌  VNC客户端: ${GREEN}localhost:5901${NC} (无密码)"
    echo ""
    echo -e "${CYAN}🎮 游戏功能:${NC}"
    echo -e "  🚀  启动游戏选择器: ${YELLOW}docker exec -it $CONTAINER_NAME /home/pi/start-nes-games.sh${NC}"
    echo -e "  📋  查看游戏列表: ${YELLOW}docker exec $CONTAINER_NAME python3 /home/pi/GamePlayer-Raspberry/scripts/rom_manager.py --roms-dir /home/pi/RetroPie/roms/nes list${NC}"
    echo ""
    echo -e "${CYAN}🛠️ 管理命令:${NC}"
    echo -e "  📊  查看容器状态: ${YELLOW}docker ps${NC}"
    echo -e "  📝  查看容器日志: ${YELLOW}docker logs $CONTAINER_NAME${NC}"
    echo -e "  🔧  进入容器: ${YELLOW}docker exec -it $CONTAINER_NAME bash${NC}"
    echo -e "  🛑  停止容器: ${YELLOW}docker stop $CONTAINER_NAME${NC}"
    echo ""
    echo -e "${CYAN}🍓 树莓派环境特性:${NC}"
    echo -e "  👤  用户: ${GREEN}pi${NC} (密码: raspberry)"
    echo -e "  📁  主目录: ${GREEN}/home/pi${NC}"
    echo -e "  🎮  ROM目录: ${GREEN}/home/pi/RetroPie/roms/nes${NC}"
    echo -e "  ⚙️   配置目录: ${GREEN}/home/pi/RetroPie/configs${NC}"
    echo ""
}

# 启动游戏界面
launch_game_interface() {
    log_step "启动游戏选择界面..."
    
    # 在容器中启动游戏启动器
    docker exec -d "$CONTAINER_NAME" bash -c "
        export DISPLAY=:1
        cd /home/pi/GamePlayer-Raspberry
        python3 scripts/nes_game_launcher.py --roms-dir /home/pi/RetroPie/roms/nes
    " >/dev/null 2>&1
    
    log_success "✅ 游戏界面已启动"
    log_info "请在VNC界面中查看游戏选择器"
}

# 主菜单
show_menu() {
    echo ""
    echo -e "${CYAN}请选择操作:${NC}"
    echo "1) 🚀 启动完整环境（推荐）"
    echo "2) 🎮 仅启动游戏界面"
    echo "3) 📥 下载50款NES游戏"
    echo "4) 🌐 启动Web管理界面"
    echo "5) 🔧 进入容器终端"
    echo "6) 📊 查看容器状态"
    echo "7) 🛑 停止并清理"
    echo "8) ❌ 退出"
    echo ""
    read -p "请输入选择 (1-8): " choice
    
    case $choice in
        1)
            full_setup
            ;;
        2)
            launch_game_interface
            ;;
        3)
            download_50_roms
            ;;
        4)
            start_web_manager
            ;;
        5)
            docker exec -it "$CONTAINER_NAME" bash
            ;;
        6)
            docker ps -a | grep "$CONTAINER_NAME"
            docker logs --tail 20 "$CONTAINER_NAME"
            ;;
        7)
            cleanup
            ;;
        8)
            log_info "👋 再见！"
            exit 0
            ;;
        *)
            log_error "无效选择，请重试"
            show_menu
            ;;
    esac
}

# 完整设置
full_setup() {
    check_docker
    build_image
    stop_existing_container
    start_container
    wait_for_services
    download_50_roms
    launch_game_interface
    start_web_manager
    show_access_info
}

# 清理
cleanup() {
    log_step "清理环境..."
    
    if docker ps | grep -q "$CONTAINER_NAME"; then
        docker stop "$CONTAINER_NAME"
    fi
    
    if docker ps -a | grep -q "$CONTAINER_NAME"; then
        docker rm "$CONTAINER_NAME"
    fi
    
    log_success "✅ 环境已清理"
}

# 主函数
main() {
    show_banner
    
    # 检查参数
    if [ "$1" = "--auto" ]; then
        full_setup
        exit 0
    elif [ "$1" = "--cleanup" ]; then
        cleanup
        exit 0
    fi
    
    # 检查容器是否已运行
    if docker ps | grep -q "$CONTAINER_NAME"; then
        log_info "检测到容器正在运行"
        show_access_info
        show_menu
    else
        show_menu
    fi
}

# 信号处理
trap 'log_error "脚本被中断"; cleanup; exit 1' INT TERM

# 运行主函数
main "$@"
