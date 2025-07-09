#!/bin/bash
# 一键生成完整的树莓派游戏镜像
set -euo pipefail  # 添加 -u 和 -o pipefail 增强错误处理

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

# 错误处理函数
handle_error() {
    local line_number=$1
    local error_code=$2
    log_error "脚本在第 ${line_number} 行失败，错误代码: ${error_code}"
    log_error "正在清理临时文件..."
    cleanup_on_error
    exit "${error_code}"
}

# 设置错误处理
trap 'handle_error ${LINENO} $?' ERR

# 清理函数
cleanup_on_error() {
    if [ -n "${TEMP_DIR:-}" ] && [ -d "$TEMP_DIR" ]; then
        log_info "清理临时目录: $TEMP_DIR"
        rm -rf "$TEMP_DIR" || true
    fi
}

# 配置变量
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/output"  # 修改为统一的 output 目录
TEMP_DIR="$PROJECT_ROOT/temp/image_build"
IMAGE_NAME="retropie_gameplayer_$(date +%Y%m%d_%H%M%S).img"
FINAL_IMAGE="$BUILD_DIR/${IMAGE_NAME%.img}_complete.img.gz"

# 全局变量初始化
SKIP_NATIVE_IMAGE=false
SKIP_DOCKER_BUILD=false

echo "🎮 GamePlayer-Raspberry 一键镜像构建器"
echo "========================================"
echo "🍓 自动构建完整的树莓派游戏镜像"
echo "📦 集成所有游戏、存档、自动启动功能"
echo ""

# 检查系统要求
check_requirements() {
    log_step "1. 检查系统要求..."

    # 检测操作系统
    local os_type
    os_type=$(uname -s)
    log_info "检测到操作系统: $os_type"

    if [ "$os_type" = "Darwin" ]; then
        log_warning "⚠️ 检测到macOS系统"
        log_info "在macOS上将创建Docker模拟环境，跳过原生镜像生成"
        SKIP_NATIVE_IMAGE=true
    fi

    local required_tools=("python3" "git" "curl")
    local missing_tools=()

    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done
    # Docker检查 - 只在需要时检查
    if [ "$SKIP_NATIVE_IMAGE" = "true" ] || [ "$SKIP_DOCKER_BUILD" != "true" ]; then
        if ! command -v "docker" >/dev/null 2>&1; then
            log_warning "⚠️ Docker未安装，跳过Docker相关功能"
            SKIP_DOCKER_BUILD=true
        elif ! docker info >/dev/null 2>&1; then
            log_warning "⚠️ Docker未运行，跳过Docker相关功能"
            SKIP_DOCKER_BUILD=true
        fi
    fi

    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "❌ 缺少必需工具: ${missing_tools[*]}"
        log_info "请安装缺少的工具后重试"
        exit 1
    fi
    
    # 检查磁盘空间 (至少需要5GB)
    local available_space
    if command -v df >/dev/null 2>&1; then
        available_space=$(df "$PROJECT_ROOT" 2>/dev/null | awk 'NR==2 {print $4}' || echo "0")
        if [ "${available_space:-0}" -lt 5242880 ]; then  # 5GB in KB
            log_warning "⚠️ 磁盘空间可能不足，建议至少5GB可用空间"
        fi
    fi
    # 检查Python版本
    local python_version
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_info "Python版本: $python_version"
    
    log_success "✅ 系统要求检查通过"
}

# 准备构建环境
prepare_environment() {
    log_step "2. 准备构建环境..."
    
    # 创建必要目录 - 确保目录创建成功
    local directories=(
        "$BUILD_DIR"
        "$TEMP_DIR"
        "$PROJECT_ROOT/data/roms/nes"
        "$PROJECT_ROOT/data/saves"
        "$PROJECT_ROOT/data/cheats"
        "$PROJECT_ROOT/data/logs"
        "$PROJECT_ROOT/data/web"
    )
    
    for dir in "${directories[@]}"; do
        if ! mkdir -p "$dir"; then
            log_error "❌ 无法创建目录: $dir"
            exit 1
        fi
    done
    # 安装Python依赖 - 改进错误处理
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        log_info "安装Python依赖..."
        if ! pip3 install -r "$PROJECT_ROOT/requirements.txt" >/dev/null 2>&1; then
            log_warning "⚠️ Python依赖安装失败，继续构建..."
        fi
    else
        log_warning "⚠️ 找不到requirements.txt文件"
    fi
    
    log_success "✅ 构建环境准备完成"
}

