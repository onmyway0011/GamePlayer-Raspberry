#!/bin/bash
# 自动运行NES游戏演示脚本

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
    echo "║                🎮 自动运行NES游戏演示                       ║"
    echo "║                                                              ║"
    echo "║  ✅ 真正的NES模拟器                                         ║"
    echo "║  🎮 自动运行游戏                                            ║"
    echo "║  🖥️ Pygame图形界面                                         ║"
    echo "║  🎯 完整游戏体验                                            ║"
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
    
    # 检查Pygame
    if ! python3 -c "import pygame" 2>/dev/null; then
        log_warning "Pygame未安装，正在安装..."
        pip3 install pygame
    fi
    
    log_success "✅ 系统依赖检查通过"
}

# 准备游戏
prepare_games() {
    log_step "准备游戏文件..."
    
    # 清理旧文件
    rm -rf demo_auto_games
    
    # 下载演示游戏
    python3 scripts/rom_downloader.py --output demo_auto_games --category demo_roms
    
    # 统计结果
    local rom_count=$(find demo_auto_games -name "*.nes" | wc -l)
    log_success "✅ 准备了 $rom_count 款演示游戏"
}

# 列出可用模拟器
list_emulators() {
    log_step "检查可用模拟器..."
    
    echo ""
    python3 scripts/run_nes_game.py --list-emulators
    echo ""
}

# 演示单个游戏
demo_single_game() {
    local rom_file="$1"
    local game_name=$(basename "$rom_file" .nes)
    
    log_step "演示游戏: $game_name"
    
    echo ""
    log_info "🎮 即将启动游戏: $game_name"
    log_info "📋 游戏控制:"
    log_info "   • WASD/方向键: 移动"
    log_info "   • 空格/Z: A按钮 (开火)"
    log_info "   • Shift/X: B按钮"
    log_info "   • Enter: Start"
    log_info "   • P: 暂停"
    log_info "   • ESC: 退出游戏"
    echo ""
    
    read -p "按回车键启动游戏，或按Ctrl+C跳过..." 
    
    # 启动游戏
    log_info "🚀 启动游戏: $game_name"
    
    # 使用timeout限制游戏运行时间（演示用）
    timeout 30s python3 scripts/run_nes_game.py "$rom_file" || {
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            log_info "⏰ 演示时间结束（30秒）"
        else
            log_info "👋 游戏已退出"
        fi
    }
    
    echo ""
    log_success "✅ 游戏演示完成: $game_name"
    echo ""
}

# 演示游戏启动器
demo_game_launcher() {
    log_step "演示游戏启动器..."
    
    echo ""
    log_info "🎮 即将启动游戏选择界面"
    log_info "📋 启动器控制:"
    log_info "   • ↑↓: 选择游戏"
    log_info "   • Enter: 启动游戏"
    log_info "   • R: 刷新列表"
    log_info "   • Q: 退出"
    echo ""
    
    read -p "按回车键启动游戏选择器，或按Ctrl+C跳过..."
    
    # 启动游戏选择器（限制时间）
    log_info "🚀 启动游戏选择器..."
    
    timeout 60s python3 scripts/nes_game_launcher.py --roms-dir demo_auto_games || {
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            log_info "⏰ 演示时间结束（60秒）"
        else
            log_info "👋 游戏选择器已退出"
        fi
    }
    
    echo ""
    log_success "✅ 游戏启动器演示完成"
    echo ""
}

# 显示游戏统计
show_game_stats() {
    log_step "显示游戏统计信息..."
    
    if [ ! -d "demo_auto_games" ]; then
        log_error "游戏目录不存在"
        return 1
    fi
    
    echo ""
    echo -e "${CYAN}📊 游戏统计信息:${NC}"
    
    # 总数统计
    local total_roms=$(find demo_auto_games -name "*.nes" | wc -l)
    echo -e "  🎮 总游戏数: ${GREEN}$total_roms${NC} 款"
    
    # 大小统计
    local total_size=$(du -sh demo_auto_games | cut -f1)
    echo -e "  💾 总大小: ${GREEN}$total_size${NC}"
    
    # 列出游戏
    echo -e "  📋 游戏列表:"
    find demo_auto_games -name "*.nes" | while read rom_file; do
        local game_name=$(basename "$rom_file" .nes)
        local file_size=$(du -h "$rom_file" | cut -f1)
        echo -e "    • ${game_name} (${file_size})"
    done
    
    echo ""
}

# 主演示流程
main_demo() {
    show_banner
    
    log_info "🚀 开始自动运行NES游戏演示..."
    echo ""
    
    # 检查依赖
    check_dependencies
    
    # 准备游戏
    prepare_games
    
    # 显示统计
    show_game_stats
    
    # 列出模拟器
    list_emulators
    
    # 演示单个游戏
    echo ""
    log_info "接下来将演示自动运行游戏..."
    
    # 找到第一个ROM文件
    local first_rom=$(find demo_auto_games -name "*.nes" | head -1)
    if [ -n "$first_rom" ]; then
        demo_single_game "$first_rom"
    else
        log_error "没有找到ROM文件"
    fi
    
    # 演示游戏启动器
    echo ""
    log_info "接下来将演示游戏选择界面..."
    demo_game_launcher
    
    # 完成演示
    echo ""
    log_success "🎉 自动运行游戏演示完成！"
    echo ""
    echo -e "${CYAN}🎮 演示总结:${NC}"
    echo -e "  ✅ 真正的NES模拟器运行"
    echo -e "  ✅ 自动游戏启动功能"
    echo -e "  ✅ 图形界面游戏选择器"
    echo -e "  ✅ 完整的游戏控制"
    echo -e "  ✅ ROM文件管理"
    echo ""
    echo -e "${CYAN}📱 完整功能体验:${NC}"
    echo -e "  🐳 Docker环境: ${YELLOW}./scripts/raspberry_docker_sim.sh${NC}"
    echo -e "  🎮 游戏启动器: ${YELLOW}python3 scripts/nes_game_launcher.py${NC}"
    echo -e "  🎯 单个游戏: ${YELLOW}python3 scripts/run_nes_game.py <rom_file>${NC}"
    echo -e "  📋 ROM管理: ${YELLOW}python3 scripts/rom_manager.py${NC}"
    echo ""
    
    # 询问是否清理
    read -p "是否清理演示文件？(y/N): " cleanup_choice
    if [[ $cleanup_choice =~ ^[Yy]$ ]]; then
        rm -rf demo_auto_games
        log_success "✅ 演示文件已清理"
    else
        log_info "演示文件保留在 demo_auto_games/ 目录中"
        echo ""
        log_info "🎮 继续体验:"
        echo "  python3 scripts/nes_game_launcher.py --roms-dir demo_auto_games"
        echo "  python3 scripts/run_nes_game.py demo_auto_games/<game>.nes"
    fi
}

# 错误处理
trap 'log_error "演示过程中发生错误"; exit 1' ERR

# 信号处理
trap 'log_info "演示被中断"; exit 0' INT TERM

# 运行演示
main_demo
