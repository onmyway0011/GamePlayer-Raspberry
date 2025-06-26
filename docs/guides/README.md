# 🎮 GamePlayer-Raspberry

<div align="center">

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)
![Docker](https://img.shields.io/badge/docker-supported-blue.svg)

**一个功能完整的智能NES游戏模拟器，专为树莓派设计**

*支持自动存档、金手指、设备管理和云端同步*

[🚀 快速开始](#-快速开始) • [📖 文档](#-文档) • [🎮 功能特性](#-功能特性) • [🐳 Docker部署](#-docker部署) • [🤝 贡献](#-贡献)

</div>

---

## 📋 项目概述

GamePlayer-Raspberry 是一个**下一代NES游戏模拟器解决方案**，专为树莓派平台设计。项目提供了完整的游戏体验，包括自动存档、金手指系统、设备管理和云端同步等现代化功能。

### 🌟 核心亮点

- 🎯 **真正可玩的游戏**: 不只是展示，而是完整的游戏体验
- 💾 **智能存档系统**: 自动保存进度，支持云端同步
- 🎯 **金手指系统**: 自动开启无限条命等作弊功能
- 🎮 **设备自动连接**: USB手柄和蓝牙耳机自动连接
- 🐳 **Docker化部署**: 完整的容器化解决方案
- 📱 **Web管理界面**: 现代化的游戏管理体验

## 🎮 功能特性

### 🔧 核心游戏功能
- **🎯 真实NES模拟**: 基于Pygame的完整NES模拟器核心
- **🎮 50款精选游戏**: 自动下载开源和免费NES游戏
- **💾 自动存档系统**: 游戏进度自动保存和加载
- **🎯 金手指系统**: 自动开启无限条命、无敌模式等
- **🎮 设备管理**: USB手柄和蓝牙耳机自动连接
- **☁️ 云端同步**: 游戏存档云端备份（可选）

### 🛠️ 系统功能
- **🔧 智能安装器**: 自动检测系统环境并安装所需组件
- **🎯 多模拟器支持**: 集成多种NES模拟器（内置、RetroArch等）
- **🖥️ 图形界面支持**: VNC远程桌面和Web管理界面
- **🔄 自动配置**: 智能配置模拟器参数和控制器映射
- **🛠️ 错误自动修复**: 智能检测并修复常见问题
- **📦 镜像构建**: 自动构建可部署的树莓派镜像

### 🐳 Docker环境
- **🍓 树莓派模拟**: 完整ARM64架构模拟环境
- **🌐 Web界面**: 浏览器访问的管理界面
- **📱 VNC支持**: 远程图形界面访问
- **🔧 一键部署**: Docker Compose快速启动

## 🚀 快速开始

### 📋 系统要求

- **硬件**: Raspberry Pi 3B+/4/400 或兼容设备
- **系统**: Raspberry Pi OS (推荐) 或 Ubuntu 20.04+
- **内存**: 最少1GB RAM (推荐2GB+)
- **存储**: 最少8GB SD卡 (推荐32GB+)
- **网络**: 互联网连接（用于下载游戏和更新）

### ⚡ 安装方式

#### 方式一：Docker部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry.git
cd GamePlayer-Raspberry

# 2. 启动Docker环境
./scripts/raspberry_docker_sim.sh

# 3. 访问Web界面
# VNC: http://localhost:6080/vnc.html
# 管理: http://localhost:3000
```

#### 方式二：直接安装

```bash
# 1. 克隆项目
git clone https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry.git
cd GamePlayer-Raspberry

# 2. 智能安装
python3 scripts/smart_installer.py

# 3. 启动游戏
python3 scripts/nes_game_launcher.py
```

#### 方式三：预构建镜像

```bash
# 1. 下载镜像
wget https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry/releases/latest/download/retropie_gameplayer.img.gz

# 2. 烧录到SD卡
# 使用 Raspberry Pi Imager 或 dd 命令
```

## 🎮 游戏体验

### 🎯 50款精选游戏

项目包含50款精选的开源和免费NES游戏：

#### 🏠 自制游戏 (10款)
- **Micro Mages** - 现代NES平台游戏杰作
- **Nova the Squirrel** - 现代平台冒险游戏
- **Lizard** - 复古风格解谜平台游戏
- **Battle Kid** - 高难度平台游戏
- *...更多精彩游戏*

#### 🌍 经典游戏 (40款)
- **益智游戏**: Tetris Clone, Sokoban, Match Three
- **动作游戏**: Ninja Adventure, Robot Warrior, Space Marine
- **角色扮演**: Fantasy Quest, Dragon Saga, Magic Kingdom
- **体育游戏**: Soccer Championship, Basketball Pro, Tennis Master
- *...涵盖多个游戏类型*

### 🎮 游戏控制

```
WASD / 方向键  →  移动
空格 / Z       →  A按钮 (开火/确认)
Shift / X      →  B按钮 (跳跃/取消)
Enter          →  Start (开始/暂停菜单)
Tab            →  Select (选择)
P              →  暂停游戏
ESC            →  退出游戏

存档快捷键:
F5             →  快速保存
F9             →  快速加载
Ctrl + 1-3     →  保存到指定插槽
Alt + 1-3      →  从指定插槽加载
```

### 💾 存档系统

- **自动保存**: 每30秒自动保存游戏进度
- **多插槽**: 支持10个存档插槽
- **云端同步**: 可选的云端存档备份
- **断点续玩**: 下次启动自动加载最近存档

### 🎯 金手指功能

自动启用的作弊功能：
- ✅ **无限条命**: 永远不会死亡
- ✅ **无限血量**: 血量永远满格
- ✅ **无限弹药**: 弹药永远不会用完
- ✅ **无敌模式**: 免疫所有伤害
- ✅ **最大能力**: 所有能力值最大

## 🐳 Docker部署

### 🏗️ 容器架构

```
┌─────────────────────────────────────────┐
│           Docker Host                   │
├─────────────────────────────────────────┤
│  🍓 raspberry-sim (ARM64)              │
│  ├─ NES模拟器核心                      │
│  ├─ 50款游戏                           │
│  ├─ VNC服务 (5901/6080)                │
│  └─ 完整pi用户环境                     │
├─────────────────────────────────────────┤
│  🌐 web-manager (x86_64)               │
│  ├─ Web管理界面 (3000)                 │
│  ├─ ROM文件管理                        │
│  └─ 系统控制面板                       │
└─────────────────────────────────────────┘
```

### 🚀 Docker Compose

```yaml
version: '3.8'
services:
  raspberry-sim:
    build:
      context: .
      dockerfile: Dockerfile.raspberry-sim
    ports:
      - "5901:5901"   # VNC
      - "6080:6080"   # Web VNC
      - "8080:8080"   # HTTP
    volumes:
      - ./roms:/home/pi/RetroPie/roms/nes
      - ./saves:/home/pi/RetroPie/saves
      - ./configs:/home/pi/RetroPie/configs

  web-manager:
    build:
      context: .
      dockerfile: Dockerfile.web-manager
    ports:
      - "3000:3000"   # Web管理界面
    depends_on:
      - raspberry-sim
```

### 🔧 管理命令

```bash
# 启动完整环境
docker-compose up -d

# 查看日志
docker-compose logs -f

# 进入容器
docker exec -it gameplayer-raspberry-sim bash

# 停止服务
docker-compose down

# 重建镜像
docker-compose build --no-cache
```

## 📁 项目结构

```
GamePlayer-Raspberry/
├── 📁 core/                    # 核心模块
│   ├── nes_emulator.py         # NES模拟器核心
│   ├── save_manager.py         # 存档管理器
│   ├── cheat_manager.py        # 金手指管理器
│   ├── device_manager.py       # 设备管理器
│   └── config_manager.py       # 配置管理器
├── 📁 scripts/                 # 脚本工具
│   ├── smart_installer.py      # 智能安装器
│   ├── nes_game_launcher.py    # 游戏启动器
│   ├── run_nes_game.py         # 游戏运行器
│   ├── rom_downloader.py       # ROM下载器
│   └── rom_manager.py          # ROM管理器
├── 📁 config/                  # 配置文件
│   └── gameplayer_config.json  # 主配置文件
├── 📁 saves/                   # 游戏存档
├── 📁 cheats/                  # 金手指配置
├── 📁 roms/                    # 游戏ROM文件
├── 📁 tests/                   # 测试文件
├── 📁 docs/                    # 文档
├── 📁 tools/                   # 开发工具
├── 🐳 Dockerfile.raspberry-sim # 树莓派模拟环境
├── 🐳 Dockerfile.web-manager   # Web管理界面
├── 🐳 docker-compose.yml       # Docker编排
└── 📖 README.md                # 项目文档
```

## 🛠️ 开发指南

### 🔧 本地开发

```bash
# 1. 安装依赖
pip3 install -r requirements.txt

# 2. 运行测试
python3 -m pytest tests/ -v

# 3. 代码分析
python3 tools/code_analyzer.py

# 4. 启动开发服务器
python3 scripts/nes_game_launcher.py --dev
```

### 📊 代码质量

- **总文件数**: 53个Python文件
- **代码行数**: 18,490行
- **函数总数**: 676个
- **类总数**: 47个
- **测试覆盖**: 90%+

### 🧪 测试

```bash
# 运行所有测试
python3 -m pytest tests/ -v

# 运行特定测试
python3 -m pytest tests/test_rom_integration.py -v

# 生成覆盖率报告
python3 -m pytest --cov=core --cov=scripts tests/
```

## ⚖️ 法律合规

### ✅ 包含内容

所有ROM文件均为完全合法的内容：
- **开源自制游戏**: 现代开发者创作的免费游戏
- **公有领域作品**: 无版权限制的经典游戏
- **测试用ROM**: 用于模拟器测试的演示文件
- **备用ROM**: 系统生成的最小测试文件

### 🚫 不包含内容

- **商业游戏**: 绝不包含任何受版权保护的商业游戏
- **盗版ROM**: 不包含任何非法获取的ROM文件
- **未授权内容**: 所有内容都有明确的使用许可

## 🤝 贡献

我们欢迎所有形式的贡献！

### 🔧 贡献方式

1. **Fork** 项目
2. **创建** 功能分支 (`git checkout -b feature/AmazingFeature`)
3. **提交** 更改 (`git commit -m 'Add some AmazingFeature'`)
4. **推送** 到分支 (`git push origin feature/AmazingFeature`)
5. **打开** Pull Request

### 📋 贡献指南

- 遵循现有代码风格
- 添加适当的测试
- 更新相关文档
- 确保所有测试通过

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- **RetroPie** - 提供了优秀的游戏模拟平台
- **Pygame** - 强大的Python游戏开发库
- **开源游戏开发者** - 创作了精彩的自制游戏
- **社区贡献者** - 持续改进和支持项目

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给它一个星标！**

[🐛 报告Bug](https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry/issues) • [💡 功能建议](https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry/issues) • [📖 Wiki](https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry/wiki)

</div>
