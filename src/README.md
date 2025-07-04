
## 🚀 最新构建信息

**构建时间**: 2025-07-04 10:42:47  
**构建版本**: 1.0.0  
**支持平台**: Raspberry Pi 3B+/4/400  

### 📦 可用下载

- **完整部署包**: `output/gameplayer-raspberry-20250704.tar.gz`
- **树莓派镜像**: `output/*_gameplayer.img.gz`
- **校验文件**: `output/*.sha256`

### ⚡ 快速开始

#### 方式一：使用预构建镜像（推荐）
```bash
# 1. 下载镜像文件
wget https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry/releases/latest/download/retropie_gameplayer.img.gz

# 2. 验证校验和
sha256sum -c retropie_gameplayer.img.gz.sha256

# 3. 使用 Raspberry Pi Imager 烧录到SD卡
```

#### 方式二：智能安装
```bash
# 克隆项目
git clone https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry.git
cd GamePlayer-Raspberry

# 一键安装（自动跳过已安装组件）
python3 scripts/smart_installer.py

# 运行测试
python3 -m pytest tests/ -v
```

### 🎮 GUI 可视化界面

支持 Docker 容器化的图形界面，可在浏览器中查看游戏运行效果：

```bash
# 启动 GUI 环境
./scripts/docker_gui_simulation.sh

# 访问 Web VNC
open http://localhost:6080/vnc.html
```

### 🔧 高级功能

- **智能版本检测**: 自动跳过已安装且版本匹配的组件
- **一键镜像生成**: 自动构建可烧录的树莓派镜像
- **Docker 支持**: 完整的容器化开发环境
- **可视化界面**: 支持 VNC 远程桌面访问



## 🚀 最新构建信息

**构建时间**: 2025-07-04 10:39:22  
**构建版本**: 1.0.0  
**支持平台**: Raspberry Pi 3B+/4/400  

### 📦 可用下载

- **完整部署包**: `output/gameplayer-raspberry-20250704.tar.gz`
- **树莓派镜像**: `output/*_gameplayer.img.gz`
- **校验文件**: `output/*.sha256`

### ⚡ 快速开始

#### 方式一：使用预构建镜像（推荐）
```bash
# 1. 下载镜像文件
wget https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry/releases/latest/download/retropie_gameplayer.img.gz

# 2. 验证校验和
sha256sum -c retropie_gameplayer.img.gz.sha256

# 3. 使用 Raspberry Pi Imager 烧录到SD卡
```

#### 方式二：智能安装
```bash
# 克隆项目
git clone https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry.git
cd GamePlayer-Raspberry

# 一键安装（自动跳过已安装组件）
python3 scripts/smart_installer.py

# 运行测试
python3 -m pytest tests/ -v
```

### 🎮 GUI 可视化界面

支持 Docker 容器化的图形界面，可在浏览器中查看游戏运行效果：

```bash
# 启动 GUI 环境
./scripts/docker_gui_simulation.sh

# 访问 Web VNC
open http://localhost:6080/vnc.html
```

### 🔧 高级功能

- **智能版本检测**: 自动跳过已安装且版本匹配的组件
- **一键镜像生成**: 自动构建可烧录的树莓派镜像
- **Docker 支持**: 完整的容器化开发环境
- **可视化界面**: 支持 VNC 远程桌面访问



## 🚀 最新构建信息

**构建时间**: 2025-07-04 10:38:28  
**构建版本**: 1.0.0  
**支持平台**: Raspberry Pi 3B+/4/400  

### 📦 可用下载

- **完整部署包**: `output/gameplayer-raspberry-20250704.tar.gz`
- **树莓派镜像**: `output/*_gameplayer.img.gz`
- **校验文件**: `output/*.sha256`

### ⚡ 快速开始

#### 方式一：使用预构建镜像（推荐）
```bash
# 1. 下载镜像文件
wget https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry/releases/latest/download/retropie_gameplayer.img.gz

# 2. 验证校验和
sha256sum -c retropie_gameplayer.img.gz.sha256

# 3. 使用 Raspberry Pi Imager 烧录到SD卡
```

#### 方式二：智能安装
```bash
# 克隆项目
git clone https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry.git
cd GamePlayer-Raspberry

# 一键安装（自动跳过已安装组件）
python3 scripts/smart_installer.py

# 运行测试
python3 -m pytest tests/ -v
```

### 🎮 GUI 可视化界面

支持 Docker 容器化的图形界面，可在浏览器中查看游戏运行效果：

```bash
# 启动 GUI 环境
./scripts/docker_gui_simulation.sh

# 访问 Web VNC
open http://localhost:6080/vnc.html
```

### 🔧 高级功能

- **智能版本检测**: 自动跳过已安装且版本匹配的组件
- **一键镜像生成**: 自动构建可烧录的树莓派镜像
- **Docker 支持**: 完整的容器化开发环境
- **可视化界面**: 支持 VNC 远程桌面访问


# 源代码目录

## 目录结构

- `core/` - 核心模块
- `scripts/` - 脚本工具
- `web/` - Web相关文件
- `systems/` - 系统集成模块
