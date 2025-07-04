#!/bin/bash
# 简单的Web VNC游戏环境

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🎮 GamePlayer-Raspberry Web VNC"
echo "==============================="

CONTAINER_NAME="gameplayer-web-vnc"
VNC_PORT=5903
WEB_PORT=6082

# 清理现有容器
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

echo -e "${BLUE}[INFO]${NC} 启动Web VNC游戏环境..."

# 启动容器
docker run -d \
    --name $CONTAINER_NAME \
    -p $VNC_PORT:5901 \
    -p $WEB_PORT:6080 \
    -e VNC_PW=password \
    -e VNC_RESOLUTION=1024x768 \
    -v "$(pwd):/workspace" \
    --shm-size=512m \
    consol/ubuntu-xfce-vnc:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[SUCCESS]${NC} ✅ 容器启动成功"
else
    echo "❌ 容器启动失败"
    exit 1
fi

# 等待服务启动
echo -e "${BLUE}[INFO]${NC} 等待VNC服务启动..."
sleep 15

# 检查服务状态
if docker ps | grep -q $CONTAINER_NAME; then
    echo -e "${GREEN}[SUCCESS]${NC} ✅ VNC服务运行正常"
else
    echo "❌ VNC服务未正常运行"
    docker logs $CONTAINER_NAME
    exit 1
fi

# 在容器中安装游戏环境
echo -e "${BLUE}[INFO]${NC} 安装游戏环境..."
docker exec $CONTAINER_NAME bash -c "
    apt-get update >/dev/null 2>&1
    apt-get install -y python3-pygame python3-pip >/dev/null 2>&1
    
    # 创建简单的NES风格游戏
    cat > /tmp/nes_game.py << 'EOF'
import pygame
import sys
import random
import math

# 初始化pygame
pygame.init()

# 设置屏幕
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('🎮 GamePlayer-Raspberry - NES Style Game')

# 颜色 (NES调色板)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (252, 116, 96)
GREEN = (0, 168, 0)
BLUE = (0, 88, 248)
YELLOW = (252, 188, 176)
PURPLE = (188, 0, 188)
CYAN = (0, 184, 248)

# 游戏变量
clock = pygame.time.Clock()
running = True
player_x, player_y = WIDTH // 2, HEIGHT // 2
player_speed = 5
enemies = []
score = 0
font = pygame.font.Font(None, 36)

# 创建敌人
for i in range(5):
    enemy_x = random.randint(50, WIDTH - 50)
    enemy_y = random.randint(50, HEIGHT - 50)
    enemies.append([enemy_x, enemy_y, random.choice([RED, PURPLE, CYAN])])

print('🎮 NES风格游戏启动!')
print('🕹️ 使用WASD移动，ESC退出')

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # 获取按键状态
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player_y = max(20, player_y - player_speed)
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player_y = min(HEIGHT - 20, player_y + player_speed)
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player_x = max(20, player_x - player_speed)
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player_x = min(WIDTH - 20, player_x + player_speed)
    
    # 移动敌人
    for enemy in enemies:
        enemy[0] += random.randint(-2, 2)
        enemy[1] += random.randint(-2, 2)
        enemy[0] = max(20, min(WIDTH - 20, enemy[0]))
        enemy[1] = max(20, min(HEIGHT - 20, enemy[1]))
        
        # 检查碰撞
        dist = math.sqrt((player_x - enemy[0])**2 + (player_y - enemy[1])**2)
        if dist < 30:
            score += 10
            enemy[0] = random.randint(50, WIDTH - 50)
            enemy[1] = random.randint(50, HEIGHT - 50)
    
    # 绘制
    screen.fill(BLACK)
    
    # 绘制玩家
    pygame.draw.circle(screen, GREEN, (int(player_x), int(player_y)), 15)
    pygame.draw.circle(screen, WHITE, (int(player_x), int(player_y)), 15, 2)
    
    # 绘制敌人
    for enemy in enemies:
        pygame.draw.rect(screen, enemy[2], (enemy[0]-10, enemy[1]-10, 20, 20))
        pygame.draw.rect(screen, WHITE, (enemy[0]-10, enemy[1]-10, 20, 20), 2)
    
    # 绘制UI
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (10, 10))
    
    title_text = font.render('GamePlayer-Raspberry', True, YELLOW)
    screen.blit(title_text, (WIDTH//2 - 150, 10))
    
    controls_text = pygame.font.Font(None, 24).render('WASD: Move | ESC: Exit', True, WHITE)
    screen.blit(controls_text, (10, HEIGHT - 30))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print(f'🎉 游戏结束! 最终得分: {score}')
EOF

    # 启动游戏
    export DISPLAY=:1
    python3 /tmp/nes_game.py &
    
    echo '🎮 游戏已在VNC中启动!'
"

echo ""
echo "🎉 Web VNC游戏环境启动完成！"
echo "============================="
echo ""
echo "📱 访问方式："
echo "  🌐 Web VNC: http://localhost:$WEB_PORT"
echo "  🔑 密码: password"
echo ""
echo "🎮 游戏说明："
echo "  • 绿色圆圈是玩家"
echo "  • 彩色方块是敌人"
echo "  • 碰撞敌人获得分数"
echo "  • WASD键移动，ESC退出"
echo ""
echo "🔧 管理命令："
echo "  查看日志: docker logs $CONTAINER_NAME"
echo "  停止容器: docker stop $CONTAINER_NAME"
echo ""

# 自动打开浏览器
if command -v open >/dev/null 2>&1; then
    echo -e "${BLUE}[INFO]${NC} 正在打开浏览器..."
    open "http://localhost:$WEB_PORT"
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:$WEB_PORT"
else
    echo "请手动打开浏览器访问: http://localhost:$WEB_PORT"
fi

echo "🎮 享受NES风格游戏！"
