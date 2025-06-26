#!/bin/bash
# 完整功能演示脚本
# 展示所有新增的高级功能

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
    echo "║              🎮 GamePlayer-Raspberry 3.0.0                  ║"
    echo "║                   完整功能演示                               ║"
    echo "║                                                              ║"
    echo "║  💾 自动存档系统     🎯 金手指系统                          ║"
    echo "║  🎮 设备自动连接     ⚙️ 配置管理                           ║"
    echo "║  🐳 Docker环境       📱 Web界面                             ║"
    echo "║  🛠️ 代码优化        📖 专业文档                            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 检查依赖
check_dependencies() {
    log_step "检查系统依赖..."
    
    local missing_deps=()
    
    # 检查Python
    if ! command -v python3 >/dev/null 2>&1; then
        missing_deps+=("python3")
    fi
    
    # 检查Git
    if ! command -v git >/dev/null 2>&1; then
        missing_deps+=("git")
    fi
    
    # 检查Docker (可选)
    if ! command -v docker >/dev/null 2>&1; then
        log_warning "Docker未安装 (Docker功能将跳过)"
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "缺少依赖: ${missing_deps[*]}"
        exit 1
    fi
    
    log_success "✅ 系统依赖检查通过"
}

# 演示配置管理
demo_config_management() {
    log_step "演示配置管理系统..."
    
    echo ""
    log_info "🔧 配置管理功能:"
    log_info "   • 统一配置文件管理"
    log_info "   • 模块化配置支持"
    log_info "   • 配置验证和导入导出"
    echo ""
    
    # 测试配置管理器
    python3 -c "
from core.config_manager import ConfigManager
config = ConfigManager()
print('📋 配置信息:')
info = config.get_config_info()
for key, value in info.items():
    print(f'  • {key}: {value}')

print('\n⚙️ 模拟器配置:')
emu_config = config.get_emulator_config()
for key, value in emu_config.items():
    print(f'  • {key}: {value}')
"
    
    log_success "✅ 配置管理演示完成"
}

# 演示存档系统
demo_save_system() {
    log_step "演示自动存档系统..."
    
    echo ""
    log_info "💾 存档系统功能:"
    log_info "   • 自动保存游戏进度"
    log_info "   • 多插槽存档支持"
    log_info "   • 云端同步功能"
    log_info "   • 存档完整性验证"
    echo ""
    
    # 测试存档管理器
    python3 -c "
from core.save_manager import SaveManager
import tempfile
import os

# 创建临时存档目录
temp_dir = tempfile.mkdtemp()
save_manager = SaveManager(temp_dir)

# 模拟游戏状态
game_state = {
    'player_x': 100,
    'player_y': 200,
    'score': 1500,
    'level': 3,
    'lives': 5
}

# 测试保存
rom_path = 'test_game.nes'
success = save_manager.save_game(rom_path, game_state, slot=1)
print(f'💾 保存测试: {\"成功\" if success else \"失败\"}')

# 测试加载
loaded_state = save_manager.load_game(rom_path, slot=1)
if loaded_state:
    print('📂 加载测试: 成功')
    print(f'   分数: {loaded_state[\"score\"]}')
    print(f'   等级: {loaded_state[\"level\"]}')
    print(f'   生命: {loaded_state[\"lives\"]}')
else:
    print('📂 加载测试: 失败')

# 清理
import shutil
shutil.rmtree(temp_dir)
"
    
    log_success "✅ 存档系统演示完成"
}

# 演示金手指系统
demo_cheat_system() {
    log_step "演示金手指系统..."
    
    echo ""
    log_info "🎯 金手指功能:"
    log_info "   • 自动开启无限条命"
    log_info "   • 无限血量和弹药"
    log_info "   • 无敌模式"
    log_info "   • 游戏特定作弊码"
    echo ""
    
    # 测试金手指管理器
    python3 -c "
from core.cheat_manager import CheatManager
import tempfile

# 创建临时作弊码目录
temp_dir = tempfile.mkdtemp()
cheat_manager = CheatManager(temp_dir)

# 获取可用作弊码
rom_path = 'super_mario.nes'
cheats = cheat_manager.get_available_cheats(rom_path)

print('🎯 可用作弊码:')
for cheat_id, cheat_data in list(cheats.items())[:5]:  # 显示前5个
    print(f'  • {cheat_data[\"name\"]}: {cheat_data[\"description\"]}')

# 自动启用作弊码
enabled_count = cheat_manager.auto_enable_cheats(rom_path)
print(f'\n✅ 自动启用了 {enabled_count} 个作弊码')

# 获取状态
status = cheat_manager.get_cheat_status()
print(f'📊 作弊码状态: {status[\"enabled_cheats\"]} 个已启用')

# 清理
import shutil
shutil.rmtree(temp_dir)
"
    
    log_success "✅ 金手指系统演示完成"
}

