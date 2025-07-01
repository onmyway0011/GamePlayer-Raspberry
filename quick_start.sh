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

# 检查Python依赖
check_python_deps() {
    log_info "🔍 检查Python依赖..."
    
    local missing_deps=()
    
    # 检查pygame
    if ! python3 -c "import pygame" 2>/dev/null; then
        missing_deps+=("pygame")
    fi
    
    # 检查requests
    if ! python3 -c "import requests" 2>/dev/null; then
        missing_deps+=("requests")
    fi
    
    # 检查pytest
    if ! python3 -c "import pytest" 2>/dev/null; then
        missing_deps+=("pytest")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_warning "⚠️ 检测到缺失的Python依赖: ${missing_deps[*]}"
        echo -n "是否自动安装? (y/N): "
        read -r install_choice
        if [[ $install_choice =~ ^[Yy]$ ]]; then
            log_info "📦 安装Python依赖..."
            pip3 install "${missing_deps[@]}" || {
                log_error "❌ 依赖安装失败，请手动安装: pip3 install ${missing_deps[*]}"
                return 1
            }
            log_success "✅ 依赖安装完成"
        else
            log_warning "⚠️ 跳过依赖安装，某些功能可能无法正常工作"
        fi
    else
        log_success "✅ Python依赖检查通过"
    fi
}

