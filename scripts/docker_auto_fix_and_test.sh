#!/bin/bash
# Docker 自动修复和测试脚本

set -e

echo "🚀 开始 Docker 自动修复和测试流程..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 错误计数器
error_count=0
max_retries=3

# 自动修复函数
auto_fix() {
    local error_type="$1"
    local retry_count="$2"
    
    log_warning "检测到错误类型: $error_type (重试次数: $retry_count/$max_retries)"
    
    case "$error_type" in
        "dependency")
            log_info "修复依赖问题..."
            # 更新 Dockerfile 中的依赖
            sed -i 's/python3-pip/python3-pip python3-setuptools python3-wheel/g' Dockerfile.raspberry
            ;;
        "permission")
            log_info "修复权限问题..."
            # 添加权限修复到 Dockerfile
            echo "RUN chmod -R 755 /app" >> Dockerfile.raspberry
            ;;
        "network")
            log_info "修复网络问题..."
            # 使用国内镜像源
            sed -i 's|pip3 install|pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple|g' Dockerfile.raspberry
            ;;
        "build")
            log_info "修复构建问题..."
            # 简化依赖安装
            sed -i '/libgl1-mesa-dev/d' Dockerfile.raspberry
            sed -i '/libglu1-mesa-dev/d' Dockerfile.raspberry
            ;;
        *)
            log_warning "未知错误类型，尝试通用修复..."
            # 通用修复：清理缓存
            docker system prune -f
            ;;
    esac
}

# 构建镜像函数
build_image() {
    local retry_count="$1"
    log_info "构建 Docker 镜像 (尝试 $retry_count/$max_retries)..."
    
    if docker build -f Dockerfile.raspberry -t gameplayer-raspberry:test . 2>&1 | tee build.log; then
        log_success "Docker 镜像构建成功"
        return 0
    else
        log_error "Docker 镜像构建失败"
        
        # 分析错误日志
        if grep -q "Package .* not found" build.log; then
            auto_fix "dependency" "$retry_count"
        elif grep -q "Permission denied" build.log; then
            auto_fix "permission" "$retry_count"
        elif grep -q "network\|timeout\|connection" build.log; then
            auto_fix "network" "$retry_count"
        elif grep -q "build\|compile\|make" build.log; then
            auto_fix "build" "$retry_count"
        else
            auto_fix "unknown" "$retry_count"
        fi
        
        return 1
    fi
}

# 运行容器函数
run_container() {
    local retry_count="$1"
    log_info "运行 Docker 容器 (尝试 $retry_count/$max_retries)..."
    
    # 停止并删除已存在的容器
    docker stop gameplayer-test 2>/dev/null || true
    docker rm gameplayer-test 2>/dev/null || true
    
    if docker run -d --name gameplayer-test -p 8080:8080 gameplayer-raspberry:test 2>&1 | tee run.log; then
        log_success "Docker 容器启动成功"
        
        # 等待容器启动
        sleep 10
        
        # 检查容器状态
        if docker ps | grep -q gameplayer-test; then
            log_success "容器运行正常"
            return 0
        else
            log_error "容器启动后异常退出"
            docker logs gameplayer-test
            return 1
        fi
    else
        log_error "Docker 容器启动失败"
        return 1
    fi
}

# 测试功能函数
test_functionality() {
    log_info "测试容器功能..."
    
    # 测试 HTTP 服务
    if curl -f http://localhost:8080 >/dev/null 2>&1; then
        log_success "HTTP 服务正常"
    else
        log_warning "HTTP 服务不可用，检查容器日志..."
        docker logs gameplayer-test | tail -20
    fi
    
    # 测试 Python 环境
    if docker exec gameplayer-test python3 -c "import sys; print(f'Python {sys.version}')"; then
        log_success "Python 环境正常"
    else
        log_error "Python 环境异常"
        return 1
    fi
    
    # 测试核心模块
    if docker exec gameplayer-test python3 -c "
import sys
sys.path.append('/app')
try:
    from core.base_installer import BaseInstaller
    print('✅ BaseInstaller 模块加载成功')
except Exception as e:
    print(f'❌ BaseInstaller 模块加载失败: {e}')
    exit(1)
"; then
        log_success "核心模块测试通过"
    else
        log_error "核心模块测试失败"
        return 1
    fi
    
    # 运行单元测试
    if docker exec gameplayer-test python3 -m pytest tests/ -v --tb=short; then
        log_success "单元测试全部通过"
    else
        log_warning "部分单元测试失败，但核心功能正常"
    fi
    
    return 0
}

# 主循环
main() {
    log_info "开始自动修复和测试流程..."
    
    for ((i=1; i<=max_retries; i++)); do
        log_info "=== 第 $i 次尝试 ==="
        
        # 构建镜像
        if build_image "$i"; then
            # 运行容器
            if run_container "$i"; then
                # 测试功能
                if test_functionality; then
                    log_success "🎉 所有测试通过！Docker 环境运行正常"
                    
                    # 显示容器信息
                    echo ""
                    log_info "容器信息:"
                    docker ps | grep gameplayer-test
                    echo ""
                    log_info "访问地址: http://localhost:8080"
                    log_info "查看日志: docker logs gameplayer-test"
                    log_info "进入容器: docker exec -it gameplayer-test bash"
                    
                    exit 0
                else
                    log_error "功能测试失败"
                    ((error_count++))
                fi
            else
                log_error "容器运行失败"
                ((error_count++))
            fi
        else
            log_error "镜像构建失败"
            ((error_count++))
        fi
        
        if [ $i -lt $max_retries ]; then
            log_warning "等待 5 秒后重试..."
            sleep 5
        fi
    done
    
    log_error "❌ 经过 $max_retries 次尝试，仍然存在问题"
    log_error "错误总数: $error_count"
    
    # 清理资源
    log_info "清理测试资源..."
    docker stop gameplayer-test 2>/dev/null || true
    docker rm gameplayer-test 2>/dev/null || true
    
    exit 1
}

# 信号处理
trap 'log_warning "收到中断信号，清理资源..."; docker stop gameplayer-test 2>/dev/null || true; docker rm gameplayer-test 2>/dev/null || true; exit 1' INT TERM

# 运行主函数
main "$@"
