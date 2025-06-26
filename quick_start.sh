#!/bin/bash
# GamePlayer-Raspberry 快速启动脚本
# 适配新的项目结构

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

# 显示横幅
show_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              🎮 GamePlayer-Raspberry 3.0.0                  ║"
    echo "║                     快速启动菜单                             ║"
    echo "║                                                              ║"
    echo "║  📁 全新的项目结构 - 更清晰、更专业                         ║"
    echo "║  🎮 完整的NES游戏体验                                       ║"
    echo "║  💾 自动存档 🎯 金手指 🎮 设备管理                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 显示菜单
show_menu() {
    echo ""
    echo -e "${YELLOW}请选择操作:${NC}"
    echo ""
    echo "  1) 🎮 启动游戏选择器"
    echo "  2) 🎯 运行单个游戏"
    echo "  3) 📥 下载游戏ROM"
    echo "  4) 🐳 启动Docker环境"
    echo "  5) 🔧 运行代码分析"
    echo "  6) 🧪 运行测试"
    echo "  7) 📊 查看项目结构"
    echo "  8) 🎉 完整功能演示"
    echo "  9) ❓ 帮助信息"
    echo "  0) 🚪 退出"
    echo ""
    echo -n "请输入选择 [0-9]: "
}

# 启动游戏选择器
start_game_launcher() {
    log_info "🎮 启动游戏选择器..."
    
    if [ ! -f "src/scripts/nes_game_launcher.py" ]; then
        log_error "游戏启动器文件不存在"
        return 1
    fi
    
    # 确保有ROM目录
    mkdir -p data/roms
    
    # 检查是否有ROM文件
    rom_count=$(find data/roms -name "*.nes" 2>/dev/null | wc -l)
    if [ "$rom_count" -eq 0 ]; then
        log_warning "没有找到ROM文件，是否先下载一些游戏？(y/N)"
        read -r download_choice
        if [[ $download_choice =~ ^[Yy]$ ]]; then
            download_roms
        fi
    fi
    
    python3 src/scripts/nes_game_launcher.py --roms-dir data/roms
}