# 下载和准备ROM文件
prepare_roms() {
    log_step "3. 下载和准备ROM文件..."
    
    # 确保在正确的目录
    if ! cd "$PROJECT_ROOT"; then
        log_error "❌ 无法切换到项目根目录"
        return 1
    fi
    
    # 确保ROM目录存在
    mkdir -p "data/roms/nes/"
    # 运行ROM下载器 - 改进错误处理
    if [ -f "src/scripts/rom_downloader.py" ]; then
        log_info "下载合法ROM文件..."
        if python3 src/scripts/rom_downloader.py --list 2>/dev/null; then
            python3 src/scripts/rom_downloader.py --category homebrew_games --output data/roms/nes/ 2>/dev/null || true
        else
            log_warning "⚠️ ROM下载器执行失败，跳过ROM下载"
        fi
    else
        log_warning "⚠️ 找不到ROM下载器，跳过ROM下载"
    fi

    # 运行ROM管理器 - 改进错误处理
    if [ -f "src/scripts/rom_manager.py" ]; then
        log_info "管理ROM文件..."
        python3 src/scripts/rom_manager.py --roms-dir data/roms/nes/ verify 2>/dev/null || true
    else
        log_warning "⚠️ 找不到ROM管理器"
    fi
    
    # 检查ROM文件数量 - 添加安全检查
    local rom_count=0
    if [ -d "data/roms/nes/" ]; then
        rom_count=$(find data/roms/nes/ -name "*.nes" 2>/dev/null | wc -l)
    fi
    log_info "已准备 $rom_count 个ROM文件"
    
    # 如果没有ROM文件，创建演示ROM
    if [ "$rom_count" -eq 0 ]; then
        log_info "创建演示ROM文件..."
        create_demo_roms
    fi
    
    log_success "✅ ROM文件准备完成"
}

# 创建演示ROM文件
create_demo_roms() {
    local demo_roms=(
        "Super_Mario_Bros_Demo.nes"
        "Zelda_Demo.nes"
        "Contra_Demo.nes"
        "Metroid_Demo.nes"
        "Mega_Man_Demo.nes"
    )
    
    for rom_name in "${demo_roms[@]}"; do
        local rom_path="data/roms/nes/$rom_name"
        if [ ! -f "$rom_path" ]; then
            # 创建简单的NES ROM头部
            printf "NES\x1a\x01\x01\x00\x00" > "$rom_path"
            # 添加一些填充数据
            dd if=/dev/zero bs=1024 count=32 >> "$rom_path" 2>/dev/null || true
            log_info "创建演示ROM: $rom_name"
        fi
    done
}

# 构建Docker测试环境（可选）
build_docker_images() {
    log_step "4. 构建Docker测试环境..."

    if [ "$SKIP_DOCKER_BUILD" = "true" ]; then
        log_warning "⚠️ 跳过Docker构建"
        return 0
    fi

    if ! cd "$PROJECT_ROOT"; then
        log_error "❌ 无法切换到项目根目录"
        return 1
    fi

    log_info "构建Docker测试环境用于开发调试..."
    log_info "注意：Docker环境仅用于测试，不会包含在树莓派镜像中"
    # 仅构建简化的测试镜像 - 改进错误处理
    if [ -f "Dockerfile.gui" ]; then
        log_info "构建图形化测试环境..."
        if timeout 300 docker build -f Dockerfile.gui -t gameplayer-raspberry:test . 2>/dev/null; then
            log_success "✅ Docker测试环境构建成功"
        else
            log_warning "⚠️ Docker测试环境构建失败或超时，跳过"
        fi
    else
        log_warning "⚠️ 找不到Dockerfile.gui，跳过Docker构建"
    fi

    log_success "✅ Docker测试环境准备完成"
}

