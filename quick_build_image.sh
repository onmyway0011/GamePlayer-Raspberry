#!/bin/bash

#==================================================================================
# 🚀 GamePlayer-Raspberry 快速Docker镜像构建器
# 
# 快速构建基于Docker的游戏模拟器镜像
# 适合开发测试和快速部署
#==================================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
PROJECT_NAME="GamePlayer-Raspberry"
OUTPUT_DIR="./output"
IMAGE_NAME="gameplayer-raspberry"
CONTAINER_NAME="gameplayer-temp"

print_header() {
    clear
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║         🚀 GamePlayer-Raspberry 快速镜像构建器                  ║${NC}"
    echo -e "${BLUE}║                                                                ║${NC}"
    echo -e "${BLUE}║  ⚡ 快速构建 • 💾 最小镜像 • 🎮 核心功能                        ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_requirements() {
    print_info "检查构建环境..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        echo ""
        echo "安装指南:"
        echo "• Ubuntu/Debian: sudo apt-get install docker.io"
        echo "• CentOS/RHEL: sudo yum install docker"
        echo "• macOS: 下载Docker Desktop"
        echo "• Windows: 下载Docker Desktop"
        exit 1
    fi
    
    # 检查Docker服务
    if ! docker info &> /dev/null; then
        print_error "Docker服务未启动"
        echo "请启动Docker服务: sudo systemctl start docker"
        exit 1
    fi
    
    print_success "Docker环境检查通过"
    
    # 检查磁盘空间
    local available=$(df . | awk 'NR==2 {print int($4/1024/1024)}')
    if [ "$available" -lt 2 ]; then
        print_warning "磁盘空间不足: ${available}GB 可用 (建议至少2GB)"
    else
        print_success "磁盘空间充足: ${available}GB 可用"
    fi
}

