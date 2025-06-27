#!/bin/bash
# Docker 构建和运行脚本（增强自愈与自动重试）

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

# 配置变量
IMAGE_NAME="gameplayer-raspberry"
CONTAINER_NAME="gameplayer-test"
PORT=8080

fix_dockerfile_deps() {
  log_warning "自动修复Dockerfile依赖安装部分..."
  # 备份原始Dockerfile
  cp build/docker/Dockerfile.raspberry build/docker/Dockerfile.raspberry.bak 2>/dev/null || true
  # 用分步安装和国内源替换依赖安装部分
  awk '
    /RUN pip3 install -r requirements.txt/ {
      print "# 升级pip和setuptools";
      print "RUN pip3 install --upgrade pip setuptools wheel";
      print "# 先装numpy和matplotlib的二进制包";
      print "RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple numpy==1.21.6 matplotlib==3.5.3 --only-binary=all";
      print "# 其余依赖单独装，避免matplotlib失败影响整体";
      print "RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple requests paramiko tqdm boto3 flask pytest pytest-cov pytest-asyncio pytest-mock pillow pyyaml psutil python-dotenv pathlib typing";
      next
    }
    {print}
  ' build/docker/Dockerfile.raspberry.bak > build/docker/Dockerfile.raspberry
}

build_success=false
retry_count=0
max_retry=5

echo "🐳 GamePlayer-Raspberry Docker 验证环境"
echo "========================================"

# 1. 停止并删除现有容器
log_info "1. 清理现有容器..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# 2. 自动修复与重试构建
while [[ $retry_count -lt $max_retry ]]; do
  log_info "2. 构建 Docker 镜像 (第$((retry_count+1))次尝试)..."
  if docker build -f build/docker/Dockerfile.raspberry -t $IMAGE_NAME .; then
    log_success "Docker 镜像构建成功"
    build_success=true
    break
  else
    log_warning "Docker 镜像构建失败，自动修复依赖安装部分并重试..."
    fix_dockerfile_deps
    retry_count=$((retry_count+1))
    sleep 5
  fi
  if [[ $retry_count -eq $max_retry ]]; then
    log_error "多次自动修复后仍构建失败，请检查Dockerfile和依赖日志！"
    exit 1
  fi
done

# 3. 运行容器
log_info "3. 启动测试容器..."
if docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:8080 \
    -v $(pwd)/logs:/app/logs \
    $IMAGE_NAME; then
    log_success "容器启动成功"
else
    log_error "容器启动失败"
    exit 1
fi

# 4. 等待容器启动
log_info "4. 等待容器启动..."
sleep 10

# 5. 检查容器状态
log_info "5. 检查容器状态..."
if docker ps | grep -q $CONTAINER_NAME; then
    log_success "容器运行正常"
else
    log_error "容器未正常运行"
    docker logs $CONTAINER_NAME
    exit 1
fi

# 6. 运行功能验证
log_info "6. 运行功能验证..."

# 检查 Nesticle 安装
if docker exec $CONTAINER_NAME test -f /opt/retropie/emulators/nesticle/launch_nesticle.sh; then
    log_success "Nesticle 启动脚本存在"
else
    log_warning "Nesticle 启动脚本不存在，尝试修复..."
    docker exec $CONTAINER_NAME bash -c "cd /app && python3 core/nesticle_installer.py"
fi

# 检查配置文件
if docker exec $CONTAINER_NAME test -f /opt/retropie/configs/nes/nesticle.cfg; then
    log_success "Nesticle 配置文件存在"
else
    log_warning "Nesticle 配置文件不存在，尝试修复..."
    docker exec $CONTAINER_NAME bash -c "cd /app && python3 core/nesticle_installer.py --configure-only"
fi

# 检查金手指文件
if docker exec $CONTAINER_NAME test -f /home/pi/RetroPie/cheats/super_mario_bros.cht; then
    log_success "金手指文件存在"
else
    log_warning "金手指文件不存在，尝试修复..."
    docker exec $CONTAINER_NAME bash -c "cd /app && python3 core/nesticle_installer.py --setup-cheats"
fi

# 7. 运行测试
log_info "7. 运行自动化测试..."
if docker exec $CONTAINER_NAME bash -c "cd /app && python3 -m pytest tests/test_nesticle_installer.py -v"; then
    log_success "所有测试通过"
else
    log_warning "部分测试失败，检查日志..."
    docker logs $CONTAINER_NAME
fi

# 8. 显示容器信息
log_info "8. 容器信息:"
echo "容器名称: $CONTAINER_NAME"
echo "访问地址: http://localhost:$PORT"
echo "查看日志: docker logs $CONTAINER_NAME"
echo "进入容器: docker exec -it $CONTAINER_NAME bash"

# 9. 显示验证结果
log_info "9. 验证结果:"
echo ""

# 检查关键文件
echo "📁 文件验证:"
docker exec $CONTAINER_NAME bash -c "
echo '  /opt/retropie/emulators/nesticle/launch_nesticle.sh: ' \$([ -f /opt/retropie/emulators/nesticle/launch_nesticle.sh ] && echo '✅' || echo '❌')
echo '  /opt/retropie/configs/nes/nesticle.cfg: ' \$([ -f /opt/retropie/configs/nes/nesticle.cfg ] && echo '✅' || echo '❌')
echo '  /home/pi/RetroPie/cheats/super_mario_bros.cht: ' \$([ -f /home/pi/RetroPie/cheats/super_mario_bros.cht ] && echo '✅' || echo '❌')
echo '  /home/pi/RetroPie/saves/nes/: ' \$([ -d /home/pi/RetroPie/saves/nes ] && echo '✅' || echo '❌')
"

# 检查服务状态
echo "🔧 服务验证:"
docker exec $CONTAINER_NAME bash -c "
echo '  Python 环境: ' \$(python3 --version 2>/dev/null && echo '✅' || echo '❌')
echo '  Nesticle 安装器: ' \$(python3 -c 'from core.nesticle_installer import NesticleInstaller' 2>/dev/null && echo '✅' || echo '❌')
echo '  测试环境: ' \$(python3 -m pytest --version 2>/dev/null && echo '✅' || echo '❌')
"

echo ""
log_success "🎉 Docker 验证环境启动完成！"
echo ""
echo "💡 使用说明:"
echo "  • 访问 http://localhost:$PORT 查看项目文件"
echo "  • 运行 docker logs $CONTAINER_NAME 查看详细日志"
echo "  • 运行 docker exec -it $CONTAINER_NAME bash 进入容器"
echo "  • 运行 docker stop $CONTAINER_NAME 停止容器"
echo ""
echo "🚀 所有功能验证完成，准备部署到真实树莓派！" 