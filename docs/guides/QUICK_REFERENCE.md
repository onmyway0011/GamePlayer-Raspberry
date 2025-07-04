# 🎮 GamePlayer-Raspberry 快速参考

## 🚀 一键启动命令

### Docker图形化环境
```bash
# 完整图形化环境 (推荐)
./start_docker_gui.sh

# 简化快速环境
./start_simple_docker.sh

# Docker状态检查
./check_docker.sh
```

### 一键镜像生成
```bash
# 生成完整树莓派镜像
./src/scripts/one_click_image_builder.sh

# 高级自动构建
./src/scripts/auto_build_and_deploy.sh
```

### 本地开发环境
```bash
# 快速启动Web服务
python3 src/scripts/simple_demo_server.py

# 运行高级修复工具
python3 src/scripts/advanced_emulator_fixer.py
```

## 🌐 访问地址

| 服务 | Docker环境 | 树莓派环境 | 说明 |
|------|------------|------------|------|
| 🎮 游戏中心 | http://localhost:3020 | http://树莓派IP:8080/game_switcher/ | 游戏选择和启动 |
| 🖥️ VNC桌面 | localhost:5900 | 树莓派IP:5901 | 远程桌面连接 |
| 🌐 Web VNC | http://localhost:6080 | - | 浏览器VNC |
| 📁 文件管理 | http://localhost:8080 | http://树莓派IP:8080 | ROM文件管理 |
| 📊 系统监控 | http://localhost:9000 | http://树莓派IP:3000 | 容器/系统监控 |

## 🎮 支持的游戏系统

| 系统 | 模拟器 | ROM数量 | 特色功能 |
|------|--------|---------|----------|
| 🎯 NES | fceux, mednafen | 13款 | 金手指系统 |
| 🎮 SNES | snes9x, mednafen | 10款 | 高画质渲染 |
| 📱 Game Boy | visualboyadvance-m | 15款 | 存档状态 |
| 🎲 GBA | visualboyadvance-m | 12款 | 快进功能 |
| 🕹️ Genesis | mednafen | 8款 | 音频增强 |
| 💿 PSX | mednafen | 5款 | 3D加速 |
| 🎪 N64 | mupen64plus | 3款 | 高分辨率 |
| 🎰 Arcade | mame | 20+款 | 街机经典 |

## 🔧 管理命令

### Docker环境
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

### 树莓派环境
```bash
# 查看系统状态
sudo systemctl status gameplayer

# 重启游戏服务
sudo systemctl restart gameplayer

# 查看系统日志
journalctl -u gameplayer -f

# 运行自动修复
python3 /home/pi/GamePlayer-Raspberry/src/scripts/advanced_emulator_fixer.py
```

## 📁 文件目录结构

```
GamePlayer-Raspberry/
├── data/
│   ├── roms/           # ROM文件目录
│   │   ├── nes/        # NES游戏ROM
│   │   ├── snes/       # SNES游戏ROM
│   │   ├── gameboy/    # Game Boy ROM
│   │   └── gba/        # GBA游戏ROM
│   ├── saves/          # 游戏存档目录
│   └── web/images/     # 游戏封面图片
├── config/             # 配置文件目录
├── logs/               # 日志文件目录
├── src/scripts/        # 核心脚本目录
├── docs/               # 文档目录
└── output/             # 一键镜像生成输出目录
    ├── retropie_gameplayer_complete.img.gz # 完整镜像文件 (~2.5GB)
    ├── retropie_gameplayer_complete.img.info # 镜像信息文件
    ├── README_镜像使用说明.md # 使用指南
    ├── logs/           # 构建日志
    └── reports/        # 构建报告
```

## 🎯 金手指系统

### 支持的作弊码类型
- **无限生命**: 游戏角色不会死亡
- **无敌模式**: 免疫所有伤害
- **最大能力**: 所有属性达到最大值
- **关卡选择**: 解锁所有关卡
- **无限道具**: 道具数量不减少

### 激活方式
```bash
# 自动激活所有作弊码
python3 src/scripts/auto_cheat_activator.py

# 手动配置特定游戏
python3 src/scripts/cheat_code_manager.py --game "Super Mario Bros"
```

## 🔊 音频和输入设备

### USB设备自动连接
- **USB手柄**: 插入即用，自动配置按键映射
- **USB音频**: 自动切换音频输出设备
- **键盘鼠标**: 即插即用，支持游戏控制

### 蓝牙设备连接
```bash
# 自动连接蓝牙耳机
python3 src/scripts/bluetooth_audio_connector.py

# 手动配置蓝牙设备
bluetoothctl
```

## 🐛 故障排除

### 常见问题
```bash
# Docker启动失败
open -a Docker  # macOS启动Docker Desktop

# 游戏启动失败
python3 src/scripts/advanced_emulator_fixer.py

# VNC连接失败
netstat -an | grep 5900  # 检查端口

# Web界面无法访问
curl http://localhost:3020/api/status  # 检查服务状态
```

### 日志查看
```bash
# Docker环境日志
docker compose logs -f

# 树莓派系统日志
tail -f /home/pi/GamePlayer-Raspberry/logs/system.log

# 游戏启动日志
tail -f /home/pi/GamePlayer-Raspberry/logs/game_launcher.log
```

## 📊 系统要求

### Docker环境
- **CPU**: 2核心+ (推荐4核心)
- **内存**: 4GB+ (推荐8GB)
- **存储**: 10GB+ 可用空间
- **网络**: 互联网连接

### 树莓派环境
- **型号**: Raspberry Pi 3B+/4/400
- **内存**: 2GB+ (推荐4GB)
- **存储**: 32GB+ SD卡 (推荐64GB)
- **电源**: 5V 3A 官方电源

## 🎉 快速开始

1. **选择部署方式**:
   - Docker图形化: `./start_docker_gui.sh`
   - 树莓派镜像: `./src/scripts/one_click_image_builder.sh`

2. **访问游戏界面**:
   - 打开浏览器访问对应的游戏中心地址

3. **开始游戏**:
   - 点击游戏封面即可启动游戏

4. **享受游戏时光**! 🎮

---

**更多详细信息请查看完整文档:**
- [Docker使用指南](DOCKER_GUI_GUIDE.md)
- [镜像构建指南](IMAGE_BUILDER_GUIDE.md)
- [主要README](../README.md)
