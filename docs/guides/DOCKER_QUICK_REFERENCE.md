# 🐳 Docker图形化环境快速参考

## 🚀 一键启动

```bash
# 完整图形化环境 (推荐)
./start_docker_gui.sh

# 简化快速环境
./start_simple_docker.sh

# Docker状态检查
./check_docker.sh
```

## 🌐 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 🎮 游戏中心 | http://localhost:3020 | 游戏选择和启动 |
| 🖥️ VNC桌面 | localhost:5900 | 远程桌面连接 |
| 🌐 Web VNC | http://localhost:6080 | 浏览器VNC |
| 📁 文件管理 | http://localhost:8080 | ROM文件管理 |
| 📊 系统监控 | http://localhost:9000 | 容器监控 |

## 🔧 管理命令

```bash
# 查看容器状态
docker compose -f docker-compose.gui.yml ps

# 查看日志
docker compose -f docker-compose.gui.yml logs -f

# 进入容器
docker exec -it gameplayer-raspberry-gui bash

# 停止服务
docker compose -f docker-compose.gui.yml down

# 重启服务
docker compose -f docker-compose.gui.yml restart
```

## 🖥️ VNC连接

### macOS
```bash
# 内置VNC: Finder → Cmd+K → vnc://localhost:5900
# 第三方: brew install --cask vnc-viewer
```

### Windows/Linux
```bash
# 下载VNC Viewer: https://www.realvnc.com/download/viewer/
# 连接: localhost:5900, 密码: gamer123
```

## 📁 文件同步

```
本地目录 → 容器目录
./data/roms/ → /home/gamer/GamePlayer-Raspberry/data/roms/
./data/saves/ → /home/gamer/GamePlayer-Raspberry/data/saves/
./config/ → /home/gamer/GamePlayer-Raspberry/config/
./logs/ → /home/gamer/GamePlayer-Raspberry/logs/
```

## 🐛 故障排除

```bash
# Docker未启动
open -a Docker  # macOS
sudo systemctl start docker  # Linux

# 容器启动失败
docker compose logs
docker compose build --no-cache

# VNC连接失败
netstat -an | grep 5900
docker exec -it <container> pkill x11vnc

# 游戏启动失败
docker exec -it <container> python3 src/scripts/advanced_emulator_fixer.py
```

## 🎮 添加游戏

1. 将ROM文件放入 `./data/roms/nes/` (或对应系统目录)
2. 刷新 http://localhost:3020
3. 点击游戏封面启动

## 📊 系统要求

- **CPU**: 2核心+ (推荐4核心)
- **内存**: 4GB+ (推荐8GB)
- **存储**: 10GB+ 可用空间
- **网络**: 互联网连接 (首次构建)

---

**🎉 享受Docker图形化游戏体验！**
