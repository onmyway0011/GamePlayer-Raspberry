#!/bin/bash

#==================================================================================
# 🎮 GamePlayer-Raspberry 完整镜像构建系统
# 
# 这个脚本整合了所有构建功能：
# - 🔧 自动化测试和修复
# - 💾 ROM下载和管理
# - 🏗️ 镜像构建 (完整版 / 快速版)
# - 🌐 Web服务启动
# - 🐳 Docker构建
#
# 使用方法：
# ./build_complete_image.sh [选项]
#==================================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# 项目信息
PROJECT_NAME="GamePlayer-Raspberry"
PROJECT_VERSION="2.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_header() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                🎮 GamePlayer-Raspberry 完整构建系统 v${PROJECT_VERSION}                ║${NC}"
    echo -e "${CYAN}╠══════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║                                                                              ║${NC}"
    echo -e "${CYAN}║  🔧 自动化测试   💾 ROM下载   🏗️ 镜像构建   🌐 Web服务   🐳 Docker支持      ║${NC}"
    echo -e "${CYAN}║                                                                              ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_menu() {
    echo -e "${WHITE}📋 可用选项:${NC}"
    echo ""
    echo -e "${GREEN}1.${NC} 🧪 运行自动化测试和修复"
    echo -e "${GREEN}2.${NC} 💾 下载游戏ROM文件"
    echo -e "${GREEN}3.${NC} 🚀 快速构建Docker镜像"
    echo -e "${GREEN}4.${NC} 🏗️ 完整树莓派镜像构建"
    echo -e "${GREEN}5.${NC} 🌐 启动Web演示服务器"
    echo -e "${GREEN}6.${NC} 📊 显示项目状态"
    echo -e "${GREEN}7.${NC} 🔄 完整构建流程 (推荐)"
    echo -e "${GREEN}8.${NC} 🧹 清理构建文件"
    echo ""
    echo -e "${YELLOW}0.${NC} 退出"
    echo ""
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

run_tests() {
    print_info "运行自动化测试和修复..."
    echo ""
    
    if [ -f "automated_test_and_fix.py" ]; then
        python3 automated_test_and_fix.py
        echo ""
        print_success "测试完成！查看 test_fix_summary.txt 了解详情"
    else
        print_error "找不到测试脚本 automated_test_and_fix.py"
    fi
}

download_roms() {
    print_info "下载游戏ROM文件..."
    echo ""
    
    # 创建ROM下载器脚本
    if [ ! -f "rom_downloader.py" ]; then
        print_info "创建ROM下载器..."
        create_rom_downloader
    fi
    
    python3 rom_downloader.py
    echo ""
    print_success "ROM下载完成！查看 data/roms/ 目录"
}

create_rom_downloader() {
    cat > rom_downloader.py << 'EOF'
#!/usr/bin/env python3
"""
简化的ROM下载器 - 创建示例ROM文件
"""
import os
import json
from pathlib import Path

def create_sample_roms():
    """创建示例ROM文件"""
    base_dir = Path("data/roms")
    systems = {
        "nes": [".nes"],
        "snes": [".smc"],
        "gameboy": [".gb"],
        "gba": [".gba"],
        "genesis": [".md"]
    }
    
    # 创建目录
    for system in systems:
        (base_dir / system).mkdir(parents=True, exist_ok=True)
    
    # 示例游戏名称
    games = [
        "Adventure Quest", "Space Fighter", "Puzzle Master", "Racing Pro",
        "Ninja Warrior", "Magic Kingdom", "Robot Battle", "Super Platform",
        "Card Master", "Sports Champion", "Mystery Castle", "Ocean Explorer",
        "Sky Racer", "Dragon Legend", "Pixel Fighter", "Time Traveler"
    ]
    
    # 生成最小有效ROM
    def create_nes_rom(name):
        header = bytearray(16)
        header[0:4] = b'NES\x1a'
        header[4] = 1  # 16KB PRG
        header[5] = 1  # 8KB CHR
        prg = bytearray(16384)
        chr = bytearray(8192)
        # 设置重置向量
        prg[0x3FFC] = 0x00
        prg[0x3FFD] = 0x80
        return bytes(header + prg + chr)
    
    total_created = 0
    for system, exts in systems.items():
        for i, game in enumerate(games):
            if i >= 10:  # 每个系统10个游戏
                break
            filename = f"{game.lower().replace(' ', '_')}{exts[0]}"
            filepath = base_dir / system / filename
            
            if not filepath.exists():
                # 为所有系统创建NES格式的ROM（简化）
                rom_data = create_nes_rom(game)
                with open(filepath, 'wb') as f:
                    f.write(rom_data)
                total_created += 1
                print(f"✅ 创建: {filepath}")
    
    print(f"\n🎮 创建了 {total_created} 个示例ROM文件")
    
    # 生成ROM目录
    catalog = {"systems": {}}
    for system in systems:
        roms = []
        for rom_file in (base_dir / system).glob("*"):
            roms.append({
                "name": rom_file.stem.replace("_", " ").title(),
                "filename": rom_file.name,
                "size": rom_file.stat().st_size
            })
        catalog["systems"][system] = {"count": len(roms), "roms": roms}
    
    with open(base_dir / "catalog.json", 'w') as f:
        json.dump(catalog, f, indent=2)

if __name__ == "__main__":
    create_sample_roms()
EOF
    chmod +x rom_downloader.py
}

