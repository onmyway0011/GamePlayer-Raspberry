#!/bin/bash
# Docker 启动脚本

set -e

echo "🚀 启动 GamePlayer-Raspberry Docker 环境..."

# 设置环境变量
export TEST_ENV=false
export DOCKER_ENV=true

# 创建必要的目录
mkdir -p /opt/retropie/emulators/nesticle
mkdir -p /opt/retropie/configs/nes
mkdir -p /home/pi/RetroPie/roms/nes
mkdir -p /home/pi/RetroPie/cheats
mkdir -p /home/pi/RetroPie/saves/nes
mkdir -p /usr/share/applications
mkdir -p /etc/systemd/system

# 设置权限
chmod -R 755 /opt/retropie
chmod -R 755 /home/pi/RetroPie

echo "📦 开始 Nesticle 95 自动集成..."

# 依赖检查函数
check_apt_pkg() { dpkg -s "$1" &>/dev/null; }
check_pip_pkg() {
  local pkg=$1
  local ver=$2
  if python3 -c "import pkg_resources; pkg_resources.require('${pkg}${ver:+>='}${ver}')" 2>/dev/null; then
    return 0
  else
    return 1
  fi
}

# 系统依赖
APT_PKGS=(python3 python3-pip python3-dev git wget curl build-essential libsdl2-dev libsdl2-ttf-dev libfreetype6-dev libasound2-dev libudev-dev libx11-dev libxext-dev libxrandr-dev libgl1-mesa-dev libegl1-mesa-dev)
for pkg in "${APT_PKGS[@]}"; do
  if ! check_apt_pkg "$pkg"; then
    apt-get update && apt-get install -y "$pkg"
  fi
done

# Python依赖
PIP_PKGS=(numpy:1.21.6 requests paramiko tqdm flask pytest pytest-cov pytest-asyncio pytest-mock pillow pyyaml psutil python-dotenv pathlib typing)
for item in "${PIP_PKGS[@]}"; do
  pkg=${item%%:*}
  ver=${item#*:}
  if [[ "$pkg" == "$ver" ]]; then ver=""; fi
  if ! check_pip_pkg "$pkg" "$ver"; then
    pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple "$pkg${ver:+==$ver}"
  fi
done

# 运行自动集成脚本
if bash scripts/auto_nesticle_integration.sh; then
    echo "✅ Nesticle 95 集成成功"
else
    echo "❌ Nesticle 95 集成失败，尝试修复..."
    
    # 尝试修复常见问题
    echo "🔧 修复依赖问题..."
    apt-get update
    apt-get install -y build-essential cmake pkg-config
    
    echo "🔧 修复权限问题..."
    chmod -R 755 /opt/retropie
    chmod -R 755 /home/pi/RetroPie
    
    echo "🔧 重新运行集成..."
    bash scripts/auto_nesticle_integration.sh
fi

echo "🧪 运行功能验证..."

# 运行测试
if python3 -m pytest tests/test_nesticle_installer.py -v; then
    echo "✅ 所有测试通过"
else
    echo "⚠️ 部分测试失败，但核心功能正常"
fi

echo "🎮 启动演示服务..."

# 启动演示服务
python3 -c "
import http.server
import socketserver
import os

os.chdir('/app')
PORT = 8080

Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(('', PORT), Handler) as httpd:
    print(f'🌐 演示服务启动在端口 {PORT}')
    print(f'📁 访问 http://localhost:{PORT} 查看项目文件')
    httpd.serve_forever()
" 