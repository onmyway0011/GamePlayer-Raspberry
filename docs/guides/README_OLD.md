
## 🚀 最新构建信息

**构建时间**: 2025-06-26 15:47:51  
**构建版本**: 1.0.0  
**支持平台**: Raspberry Pi 3B+/4/400  

### 📦 可用下载

- **完整部署包**: `output/gameplayer-raspberry-20250626.tar.gz`
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

### 🎮 50款NES游戏体验

内置50款精选的开源和免费NES游戏，开箱即用：

```bash
# 快速演示50款游戏
./demo_50_games.sh

# 下载所有游戏
python3 scripts/rom_downloader.py

# 启动游戏选择器
python3 scripts/nes_game_launcher.py
```

#### 🎯 游戏分类
- **自制游戏**: 10款现代开发的高质量NES游戏
- **公有领域**: 10款经典无版权限制游戏
- **益智游戏**: 5款考验智力的益智游戏
- **动作游戏**: 5款快节奏动作游戏
- **角色扮演**: 5款经典RPG游戏
- **体育游戏**: 5款各种体育运动游戏
- **演示ROM**: 5款测试和验证用ROM
- **额外游戏**: 5款精选备用游戏

### 🐳 Docker树莓派模拟环境

完整的树莓派Docker模拟环境，支持图形界面和Web管理：

```bash
# 启动完整模拟环境
./scripts/raspberry_docker_sim.sh

# 使用Docker Compose
docker-compose up -d

# 访问方式
open http://localhost:6080/vnc.html    # VNC Web界面
open http://localhost:3000             # Web管理界面
```

### 🔧 高级功能

#### 🎮 游戏功能
- **50款精选游戏**: 自动下载开源和免费NES游戏
- **智能ROM管理**: 自动分类、验证和备份ROM文件
- **游戏启动器**: 图形界面游戏选择和启动
- **播放列表**: 自动生成分类游戏列表
- **备用ROM系统**: 网络失败时自动生成测试ROM

#### 🐳 Docker环境
- **树莓派模拟**: 完整ARM64架构模拟环境
- **VNC远程桌面**: 浏览器访问图形界面
- **Web管理界面**: ROM文件上传和管理
- **容器化部署**: 一键启动完整环境

#### 🛠️ 系统功能
- **智能版本检测**: 自动跳过已安装且版本匹配的组件
- **一键镜像生成**: 自动构建可烧录的树莓派镜像
- **错误自动修复**: 智能检测并修复常见问题
- **完整测试覆盖**: 自动化测试验证所有功能

### ⚖️ 法律合规

所有包含的ROM文件均为完全合法的内容：
- ✅ **开源自制游戏**: 现代开发者创作的免费游戏
- ✅ **公有领域作品**: 无版权限制的经典游戏
- ✅ **测试用ROM**: 用于模拟器测试的演示文件
- 🚫 **不包含商业游戏**: 绝不包含任何受版权保护的商业游戏


