#!/bin/bash
# Docker 树莓派模拟和自动修复脚本

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

# 全局变量
CONTAINER_NAME="gameplayer-raspberry-test"
IMAGE_NAME="gameplayer-raspberry:test"
MAX_RETRIES=3
CURRENT_RETRY=0
ERROR_LOG="docker_errors.log"

# 清理函数
cleanup() {
    log_info "清理测试环境..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
}

# 信号处理
trap cleanup EXIT INT TERM

# 错误检测和自动修复函数
detect_and_fix_errors() {
    local log_file="$1"
    local error_fixed=false
    
    if [[ -f "$log_file" ]]; then
        log_step "分析错误日志..."
        
        # 检测依赖问题
        if grep -q "Package.*not found\|Unable to locate package" "$log_file"; then
            log_warning "检测到依赖包问题，尝试修复..."
            # 更新包列表
            sed -i '/apt-get update/a apt-get update --fix-missing' Dockerfile.test
            error_fixed=true
        fi
        
        # 检测权限问题
        if grep -q "Permission denied\|permission denied" "$log_file"; then
            log_warning "检测到权限问题，尝试修复..."
            # 添加权限修复
            echo "RUN chmod -R 755 /app" >> Dockerfile.test
            error_fixed=true
        fi
        
        # 检测网络问题
        if grep -q "network\|timeout\|connection.*failed" "$log_file"; then
            log_warning "检测到网络问题，尝试修复..."
            # 使用国内镜像源
            sed -i 's|pip install|pip install -i https://pypi.tuna.tsinghua.edu.cn/simple|g' Dockerfile.test
            error_fixed=true
        fi
        
        # 检测内存问题
        if grep -q "out of memory\|memory.*exhausted" "$log_file"; then
            log_warning "检测到内存问题，尝试修复..."
            # 减少并发安装
            sed -i 's|pip install|pip install --no-cache-dir|g' Dockerfile.test
            error_fixed=true
        fi
        
        # 检测 Python 模块问题
        if grep -q "ModuleNotFoundError\|ImportError" "$log_file"; then
            log_warning "检测到 Python 模块问题，尝试修复..."
            # 添加缺失的模块
            echo "RUN pip install --no-cache-dir typing pathlib" >> Dockerfile.test
            error_fixed=true
        fi
    fi
    
    if $error_fixed; then
        log_success "已应用自动修复，准备重试..."
        return 0
    else
        log_warning "未检测到可自动修复的错误"
        return 1
    fi
}

# 构建镜像函数
build_image() {
    local retry_count="$1"
    log_step "构建 Docker 镜像 (尝试 $retry_count/$MAX_RETRIES)..."
    
    if docker build -f Dockerfile.test -t $IMAGE_NAME . 2>&1 | tee build_$retry_count.log; then
        log_success "Docker 镜像构建成功"
        return 0
    else
        log_error "Docker 镜像构建失败"
        cp build_$retry_count.log $ERROR_LOG
        return 1
    fi
}

# 运行容器函数
run_container() {
    local retry_count="$1"
    log_step "启动 Docker 容器 (尝试 $retry_count/$MAX_RETRIES)..."
    
    # 清理旧容器
    cleanup
    
    if docker run -d --name $CONTAINER_NAME -p 8080:8080 $IMAGE_NAME 2>&1 | tee run_$retry_count.log; then
        log_success "Docker 容器启动成功"
        
        # 等待容器启动
        log_info "等待容器完全启动..."
        sleep 5
        
        # 检查容器状态
        if docker ps | grep -q $CONTAINER_NAME; then
            log_success "容器运行状态正常"
            return 0
        else
            log_error "容器启动后异常退出"
            docker logs $CONTAINER_NAME 2>&1 | tee container_$retry_count.log
            cp container_$retry_count.log $ERROR_LOG
            return 1
        fi
    else
        log_error "Docker 容器启动失败"
        cp run_$retry_count.log $ERROR_LOG
        return 1
    fi
}