# 演示设备管理
demo_device_management() {
    log_step "演示设备管理系统..."
    
    echo ""
    log_info "🎮 设备管理功能:"
    log_info "   • USB手柄自动检测"
    log_info "   • 蓝牙耳机自动连接"
    log_info "   • 跨平台设备支持"
    log_info "   • 设备状态监控"
    echo ""
    
    # 测试设备管理器
    python3 -c "
from core.device_manager import DeviceManager

device_manager = DeviceManager()

# 扫描USB控制器
controllers = device_manager.scan_usb_controllers()
print(f'🎮 检测到 {len(controllers)} 个USB控制器')
for controller in controllers:
    print(f'  • {controller[\"name\"]} ({controller[\"type\"]})')

# 扫描蓝牙设备
audio_devices = device_manager.scan_bluetooth_devices()
print(f'\n🎧 检测到 {len(audio_devices)} 个蓝牙设备')
for device in audio_devices[:3]:  # 显示前3个
    print(f'  • {device[\"name\"]} ({device[\"type\"]})')

# 获取设备状态
status = device_manager.get_device_status()
print(f'\n📊 设备状态:')
print(f'  • 控制器: {status[\"controllers\"][\"count\"]} 个')
print(f'  • 音频设备: {status[\"audio_devices\"][\"count\"]} 个')
"
    
    log_success "✅ 设备管理演示完成"
}

# 演示代码分析
demo_code_analysis() {
    log_step "演示代码分析工具..."
    
    echo ""
    log_info "🔍 代码分析功能:"
    log_info "   • 代码复杂度分析"
    log_info "   • 代码风格检查"
    log_info "   • 导入语句分析"
    log_info "   • 优化建议生成"
    echo ""
    
    # 运行代码分析（简化版）
    python3 tools/code_analyzer.py --summary-only
    
    log_success "✅ 代码分析演示完成"
}

# 演示游戏运行
demo_game_running() {
    log_step "演示游戏运行功能..."
    
    echo ""
    log_info "🎮 游戏运行功能:"
    log_info "   • 真正的NES模拟器"
    log_info "   • 自动ROM下载"
    log_info "   • 智能模拟器选择"
    log_info "   • 完整游戏体验"
    echo ""
    
    # 检查可用模拟器
    python3 scripts/run_nes_game.py --list-emulators
    
    # 下载演示ROM
    log_info "📥 下载演示ROM..."
    python3 scripts/rom_downloader.py --output demo_roms --category demo_roms
    
    # 列出下载的游戏
    if [ -d "demo_roms" ]; then
        local rom_count=$(find demo_roms -name "*.nes" | wc -l)
        log_success "✅ 下载了 $rom_count 款演示游戏"
        
        echo ""
        log_info "🎮 可用游戏:"
        find demo_roms -name "*.nes" | head -5 | while read rom_file; do
            local game_name=$(basename "$rom_file" .nes)
            echo "  • $game_name"
        done
    fi
    
    log_success "✅ 游戏运行演示完成"
}

# 演示Docker环境
demo_docker_environment() {
    log_step "演示Docker环境..."
    
    if ! command -v docker >/dev/null 2>&1; then
        log_warning "⚠️ Docker未安装，跳过Docker演示"
        return
    fi
    
    echo ""
    log_info "🐳 Docker环境功能:"
    log_info "   • 树莓派ARM64模拟"
    log_info "   • VNC远程桌面"
    log_info "   • Web管理界面"
    log_info "   • 容器化部署"
    echo ""
    
    # 检查Docker镜像
    if docker images | grep -q "gameplayer-raspberry"; then
        log_info "📦 发现现有Docker镜像"
    else
        log_info "📦 Docker镜像需要构建"
    fi
    
    # 显示Docker配置
    if [ -f "docker-compose.yml" ]; then
        log_info "📋 Docker Compose配置:"
        echo "  • raspberry-sim: ARM64模拟环境"
        echo "  • web-manager: Web管理界面"
        echo "  • 端口映射: 5901(VNC), 6080(Web VNC), 3000(管理), 8080(HTTP)"
    fi
    
    log_success "✅ Docker环境演示完成"
}