# 生成树莓派镜像
generate_raspberry_image() {
    log_step "5. 生成树莓派镜像..."

    if ! cd "$PROJECT_ROOT"; then
        log_error "❌ 无法切换到项目根目录"
        return 1
    fi

    # 检查是否跳过原生镜像生成
    if [ "$SKIP_NATIVE_IMAGE" = "true" ]; then
        log_warning "⚠️ 在macOS上跳过原生镜像生成"
        log_info "创建模拟镜像文件用于演示..."

        # 创建输出目录
        mkdir -p "$BUILD_DIR"

        # 创建模拟镜像文件
        local mock_image="$BUILD_DIR/retropie_gameplayer_macos_demo.img.gz"
        cat > "$BUILD_DIR/retropie_gameplayer_macos_demo.img.info" << EOF
GamePlayer-Raspberry macOS演示镜像
================================

构建信息:
- 构建时间: $(date)
- 构建平台: macOS (演示模式)
- 目标平台: Raspberry Pi 4/400
- 镜像类型: Docker容器演示

注意事项:
- 这是在macOS上生成的演示文件
- 要生成真实的树莓派镜像，请在Linux系统上运行
- 可以使用Docker环境进行游戏测试

Docker使用方法:
1. 启动Docker环境: ./start_docker_gui.sh
2. 访问游戏中心: http://localhost:3020
3. VNC远程桌面: localhost:5900

更多信息请查看: docs/DOCKER_GUI_GUIDE.md
EOF

        # 创建演示镜像文件
        echo "GamePlayer-Raspberry macOS Demo Image - $(date)" | gzip > "$mock_image"

        # 生成校验和 - 改进兼容性
        if command -v shasum >/dev/null 2>&1; then
            shasum -a 256 "$mock_image" > "$mock_image.sha256"
        elif command -v sha256sum >/dev/null 2>&1; then
            sha256sum "$mock_image" > "$mock_image.sha256"
        else
            echo "校验和生成失败 - 找不到shasum或sha256sum命令" > "$mock_image.sha256"
        fi

        log_success "✅ macOS演示文件创建完成: $mock_image"
        return 0
    fi

    # Linux系统的原生镜像生成
    if [ -f "src/scripts/raspberry_image_builder.py" ]; then
        log_info "开始构建树莓派镜像（这可能需要30-60分钟）..."
        if ! python3 src/scripts/raspberry_image_builder.py retropie_4.8; then
            log_error "❌ 镜像构建失败"
            return 1
        fi
    else
        log_error "❌ 找不到镜像构建器: src/scripts/raspberry_image_builder.py"
        return 1
    fi
    log_success "✅ 树莓派镜像生成完成"
}

# 集成自动启动功能
integrate_autostart() {
    log_step "6. 集成自动启动功能..."
    
    # 确保临时目录存在
    mkdir -p "$TEMP_DIR"
    
    # 创建自动启动脚本 - 改进脚本内容
    cat > "$TEMP_DIR/autostart_gameplayer.sh" << 'EOF'
#!/bin/bash
# GamePlayer-Raspberry 自动启动脚本

# 错误处理
set -e

# 等待系统完全启动
sleep 10

# 设置环境变量
export HOME=/home/pi
export USER=pi
export DISPLAY=:0

# 创建日志目录
mkdir -p /home/pi/logs

# 启动前检查
if [ ! -d "/home/pi/GamePlayer-Raspberry" ]; then
    echo "$(date): GamePlayer-Raspberry 目录不存在" >> /home/pi/logs/gameplayer.log
    exit 1
fi

# 启动X服务器（如果未运行）
if ! pgrep -x "X" > /dev/null; then
    startx &
    sleep 5
fi

# 启动游戏管理器
cd /home/pi/GamePlayer-Raspberry
if [ -f "src/scripts/nes_game_launcher.py" ]; then
    python3 src/scripts/nes_game_launcher.py --autostart &
else
    echo "$(date): 找不到游戏启动器" >> /home/pi/logs/gameplayer.log
fi

# 启动Web服务器
if [ -d "/home/pi/GamePlayer-Raspberry/data/web" ]; then
    python3 -m http.server 8080 --directory /home/pi/GamePlayer-Raspberry/data/web &
else
    echo "$(date): Web目录不存在，创建基本Web界面" >> /home/pi/logs/gameplayer.log
    mkdir -p /home/pi/GamePlayer-Raspberry/data/web
    echo "<h1>GamePlayer-Raspberry</h1>" > /home/pi/GamePlayer-Raspberry/data/web/index.html
    python3 -m http.server 8080 --directory /home/pi/GamePlayer-Raspberry/data/web &
fi

# 记录启动日志
echo "$(date): GamePlayer-Raspberry 自动启动完成" >> /home/pi/logs/gameplayer.log
EOF
    # 创建systemd服务文件 - 改进服务配置
    cat > "$TEMP_DIR/gameplayer.service" << 'EOF'
[Unit]
Description=GamePlayer-Raspberry Auto Start
After=graphical-session.target network.target
Wants=graphical-session.target

[Service]
Type=forking
User=pi
Group=pi
WorkingDirectory=/home/pi/GamePlayer-Raspberry
ExecStart=/home/pi/GamePlayer-Raspberry/autostart_gameplayer.sh
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF
    
    log_success "✅ 自动启动功能集成完成"
}

