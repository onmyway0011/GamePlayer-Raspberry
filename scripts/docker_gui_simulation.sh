#!/bin/bash
# Docker GUI 树莓派模拟脚本

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
CONTAINER_NAME="gameplayer-gui"
IMAGE_NAME="gameplayer-raspberry:gui"
VNC_PORT=5901
NOVNC_PORT=6080
HTTP_PORT=8080

# 清理函数
cleanup() {
    log_info "清理 GUI 测试环境..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
}

# 信号处理
trap cleanup EXIT INT TERM

# 检查 Docker 状态
check_docker() {
    log_step "检查 Docker 环境..."
    
    if ! docker --version >/dev/null 2>&1; then
        log_error "Docker 未安装或未启动"
        exit 1
    fi
    
    if ! docker ps >/dev/null 2>&1; then
        log_error "Docker 守护进程未运行"
        exit 1
    fi
    
    log_success "Docker 环境正常"
}

# 构建 GUI 镜像
build_gui_image() {
    log_step "构建 GUI Docker 镜像..."
    
    if docker build -f Dockerfile.gui -t $IMAGE_NAME . 2>&1 | tee gui_build.log; then
        log_success "GUI Docker 镜像构建成功"
        return 0
    else
        log_error "GUI Docker 镜像构建失败"
        log_info "查看构建日志: gui_build.log"
        return 1
    fi
}

# 启动 GUI 容器
start_gui_container() {
    log_step "启动 GUI 容器..."
    
    # 清理旧容器
    cleanup
    
    # 启动新容器
    if docker run -d \
        --name $CONTAINER_NAME \
        -p $HTTP_PORT:8080 \
        -p $VNC_PORT:5901 \
        -p $NOVNC_PORT:6080 \
        --shm-size=1g \
        $IMAGE_NAME 2>&1 | tee gui_run.log; then
        
        log_success "GUI 容器启动成功"
        
        # 等待服务启动
        log_info "等待 GUI 服务启动..."
        sleep 10
        
        # 检查容器状态
        if docker ps | grep -q $CONTAINER_NAME; then
            log_success "容器运行状态正常"
            return 0
        else
            log_error "容器启动后异常退出"
            docker logs $CONTAINER_NAME
            return 1
        fi
    else
        log_error "GUI 容器启动失败"
        return 1
    fi
}

# 测试 GUI 服务
test_gui_services() {
    log_step "测试 GUI 服务..."
    
    # 测试 HTTP 服务
    log_info "测试 HTTP 服务 (端口 $HTTP_PORT)..."
    local http_test_count=0
    while [ $http_test_count -lt 10 ]; do
        if curl -f -s http://localhost:$HTTP_PORT >/dev/null 2>&1; then
            log_success "✅ HTTP 服务正常响应"
            break
        else
            log_info "等待 HTTP 服务启动... ($((http_test_count + 1))/10)"
            sleep 2
            ((http_test_count++))
        fi
    done
    
    # 测试 noVNC 服务
    log_info "测试 noVNC Web 服务 (端口 $NOVNC_PORT)..."
    local novnc_test_count=0
    while [ $novnc_test_count -lt 10 ]; do
        if curl -f -s http://localhost:$NOVNC_PORT >/dev/null 2>&1; then
            log_success "✅ noVNC Web 服务正常响应"
            break
        else
            log_info "等待 noVNC 服务启动... ($((novnc_test_count + 1))/10)"
            sleep 2
            ((novnc_test_count++))
        fi
    done
    
    # 测试 VNC 端口
    log_info "测试 VNC 服务 (端口 $VNC_PORT)..."
    if nc -z localhost $VNC_PORT 2>/dev/null; then
        log_success "✅ VNC 服务端口正常"
    else
        log_warning "⚠️ VNC 服务端口未响应"
    fi
    
    # 测试容器内部服务
    log_info "测试容器内部服务..."
    if docker exec $CONTAINER_NAME ps aux | grep -E "(Xvfb|fluxbox|x11vnc)" >/dev/null; then
        log_success "✅ GUI 服务进程正常运行"
    else
        log_warning "⚠️ 部分 GUI 服务可能未启动"
    fi
    
    return 0
}