# 显示项目统计
show_project_stats() {
    log_step "显示项目统计信息..."
    
    echo ""
    echo -e "${CYAN}📊 项目统计信息:${NC}"
    
    # 文件统计
    local py_files=$(find . -name "*.py" -not -path "./.git/*" -not -path "./venv/*" | wc -l)
    local total_lines=$(find . -name "*.py" -not -path "./.git/*" -not -path "./venv/*" -exec wc -l {} + | tail -1 | awk '{print $1}')
    local sh_files=$(find . -name "*.sh" -not -path "./.git/*" | wc -l)
    local docker_files=$(find . -name "Dockerfile*" -o -name "docker-compose.yml" | wc -l)
    
    echo -e "  📄 Python文件: ${GREEN}$py_files${NC} 个"
    echo -e "  📝 代码行数: ${GREEN}$total_lines${NC} 行"
    echo -e "  📜 Shell脚本: ${GREEN}$sh_files${NC} 个"
    echo -e "  🐳 Docker文件: ${GREEN}$docker_files${NC} 个"
    
    # 目录统计
    echo -e "\n📁 目录结构:"
    echo -e "  • core/: ${GREEN}$(ls core/*.py 2>/dev/null | wc -l)${NC} 个核心模块"
    echo -e "  • scripts/: ${GREEN}$(ls scripts/*.py 2>/dev/null | wc -l)${NC} 个脚本工具"
    echo -e "  • tools/: ${GREEN}$(ls tools/*.py 2>/dev/null | wc -l)${NC} 个开发工具"
    echo -e "  • config/: ${GREEN}$(ls config/*.json 2>/dev/null | wc -l)${NC} 个配置文件"
    
    # 功能统计
    echo -e "\n🎮 功能模块:"
    echo -e "  • 💾 存档系统: ${GREEN}完整实现${NC}"
    echo -e "  • 🎯 金手指系统: ${GREEN}完整实现${NC}"
    echo -e "  • 🎮 设备管理: ${GREEN}完整实现${NC}"
    echo -e "  • ⚙️ 配置管理: ${GREEN}完整实现${NC}"
    echo -e "  • 🐳 Docker环境: ${GREEN}完整实现${NC}"
    echo -e "  • 🛠️ 开发工具: ${GREEN}完整实现${NC}"
    
    echo ""
}

# 显示使用指南
show_usage_guide() {
    log_step "显示使用指南..."
    
    echo ""
    echo -e "${CYAN}🚀 快速开始指南:${NC}"
    echo ""
    echo -e "${YELLOW}1. 直接运行游戏:${NC}"
    echo "   python3 scripts/nes_game_launcher.py"
    echo ""
    echo -e "${YELLOW}2. Docker环境:${NC}"
    echo "   ./scripts/raspberry_docker_sim.sh"
    echo "   # 访问: http://localhost:6080/vnc.html"
    echo ""
    echo -e "${YELLOW}3. 单个游戏运行:${NC}"
    echo "   python3 scripts/run_nes_game.py <rom_file>"
    echo ""
    echo -e "${YELLOW}4. ROM管理:${NC}"
    echo "   python3 scripts/rom_downloader.py"
    echo "   python3 scripts/rom_manager.py list"
    echo ""
    echo -e "${YELLOW}5. 代码分析:${NC}"
    echo "   python3 tools/code_analyzer.py"
    echo "   python3 tools/auto_optimizer.py"
    echo ""
    
    echo -e "${CYAN}🎮 游戏控制:${NC}"
    echo "  WASD/方向键: 移动"
    echo "  空格/Z: A按钮 (开火)"
    echo "  Shift/X: B按钮 (跳跃)"
    echo "  F5: 快速保存"
    echo "  F9: 快速加载"
    echo "  ESC: 退出游戏"
    echo ""
}

# 主演示流程
main_demo() {
    show_banner
    
    log_info "🚀 开始完整功能演示..."
    echo ""
    
    # 检查依赖
    check_dependencies
    
    # 演示各个功能模块
    demo_config_management
    echo ""
    
    demo_save_system
    echo ""
    
    demo_cheat_system
    echo ""
    
    demo_device_management
    echo ""
    
    demo_code_analysis
    echo ""
    
    demo_game_running
    echo ""
    
    demo_docker_environment
    echo ""
    
    # 显示统计信息
    show_project_stats
    
    # 显示使用指南
    show_usage_guide
    
    # 完成演示
    echo ""
    log_success "🎉 完整功能演示完成！"
    echo ""
    echo -e "${CYAN}🌟 GamePlayer-Raspberry 3.0.0 特性总结:${NC}"
    echo -e "  ✅ 真正可玩的NES游戏"
    echo -e "  ✅ 自动存档和云端同步"
    echo -e "  ✅ 金手指和作弊功能"
    echo -e "  ✅ 设备自动连接"
    echo -e "  ✅ Docker化部署"
    echo -e "  ✅ 专业级代码质量"
    echo -e "  ✅ 完整的文档和工具"
    echo ""
    echo -e "${GREEN}现在您可以享受完整的NES游戏体验了！${NC} 🎮✨"
    echo ""
    
    # 询问是否清理演示文件
    read -p "是否清理演示文件？(y/N): " cleanup_choice
    if [[ $cleanup_choice =~ ^[Yy]$ ]]; then
        rm -rf demo_roms 2>/dev/null || true
        log_success "✅ 演示文件已清理"
    fi
}

# 错误处理
trap 'log_error "演示过程中发生错误"; exit 1' ERR

# 信号处理
trap 'log_info "演示被中断"; exit 0' INT TERM

# 运行演示
main_demo
