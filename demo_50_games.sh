#!/bin/bash
# 50款NES游戏演示脚本

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

# 显示横幅
show_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🎮 50款NES游戏演示                       ║"
    echo "║                                                              ║"
    echo "║  🍓 完整树莓派环境模拟                                      ║"
    echo "║  🎮 50款精选NES游戏                                         ║"
    echo "║  🖥️ VNC图形界面                                             ║"
    echo "║  🌐 Web管理界面                                             ║"
    echo "║  🐳 Docker容器化                                            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 检查依赖
check_dependencies() {
    log_step "检查系统依赖..."
    
    # 检查Python
    if ! command -v python3 >/dev/null 2>&1; then
        log_error "Python3未安装"
        exit 1
    fi
    
    # 检查Docker
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker未安装"
        exit 1
    fi
    
    log_success "✅ 系统依赖检查通过"
}

# 下载50款游戏
download_50_games() {
    log_step "下载50款NES游戏..."
    
    # 清理旧文件
    rm -rf demo_50_games
    
    # 下载游戏
    python3 scripts/rom_downloader.py --output demo_50_games
    
    # 统计结果
    local rom_count=$(find demo_50_games -name "*.nes" | wc -l)
    log_success "✅ 成功下载 $rom_count 款游戏"
    
    # 显示游戏列表
    log_info "📋 游戏列表预览:"
    python3 scripts/rom_manager.py --roms-dir demo_50_games list | head -15
    echo "..."
    echo "（还有更多游戏）"
}

# 启动游戏启动器
start_game_launcher() {
    log_step "启动游戏选择界面..."
    
    log_info "🎮 启动NES游戏启动器"
    log_info "使用方向键选择游戏，回车启动，Q键退出"
    
    # 启动游戏启动器
    python3 scripts/nes_game_launcher.py --roms-dir demo_50_games &
    local launcher_pid=$!
    
    log_success "✅ 游戏启动器已启动 (PID: $launcher_pid)"
    log_info "按任意键继续..."
    read -n 1
    
    # 停止启动器
    kill $launcher_pid 2>/dev/null || true
}

# 演示简单播放器
demo_simple_player() {
    log_step "演示简单NES播放器..."
    
    # 选择一个ROM文件
    local rom_file=$(find demo_50_games -name "*.nes" | head -1)
    
    if [ -z "$rom_file" ]; then
        log_error "没有找到ROM文件"
        return 1
    fi
    
    log_info "🎮 启动游戏: $(basename "$rom_file")"
    log_info "使用WASD移动，空格射击，ESC退出"
    
    # 启动简单播放器
    python3 scripts/simple_nes_player.py "$rom_file" &
    local player_pid=$!
    
    log_success "✅ 游戏播放器已启动 (PID: $player_pid)"
    log_info "按任意键继续..."
    read -n 1
    
    # 停止播放器
    kill $player_pid 2>/dev/null || true
}

# 显示统计信息
show_statistics() {
    log_step "显示游戏统计信息..."
    
    if [ ! -d "demo_50_games" ]; then
        log_error "游戏目录不存在"
        return 1
    fi
    
    echo ""
    echo -e "${CYAN}📊 游戏统计信息:${NC}"
    
    # 总数统计
    local total_roms=$(find demo_50_games -name "*.nes" | wc -l)
    echo -e "  🎮 总游戏数: ${GREEN}$total_roms${NC} 款"
    
    # 大小统计
    local total_size=$(du -sh demo_50_games | cut -f1)
    echo -e "  💾 总大小: ${GREEN}$total_size${NC}"
    
    # 分类统计
    if [ -f "demo_50_games/rom_catalog.json" ]; then
        echo -e "  📂 游戏分类:"
        python3 -c "
import json
try:
    with open('demo_50_games/rom_catalog.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    for category, info in catalog.get('categories', {}).items():
        rom_count = len(info.get('roms', {}))
        print(f'    • {info.get(\"name\", category)}: {rom_count}款')
except Exception as e:
    print(f'    • 无法读取分类信息: {e}')
"
    fi
    
    # 播放列表
    local playlists=$(find demo_50_games/playlists -name "*.m3u" 2>/dev/null | wc -l)
    echo -e "  📝 播放列表: ${GREEN}$playlists${NC} 个"
    
    echo ""
}

# 清理演示文件
cleanup_demo() {
    log_step "清理演示文件..."
    
    # 停止所有相关进程
    pkill -f "nes_game_launcher.py" 2>/dev/null || true
    pkill -f "simple_nes_player.py" 2>/dev/null || true
    
    # 清理文件
    rm -rf demo_50_games
    
    log_success "✅ 演示文件已清理"
}

# 主演示流程
main_demo() {
    show_banner
    
    log_info "🚀 开始50款NES游戏演示..."
    echo ""
    
    # 检查依赖
    check_dependencies
    
    # 下载游戏
    download_50_games
    
    # 显示统计
    show_statistics
    
    # 演示游戏启动器
    echo ""
    log_info "接下来将演示游戏选择界面..."
    read -p "按回车继续..." 
    start_game_launcher
    
    # 演示简单播放器
    echo ""
    log_info "接下来将演示游戏播放器..."
    read -p "按回车继续..."
    demo_simple_player
    
    # 完成演示
    echo ""
    log_success "🎉 演示完成！"
    echo ""
    echo -e "${CYAN}📱 完整功能体验:${NC}"
    echo -e "  🐳 Docker环境: ${YELLOW}./scripts/raspberry_docker_sim.sh${NC}"
    echo -e "  🌐 Web界面: ${YELLOW}docker-compose up${NC}"
    echo -e "  📋 ROM管理: ${YELLOW}python3 scripts/rom_manager.py${NC}"
    echo ""
    
    # 询问是否清理
    read -p "是否清理演示文件？(y/N): " cleanup_choice
    if [[ $cleanup_choice =~ ^[Yy]$ ]]; then
        cleanup_demo
    else
        log_info "演示文件保留在 demo_50_games/ 目录中"
    fi
}

# 错误处理
trap 'log_error "演示过程中发生错误"; cleanup_demo; exit 1' ERR

# 运行演示
main_demo