create_dockerfile() {
    print_info "创建Dockerfile..."
    
    cat > Dockerfile.quick << 'EOF'
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    mednafen \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . /app/

# 安装Python依赖
RUN pip install --no-cache-dir \
    aiohttp \
    aiohttp-cors \
    asyncio

# 创建必要目录
RUN mkdir -p /app/data/roms/nes \
    /app/data/roms/snes \
    /app/data/roms/gameboy \
    /app/data/roms/gba \
    /app/data/roms/genesis \
    /app/data/saves \
    /app/config/emulators \
    /app/logs

# 设置权限
RUN chmod +x /app/*.py /app/*.sh

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# 启动命令
CMD ["python3", "simple_demo_server.py", "--port", "8080", "--host", "0.0.0.0"]
EOF
    
    print_success "Dockerfile创建完成"
}

build_image() {
    print_info "构建Docker镜像..."
    
    # 构建镜像
    docker build -t "${IMAGE_NAME}:latest" -f Dockerfile.quick . || {
        print_error "Docker镜像构建失败"
        exit 1
    }
    
    print_success "Docker镜像构建完成"
}

export_image() {
    print_info "导出Docker镜像..."
    
    # 创建输出目录
    mkdir -p "${OUTPUT_DIR}"
    
    # 创建容器
    print_info "创建临时容器..."
    CONTAINER_ID=$(docker create "${IMAGE_NAME}:latest")
    
    # 导出镜像
    print_info "导出镜像文件..."
    docker export "$CONTAINER_ID" | gzip > "${OUTPUT_DIR}/GamePlayer-Raspberry-Quick.tar.gz"
    
    # 清理临时容器
    docker rm "$CONTAINER_ID" &> /dev/null
    
    # 生成镜像信息
    local image_size=$(du -h "${OUTPUT_DIR}/GamePlayer-Raspberry-Quick.tar.gz" | cut -f1)
    local build_date=$(date '+%Y-%m-%d %H:%M:%S')
    
    cat > "${OUTPUT_DIR}/image_info.json" << EOF
{
  "name": "GamePlayer-Raspberry-Quick",
  "version": "2.0.0",
  "type": "Docker Container Image",
  "size": "${image_size}",
  "build_date": "${build_date}",
  "base_image": "python:3.9-slim",
  "features": [
    "Web管理界面",
    "游戏模拟器",
    "ROM管理",
    "自动化配置"
  ],
  "ports": [8080],
  "usage": {
    "import": "gunzip -c GamePlayer-Raspberry-Quick.tar.gz | docker import - gameplayer:latest",
    "run": "docker run -d -p 8080:8080 --name gameplayer gameplayer:latest",
    "access": "http://localhost:8080"
  }
}
EOF
    
    print_success "镜像导出完成: ${image_size}"
}

create_usage_guide() {
    print_info "生成使用指南..."
    
    cat > "${OUTPUT_DIR}/DOCKER_USAGE.md" << 'EOF'
# 🚀 GamePlayer-Raspberry Docker镜像使用指南

## 📦 镜像信息
- **文件**: GamePlayer-Raspberry-Quick.tar.gz
- **类型**: Docker容器镜像
- **基础**: python:3.9-slim
- **功能**: 完整的复古游戏模拟器

## 🔧 使用方法

### 1. 导入镜像
```bash
# 解压并导入Docker镜像
gunzip -c GamePlayer-Raspberry-Quick.tar.gz | docker import - gameplayer:latest

# 验证导入
docker images | grep gameplayer
```

### 2. 运行容器

#### 基础运行
```bash
# 简单启动
docker run -d -p 8080:8080 --name gameplayer gameplayer:latest

# 访问Web界面
# http://localhost:8080
```
#### 完整功能运行 (推荐)
```bash
# 创建数据目录
mkdir -p ./roms ./saves ./config

# 运行容器并挂载数据
docker run -d \
  --name gameplayer \
  -p 8080:8080 \
  -v $(pwd)/roms:/app/data/roms \
  -v $(pwd)/saves:/app/data/saves \
  -v $(pwd)/config:/app/config \
  --restart unless-stopped \
  gameplayer:latest
```

### 3. 管理容器

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs gameplayer

# 停止容器
docker stop gameplayer

# 启动容器
docker start gameplayer

# 删除容器
docker rm gameplayer

# 进入容器
docker exec -it gameplayer /bin/bash
```

## 📁 目录挂载

| 容器路径 | 说明 | 建议挂载 |
|---------|------|----------|
| `/app/data/roms` | ROM文件目录 | `./roms` |
| `/app/data/saves` | 游戏存档目录 | `./saves` |
| `/app/config` | 配置文件目录 | `./config` |
| `/app/logs` | 日志文件目录 | `./logs` |

## 🎮 添加游戏

### 方法1: 直接复制 (推荐)
```bash
# 将ROM文件复制到挂载目录
cp your_game.nes ./roms/nes/
cp your_game.smc ./roms/snes/

# 重启容器刷新游戏列表
docker restart gameplayer
```

### 方法2: 容器内复制
```bash
# 复制到运行中的容器
docker cp your_game.nes gameplayer:/app/data/roms/nes/
```

## 🌐 Web界面功能

访问 `http://localhost:8080` 体验:

- 🎮 **游戏启动器** - 直观的游戏选择界面
- ⚙️ **设置管理** - 模拟器和系统配置
- 📊 **统计信息** - 游戏时间和使用数据
- 📁 **文件管理** - ROM文件上传和管理
- 🎯 **金手指** - 游戏作弊码管理

## 🔧 故障排除

### 容器无法启动
```bash
# 检查端口占用
lsof -i :8080

# 查看详细错误
docker logs gameplayer

# 重新创建容器
docker rm gameplayer
docker run -d -p 8080:8080 --name gameplayer gameplayer:latest
```

### Web界面无法访问
```bash
# 检查容器状态
docker ps

# 检查容器IP
docker inspect gameplayer | grep IPAddress

# 尝试容器IP访问
curl http://容器IP:8080
```

### 游戏无法启动
1. 确认ROM文件格式正确
2. 检查文件权限: `ls -la ./roms/`
3. 重启容器: `docker restart gameplayer`

## 📈 性能优化

### 资源限制
```bash
# 限制内存和CPU使用
docker run -d \
  --memory=1g \
  --cpus=1.5 \
  -p 8080:8080 \
  --name gameplayer \
  gameplayer:latest
```

### 网络优化
```bash
# 使用host网络模式 (Linux)
docker run -d \
  --network host \
  --name gameplayer \
  gameplayer:latest
```

## 🐳 Docker Compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'
services:
  gameplayer:
    image: gameplayer:latest
    container_name: gameplayer
    ports:
      - "8080:8080"
    volumes:
      - ./roms:/app/data/roms
      - ./saves:/app/data/saves
      - ./config:/app/config
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```bash
# 启动服务
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 🎯 高级用法

### 多实例部署
```bash
# 启动多个游戏服务器实例
docker run -d -p 8080:8080 --name gameplayer1 gameplayer:latest
docker run -d -p 8081:8080 --name gameplayer2 gameplayer:latest
docker run -d -p 8082:8080 --name gameplayer3 gameplayer:latest
```

### 数据备份
```bash
# 备份游戏数据
tar -czf gameplayer_backup_$(date +%Y%m%d).tar.gz roms/ saves/ config/

# 恢复数据
tar -xzf gameplayer_backup_YYYYMMDD.tar.gz
```

---

## 🎉 开始游戏！

现在你已经有了一个完整运行的复古游戏模拟器！

1. 📱 **在任何设备上访问** - 手机、平板、电脑都能玩
2. 🎮 **添加你喜欢的游戏** - 支持多种经典游戏格式
3. ⚙️ **自定义设置** - 调整画面、音效、控制器
4. 💾 **保存进度** - 游戏存档自动管理
5. 🌐 **随时随地** - 只要有网络就能玩

**享受复古游戏的乐趣！** 🎮✨
EOF
    
    print_success "使用指南生成完成"
}

cleanup() {
    print_info "清理临时文件..."
    
    # 删除临时Dockerfile
    rm -f Dockerfile.quick
    
    # 可选：删除构建的Docker镜像
    read -p "是否删除本地Docker镜像以节省空间？(y/N): " delete_image
    if [[ $delete_image =~ ^[Yy]$ ]]; then
        docker rmi "${IMAGE_NAME}:latest" &> /dev/null || true
        print_success "Docker镜像已删除"
    fi
}

show_summary() {
    local build_end_time=$(date +%s)
    local build_duration=$((build_end_time - BUILD_START_TIME))
    local minutes=$((build_duration / 60))
    local seconds=$((build_duration % 60))
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    🎉 构建完成！                                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${BLUE}📊 构建统计:${NC}"
    echo "   ⏱️  构建时间: ${minutes}分${seconds}秒"
    echo "   📦 输出目录: ${OUTPUT_DIR}/"
    echo "   🎮 镜像文件: GamePlayer-Raspberry-Quick.tar.gz"
    echo "   📋 使用指南: DOCKER_USAGE.md"
    echo ""
    echo -e "${BLUE}🚀 快速启动:${NC}"
    echo "   1. gunzip -c ${OUTPUT_DIR}/GamePlayer-Raspberry-Quick.tar.gz | docker import - gameplayer:latest"
    echo "   2. docker run -d -p 8080:8080 --name gameplayer gameplayer:latest"
    echo "   3. 浏览器访问: http://localhost:8080"
    echo ""
    
    echo -e "${BLUE}📖 详细说明:${NC}"
    echo "   查看完整使用指南: cat ${OUTPUT_DIR}/DOCKER_USAGE.md"
    echo ""
}

main() {
    local BUILD_START_TIME=$(date +%s)
    
    print_header
    
    echo -e "${YELLOW}🔧 快速构建模式说明:${NC}"
    echo "• 基于Docker容器构建"
    echo "• 包含核心游戏功能"
    echo "• 构建时间: 10-30分钟"
    echo "• 镜像大小: 约1-2GB"
    echo ""
    
    case "${1:-}" in
        --help|-h)
            echo "GamePlayer-Raspberry 快速构建器"
            echo ""
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --help, -h     显示帮助信息"
            echo "  --no-cleanup   不清理临时文件"
            echo ""
            exit 0
            ;;
        *)
            read -p "确认开始快速构建？(y/N): " confirm
            if [[ ! $confirm =~ ^[Yy]$ ]]; then
                echo "构建已取消"
                exit 0
            fi
            ;;
    esac
    
    echo ""
    
    # 执行构建步骤
    check_requirements
    create_dockerfile
    build_image
    export_image
    create_usage_guide
    
    if [[ "${1:-}" != "--no-cleanup" ]]; then
        cleanup
    fi
    
    show_summary
    
    print_success "🎮 GamePlayer-Raspberry 快速镜像构建完成！"
}

# 运行主函数
main "$@"