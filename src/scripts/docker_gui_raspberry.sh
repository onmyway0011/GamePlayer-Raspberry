#!/bin/bash
# Docker GUI 树莓派游戏系统启动脚本

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

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 配置变量
IMAGE_NAME="gameplayer-raspberry-gui"
CONTAINER_NAME="gameplayer-gui"
VNC_PORT=5901
NOVNC_PORT=6080
HTTP_PORT=8080

echo "🎮 GamePlayer-Raspberry GUI Docker 环境"
echo "========================================"
echo "🍓 树莓派模拟系统 + 图形界面 + Web访问"
echo ""

# 1. 检查Docker状态
log_step "1. 检查Docker环境..."
if ! docker info >/dev/null 2>&1; then
    log_error "❌ Docker未运行，请启动Docker Desktop"
    exit 1
fi
log_success "✅ Docker运行正常"

# 2. 停止现有容器
log_step "2. 清理现有容器..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true
log_success "✅ 容器清理完成"

# 3. 创建必要的目录
log_step "3. 创建数据目录..."
mkdir -p data/roms/nes
mkdir -p data/saves
mkdir -p data/cheats
mkdir -p data/logs
mkdir -p config/system
log_success "✅ 目录创建完成"

# 4. 构建Docker镜像
log_step "4. 构建GUI镜像..."
if docker build -f build/docker/Dockerfile.gui -t $IMAGE_NAME . 2>&1 | tee build.log; then
    log_success "✅ 镜像构建成功"
else
    log_error "❌ 镜像构建失败，查看 build.log 了解详情"
    exit 1
fi

# 5. 启动容器
log_step "5. 启动GUI容器..."
docker run -d \
    --name $CONTAINER_NAME \
    --platform linux/amd64 \
    -p $VNC_PORT:5901 \
    -p $NOVNC_PORT:6080 \
    -p $HTTP_PORT:8080 \
    -v "$(pwd)/data/roms:/app/roms:rw" \
    -v "$(pwd)/data/saves:/app/saves:rw" \
    -v "$(pwd)/data/cheats:/app/cheats:rw" \
    -v "$(pwd)/config:/app/config:rw" \
    --shm-size=1g \
    --privileged \
    $IMAGE_NAME

if [ $? -eq 0 ]; then
    log_success "✅ 容器启动成功"
else
    log_error "❌ 容器启动失败"
    exit 1
fi

# 6. 等待服务启动
log_step "6. 等待服务启动..."
sleep 10

# 7. 检查服务状态
log_step "7. 检查服务状态..."
if docker ps | grep -q $CONTAINER_NAME; then
    log_success "✅ 容器运行正常"
else
    log_error "❌ 容器未正常运行"
    docker logs $CONTAINER_NAME
    exit 1
fi

# 8. 测试Web服务
log_step "8. 测试Web服务..."
sleep 5
if curl -s http://localhost:$NOVNC_PORT >/dev/null; then
    log_success "✅ Web VNC服务正常"
else
    log_warning "⚠️ Web VNC服务可能还在启动中"
fi

# 9. 显示访问信息
echo ""
echo "🎉 树莓派GUI系统启动完成！"
echo "================================"
echo ""
echo "📱 访问方式："
echo "  🌐 Web VNC:    http://localhost:$NOVNC_PORT"
echo "  🖥️ VNC客户端:  localhost:$VNC_PORT"
echo "  📁 文件服务:   http://localhost:$HTTP_PORT"
echo ""
echo "🎮 游戏控制："
echo "  WASD / 方向键  →  移动"
echo "  空格 / Z       →  A按钮"
echo "  Shift / X      →  B按钮"
echo "  Enter          →  Start"
echo "  Tab            →  Select"
echo "  ESC            →  退出游戏"
echo ""
echo "🔧 管理命令："
echo "  查看日志: docker logs $CONTAINER_NAME"
echo "  进入容器: docker exec -it $CONTAINER_NAME bash"
echo "  停止容器: docker stop $CONTAINER_NAME"
echo "  重启容器: docker restart $CONTAINER_NAME"
echo ""
echo "📋 下一步："
echo "  1. 打开浏览器访问: http://localhost:$NOVNC_PORT"
echo "  2. 点击 'Connect' 连接到桌面"
echo "  3. 启动游戏模拟器"
echo "  4. 享受游戏！"
echo ""

# 10. 自动打开浏览器（可选）
read -p "🌐 是否自动打开浏览器？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "正在打开浏览器..."
    if command -v open >/dev/null 2>&1; then
        open "http://localhost:$NOVNC_PORT"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "http://localhost:$NOVNC_PORT"
    else
        log_warning "无法自动打开浏览器，请手动访问: http://localhost:$NOVNC_PORT"
    fi
fi

echo "🎮 GamePlayer-Raspberry GUI 系统已就绪！"
