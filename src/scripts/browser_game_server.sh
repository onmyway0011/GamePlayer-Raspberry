#!/bin/bash
# 浏览器游戏服务器 - 直接在浏览器中运行游戏

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🎮 GamePlayer-Raspberry 浏览器游戏服务器"
echo "========================================"

CONTAINER_NAME="gameplayer-browser"
WEB_PORT=3000

# 清理现有容器
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

echo -e "${BLUE}[INFO]${NC} 启动浏览器游戏服务器..."

# 创建游戏HTML文件
mkdir -p data/web
cat > data/web/index.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 GamePlayer-Raspberry</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            font-family: 'Courier New', monospace;
            color: white;
            text-align: center;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        h1 {
            color: #00ff00;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            margin-bottom: 30px;
        }
        canvas {
            border: 3px solid #00ff00;
            border-radius: 10px;
            background: #000;
            box-shadow: 0 0 20px rgba(0,255,0,0.3);
        }
        .controls {
            margin: 20px 0;
            padding: 15px;
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            border: 1px solid #00ff00;
        }
        .score {
            font-size: 24px;
            color: #ffff00;
            margin: 10px 0;
        }
        .instructions {
            margin: 20px 0;
            font-size: 16px;
            line-height: 1.6;
        }
        .key {
            background: #333;
            color: #00ff00;
            padding: 5px 10px;
            border-radius: 5px;
            margin: 0 5px;
            border: 1px solid #00ff00;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 GamePlayer-Raspberry</h1>
        <div class="score">得分: <span id="score">0</span></div>
        
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        
        <div class="controls">
            <div class="instructions">
                <h3>🕹️ 游戏控制</h3>
                <p>
                    <span class="key">W</span> <span class="key">A</span> <span class="key">S</span> <span class="key">D</span> 或 方向键 - 移动
                </p>
                <p>
                    <span class="key">空格</span> - 发射子弹 | <span class="key">R</span> - 重新开始
                </p>
            </div>
        </div>
        
        <div class="instructions">
            <h3>🎯 游戏目标</h3>
            <p>控制绿色飞船，射击红色敌人，避免碰撞！</p>
            <p>这是一个经典的NES风格射击游戏</p>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreElement = document.getElementById('score');

        // 游戏状态
        let score = 0;
        let gameRunning = true;
        
        // 玩家
        const player = {
            x: canvas.width / 2,
            y: canvas.height - 50,
            width: 30,
            height: 30,
            speed: 5,
            color: '#00ff00'
        };

        // 子弹数组
        const bullets = [];
        const bulletSpeed = 7;

        // 敌人数组
        const enemies = [];
        const enemySpeed = 2;

        // 按键状态
        const keys = {};

        // 事件监听
        document.addEventListener('keydown', (e) => {
            keys[e.key.toLowerCase()] = true;
            if (e.key === ' ') {
                e.preventDefault();
                shootBullet();
            }
            if (e.key.toLowerCase() === 'r') {
                resetGame();
            }
        });

        document.addEventListener('keyup', (e) => {
            keys[e.key.toLowerCase()] = false;
        });

        // 射击子弹
        function shootBullet() {
            bullets.push({
                x: player.x + player.width / 2,
                y: player.y,
                width: 4,
                height: 10,
                color: '#ffff00'
            });
        }

        // 创建敌人
        function createEnemy() {
            enemies.push({
                x: Math.random() * (canvas.width - 30),
                y: -30,
                width: 25,
                height: 25,
                color: '#ff0000'
            });
        }

        // 更新游戏
        function update() {
            if (!gameRunning) return;

            // 移动玩家
            if (keys['w'] || keys['arrowup']) player.y = Math.max(0, player.y - player.speed);
            if (keys['s'] || keys['arrowdown']) player.y = Math.min(canvas.height - player.height, player.y + player.speed);
            if (keys['a'] || keys['arrowleft']) player.x = Math.max(0, player.x - player.speed);
            if (keys['d'] || keys['arrowright']) player.x = Math.min(canvas.width - player.width, player.x + player.speed);

            // 更新子弹
            for (let i = bullets.length - 1; i >= 0; i--) {
                bullets[i].y -= bulletSpeed;
                if (bullets[i].y < 0) {
                    bullets.splice(i, 1);
                }
            }

            // 更新敌人
            for (let i = enemies.length - 1; i >= 0; i--) {
                enemies[i].y += enemySpeed;
                if (enemies[i].y > canvas.height) {
                    enemies.splice(i, 1);
                }
            }

            // 检查子弹与敌人碰撞
            for (let i = bullets.length - 1; i >= 0; i--) {
                for (let j = enemies.length - 1; j >= 0; j--) {
                    if (bullets[i] && enemies[j] && 
                        bullets[i].x < enemies[j].x + enemies[j].width &&
                        bullets[i].x + bullets[i].width > enemies[j].x &&
                        bullets[i].y < enemies[j].y + enemies[j].height &&
                        bullets[i].y + bullets[i].height > enemies[j].y) {
                        
                        bullets.splice(i, 1);
                        enemies.splice(j, 1);
                        score += 10;
                        scoreElement.textContent = score;
                        break;
                    }
                }
            }

            // 检查玩家与敌人碰撞
            for (let enemy of enemies) {
                if (player.x < enemy.x + enemy.width &&
                    player.x + player.width > enemy.x &&
                    player.y < enemy.y + enemy.height &&
                    player.y + player.height > enemy.y) {
                    
                    gameRunning = false;
                    alert(`游戏结束！最终得分: ${score}\n按R键重新开始`);
                }
            }

            // 随机生成敌人
            if (Math.random() < 0.02) {
                createEnemy();
            }
        }

        // 绘制游戏
        function draw() {
            // 清空画布
            ctx.fillStyle = '#000011';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // 绘制星空背景
            ctx.fillStyle = '#ffffff';
            for (let i = 0; i < 50; i++) {
                const x = (Date.now() * 0.01 + i * 123) % canvas.width;
                const y = (Date.now() * 0.02 + i * 456) % canvas.height;
                ctx.fillRect(x, y, 1, 1);
            }

            // 绘制玩家
            ctx.fillStyle = player.color;
            ctx.fillRect(player.x, player.y, player.width, player.height);
            
            // 绘制玩家细节
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(player.x + 5, player.y + 5, 20, 5);
            ctx.fillRect(player.x + 12, player.y, 6, 15);

            // 绘制子弹
            ctx.fillStyle = '#ffff00';
            for (let bullet of bullets) {
                ctx.fillRect(bullet.x, bullet.y, bullet.width, bullet.height);
            }

            // 绘制敌人
            for (let enemy of enemies) {
                ctx.fillStyle = enemy.color;
                ctx.fillRect(enemy.x, enemy.y, enemy.width, enemy.height);
                
                // 敌人细节
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(enemy.x + 5, enemy.y + 5, 15, 3);
                ctx.fillRect(enemy.x + 10, enemy.y + 15, 5, 8);
            }

            // 绘制游戏标题
            if (!gameRunning) {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                ctx.fillStyle = '#ff0000';
                ctx.font = '48px Courier New';
                ctx.textAlign = 'center';
                ctx.fillText('游戏结束', canvas.width / 2, canvas.height / 2);
                
                ctx.fillStyle = '#ffffff';
                ctx.font = '24px Courier New';
                ctx.fillText('按 R 键重新开始', canvas.width / 2, canvas.height / 2 + 50);
            }
        }

        // 重置游戏
        function resetGame() {
            score = 0;
            scoreElement.textContent = score;
            gameRunning = true;
            bullets.length = 0;
            enemies.length = 0;
            player.x = canvas.width / 2;
            player.y = canvas.height - 50;
        }

        // 游戏循环
        function gameLoop() {
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }

        // 启动游戏
        console.log('🎮 GamePlayer-Raspberry 浏览器游戏启动!');
        gameLoop();
    </script>
</body>
</html>
EOF

# 启动Web服务器容器
docker run -d \
    --name $CONTAINER_NAME \
    -p $WEB_PORT:80 \
    -v "$(pwd)/data/web:/usr/share/nginx/html:ro" \
    nginx:alpine

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[SUCCESS]${NC} ✅ 游戏服务器启动成功"
else
    echo "❌ 服务器启动失败"
    exit 1
fi

# 等待服务启动
echo -e "${BLUE}[INFO]${NC} 等待Web服务启动..."
sleep 5

# 检查服务状态
if docker ps | grep -q $CONTAINER_NAME; then
    echo -e "${GREEN}[SUCCESS]${NC} ✅ Web服务运行正常"
else
    echo "❌ Web服务未正常运行"
    docker logs $CONTAINER_NAME
    exit 1
fi

echo ""
echo "🎉 浏览器游戏服务器启动完成！"
echo "==============================="
echo ""
echo "📱 访问方式："
echo "  🌐 游戏地址: http://localhost:$WEB_PORT"
echo ""
echo "🎮 游戏特色："
echo "  • 经典NES风格射击游戏"
echo "  • 直接在浏览器中运行"
echo "  • 支持键盘控制"
echo "  • 实时得分系统"
echo ""
echo "🕹️ 控制说明："
echo "  WASD/方向键 - 移动飞船"
echo "  空格键 - 发射子弹"
echo "  R键 - 重新开始"
echo ""
echo "🔧 管理命令："
echo "  查看日志: docker logs $CONTAINER_NAME"
echo "  停止服务: docker stop $CONTAINER_NAME"
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

echo "🎮 享受经典NES风格游戏！"