# 运行单个游戏
run_single_game() {
    log_info "🎯 运行单个游戏..."
    
    # 列出可用的ROM文件
    if [ ! -d "data/roms" ] || [ -z "$(ls -A data/roms/*.nes 2>/dev/null)" ]; then
        log_warning "没有找到ROM文件，请先下载游戏"
        return 1
    fi
    
    echo ""
    echo "可用的游戏:"
    local i=1
    declare -a rom_files
    
    for rom_file in data/roms/*.nes; do
        if [ -f "$rom_file" ]; then
            local game_name=$(basename "$rom_file" .nes)
            echo "  $i) $game_name"
            rom_files[$i]="$rom_file"
            ((i++))
        fi
    done
    
    echo ""
    echo -n "请选择游戏编号: "
    read -r game_choice
    
    if [[ "$game_choice" =~ ^[0-9]+$ ]] && [ -n "${rom_files[$game_choice]}" ]; then
        python3 src/scripts/run_nes_game.py "${rom_files[$game_choice]}"
    else
        log_error "无效的选择"
    fi
}

# 下载ROM文件
download_roms() {
    log_info "📥 下载游戏ROM..."
    
    mkdir -p data/roms
    python3 src/scripts/rom_downloader.py --output data/roms
    
    local rom_count=$(find data/roms -name "*.nes" 2>/dev/null | wc -l)
    log_success "✅ 下载完成，共 $rom_count 款游戏"
}

# 启动Docker环境
start_docker() {
    log_info "🐳 启动Docker环境..."
    
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker未安装"
        return 1
    fi
    
    if [ -f "src/scripts/raspberry_docker_sim.sh" ]; then
        bash src/scripts/raspberry_docker_sim.sh
    else
        log_error "Docker启动脚本不存在"
    fi
}

# 运行代码分析
run_code_analysis() {
    log_info "🔧 运行代码分析..."
    
    python3 tools/dev/code_analyzer.py --project-root . --output docs/reports/code_analysis_report.json
    log_success "✅ 代码分析完成，报告保存在 docs/reports/"
}

# 运行测试
run_tests() {
    log_info "🧪 运行测试..."
    
    if command -v pytest >/dev/null 2>&1; then
        python3 -m pytest tests/ -v
    else
        log_warning "pytest未安装，使用unittest运行测试"
        python3 -m unittest discover tests/ -v
    fi
}

# 查看项目结构
show_project_structure() {
    log_info "📊 项目结构:"
    echo ""
    
    echo -e "${CYAN}📁 主要目录:${NC}"
    echo "  📂 src/          - 源代码"
    echo "    📂 core/       - 核心模块 (NES模拟器、存档管理等)"
    echo "    📂 scripts/    - 脚本工具 (游戏启动器、ROM管理等)"
    echo "    📂 web/        - Web相关文件"
    echo "    📂 systems/    - 系统集成模块"
    echo ""
    echo "  📂 config/       - 配置文件"
    echo "    📂 system/     - 系统配置"
    echo ""
    echo "  📂 docs/         - 文档"
    echo "    📂 guides/     - 使用指南"
    echo "    📂 reports/    - 分析报告"
    echo ""
    echo "  📂 tests/        - 测试"
    echo "    📂 unit/       - 单元测试"
    echo "    📂 fixtures/   - 测试数据"
    echo ""
    echo "  📂 build/        - 构建"
    echo "    📂 docker/     - Docker文件"
    echo "    📂 scripts/    - 构建脚本"
    echo "    📂 output/     - 构建输出"
    echo ""
    echo "  📂 data/         - 数据"
    echo "    📂 roms/       - 游戏ROM文件"
    echo "    📂 saves/      - 游戏存档"
    echo "    📂 logs/       - 日志文件"
    echo ""
    echo "  📂 tools/        - 工具"
    echo "    📂 dev/        - 开发工具"
    echo ""
    
    # 统计信息
    local py_files=$(find src/ -name "*.py" 2>/dev/null | wc -l)
    local test_files=$(find tests/ -name "*.py" 2>/dev/null | wc -l)
    local doc_files=$(find docs/ -name "*.md" 2>/dev/null | wc -l)
    
    echo -e "${CYAN}📊 统计信息:${NC}"
    echo "  📄 Python文件: $py_files 个"
    echo "  🧪 测试文件: $test_files 个"
    echo "  📖 文档文件: $doc_files 个"
}

# 完整功能演示
run_full_demo() {
    log_info "🎉 运行完整功能演示..."
    
    if [ -f "build/scripts/demo_all_features.sh" ]; then
        bash build/scripts/demo_all_features.sh
    else
        log_error "演示脚本不存在"
    fi
}

# 显示帮助信息
show_help() {
    echo ""
    echo -e "${CYAN}🎮 GamePlayer-Raspberry 使用指南${NC}"
    echo ""
    echo -e "${YELLOW}核心功能:${NC}"
    echo "  💾 自动存档系统 - 游戏进度自动保存"
    echo "  🎯 金手指系统 - 自动开启无限条命等"
    echo "  🎮 设备管理 - USB手柄和蓝牙耳机自动连接"
    echo "  ⚙️ 配置管理 - 统一的配置文件管理"
    echo ""
    echo -e "${YELLOW}游戏控制:${NC}"
    echo "  WASD/方向键 - 移动"
    echo "  空格/Z - A按钮 (开火)"
    echo "  Shift/X - B按钮 (跳跃)"
    echo "  F5 - 快速保存"
    echo "  F9 - 快速加载"
    echo "  ESC - 退出游戏"
    echo ""
    echo -e "${YELLOW}快速命令:${NC}"
    echo "  python3 src/scripts/nes_game_launcher.py  # 启动游戏选择器"
    echo "  python3 src/scripts/rom_downloader.py     # 下载ROM文件"
    echo "  python3 tools/dev/code_analyzer.py        # 代码分析"
    echo ""
}

# 主循环
main() {
    show_banner
    
    while true; do
        show_menu
        read -r choice
        
        case $choice in
            1) start_game_launcher ;;
            2) run_single_game ;;
            3) download_roms ;;
            4) start_docker ;;
            5) run_code_analysis ;;
            6) run_tests ;;
            7) show_project_structure ;;
            8) run_full_demo ;;
            9) show_help ;;
            0) 
                log_info "👋 再见！"
                exit 0
                ;;
            *)
                log_error "无效的选择，请重新输入"
                ;;
        esac
        
        echo ""
        echo -n "按Enter键继续..."
        read -r
    done
}

# 运行主程序
main
