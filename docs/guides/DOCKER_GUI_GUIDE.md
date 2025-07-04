# 🎮 GamePlayer-Raspberry Docker图形化运行指南

## 📋 概述

本指南将帮助您在Docker容器中运行GamePlayer-Raspberry的完整图形化环境，支持：

- 🖥️ VNC远程桌面访问
- 🌐 Web界面管理
- 🎮 完整的模拟器支持
- 📁 文件管理界面
- 📊 系统监控面板

## 🚀 快速启动

### 1. 一键启动

```bash
chmod +x start_docker_gui.sh
./start_docker_gui.sh
```

### 2. 手动启动

```bash
# 构建并启动服务
docker-compose -f docker-compose.gui.yml up -d --build

# 查看服务状态
docker-compose -f docker-compose.gui.yml ps
```

## 🌐 访问地址

启动成功后，您可以通过以下地址访问各种服务：

### 主要服务

- **🎮 游戏中心**: [http://localhost:3020](http://localhost:3020)
- **🖥️ VNC桌面**: localhost:5900 (密码: gamer123)
- **🌐 Web VNC**: [http://localhost:6080](http://localhost:6080)
- **📁 文件管理**: [http://localhost:8080](http://localhost:8080)
- **📊 系统监控**: [http://localhost:9000](http://localhost:9000)

## 🖥️ VNC远程桌面连接

### Windows系统

1. **下载VNC Viewer**

   - 访问 [https://www.realvnc.com/download/viewer/](https://www.realvnc.com/download/viewer/)
   - 下载并安装VNC Viewer

2. **连接设置**

   - 地址: `localhost:5900`
   - 密码: `gamer123`
   - 分辨率: 1920x1080

### macOS系统

1. **使用内置VNC客户端**

   - 打开Finder
   - 按 `Cmd+K`
   - 输入: `vnc://localhost:5900`
   - 密码: `gamer123`

2. **或使用第三方客户端**

   ```bash
   brew install --cask vnc-viewer
   ```

### Linux系统

1. **安装VNC客户端**

   ```bash
   # Ubuntu/Debian
   sudo apt install remmina
   
   # CentOS/RHEL
   sudo yum install tigervnc
   ```

2. **连接命令**

   ```bash
   vncviewer localhost:5900
   ```

## 🎮 游戏操作指南

### 1. 通过Web界面

1. 打开 [http://localhost:3020](http://localhost:3020)
2. 浏览游戏列表
3. 点击游戏封面启动
4. 游戏将在VNC桌面中运行

### 2. 通过VNC桌面

1. 连接VNC桌面 (localhost:5900)
2. 打开终端
3. 运行游戏启动命令:

   ```bash
   cd /home/gamer/GamePlayer-Raspberry
   python3 src/scripts/improved_game_launcher.py --launch nes super_mario_bros
   ```

### 3. 直接运行模拟器

在VNC桌面中直接运行模拟器：

```bash
# NES游戏
fceux /home/gamer/GamePlayer-Raspberry/data/roms/nes/Super_Mario_Bros.nes

# SNES游戏
snes9x-gtk /home/gamer/GamePlayer-Raspberry/data/roms/snes/Super_Mario_World.smc

# GBA游戏
visualboyadvance-m /home/gamer/GamePlayer-Raspberry/data/roms/gba/Pokemon_Ruby.gba

# 多系统模拟器
mednafen /home/gamer/GamePlayer-Raspberry/data/roms/nes/Legend_of_Zelda.nes
```

## 📁 文件管理

### 1. 通过Web文件管理器

- 访问: [http://localhost:8080](http://localhost:8080)
- 可以上传、下载、编辑文件
- 支持ROM文件管理

### 2. 通过Docker卷映射

本地目录会自动同步到容器：

```
./data/roms/     -> /home/gamer/GamePlayer-Raspberry/data/roms/
./data/saves/    -> /home/gamer/GamePlayer-Raspberry/data/saves/
./config/        -> /home/gamer/GamePlayer-Raspberry/config/
./logs/          -> /home/gamer/GamePlayer-Raspberry/logs/
```

### 3. 添加ROM文件

1. 将ROM文件放入对应目录：

   - NES: `./data/roms/nes/`
   - SNES: `./data/roms/snes/`
   - Game Boy: `./data/roms/gameboy/`
   - GBA: `./data/roms/gba/`

2. 重启Web服务或刷新页面即可看到新游戏

## 🔧 管理命令

### 查看服务状态

```bash
docker-compose -f docker-compose.gui.yml ps
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose -f docker-compose.gui.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.gui.yml logs -f gameplayer-gui
```

### 进入容器

```bash
# 进入主容器
docker exec -it gameplayer-raspberry-gui bash

# 进入后可以运行各种命令
cd /home/gamer/GamePlayer-Raspberry
python3 src/scripts/advanced_emulator_fixer.py --status
```

### 重启服务

```bash
# 重启所有服务
docker-compose -f docker-compose.gui.yml restart

# 重启特定服务
docker-compose -f docker-compose.gui.yml restart gameplayer-gui
```

### 停止服务

```bash
docker-compose -f docker-compose.gui.yml down
```

### 完全清理

```bash
# 停止并删除所有容器、网络
docker-compose -f docker-compose.gui.yml down -v

# 删除镜像
docker rmi $(docker images "*gameplayer*" -q)
```

## 🎯 高级功能

### 1. 系统监控

- 访问: [http://localhost:9000](http://localhost:9000)
- 可以监控容器状态、资源使用
- 管理Docker容器和镜像

### 2. 自动修复工具

容器启动时会自动运行高级修复工具：

```bash
python3 src/scripts/advanced_emulator_fixer.py --no-progress
```

### 3. 健康检查

系统会自动检查Web服务健康状态：

```bash
curl -f http://localhost:3020/api/status
```

## 🐛 故障排除

### 1. 容器启动失败

```bash
# 查看详细错误信息
docker-compose -f docker-compose.gui.yml logs gameplayer-gui

# 重新构建镜像
docker-compose -f docker-compose.gui.yml build --no-cache
```

### 2. VNC连接失败

```bash
# 检查VNC端口是否开放
netstat -an | grep 5900

# 重启VNC服务
docker exec -it gameplayer-raspberry-gui bash
pkill x11vnc
~/.vnc/start_vnc.sh
```

### 3. 游戏启动失败

```bash
# 检查模拟器是否安装
docker exec -it gameplayer-raspberry-gui which mednafen
docker exec -it gameplayer-raspberry-gui which fceux

# 检查ROM文件
docker exec -it gameplayer-raspberry-gui ls -la /home/gamer/GamePlayer-Raspberry/data/roms/nes/
```

### 4. 音频问题

```bash
# 检查音频设备
docker exec -it gameplayer-raspberry-gui aplay -l

# 重启音频服务
docker exec -it gameplayer-raspberry-gui pulseaudio --kill
docker exec -it gameplayer-raspberry-gui pulseaudio --start
```

## 📊 性能优化

### 1. 分配更多资源

编辑 `docker-compose.gui.yml`：

```yaml
services:
  gameplayer-gui:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          memory: 2G
```

### 2. 使用GPU加速

如果有NVIDIA GPU：

```yaml
services:
  gameplayer-gui:
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
```

### 3. 优化网络

```yaml
networks:
  gameplayer-network:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: br-gameplayer
```

## 🎮 享受游戏！

现在您可以：

1. 🌐 通过Web界面浏览和启动游戏
2. 🖥️ 通过VNC远程桌面直接操作
3. 📁 通过文件管理器上传ROM文件
4. 📊 通过监控面板查看系统状态

**祝您游戏愉快！** 🎉

## 享受你的游戏时光
