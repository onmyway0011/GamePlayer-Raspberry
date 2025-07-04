# 🍎 macOS用户使用指南

## 🎯 概述

由于macOS系统的限制，无法直接生成树莓派镜像文件。但是，您可以使用Docker环境来体验完整的GamePlayer-Raspberry功能。

## 🚫 macOS系统限制

### 为什么不能生成镜像？

- **缺少Linux工具**: `losetup`、`kpartx`等工具仅在Linux系统中可用
- **文件系统差异**: 树莓派镜像需要Linux文件系统支持
- **权限模型**: macOS的权限模型与Linux不同

### 解决方案

使用Docker容器环境，可以获得与树莓派几乎相同的游戏体验。

## 🐳 推荐使用Docker环境

### 快速启动

```bash
# 一键启动完整图形化环境
./start_docker_gui.sh

# 或启动简化环境
./start_simple_docker.sh
```

### 访问方式

- **游戏中心**: [http://localhost:3020](http://localhost:3020)
- **VNC桌面**: localhost:5900 (密码: gamer123)
- **Web VNC**: [http://localhost:6080](http://localhost:6080)
- **文件管理**: [http://localhost:8080](http://localhost:8080)

## 🎮 功能对比

| 功能 | 树莓派原生 | Docker环境 | 说明 |
|------|------------|------------|------|
| 🎯 游戏运行 | ✅ | ✅ | 完全相同的游戏体验 |
| 🎮 模拟器 | ✅ | ✅ | 4种模拟器完整支持 |
| 💾 存档系统 | ✅ | ✅ | 自动保存/加载 |
| 🎯 金手指 | ✅ | ✅ | 预配置作弊码 |
| 🌐 Web界面 | ✅ | ✅ | 游戏选择和管理 |
| 🖥️ VNC远程 | ✅ | ✅ | 远程桌面访问 |
| 🔊 音频输出 | ✅ | ✅ | 支持音频播放 |
| 🎮 手柄支持 | ✅ | ⚠️ | 需要额外配置 |
| 📱 移动访问 | ✅ | ✅ | 响应式Web界面 |

## 🔧 Docker环境配置

### 系统要求

- **macOS**: 10.14+ (推荐11.0+)
- **Docker Desktop**: 最新版本
- **内存**: 4GB+ (推荐8GB)
- **存储**: 10GB+ 可用空间

### 安装Docker Desktop

1. 访问 [Docker官网](https://www.docker.com/products/docker-desktop)
2. 下载macOS版本
3. 安装并启动Docker Desktop
4. 确保Docker正在运行

### 验证安装

```bash
# 检查Docker版本
docker --version

# 检查Docker运行状态
docker info
```

## 🎯 使用步骤

### 1. 克隆项目

```bash
git clone https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry.git
cd GamePlayer-Raspberry
```

### 2. 运行一键构建

```bash
# 运行一键镜像构建器（会自动适配macOS）
./src/scripts/one_click_image_builder.sh
```

### 3. 启动Docker环境

```bash
# 启动完整图形化环境
./start_docker_gui.sh
```

### 4. 访问游戏界面

- 打开浏览器访问: [http://localhost:3020](http://localhost:3020)
- 或使用VNC客户端连接: localhost:5900

## 🎮 游戏操作

### 通过Web界面

1. 访问 [http://localhost:3020](http://localhost:3020)
2. 浏览游戏列表
3. 点击游戏封面启动

### 通过VNC桌面

1. 使用VNC客户端连接 localhost:5900
2. 密码: gamer123
3. 在桌面环境中操作

### 键盘控制

- **方向键**: 移动
- **Z键**: A按钮
- **X键**: B按钮
- **Enter**: Start
- **Shift**: Select

## 🔊 音频配置

### 启用音频输出

```bash
# 检查音频设备
docker exec -it gameplayer-raspberry-gui aplay -l

# 测试音频
docker exec -it gameplayer-raspberry-gui speaker-test -t wav
```

### 音频故障排除

如果没有声音：

1. 检查macOS音量设置
2. 确认Docker音频权限
3. 重启Docker容器

## 🎮 手柄配置

### USB手柄

1. 连接USB手柄到Mac
2. 重启Docker容器
3. 手柄会自动映射到容器

### 蓝牙手柄

```bash
# 进入容器配置蓝牙
docker exec -it gameplayer-raspberry-gui bash

# 扫描蓝牙设备
bluetoothctl scan on

# 配对设备
bluetoothctl pair [设备MAC地址]
```

## 📁 文件管理

### 数据持久化

Docker环境会自动同步以下目录：

- `./data/roms/` ↔ 容器ROM目录
- `./data/saves/` ↔ 容器存档目录
- `./config/` ↔ 容器配置目录

### 添加新游戏

1. 将ROM文件放入 `./data/roms/对应系统/`
2. 重启Docker容器
3. 游戏会自动出现在列表中

## 🐛 故障排除

### Docker启动失败

```bash
# 检查Docker状态
docker info

# 重启Docker Desktop
# 在应用程序中重启Docker Desktop
```

### 容器无法访问

```bash
# 检查容器状态
docker ps

# 查看容器日志
docker logs gameplayer-raspberry-gui

# 重启容器
docker restart gameplayer-raspberry-gui
```

### VNC连接失败

```bash
# 检查VNC端口
netstat -an | grep 5900

# 重启VNC服务
docker exec -it gameplayer-raspberry-gui supervisorctl restart vnc
```

### 游戏无法启动

```bash
# 进入容器检查
docker exec -it gameplayer-raspberry-gui bash

# 运行修复工具
python3 /app/src/scripts/advanced_emulator_fixer.py
```

## 🔄 更新和维护

### 更新项目

```bash
# 拉取最新代码
git pull origin main

# 重新构建Docker镜像
docker compose -f docker-compose.gui.yml build --no-cache

# 重启服务
./start_docker_gui.sh
```

### 清理Docker

```bash
# 清理未使用的镜像
docker image prune

# 清理未使用的容器
docker container prune

# 清理未使用的卷
docker volume prune
```

## 💡 性能优化

### Docker资源配置

1. 打开Docker Desktop设置
2. 调整资源分配：

   - **CPU**: 4核心+
   - **内存**: 6GB+
   - **磁盘**: 20GB+

### 游戏性能优化

```bash
# 进入容器
docker exec -it gameplayer-raspberry-gui bash

# 调整模拟器设置
# 编辑配置文件降低画质提升性能
```

## 🌟 高级功能

### 自定义配置

```bash
# 编辑Docker Compose配置
vim docker-compose.gui.yml

# 添加自定义端口映射
# 修改环境变量
```

### 多用户访问

```bash
# 配置多个VNC端口
# 在docker-compose.yml中添加多个服务
```

## 📞 获取帮助

如果遇到问题：

1. 查看 [Docker使用指南](DOCKER_GUI_GUIDE.md)
2. 访问 [GitHub Issues](https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry/issues)
3. 查看 [故障排除指南](TROUBLESHOOTING.md)

---

**🎮 在macOS上享受完整的复古游戏体验！**
