#!/bin/bash
# 快速GUI启动脚本 - 使用现有镜像

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🚀 GamePlayer-Raspberry 快速GUI启动"
echo "===================================="

# 检查是否有现有的GUI镜像
if docker images | grep -q "gameplayer-raspberry.*gui"; then
    IMAGE_NAME=$(docker images | grep "gameplayer-raspberry.*gui" | head -1 | awk '{print $1":"$2}')
    log_info "发现现有GUI镜像: $IMAGE_NAME"
else
    log_info "使用基础镜像创建GUI环境..."
    IMAGE_NAME="python:3.9-slim"
fi

CONTAINER_NAME="gameplayer-gui-quick"
VNC_PORT=5902
NOVNC_PORT=6081
HTTP_PORT=8081

# 停止现有容器
log_info "清理现有容器..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# 创建数据目录
mkdir -p data/roms data/saves data/logs

# 启动容器
log_info "启动GUI容器..."
docker run -d \
    --name $CONTAINER_NAME \
    -p $VNC_PORT:5901 \
    -p $NOVNC_PORT:6080 \
    -p $HTTP_PORT:8080 \
    -v "$(pwd):/app" \
    -w /app \
    --privileged \
    $IMAGE_NAME \
    bash -c "
    # 安装基础GUI组件
    apt-get update && apt-get install -y \
        xvfb x11vnc fluxbox \
        python3-pygame \
        wget curl \
        firefox-esr \
        >/dev/null 2>&1
    
    # 设置VNC
    export DISPLAY=:1
    Xvfb :1 -screen 0 1024x768x24 &
    sleep 2
    fluxbox &
    sleep 2
    x11vnc -display :1 -nopw -listen localhost -xkb -forever -shared &
    
    # 启动简单的HTTP服务器
    cd /app
    python3 -m http.server $HTTP_PORT &
    
    # 创建简单的游戏演示
    cat > /tmp/demo_game.py << 'EOF'
import pygame
import sys
import os

# 设置显示
os.environ['DISPLAY'] = ':1'

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('GamePlayer-Raspberry Demo')

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

clock = pygame.time.Clock()
running = True
x, y = 400, 300
dx, dy = 3, 3

print('🎮 游戏演示启动! 在VNC中查看')

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                dx, dy = -dx, -dy
    
    x += dx
    y += dy
    
    if x <= 20 or x >= 780:
        dx = -dx
    if y <= 20 or y >= 580:
        dy = -dy
    
    screen.fill(BLACK)
    pygame.draw.circle(screen, RED, (int(x), int(y)), 20)
    
    font = pygame.font.Font(None, 48)
    text = font.render('GamePlayer-Raspberry', True, WHITE)
    screen.blit(text, (150, 50))
    
    text2 = pygame.font.Font(None, 32).render('Press SPACE to reverse, ESC to exit', True, GREEN)
    screen.blit(text2, (180, 520))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
EOF
    
    # 启动游戏演示
    python3 /tmp/demo_game.py &
    
    echo '🎉 GUI环境启动完成!'
    echo '📱 访问: http://localhost:$NOVNC_PORT'
    echo '🎮 游戏已在VNC中运行'
    
    # 保持容器运行
    tail -f /dev/null
    "

if [ $? -eq 0 ]; then
    log_success "✅ 容器启动成功"
else
    log_error "❌ 容器启动失败"
    exit 1
fi

# 等待服务启动
log_info "等待服务启动..."
sleep 15

# 检查容器状态
if docker ps | grep -q $CONTAINER_NAME; then
    log_success "✅ 容器运行正常"
else
    log_error "❌ 容器未正常运行"
    docker logs $CONTAINER_NAME
    exit 1
fi

echo ""
echo "🎉 快速GUI环境启动完成！"
echo "=========================="
echo ""
echo "📱 访问方式："
echo "  🌐 Web界面: http://localhost:$NOVNC_PORT"
echo "  📁 文件浏览: http://localhost:$HTTP_PORT"
echo ""
echo "🎮 游戏控制："
echo "  空格键 - 改变方向"
echo "  ESC键  - 退出游戏"
echo ""
echo "🔧 管理命令："
echo "  查看日志: docker logs $CONTAINER_NAME"
echo "  停止容器: docker stop $CONTAINER_NAME"
echo ""

# 自动打开浏览器
if command -v open >/dev/null 2>&1; then
    log_info "正在打开浏览器..."
    open "http://localhost:$NOVNC_PORT"
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:$NOVNC_PORT"
else
    echo "请手动打开浏览器访问: http://localhost:$NOVNC_PORT"
fi

echo "🎮 享受游戏！"
