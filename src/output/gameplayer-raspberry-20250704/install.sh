#!/bin/bash
# GamePlayer-Raspberry 安装脚本

set -e

echo "🚀 开始安装 GamePlayer-Raspberry..."

# 检查Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ 请先安装 Python 3.7+"
    exit 1
fi

# 安装依赖
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt

# 运行智能安装器
echo "🔧 运行智能安装器..."
python3 scripts/smart_installer.py

# 运行测试
echo "🧪 运行测试..."
python3 -m pytest tests/ -v

echo "✅ 安装完成!"
echo ""
echo "使用方法:"
echo "  python3 core/nesticle_installer.py    # 安装 Nesticle 模拟器"
echo "  python3 core/virtuanes_installer.py   # 安装 VirtuaNES 模拟器"
echo "  python3 core/hdmi_config.py           # HDMI 配置优化"
echo ""
echo "镜像烧录:"
echo "  使用 Raspberry Pi Imager 烧录 .img.gz 文件到SD卡"
