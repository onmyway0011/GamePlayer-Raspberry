#!/bin/bash
set -e

# 自动修复依赖并循环运行主程序，直到无报错
MAX_RETRY=5
RETRY=0

while [ $RETRY -lt $MAX_RETRY ]; do
  echo "[INFO] 第$((RETRY+1))次尝试安装依赖并运行主程序..."
  pip3 install --upgrade pip setuptools wheel || true
  pip3 install --no-cache-dir -r config/requirements.txt || true
  # 运行主程序（可根据实际情况修改为主入口脚本）
  python3 web_config.py && break
  echo "[WARN] 运行出错，自动修复依赖后重试..."
  RETRY=$((RETRY+1))
  sleep 2
done

if [ $RETRY -ge $MAX_RETRY ]; then
  echo "[ERR] 多次自动修复后仍有问题，请检查依赖和代码。"
  exit 1
fi 