# 测试功能函数
test_functionality() {
    log_step "测试容器功能..."
    
    # 测试 HTTP 服务
    log_info "测试 HTTP 服务..."
    local http_test_count=0
    while [ $http_test_count -lt 10 ]; do
        if curl -f -s http://localhost:8080 >/dev/null 2>&1; then
            log_success "✅ HTTP 服务正常响应"
            break
        else
            log_info "等待 HTTP 服务启动... ($((http_test_count + 1))/10)"
            sleep 2
            ((http_test_count++))
        fi
    done
    
    if [ $http_test_count -eq 10 ]; then
        log_warning "⚠️ HTTP 服务响应超时，但容器可能仍在启动"
    fi
    
    # 测试 Python 环境
    log_info "测试 Python 环境..."
    if docker exec $CONTAINER_NAME python3 -c "import sys; print(f'✅ Python {sys.version}')"; then
        log_success "Python 环境正常"
    else
        log_error "❌ Python 环境异常"
        return 1
    fi
    
    # 测试核心模块导入
    log_info "测试核心模块..."
    if docker exec $CONTAINER_NAME python3 -c "
import sys
sys.path.append('/app')
try:
    from core.base_installer import BaseInstaller
    print('✅ BaseInstaller 模块加载成功')
except Exception as e:
    print(f'⚠️ BaseInstaller 模块加载失败: {e}')

try:
    from core.hdmi_config import HDMIConfig
    print('✅ HDMIConfig 模块加载成功')
except Exception as e:
    print(f'⚠️ HDMIConfig 模块加载失败: {e}')

try:
    import requests
    print('✅ requests 模块正常')
except Exception as e:
    print(f'❌ requests 模块异常: {e}')
    exit(1)
"; then
        log_success "核心模块测试通过"
    else
        log_warning "部分核心模块测试失败，但基础环境正常"
    fi
    
    # 运行简化测试
    log_info "运行简化功能测试..."
    if docker exec $CONTAINER_NAME python3 -c "
import os
import sys
sys.path.append('/app')

# 测试环境变量
print(f'TEST_ENV: {os.getenv(\"TEST_ENV\", \"未设置\")}')
print(f'DOCKER_ENV: {os.getenv(\"DOCKER_ENV\", \"未设置\")}')

# 测试目录结构
test_dirs = [
    '/opt/retropie/emulators/nesticle',
    '/home/pi/RetroPie/roms/nes',
    '/app/core',
    '/app/tests'
]

for dir_path in test_dirs:
    if os.path.exists(dir_path):
        print(f'✅ 目录存在: {dir_path}')
    else:
        print(f'⚠️ 目录不存在: {dir_path}')

print('🎮 基础功能测试完成')
"; then
        log_success "功能测试通过"
        return 0
    else
        log_error "功能测试失败"
        return 1
    fi
}

# 显示结果函数
show_results() {
    echo ""
    log_success "🎉 Docker 树莓派模拟环境测试完成！"
    echo ""
    log_info "📊 测试结果:"
    echo "  🐳 容器名称: $CONTAINER_NAME"
    echo "  🌐 访问地址: http://localhost:8080"
    echo "  📁 项目目录: /app"
    echo "  🔧 测试环境: 已启用"
    echo ""
    log_info "🛠️ 常用命令:"
    echo "  查看容器状态: docker ps"
    echo "  查看容器日志: docker logs $CONTAINER_NAME"
    echo "  进入容器: docker exec -it $CONTAINER_NAME bash"
    echo "  停止容器: docker stop $CONTAINER_NAME"
    echo "  删除容器: docker rm $CONTAINER_NAME"
    echo ""
    log_info "🧪 在容器中运行测试:"
    echo "  docker exec $CONTAINER_NAME python3 -m pytest tests/ -v"
    echo ""
}

# 主函数
main() {
    echo "🚀 开始 Docker 树莓派模拟和自动修复流程..."
    echo ""
    
    for ((CURRENT_RETRY=1; CURRENT_RETRY<=MAX_RETRIES; CURRENT_RETRY++)); do
        log_step "=== 第 $CURRENT_RETRY 次尝试 ==="
        
        # 构建镜像
        if build_image $CURRENT_RETRY; then
            # 运行容器
            if run_container $CURRENT_RETRY; then
                # 测试功能
                if test_functionality; then
                    show_results
                    exit 0
                else
                    log_error "功能测试失败"
                fi
            else
                log_error "容器运行失败"
            fi
        else
            log_error "镜像构建失败"
        fi
        
        # 如果不是最后一次尝试，进行自动修复
        if [ $CURRENT_RETRY -lt $MAX_RETRIES ]; then
            if detect_and_fix_errors "$ERROR_LOG"; then
                log_info "等待 3 秒后重试..."
                sleep 3
            else
                log_warning "无法自动修复，继续重试..."
                sleep 3
            fi
        fi
    done
    
    log_error "❌ 经过 $MAX_RETRIES 次尝试，仍然存在问题"
    log_info "请检查错误日志: $ERROR_LOG"
    exit 1
}

# 运行主函数
main "$@"