# 确保目录结构
ensure_directories() {
    log_info "📁 确保目录结构..."
    
    local dirs=(
        "data/roms/nes"
        "data/saves"
        "data/logs"
        "data/cheats"
        "config/system"
        "docs/reports"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_info "✅ 创建目录: $dir"
        fi
    done
    
    log_success "✅ 目录结构检查完成"
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
    
    # 检查pygame依赖
    if ! python3 -c "import pygame" 2>/dev/null; then
        log_error "❌ pygame未安装，无法启动游戏选择器"
        log_info "请运行: pip3 install pygame"
        return 1
    fi
    
    if [ ! -f "src/scripts/nes_game_launcher.py" ]; then
        log_error "❌ 游戏启动器文件不存在"
        return 1
    fi
    
    # 确保有ROM目录
    mkdir -p data/roms/nes
    
    # 检查是否有ROM文件
    rom_count=$(find data/roms/nes -name "*.nes" 2>/dev/null | wc -l)
    if [ "$rom_count" -eq 0 ]; then
        log_warning "⚠️ 没有找到ROM文件，是否先下载一些游戏？(y/N)"
        read -r download_choice
        if [[ $download_choice =~ ^[Yy]$ ]]; then
            download_roms
        fi
    fi
    
    # 启动游戏选择器
    python3 src/scripts/nes_game_launcher.py --roms-dir data/roms/nes
}

# 运行单个游戏
run_single_game() {
    log_info "🎯 运行单个游戏..."
    
    # 列出可用的ROM文件
    if [ ! -d "data/roms/nes" ] || [ -z "$(ls -A data/roms/nes/*.nes 2>/dev/null)" ]; then
        log_warning "⚠️ 没有找到ROM文件，请先下载游戏"
        echo -n "是否现在下载游戏？(y/N): "
        read -r download_choice
        if [[ $download_choice =~ ^[Yy]$ ]]; then
            download_roms
        else
            return 1
        fi
    fi
    
    echo ""
    echo "可用的游戏:"
    local i=1
    declare -a rom_files
    
    for rom_file in data/roms/nes/*.nes; do
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
        log_error "❌ 无效的选择"
    fi
}

# 下载ROM文件
download_roms() {
    log_info "📥 下载游戏ROM..."
    
    # 检查requests依赖
    if ! python3 -c "import requests" 2>/dev/null; then
        log_error "❌ requests未安装，无法下载ROM"
        log_info "请运行: pip3 install requests"
        return 1
    fi
    
    mkdir -p data/roms/nes
    
    if [ ! -f "src/scripts/rom_downloader.py" ]; then
        log_error "❌ ROM下载器文件不存在"
        return 1
    fi
    
    # 下载ROM
    python3 src/scripts/rom_downloader.py --output data/roms/nes
    
    local rom_count=$(find data/roms/nes -name "*.nes" 2>/dev/null | wc -l)
    log_success "✅ 下载完成，共 $rom_count 款游戏"
}

# 启动Docker环境
start_docker() {
    log_info "🐳 启动Docker环境..."
    
    if ! command -v docker >/dev/null 2>&1; then
        log_error "❌ Docker未安装"
        log_info "请先安装Docker: https://docs.docker.com/get-docker/"
        return 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        log_error "❌ Docker服务未运行"
        log_info "请启动Docker Desktop或Docker服务"
        return 1
    fi
    
    if [ -f "src/scripts/raspberry_docker_sim.sh" ]; then
        bash src/scripts/raspberry_docker_sim.sh
    else
        log_error "❌ Docker启动脚本不存在"
        return 1
    fi
}

# 运行代码分析
run_code_analysis() {
    log_info "🔧 运行代码分析..."
    
    if [ ! -f "tools/dev/code_analyzer.py" ]; then
        log_error "❌ 代码分析工具不存在"
        return 1
    fi
    
    # 确保报告目录存在
    mkdir -p docs/reports
    
    python3 tools/dev/code_analyzer.py --project-root . --output docs/reports/code_analysis_report.json
    log_success "✅ 代码分析完成，报告保存在 docs/reports/"
}

# 运行测试
run_tests() {
    log_info "🧪 运行测试..."
    
    # 检查测试目录
    if [ ! -d "tests" ]; then
        log_error "❌ 测试目录不存在"
        return 1
    fi
    
    # 优先使用pytest
    if command -v pytest >/dev/null 2>&1; then
        log_info "使用pytest运行测试..."
        python3 -m pytest tests/ -v
    else
        log_warning "⚠️ pytest未安装，使用unittest运行测试"
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
    local rom_files=$(find data/roms -name "*.nes" 2>/dev/null | wc -l)
    local test_files=$(find tests/ -name "*.py" 2>/dev/null | wc -l)
    
    echo -e "${CYAN}📊 统计信息:${NC}"
    echo "  📄 Python文件: $py_files"
    echo "  🎮 ROM文件: $rom_files"
    echo "  🧪 测试文件: $test_files"
    echo ""
}

# 完整功能演示
demo_all_features() {
    log_info "🎉 启动完整功能演示..."
    
    # 检查演示脚本
    if [ -f "src/scripts/demo_all_features.py" ]; then
        python3 src/scripts/demo_all_features.py
    elif [ -f "src/scripts/enhanced_game_launcher.py" ]; then
        log_info "启动增强游戏启动器演示..."
        python3 src/scripts/enhanced_game_launcher.py
    else
        log_warning "⚠️ 演示脚本不存在，启动基础演示..."
        
        # 基础演示
        echo "🎮 GamePlayer-Raspberry 功能演示"
        echo "=================================="
        echo ""
        echo "1. 🎯 检查系统环境..."
        check_python_deps
        ensure_directories
        
        echo ""
        echo "2. 📥 下载示例ROM..."
        download_roms
        
        echo ""
        echo "3. 🎮 启动游戏选择器..."
        start_game_launcher
        
        echo ""
        echo "✅ 演示完成！"
    fi
}

# 显示帮助信息
show_help() {
    echo ""
    echo -e "${CYAN}🎮 GamePlayer-Raspberry 帮助信息${NC}"
    echo "========================================"
    echo ""
    echo -e "${YELLOW}快速开始:${NC}"
    echo "  1. 首次使用建议选择 '3' 下载游戏ROM"
    echo "  2. 然后选择 '1' 启动游戏选择器"
    echo "  3. 或者选择 '2' 直接运行单个游戏"
    echo ""
    echo -e "${YELLOW}高级功能:${NC}"
    echo "  4. Docker环境 - 完整的树莓派模拟环境"
    echo "  5. 代码分析 - 检查代码质量和优化建议"
    echo "  6. 运行测试 - 验证系统功能"
    echo "  8. 完整演示 - 体验所有功能"
    echo ""
    echo -e "${YELLOW}系统要求:${NC}"
    echo "  • Python 3.7+"
    echo "  • pygame (游戏界面)"
    echo "  • requests (ROM下载)"
    echo "  • Docker (可选，用于完整环境)"
    echo ""
    echo -e "${YELLOW}故障排除:${NC}"
    echo "  • 如遇依赖问题，脚本会自动检测并提示安装"
    echo "  • 如无ROM文件，会自动引导下载"
    echo "  • 如Docker问题，请检查Docker服务状态"
    echo ""
    echo -e "${YELLOW}更多信息:${NC}"
    echo "  • 项目文档: docs/README.md"
    echo "  • 使用指南: docs/guides/"
    echo "  • 问题反馈: 查看项目Issues"
    echo ""
}

# 主循环
main() {
    show_banner
    
    # 初始化检查
    check_python_deps
    ensure_directories
    
    # 自动开始游戏下载
    auto_download_games
    
    while true; do
        show_menu
        read -r choice
        
        case $choice in
            1)
                start_game_launcher
                ;;
            2)
                run_single_game
                ;;
            3)
                download_roms
                ;;
            4)
                start_docker
                ;;
            5)
                run_code_analysis
                ;;
            6)
                run_tests
                ;;
            7)
                show_project_structure
                ;;
            8)
                demo_all_features
                ;;
            9)
                show_help
                ;;
            0)
                log_info "👋 再见！"
                exit 0
                ;;
            *)
                log_error "❌ 无效选择，请输入 0-9"
                ;;
        esac
        
        echo ""
        echo -n "按回车键继续..."
        read -r
    done
}

# 自动下载游戏
auto_download_games() {
    log_info "🔄 检查游戏ROM状态..."
    
    # 检查ROM数量
    rom_count=$(find data/roms/nes -name "*.nes" 2>/dev/null | wc -l)
    
    if [ "$rom_count" -lt 5 ]; then
        log_warning "⚠️ 检测到ROM数量不足 ($rom_count 个)，自动开始下载..."
        echo -n "是否自动下载游戏ROM？(Y/n): "
        read -r auto_download_choice
        
        if [[ $auto_download_choice =~ ^[Nn]$ ]]; then
            log_info "跳过自动下载"
        else
            log_info "🚀 开始自动下载游戏ROM..."
            download_roms
        fi
    else
        log_success "✅ ROM数量充足 ($rom_count 个)"
    fi
}

# 信号处理
trap 'log_info "脚本被中断"; exit 1' INT TERM

# 运行主函数
main "$@"
