FROM arm32v7/raspbian:stretch

# 安装Python3和pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip git && \
    apt-get clean

# 设置工作目录
WORKDIR /code

# 复制项目代码
COPY . /code

# 自动安装依赖并自愈
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r config/requirements.txt || true

# 自动修复依赖问题脚本
COPY scripts/docker_auto_fix.sh /docker_auto_fix.sh
RUN chmod +x /docker_auto_fix.sh

# 入口：先自愈再运行主程序
ENTRYPOINT ["/docker_auto_fix.sh"] 