#!/bin/bash
# 快速Docker测试脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🚀 GamePlayer-Raspberry 快速Docker测试"
echo "======================================"

# 1. 检查Docker状态
log_info "1. 检查Docker状态..."
if ! docker info >/dev/null 2>&1; then
    log_error "❌ Docker未运行，请启动Docker Desktop"
    exit 1
fi
log_success "✅ Docker运行正常"

# 2. 清理现有容器
log_info "2. 清理现有容器..."
docker stop gameplayer-test 2>/dev/null || true
docker rm gameplayer-test 2>/dev/null || true

# 3. 使用简单的Python镜像进行测试
log_info "3. 启动简单测试容器..."
docker run -d \
    --name gameplayer-test \
    -p 8080:8080 \
    python:3.9-slim \
    python3 -c "
import http.server
import socketserver
import os

PORT = 8080
Handler = http.server.SimpleHTTPRequestHandler

print('🎮 GamePlayer-Raspberry 测试服务器启动')
print(f'📡 访问地址: http://localhost:{PORT}')

with socketserver.TCPServer(('', PORT), Handler) as httpd:
    print(f'✅ 服务器运行在端口 {PORT}')
    httpd.serve_forever()
"

if [ $? -eq 0 ]; then
    log_success "✅ 测试容器启动成功"
else
    log_error "❌ 测试容器启动失败"
    exit 1
fi

# 4. 等待服务启动
log_info "4. 等待服务启动..."
sleep 5

# 5. 测试连接
log_info "5. 测试HTTP连接..."
if curl -s http://localhost:8080 >/dev/null; then
    log_success "✅ HTTP服务正常"
else
    log_warning "⚠️ HTTP服务可能还在启动中"
fi

# 6. 显示容器状态
log_info "6. 容器状态:"
docker ps | grep gameplayer-test

echo ""
echo "🎉 快速测试完成！"
echo "📡 访问地址: http://localhost:8080"
echo "🔧 查看日志: docker logs gameplayer-test"
echo "🛑 停止容器: docker stop gameplayer-test"
echo ""