# 启动演示游戏
start_demo_game() {
    log_step "启动演示游戏..."
    
    log_info "在容器中启动 Pygame 演示..."
    docker exec -d $CONTAINER_NAME /usr/local/bin/start-game.sh
    
    log_success "演示游戏已启动"
    log_info "请通过 VNC 查看游戏界面"
}

# 运行测试
run_tests() {
    log_step "运行单元测试..."
    
    if docker exec $CONTAINER_NAME python3 -m pytest tests/ -v --tb=short; then
        log_success "✅ 所有测试通过"
    else
        log_warning "⚠️ 部分测试失败，但 GUI 环境正常"
    fi
}

# 显示访问信息
show_access_info() {
    echo ""
    log_success "🎉 GUI 环境启动完成！"
    echo ""
    log_info "📱 访问方式:"
    echo "  🌐 Web VNC (推荐): http://localhost:$NOVNC_PORT/vnc.html"
    echo "  🔗 VNC 客户端: localhost:$VNC_PORT (密码: gameplayer)"
    echo "  📁 文件浏览器: http://localhost:$HTTP_PORT"
    echo ""
    log_info "🎮 游戏控制:"
    echo "  启动演示游戏: docker exec $CONTAINER_NAME /usr/local/bin/start-game.sh"
    echo "  停止游戏: 在 VNC 中按 ESC 键"
    echo ""
    log_info "🛠️ 管理命令:"
    echo "  查看容器状态: docker ps"
    echo "  查看容器日志: docker logs $CONTAINER_NAME"
    echo "  进入容器: docker exec -it $CONTAINER_NAME bash"
    echo "  停止容器: docker stop $CONTAINER_NAME"
    echo ""
    log_info "🧪 测试命令:"
    echo "  运行单元测试: docker exec $CONTAINER_NAME python3 -m pytest tests/ -v"
    echo "  检查 GUI 进程: docker exec $CONTAINER_NAME ps aux | grep -E '(Xvfb|fluxbox|x11vnc)'"
    echo ""
}

# 等待用户操作
wait_for_user() {
    echo ""
    log_info "🎮 GUI 环境已准备就绪！"
    echo ""
    echo "请选择操作:"
    echo "  1) 启动演示游戏"
    echo "  2) 运行单元测试"
    echo "  3) 查看容器日志"
    echo "  4) 退出并清理"
    echo ""
    
    while true; do
        read -p "请输入选择 (1-4): " choice
        case $choice in
            1)
                start_demo_game
                log_info "游戏已启动，请通过浏览器访问 http://localhost:$NOVNC_PORT/vnc.html 查看"
                ;;
            2)
                run_tests
                ;;
            3)
                echo ""
                log_info "最近的容器日志:"
                docker logs --tail 20 $CONTAINER_NAME
                echo ""
                ;;
            4)
                log_info "退出并清理环境..."
                break
                ;;
            *)
                log_warning "无效选择，请输入 1-4"
                ;;
        esac
        echo ""
    done
}

# 主函数
main() {
    echo "🚀 开始 Docker GUI 树莓派模拟..."
    echo ""
    
    # 检查环境
    check_docker
    
    # 构建镜像
    if ! build_gui_image; then
        log_error "镜像构建失败，退出"
        exit 1
    fi
    
    # 启动容器
    if ! start_gui_container; then
        log_error "容器启动失败，退出"
        exit 1
    fi
    
    # 测试服务
    if ! test_gui_services; then
        log_error "服务测试失败，退出"
        exit 1
    fi
    
    # 显示访问信息
    show_access_info
    
    # 等待用户操作
    wait_for_user
    
    log_success "🎉 GUI 模拟完成！"
}

# 运行主函数
main "$@"