quick_build() {
    print_info "快速构建Docker镜像..."
    echo ""
    
    # 创建快速构建脚本
    if [ ! -f "quick_build_image.sh" ]; then
        print_info "创建快速构建脚本..."
        create_quick_build_script
    fi
    
    if [[ $EUID -eq 0 ]]; then
        ./quick_build_image.sh
    else
        sudo ./quick_build_image.sh
    fi
    echo ""
    print_success "快速构建完成！查看 output/ 目录"
}

create_quick_build_script() {
    cat > quick_build_image.sh << 'EOF'
#!/bin/bash

# 快速Docker镜像构建
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 快速构建GamePlayer Docker镜像${NC}"

# 创建输出目录
mkdir -p output

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 构建镜像
echo "🔧 构建Docker镜像..."
docker build -t gameplayer-raspberry:latest -f Dockerfile.raspberry . || {
    echo "❌ Docker构建失败，尝试使用默认Dockerfile"
    
    # 创建简单的Dockerfile
    cat > Dockerfile.simple << 'DOCKER_EOF'
FROM python:3.9-slim

WORKDIR /app
COPY . /app/

RUN pip install aiohttp aiohttp-cors
RUN apt-get update && apt-get install -y mednafen && rm -rf /var/lib/apt/lists/*

EXPOSE 8080
CMD ["python3", "simple_demo_server.py", "--port", "8080"]
DOCKER_EOF
    
    docker build -t gameplayer-raspberry:latest -f Dockerfile.simple .
}

# 创建容器并导出
echo "📦 导出镜像..."
CONTAINER_ID=$(docker create gameplayer-raspberry:latest)
docker export "$CONTAINER_ID" | gzip > output/GamePlayer-Raspberry-Quick.tar.gz
docker rm "$CONTAINER_ID"

echo -e "${GREEN}✅ 快速镜像构建完成！${NC}"
echo "📁 输出文件: output/GamePlayer-Raspberry-Quick.tar.gz"
echo ""
echo "🚀 使用方法:"
echo "1. gunzip -c output/GamePlayer-Raspberry-Quick.tar.gz | docker import - gameplayer:latest"
echo "2. docker run -d -p 8080:8080 gameplayer:latest"
echo "3. 访问: http://localhost:8080"
EOF
    chmod +x quick_build_image.sh
}

full_build() {
    print_info "完整树莓派镜像构建..."
    echo ""
    
    if [ -f "one_click_rpi_image_generator.sh" ]; then
        if [[ $EUID -eq 0 ]]; then
            ./one_click_rpi_image_generator.sh
        else
            sudo ./one_click_rpi_image_generator.sh
        fi
        echo ""
        print_success "完整构建完成！查看 output/ 目录"
    else
        print_error "找不到完整构建脚本 one_click_rpi_image_generator.sh"
        print_info "请先运行选项7进行完整构建流程"
    fi
}

start_web_server() {
    print_info "启动Web演示服务器..."
    echo ""
    
    if [ -f "simple_demo_server.py" ]; then
        print_info "Web服务器启动中，请稍候..."
        print_info "访问地址: http://localhost:8080"
        print_info "按 Ctrl+C 停止服务器"
        echo ""
        
        # 检查端口是否被占用
        if command -v lsof &> /dev/null && lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
            print_warning "端口8080已被占用，尝试停止现有服务..."
            pkill -f "simple_demo_server.py" || true
            sleep 2
        fi
        
        python3 simple_demo_server.py
    else
        print_error "找不到Web服务器 simple_demo_server.py"
    fi
}

show_status() {
    print_info "显示项目状态..."
    echo ""
    
    # 显示基本信息
    echo -e "${CYAN}📊 项目信息:${NC}"
    echo "   项目名称: $PROJECT_NAME"
    echo "   版本号: $PROJECT_VERSION"
    echo "   工作目录: $SCRIPT_DIR"
    echo ""
    
    # 检查关键文件
    echo -e "${CYAN}📁 关键文件状态:${NC}"
    local files=(
        "automated_test_and_fix.py:自动化测试脚本"
        "simple_demo_server.py:Web服务器"
        "one_click_rpi_image_generator.sh:完整镜像构建器"
        "README.md:项目文档"
    )
    
    for file_info in "${files[@]}"; do
        IFS=':' read -r file desc <<< "$file_info"
        if [ -f "$file" ]; then
            echo -e "   ✅ $desc ($file)"
        else
            echo -e "   ❌ $desc ($file) - 缺失"
        fi
    done
    echo ""
    
    # 检查目录结构
    echo -e "${CYAN}📂 目录结构:${NC}"
    local dirs=(
        "src/core:核心模块"
        "src/web:Web界面"
        "config:配置文件"
        "data/roms:ROM文件"
        "output:构建输出"
    )
    for dir_info in "${dirs[@]}"; do
        IFS=':' read -r dir desc <<< "$dir_info"
        if [ -d "$dir" ]; then
            local count=$(find "$dir" -type f 2>/dev/null | wc -l)
            echo -e "   ✅ $desc ($dir) - $count 个文件"
        else
            echo -e "   ⚠️  $desc ($dir) - 不存在"
        fi
    done
    echo ""
    
    # 检查ROM数量
    if [ -d "data/roms" ]; then
        echo -e "${CYAN}🎮 ROM文件统计:${NC}"
        local systems=("nes" "snes" "gameboy" "gba" "genesis")
        local total_roms=0
        
        for system in "${systems[@]}"; do
            if [ -d "data/roms/$system" ]; then
                local count=$(find "data/roms/$system" -type f 2>/dev/null | wc -l)
                echo -e "   🎮 $system: $count 个ROM"
                total_roms=$((total_roms + count))
            else
                echo -e "   ⚠️  $system: 目录不存在"
            fi
        done
        echo -e "   📦 总计: $total_roms 个ROM文件"
    fi
    echo ""
    
    # 检查测试结果
    if [ -f "test_fix_summary.txt" ]; then
        echo -e "${CYAN}🧪 最新测试结果:${NC}"
        tail -5 test_fix_summary.txt | while read line; do
            echo "   $line"
        done
    else
        echo -e "${CYAN}🧪 测试状态:${NC}"
        echo "   ⚠️  尚未运行测试，建议先运行选项1"
    fi
    echo ""
}

complete_build_flow() {
    print_info "开始完整构建流程..."
    echo ""
    
    # 步骤1: 运行测试
    echo -e "${YELLOW}═══ 步骤 1/5: 自动化测试和修复 ═══${NC}"
    run_tests
    echo ""
    
    # 步骤2: 下载ROM
    echo -e "${YELLOW}═══ 步骤 2/5: 下载ROM文件 ═══${NC}"
    download_roms
    echo ""
    
    # 步骤3: 检查环境
    echo -e "${YELLOW}═══ 步骤 3/5: 环境检查 ═══${NC}"
    check_environment
    echo ""
    
    # 步骤4: 选择构建类型
    echo -e "${YELLOW}═══ 步骤 4/5: 镜像构建 ═══${NC}"
    echo "选择构建类型:"
    echo "1) 快速Docker镜像 (推荐)"
    echo "2) 完整树莓派镜像"
    read -p "请选择 (1-2): " build_choice
    
    case $build_choice in
        1)
            quick_build
            ;;
        2)
            full_build
            ;;
        *)
            print_warning "无效选择，使用快速构建"
            quick_build
            ;;
    esac
    echo ""
    
    # 步骤5: 完成总结
    echo -e "${YELLOW}═══ 步骤 5/5: 构建完成 ═══${NC}"
    show_completion_summary
}

check_environment() {
    print_info "检查构建环境..."
    
    # 检查Python
    if command -v python3 &> /dev/null; then
        echo "✅ Python3: $(python3 --version)"
    else
        echo "❌ Python3 未安装"
    fi
    
    # 检查Docker
    if command -v docker &> /dev/null; then
        echo "✅ Docker: $(docker --version)"
    else
        echo "⚠️  Docker 未安装 (快速构建需要)"
    fi
    
    # 检查磁盘空间
    local available=$(df / | awk 'NR==2 {print int($4/1024/1024)}')
    if [ "$available" -gt 5 ]; then
        echo "✅ 磁盘空间: ${available}GB 可用"
    else
        echo "⚠️  磁盘空间不足: ${available}GB 可用 (建议至少5GB)"
    fi
}

show_completion_summary() {
    echo -e "${GREEN}🎉 构建流程完成！${NC}"
    echo ""
    echo -e "${CYAN}📋 构建结果:${NC}"
    
    if [ -d "output" ]; then
        echo "📁 输出目录:"
        find output -type f -exec basename {} \; 2>/dev/null | while read file; do
            echo "   📦 $file"
        done
    fi
    
    echo ""
    echo -e "${CYAN}🚀 下一步操作:${NC}"
    echo "1. 查看构建输出: ls -la output/"
    echo "2. 启动Web服务: ./build_complete_image.sh 然后选择选项5"
    echo "3. 查看详细文档: cat README.md"
    echo ""
}

cleanup_build() {
    print_info "清理构建文件..."
    echo ""
    
    # 列出将要删除的内容
    echo -e "${YELLOW}将要删除以下内容:${NC}"
    [ -d "output" ] && echo "   📁 output/ (构建输出)"
    [ -d "image_build" ] && echo "   📁 image_build/ (临时构建文件)"
    [ -f "test_fix_summary.txt" ] && echo "   📄 test_fix_summary.txt"
    [ -f "automated_test_fix.log" ] && echo "   📄 automated_test_fix.log"
    find . -name "test_fix_report_*.json" 2>/dev/null | head -5 | while read file; do
        echo "   📄 $(basename $file)"
    done
    
    read -p "确认删除？(y/N): " confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        rm -rf output/ image_build/
        rm -f test_fix_summary.txt automated_test_fix.log
        rm -f test_fix_report_*.json
        # 清理Docker镜像
        if command -v docker &> /dev/null; then
            docker rmi gameplayer-raspberry:latest 2>/dev/null || true
        fi
        
        print_success "清理完成！"
    else
        print_info "清理已取消"
    fi
}

interactive_menu() {
    while true; do
        print_header
        print_menu
        
        read -p "请选择操作 (0-8): " choice
        echo ""
        
        case $choice in
            1)
                run_tests
                ;;
            2)
                download_roms
                ;;
            3)
                quick_build
                ;;
            4)
                full_build
                ;;
            5)
                start_web_server
                ;;
            6)
                show_status
                ;;
            7)
                complete_build_flow
                ;;
            8)
                cleanup_build
                ;;
            0)
                print_info "退出构建系统"
                exit 0
                ;;
            *)
                print_error "无效选择，请输入 0-8"
                ;;
        esac
        
        if [ "$choice" != "5" ]; then  # Web服务器会阻塞，不需要暂停
            echo ""
            read -p "按任意键继续..." -n 1 -s
            echo ""
        fi
    done
}

main() {
    # 检查参数
    case "${1:-}" in
        --help|-h)
            print_header
            echo "GamePlayer-Raspberry 完整构建系统"
            echo ""
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --help, -h        显示此帮助信息"
            echo "  --test           运行自动化测试"
            echo "  --roms           下载ROM文件"
            echo "  --quick          快速构建"
            echo "  --full           完整构建"
            echo "  --server         启动Web服务器"
            echo "  --status         显示状态"
            echo "  --complete       完整构建流程"
            echo "  --clean          清理文件"
            echo ""
            echo "不带参数启动交互式菜单"
            exit 0
            ;;
        --test)
            run_tests
            ;;
        --roms)
            download_roms
            ;;
        --quick)
            quick_build
            ;;
        --full)
            full_build
            ;;
        --server)
            start_web_server
            ;;
        --status)
            show_status
            ;;
        --complete)
            complete_build_flow
            ;;
        --clean)
            cleanup_build
            ;;
        "")
            interactive_menu
            ;;
        *)
            print_error "未知选项: $1"
            echo "使用 --help 查看可用选项"
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"