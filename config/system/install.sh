#!/bin/bash

# RetroPie 安装器快速安装脚本
# 适用于 Linux 和 macOS

echo "=== RetroPie 安装器快速安装 ==="
echo "正在检查系统环境..."

# 检查Python版本
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo "✓ 找到 Python3: $PYTHON_VERSION"
else
    echo "✗ 未找到 Python3，请先安装 Python 3.7+"
    exit 1
fi

# 检查pip
if command -v pip3 &> /dev/null; then
    echo "✓ 找到 pip3"
else
    echo "✗ 未找到 pip3，请先安装 pip"
    exit 1
fi

# 检查dd命令
if command -v dd &> /dev/null; then
    echo "✓ 找到 dd 命令"
else
    echo "✗ 未找到 dd 命令"
    exit 1
fi

# 安装Python依赖
echo "正在安装Python依赖..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Python依赖安装成功"
else
    echo "✗ Python依赖安装失败"
    exit 1
fi

# 设置执行权限
chmod +x retropie_installer.py
chmod +x test_installer.py

echo "✓ 设置执行权限完成"

# 运行测试
echo "正在运行功能测试..."
python3 test_installer.py

echo ""
echo "=== 安装完成 ==="
echo "使用方法:"
echo "  python3 retropie_installer.py --help     # 查看帮助"
echo "  python3 retropie_installer.py --check-only    # 检查依赖"
echo "  sudo python3 retropie_installer.py       # 运行完整安装"
echo ""
echo "注意: 烧录操作需要 sudo 权限" 