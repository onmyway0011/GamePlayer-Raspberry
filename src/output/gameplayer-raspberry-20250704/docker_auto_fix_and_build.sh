#!/bin/bash
set -e

IMAGE_NAME="gameplayer-raspberry"
DOCKERFILE="Dockerfile.raspberry"
MAX_RETRY=10
RETRY=0

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

fix_dockerfile() {
  # 检查Dockerfile依赖安装部分是否已分步处理
  if ! grep -q "pip3 install numpy" $DOCKERFILE; then
    echo "[自动修复] 修正Dockerfile依赖安装为分步并优先二进制包..."
    # 删除原有pip install -r requirements.txt
    sed -i '/pip3 install -r requirements.txt/d' $DOCKERFILE
    # 插入分步依赖安装
    sed -i '/# 复制项目文件/a \
# 升级pip和setuptools\nRUN pip3 install --upgrade pip setuptools wheel\n# 先装numpy和matplotlib的二进制包\nRUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple numpy==1.21.6 matplotlib==3.5.3 --only-binary=all\n# 其余依赖单独装\nRUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple requests paramiko tqdm boto3 flask pytest pytest-cov pytest-asyncio pytest-mock pillow pyyaml psutil python-dotenv pathlib typing\n' $DOCKERFILE
  fi
}

while [ $RETRY -lt $MAX_RETRY ]; do
  echo "🐳 [第$((RETRY+1))次] 开始构建Docker镜像..."
  if docker build -f $DOCKERFILE -t $IMAGE_NAME .; then
    echo "✅ Docker镜像构建成功！"
    exit 0
  else
    echo "❌ Docker镜像构建失败，自动修复Dockerfile依赖安装部分..."
    fix_dockerfile
    ((RETRY++))
    sleep 2
  fi

done

echo "🚨 多次自动修复后仍构建失败，请人工检查Dockerfile和依赖日志！"
exit 1 