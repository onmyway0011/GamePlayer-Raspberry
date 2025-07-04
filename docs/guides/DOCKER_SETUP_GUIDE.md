# 🐳 Docker图形化环境设置指南

## 📋 当前状态

✅ **Docker已安装**: Docker version 28.2.2  
❌ **Docker守护进程未运行**: 需要启动Docker服务  

## 🚀 启动Docker服务

### macOS系统
1. **启动Docker Desktop**
   ```bash
   # 方法1: 通过应用程序启动
   open -a Docker
   
   # 方法2: 通过命令行启动
   sudo launchctl start com.docker.docker
   ```

2. **等待Docker启动**
   - 在菜单栏看到Docker图标
   - 图标不再显示"启动中"状态

3. **验证Docker运行**
   ```bash
   docker info
   ```

### Linux系统
```bash
# 启动Docker服务
sudo systemctl start docker

# 设置开机自启
sudo systemctl enable docker

# 验证状态
sudo systemctl status docker
```

### Windows系统
1. 启动Docker Desktop应用程序
2. 等待Docker启动完成
3. 在系统托盘看到Docker图标

## 🎮 启动GamePlayer-Raspberry Docker环境

Docker启动后，选择以下方式之一：

### 方式1: 完整图形化环境 (推荐)
```bash
./start_docker_gui.sh
```

**功能特性**:
- 🖥️ VNC远程桌面 (1920x1080)
- 🌐 Web管理界面
- 📁 文件管理器
- 📊 系统监控
- 🎮 完整模拟器支持

**访问地址**:
- 游戏中心: http://localhost:3020
- VNC桌面: localhost:5900 (密码: gamer123)
- Web VNC: http://localhost:6080
- 文件管理: http://localhost:8080
- 系统监控: http://localhost:9000

### 方式2: 简化环境 (快速启动)
```bash
./start_simple_docker.sh
```

**功能特性**:
- 🖥️ VNC远程桌面
- 🌐 Web游戏界面
- 🎮 基础模拟器支持

**访问地址**:
- 游戏中心: http://localhost:3020
- VNC桌面: localhost:5900 (无密码)

## 🔧 Docker环境管理

### 查看容器状态
```bash
# 完整环境
docker compose -f docker-compose.gui.yml ps

# 简化环境
docker compose -f docker-compose.simple.yml ps
```

### 查看日志
```bash
# 完整环境
docker compose -f docker-compose.gui.yml logs -f

# 简化环境
docker compose -f docker-compose.simple.yml logs -f
```

### 进入容器
```bash
# 完整环境
docker exec -it gameplayer-raspberry-gui bash

# 简化环境
docker exec -it gameplayer-simple bash
```

### 停止服务
```bash
# 完整环境
docker compose -f docker-compose.gui.yml down

# 简化环境
docker compose -f docker-compose.simple.yml down
```

## 🎮 VNC客户端连接

### macOS内置VNC
1. 打开Finder
2. 按 `Cmd+K`
3. 输入: `vnc://localhost:5900`
4. 输入密码 (完整环境: gamer123, 简化环境: 无密码)

### 第三方VNC客户端
```bash
# 安装VNC Viewer
brew install --cask vnc-viewer

# 连接
# 地址: localhost:5900
# 密码: gamer123 (完整环境)
```

### Web VNC (仅完整环境)
直接访问: http://localhost:6080

## 🎯 游戏操作

### 1. Web界面操作
1. 访问 http://localhost:3020
2. 浏览游戏列表
3. 点击游戏封面启动

### 2. VNC桌面操作
1. 连接VNC桌面
2. 打开终端
3. 运行游戏命令:
   ```bash
   cd /home/gamer/GamePlayer-Raspberry
   python3 src/scripts/improved_game_launcher.py --launch nes super_mario_bros
   ```

### 3. 直接运行模拟器
```bash
# 在VNC桌面终端中
mednafen /home/gamer/GamePlayer-Raspberry/data/roms/nes/Super_Mario_Bros.nes
```

## 📁 文件管理

### 本地文件同步
以下本地目录会自动同步到容器：
```
./data/roms/     -> 容器ROM目录
./data/saves/    -> 容器存档目录
./config/        -> 容器配置目录
./logs/          -> 容器日志目录
```

### 添加ROM文件
1. 将ROM文件放入本地目录:
   - NES: `./data/roms/nes/`
   - SNES: `./data/roms/snes/`
   - Game Boy: `./data/roms/gameboy/`
   - GBA: `./data/roms/gba/`

2. 刷新Web界面即可看到新游戏

## 🐛 故障排除

### Docker启动失败
```bash
# 检查Docker状态
docker info

# 重启Docker (macOS)
sudo launchctl stop com.docker.docker
sudo launchctl start com.docker.docker

# 重启Docker (Linux)
sudo systemctl restart docker
```

### 容器启动失败
```bash
# 查看详细错误
docker compose -f docker-compose.gui.yml logs

# 重新构建镜像
docker compose -f docker-compose.gui.yml build --no-cache
```

### VNC连接失败
```bash
# 检查端口是否开放
netstat -an | grep 5900

# 重启VNC服务
docker exec -it gameplayer-raspberry-gui pkill x11vnc
docker exec -it gameplayer-raspberry-gui ~/.vnc/start_vnc.sh
```

### 游戏启动失败
```bash
# 检查ROM文件
docker exec -it gameplayer-raspberry-gui ls -la /home/gamer/GamePlayer-Raspberry/data/roms/nes/

# 检查模拟器
docker exec -it gameplayer-raspberry-gui which mednafen
```

## 📊 系统要求

### 最低要求
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 10GB可用空间
- **网络**: 互联网连接 (用于下载依赖)

### 推荐配置
- **CPU**: 4核心或更多
- **内存**: 8GB RAM或更多
- **存储**: 20GB可用空间
- **显卡**: 支持硬件加速 (可选)

## 🎉 开始游戏

1. **启动Docker Desktop**
2. **运行启动脚本**: `./start_docker_gui.sh`
3. **等待构建完成** (首次运行需要几分钟)
4. **访问Web界面**: http://localhost:3020
5. **连接VNC桌面**: localhost:5900
6. **享受游戏时光**! 🎮

---

**需要帮助?** 
- 查看日志: `docker compose logs -f`
- 进入容器: `docker exec -it <container_name> bash`
- 重启服务: `docker compose restart`