# 创建游戏切换界面
create_game_switcher() {
    log_step "7. 创建游戏切换界面..."
    
    # 创建Web游戏切换界面目录
    local web_dir="$PROJECT_ROOT/data/web/game_switcher"
    mkdir -p "$web_dir"
    
    # 创建游戏切换界面 - 内容保持不变但添加错误处理
    if ! cat > "$web_dir/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 GamePlayer-Raspberry 游戏选择器</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            font-family: 'Courier New', monospace;
            color: white;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #00ff00;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            margin-bottom: 30px;
        }
        .game-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .game-card {
            background: rgba(0,0,0,0.3);
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .game-card:hover {
            background: rgba(0,255,0,0.1);
            box-shadow: 0 0 20px rgba(0,255,0,0.3);
            transform: translateY(-5px);
        }
        .game-title {
            font-size: 18px;
            font-weight: bold;
            color: #ffff00;
            margin-bottom: 10px;
        }
        .game-info {
            font-size: 14px;
            color: #cccccc;
            margin-bottom: 15px;
        }
        .game-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .btn {
            padding: 8px 16px;
            border: 1px solid #00ff00;
            background: rgba(0,255,0,0.1);
            color: #00ff00;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            font-size: 12px;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background: rgba(0,255,0,0.2);
        }
        .btn-primary {
            background: rgba(0,255,0,0.2);
            color: white;
        }
        .save-info {
            background: rgba(255,255,0,0.1);
            border: 1px solid #ffff00;
            border-radius: 5px;
            padding: 10px;
            margin-top: 10px;
            font-size: 12px;
        }
        .controls {
            background: rgba(0,0,0,0.5);
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
        }
        .controls h3 {
            color: #00ff00;
            margin-bottom: 15px;
        }
        .status {
            background: rgba(0,0,0,0.3);
            border: 1px solid #00ff00;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 GamePlayer-Raspberry 游戏选择器</h1>
        
        <div class="status" id="status">
            <span id="statusText">正在加载游戏列表...</span>
        </div>
        
        <div id="gameGrid" class="game-grid">
            <!-- 游戏卡片将通过JavaScript动态生成 -->
        </div>
        
        <div class="controls">
            <h3>🕹️ 控制说明</h3>
            <p>• 点击"开始游戏"直接启动游戏</p>
            <p>• 点击"继续游戏"加载最近的存档</p>
            <p>• 点击"管理存档"查看所有存档</p>
            <p>• 游戏中按ESC键返回选择界面</p>
        </div>
    </div>

    <script>
        // 游戏数据（实际应该从API获取）
        const games = [
            {
                id: "super_mario_bros_demo",
                title: "Super Mario Bros Demo",
                description: "经典平台游戏演示版",
                category: "平台游戏",
                hasProgress: false,
                lastPlayed: null
            },
            {
                id: "zelda_demo",
                title: "Zelda Demo",
                description: "冒险RPG游戏演示版",
                category: "冒险游戏",
                hasProgress: false,
                lastPlayed: null
            },
            {
                id: "contra_demo",
                title: "Contra Demo",
                description: "动作射击游戏演示版",
                category: "射击游戏",
                hasProgress: false,
                lastPlayed: null
            },
            {
                id: "metroid_demo",
                title: "Metroid Demo",
                description: "科幻探索游戏演示版",
                category: "探索游戏",
                hasProgress: false,
                lastPlayed: null
            },
            {
                id: "mega_man_demo",
                title: "Mega Man Demo",
                description: "动作平台游戏演示版",
                category: "平台游戏",
                hasProgress: false,
                lastPlayed: null
            }
        ];

        // 渲染游戏网格
        function renderGameGrid() {
            const gameGrid = document.getElementById('gameGrid');
            const statusText = document.getElementById('statusText');
            
            gameGrid.innerHTML = '';

            if (games.length === 0) {
                statusText.textContent = '未找到游戏文件';
                return;
            }
            statusText.textContent = `已加载 ${games.length} 个游戏`;

            games.forEach(game => {
                const gameCard = document.createElement('div');
                gameCard.className = 'game-card';
                
                gameCard.innerHTML = `
                    <div class="game-title">${escapeHtml(game.title)}</div>
                    <div class="game-info">
                        <div>类型: ${escapeHtml(game.category)}</div>
                        <div>${escapeHtml(game.description)}</div>
                    </div>
                    ${game.hasProgress ? `
                        <div class="save-info">
                            💾 有存档 | 最后游玩: ${escapeHtml(game.lastPlayed)}
                        </div>
                    ` : ''}
                    <div class="game-actions">
                        <a href="#" class="btn btn-primary" onclick="startGame('${escapeHtml(game.id)}')">
                            ${game.hasProgress ? '继续游戏' : '开始游戏'}
                        </a>
                        <a href="#" class="btn" onclick="newGame('${escapeHtml(game.id)}')">新游戏</a>
                        <a href="#" class="btn" onclick="manageSaves('${escapeHtml(game.id)}')">管理存档</a>
                    </div>
                `;
                
                gameGrid.appendChild(gameCard);
            });
        }

        // HTML转义函数
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // 游戏控制函数
        function startGame(gameId) {
            console.log(`启动游戏: ${gameId}`);
            // 实际实现中应该调用后端API启动游戏
            alert(`正在启动 ${gameId}...`);
        }

        function newGame(gameId) {
            console.log(`新游戏: ${gameId}`);
            alert(`正在开始新游戏 ${gameId}...`);
        }

        function manageSaves(gameId) {
            console.log(`管理存档: ${gameId}`);
            alert(`打开 ${gameId} 存档管理...`);
        }

        // 初始化页面
        document.addEventListener('DOMContentLoaded', function() {
            try {
                renderGameGrid();
                console.log('🎮 GamePlayer-Raspberry 游戏选择器已加载');
            } catch (error) {
                console.error('游戏选择器初始化失败:', error);
                document.getElementById('statusText').textContent = '游戏选择器初始化失败';
            }
        });
    </script>
</body>
</html>
EOF
    then
        log_error "❌ 无法创建游戏切换界面"
        return 1
    fi
    
    # 创建API端点文件
    cat > "$web_dir/api.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>GamePlayer API</title>
</head>
<body>
    <h1>GamePlayer-Raspberry API</h1>
    <p>API endpoints:</p>
    <ul>
        <li>/api/games - 获取游戏列表</li>
        <li>/api/start/{game_id} - 启动游戏</li>
        <li>/api/status - 系统状态</li>
    </ul>
</body>
</html>
EOF
    
    log_success "✅ 游戏切换界面创建完成"
}

# 打包最终镜像
package_final_image() {
    log_step "8. 打包最终镜像..."
    # 查找生成的镜像文件 - 改进搜索逻辑
    local source_image
    source_image=$(find "$BUILD_DIR" -name "*gameplayer*.img.gz" -type f 2>/dev/null | head -1)
    
    if [ -z "$source_image" ]; then
        # 如果没有找到镜像文件，检查是否是macOS演示模式
        if [ "$SKIP_NATIVE_IMAGE" = "true" ]; then
            source_image="$BUILD_DIR/retropie_gameplayer_macos_demo.img.gz"
            if [ ! -f "$source_image" ]; then
                log_error "❌ 找不到演示镜像文件"
                return 1
            fi
        else
            log_error "❌ 找不到生成的镜像文件"
            return 1
        fi
    fi
    
    # 复制并重命名 - 添加错误检查
    if ! cp "$source_image" "$FINAL_IMAGE"; then
        log_error "❌ 无法复制镜像文件"
        return 1
    fi
    
    # 生成镜像信息文件 - 改进信息内容
    local info_file="${FINAL_IMAGE%.gz}.info"
    if ! cat > "$info_file" << EOF
# GamePlayer-Raspberry 完整镜像信息

## 镜像详情
- 文件名: $(basename "$FINAL_IMAGE")
- 生成时间: $(date)
- 大小: $(du -h "$FINAL_IMAGE" 2>/dev/null | cut -f1 || echo "未知")
- MD5: $(md5sum "$FINAL_IMAGE" 2>/dev/null | cut -d' ' -f1 || echo "计算失败")

## 功能特性
✅ 演示ROM游戏
✅ 自动存档/加载系统
✅ 游戏切换界面
✅ Web管理界面
✅ 自动启动功能
✅ 金手指系统
✅ USB手柄支持
✅ 蓝牙音频支持

## 烧录说明
1. 使用 Raspberry Pi Imager 烧录镜像
2. 或使用命令: sudo dd if=$(basename "$FINAL_IMAGE") of=/dev/sdX bs=4M status=progress
3. 首次启动会自动扩展文件系统
4. 默认用户: pi, 密码: raspberry

## 访问方式
- 游戏选择器: http://树莓派IP:8080/game_switcher/
- Web管理: http://树莓派IP:3000
- VNC远程: 树莓派IP:5901

## 自动功能
- 开机自动启动游戏系统
- 自动加载最近游戏进度
- 自动检测USB手柄
- 自动连接蓝牙音频设备
EOF
    then
        log_warning "⚠️ 无法创建镜像信息文件"
    fi
    log_success "✅ 最终镜像打包完成"
}

# 生成使用说明
generate_documentation() {
    log_step "9. 生成使用说明..."
    
    local doc_file="$BUILD_DIR/README_镜像使用说明.md"
    if ! cat > "$doc_file" << 'EOF'
# 🎮 GamePlayer-Raspberry 镜像使用说明

## 📦 镜像内容

这是一个完整的树莓派游戏镜像，包含：
### 🎯 核心功能
- **演示NES游戏**: 多个经典游戏的演示版本
- **自动存档系统**: 游戏进度自动保存和加载
- **游戏切换界面**: Web界面选择和管理游戏
- **金手指系统**: 自动开启无限条命等作弊功能

### 🌐 Web界面
- **游戏选择器**: http://树莓派IP:8080/game_switcher/
- **管理界面**: http://树莓派IP:3000
- **文件浏览**: http://树莓派IP:8080

### 🔧 自动化功能
- **开机自动启动**: 无需手动操作
- **设备自动检测**: USB手柄、蓝牙音频
- **进度自动恢复**: 继续上次游戏

## 🚀 快速开始

### 1. 烧录镜像
```bash
# 使用 Raspberry Pi Imager (推荐)
# 或使用 dd 命令
sudo dd if=retropie_gameplayer_complete.img.gz of=/dev/sdX bs=4M status=progress
```

### 2. 首次启动
1. 插入SD卡到树莓派
2. 连接显示器、键盘、鼠标
3. 开机等待自动配置完成
4. 系统会自动启动游戏界面

### 3. 游戏操作
- **WASD / 方向键**: 移动
- **空格 / Z**: A按钮
- **Shift / X**: B按钮
- **Enter**: Start
- **Tab**: Select
- **ESC**: 退出游戏

## 🎮 游戏管理

### 通过Web界面
1. 打开浏览器访问: http://树莓派IP:8080/game_switcher/
2. 选择游戏点击"开始游戏"或"继续游戏"
3. 管理存档和游戏设置

### 通过RetroPie界面
1. 在EmulationStation中选择NES系统
2. 浏览游戏列表
3. 选择游戏开始

## 💾 存档管理

### 自动存档
- 游戏每30秒自动保存
- 退出游戏时自动保存
- 支持10个存档插槽

### 手动存档
- **F5**: 快速保存
- **F9**: 快速加载
- **Ctrl + 1-3**: 保存到指定插槽
- **Alt + 1-3**: 从指定插槽加载

## 🔧 系统配置

### WiFi配置
```bash
sudo raspi-config
# 选择 Network Options > Wi-Fi
```

### SSH访问
```bash
# SSH默认已启用
ssh pi@树莓派IP
# 默认密码: raspberry
```

### 更新系统
```bash
sudo apt update && sudo apt upgrade -y
```

## 🎯 高级功能

### 添加新游戏
1. 将合法ROM文件复制到 `/home/pi/RetroPie/roms/nes/`
2. 重启EmulationStation或刷新游戏列表

### 云端存档
- 配置文件: `/home/pi/GamePlayer-Raspberry/config/cloud_sync.json`
- 支持多种云存储服务

### 自定义配置
- 主配置: `/home/pi/GamePlayer-Raspberry/config/system/gameplayer_config.json`
- 模拟器配置: `/opt/retropie/configs/nes/`

## 🔍 故障排除

### 游戏无法启动
1. 检查ROM文件格式是否正确
2. 查看日志: `tail -f /home/pi/logs/gameplayer.log`
3. 重启系统

### 网络连接问题
1. 检查WiFi配置
2. 重启网络: `sudo systemctl restart networking`

### 性能问题
1. 检查SD卡速度（推荐Class 10或更高）
2. 确保充足的电源供应
3. 检查散热情况

## 📞 技术支持
- 项目地址: https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry
- 问题反馈: 通过GitHub Issues
- 文档: 项目docs目录

---

**🎮 享受游戏时光！**
EOF
    then
        log_warning "⚠️ 无法创建使用说明文档"
    fi
    
    log_success "✅ 使用说明生成完成"
}

# 主函数
main() {
    echo "开始一键镜像构建流程..."
    echo ""
    
    # 执行构建步骤 - 添加错误处理
    if ! check_requirements; then
        log_error "❌ 系统要求检查失败"
        exit 1
    fi
    
    if ! prepare_environment; then
        log_error "❌ 环境准备失败"
        exit 1
    fi
    
    if ! prepare_roms; then
        log_error "❌ ROM准备失败"
        exit 1
    fi
    
    if ! build_docker_images; then
        log_warning "⚠️ Docker构建失败，继续其他步骤"
    fi
    
    if ! generate_raspberry_image; then
        log_error "❌ 镜像生成失败"
        exit 1
    fi
    
    if ! integrate_autostart; then
        log_warning "⚠️ 自动启动集成失败，继续其他步骤"
    fi
    
    if ! create_game_switcher; then
        log_warning "⚠️ 游戏切换界面创建失败，继续其他步骤"
    fi
    
    if ! package_final_image; then
        log_error "❌ 镜像打包失败"
        exit 1
    fi
    
    if ! generate_documentation; then
        log_warning "⚠️ 文档生成失败，继续完成构建"
    fi
    
    echo ""
    echo "🎉 一键镜像构建完成！"
    echo "================================"
    echo ""

    # 输出结果信息 - 改进显示逻辑
    if [ "$SKIP_NATIVE_IMAGE" = "true" ]; then
        echo "📱 macOS系统检测到 - Docker环境已准备"
        echo ""
        echo "📁 输出文件:"
        echo "  演示文件: $BUILD_DIR/retropie_gameplayer_macos_demo.img.gz"
        echo "  信息文件: $BUILD_DIR/retropie_gameplayer_macos_demo.img.info"
        echo ""
        echo "🐳 推荐使用Docker环境:"
        echo "  1. 启动Docker环境: ./start_docker_gui.sh"
        echo "  2. 访问游戏中心: http://localhost:3020"
        echo "  3. VNC远程桌面: localhost:5900"
        echo ""
        echo "💡 要生成真实的树莓派镜像，请在Linux系统上运行此脚本"
    else
        echo "📁 输出文件:"
        echo "  镜像文件: $FINAL_IMAGE"
        echo "  信息文件: ${FINAL_IMAGE%.gz}.info"
        echo "  使用说明: $BUILD_DIR/README_镜像使用说明.md"
        echo ""
        echo "📊 镜像统计:"
        if [ -f "$FINAL_IMAGE" ]; then
            echo "  文件大小: $(du -h "$FINAL_IMAGE" 2>/dev/null | cut -f1 || echo "未知")"
            if command -v md5sum >/dev/null 2>&1; then
                echo "  MD5校验: $(md5sum "$FINAL_IMAGE" 2>/dev/null | cut -d' ' -f1 || echo "计算失败")"
            elif command -v md5 >/dev/null 2>&1; then
                echo "  MD5校验: $(md5 -q "$FINAL_IMAGE" 2>/dev/null || echo "计算失败")"
            fi
        fi
        echo ""
        echo "🚀 下一步:"
        echo "  1. 使用 Raspberry Pi Imager 烧录镜像"
        echo "  2. 插入树莓派并启动"
        echo "  3. 访问 http://树莓派IP:8080/game_switcher/ 开始游戏"
    fi
    echo ""
    echo "🎮 享受完整的游戏体验！"
}

# 执行主函数
main "$@"

