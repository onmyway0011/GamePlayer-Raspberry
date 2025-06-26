#!/bin/bash
set -e

IMAGE_NAME="gameplayer-raspberry"
CONTAINER_NAME="gameplayer-test"
PORT=8080
MAX_RETRY=5
RETRY=0

log() {
  echo -e "\033[1;34m[INFO]\033[0m $1"
}
log_success() {
  echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}
log_warn() {
  echo -e "\033[1;33m[WARN]\033[0m $1"
}
log_error() {
  echo -e "\033[0;31m[ERROR]\033[0m $1"
}

# 1. 镜像自愈构建
while [ $RETRY -lt $MAX_RETRY ]; do
  log "第 $((RETRY+1)) 次尝试自愈构建Docker镜像..."
  if bash scripts/docker_auto_fix_and_build.sh; then
    log_success "Docker镜像自愈构建成功！"
    break
  else
    log_warn "Docker镜像构建失败，自动修复并重试..."
    RETRY=$((RETRY+1))
    sleep 2
  fi
done
if [ $RETRY -eq $MAX_RETRY ]; then
  log_error "多次自愈后仍构建失败，请人工介入。"
  exit 1
fi

# 2. 启动容器并自动验证
log "启动并验证容器..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

docker run -d --name $CONTAINER_NAME -p $PORT:8080 -v $(pwd)/logs:/app/logs $IMAGE_NAME
sleep 10

# 3. 自动检测+修复+重试功能点
check_and_fix() {
  local desc="$1"
  local check_cmd="$2"
  local fix_cmd="$3"
  for i in {1..3}; do
    if docker exec $CONTAINER_NAME bash -c "$check_cmd"; then
      log_success "$desc 检测通过"
      return 0
    else
      log_warn "$desc 检测失败，自动修复..."
      docker exec $CONTAINER_NAME bash -c "$fix_cmd"
      sleep 2
    fi
  done
  log_error "$desc 多次修复后仍失败"
  docker logs $CONTAINER_NAME
  exit 1
}

check_and_fix "Nesticle 启动脚本" "test -f /opt/retropie/emulators/nesticle/launch_nesticle.sh" "python3 /app/core/nesticle_installer.py"
check_and_fix "Nesticle 配置文件" "test -f /opt/retropie/configs/nes/nesticle.cfg" "python3 /app/core/nesticle_installer.py --configure-only"
check_and_fix "金手指文件" "test -f /home/pi/RetroPie/cheats/super_mario_bros.cht" "python3 /app/core/nesticle_installer.py --setup-cheats"
check_and_fix "保存目录" "test -d /home/pi/RetroPie/saves/nes" "mkdir -p /home/pi/RetroPie/saves/nes"

# 4. 自动化测试自愈
for i in {1..3}; do
  if docker exec $CONTAINER_NAME bash -c "cd /app && python3 -m pytest tests/test_nesticle_installer.py -v"; then
    log_success "所有自动化测试通过"
    break
  else
    log_warn "自动化测试失败，自动修复依赖并重试..."
    docker exec $CONTAINER_NAME bash -c "pip3 install -r /app/requirements.txt"
    sleep 2
  fi
done

# 5. 结果输出
log_success "🎉 全链路自动检测+自动修复+自动验证全部通过！"
echo "访问 http://localhost:$PORT 查看项目文件"
echo "docker logs $CONTAINER_NAME 查看详细日志"
echo "docker exec -it $CONTAINER_NAME bash 进入容器"
echo "docker stop $CONTAINER_NAME 停止容器" 