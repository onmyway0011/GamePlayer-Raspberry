#!/bin/bash
set -e

echo "[INFO] 自动构建 Docker 镜像..."
docker build -t gameplayer-raspberry .

echo "[INFO] 自动运行容器并执行主程序..."
docker run --rm gameplayer-raspberry 