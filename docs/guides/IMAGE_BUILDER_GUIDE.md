# 💾 一键树莓派镜像生成指南

## 🚀 快速开始

### 一键构建完整镜像
```bash
git clone https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry.git
cd GamePlayer-Raspberry

# 完整自动化构建（推荐）
./src/scripts/one_click_image_builder.sh

# 或使用高级构建脚本
./src/scripts/auto_build_and_deploy.sh
```

## 📦 集成软件清单

### 🎮 游戏系统
- **4种模拟器**: mednafen、fceux、snes9x、visualboyadvance-m
- **100+游戏ROM**: 合法自制游戏、公有领域游戏、演示ROM
- **金手指系统**: 预配置作弊码（无限生命、无敌模式、关卡选择）
- **自动存档**: 游戏进度自动保存/加载，支持多存档槽

### 🌐 Web管理系统
- **游戏选择器**: http://树莓派IP:8080/game_switcher/
- **管理界面**: http://树莓派IP:3000 系统控制面板
- **文件浏览器**: http://树莓派IP:8080 ROM文件管理
- **在线游戏**: 浏览器直接运行游戏

### 🔧 系统服务
- **VNC服务**: 远程桌面访问 (端口5901)
- **音频系统**: USB音频 + 蓝牙音频自动连接
- **手柄支持**: USB手柄自动检测和配置
- **网络服务**: SSH、HTTP、VNC自动启动

### 🤖 自动化功能
- **开机自启**: 系统启动后自动进入游戏界面
- **自动更新**: 定时拉取最新ROM源和模拟器
- **自动修复**: 智能检测和修复系统问题
- **状态监控**: 实时系统状态和性能监控

## 🏗️ 构建过程

### 系统要求
- **操作系统**: Linux (推荐Ubuntu 20.04+)
- **磁盘空间**: 8GB+ 可用空间
- **内存**: 4GB+ RAM
- **权限**: 管理员权限 (sudo)
- **网络**: 互联网连接

### 构建阶段

#### 阶段1: 环境检查
```bash
# 自动检查系统要求
- 检查操作系统类型
- 验证磁盘空间
- 检查网络连接
- 验证管理员权限
```

#### 阶段2: 基础镜像
```bash
# 下载RetroPie基础镜像
- RetroPie 4.8 (Raspberry Pi 4/400)
- 自动校验MD5/SHA256
- 支持断点续传
```

#### 阶段3: 系统定制
```bash
# 安装和配置软件
- Python 3.8+环境
- Web服务器 (Flask)
- 4种游戏模拟器
- 100+游戏ROM
- 金手指系统
- 自动启动服务
```

#### 阶段4: 优化清理
```bash
# 镜像优化
- 清理APT缓存
- 删除临时文件
- 压缩镜像文件
- 生成校验和
```

## 📊 输出文件

构建完成后生成以下文件：

```
output/
├── retropie_gameplayer_complete.img.gz     # 完整镜像文件 (~2.5GB)
├── retropie_gameplayer_complete.img.info   # 镜像信息文件
├── retropie_gameplayer_complete.img.sha256 # 校验和文件
└── README_镜像使用说明.md                  # 详细使用说明
```

## 🔧 高级选项

### 自定义构建
```bash
# 指定输出目录
export BUILD_DIR="/custom/output/path"
./src/scripts/one_click_image_builder.sh

# 跳过ROM下载
export SKIP_ROM_DOWNLOAD=true
./src/scripts/one_click_image_builder.sh

# 启用调试模式
export DEBUG_MODE=true
./src/scripts/one_click_image_builder.sh
```

### 指定镜像类型
```bash
# RetroPie 4.8 (默认)
python3 src/scripts/raspberry_image_builder.py retropie_4.8

# Raspberry Pi OS Lite
python3 src/scripts/raspberry_image_builder.py raspios_lite
```

### 批量操作
```bash
# 批量烧录SD卡
./src/scripts/batch_burn_sd.sh

# 镜像压缩优化
./src/scripts/shrink_image_and_cleanup.sh
```

## ⚡ 烧录指南

### 使用Raspberry Pi Imager (推荐)
1. 下载 [Raspberry Pi Imager](https://www.raspberrypi.org/software/)
2. 选择"Use custom image"
3. 选择生成的 `.img.gz` 文件
4. 选择SD卡并烧录

### 使用命令行
```bash
# 直接烧录压缩文件
sudo dd if=retropie_gameplayer_complete.img.gz of=/dev/sdX bs=4M status=progress

# 或先解压再烧录
gunzip retropie_gameplayer_complete.img.gz
sudo dd if=retropie_gameplayer_complete.img of=/dev/sdX bs=4M status=progress conv=fsync
```

## 🎮 首次启动

1. **插入SD卡**: 将烧录好的SD卡插入树莓派
2. **连接设备**: 连接显示器、键盘、鼠标、网络
3. **开机启动**: 系统自动扩展文件系统并重启
4. **自动配置**: 首次启动自动检测硬件并配置
5. **进入游戏**: 系统自动启动游戏选择界面

## 📱 访问方式

- **本地操作**: 直接在树莓派上使用
- **Web访问**: http://树莓派IP:8080/game_switcher/
- **VNC远程**: VNC客户端连接 树莓派IP:5901
- **SSH访问**: ssh pi@树莓派IP (密码: raspberry)

## 🐛 故障排除

### 构建失败
```bash
# 检查系统要求
./src/scripts/one_click_image_builder.sh --check-only

# 清理并重试
rm -rf output/temp/
./src/scripts/one_click_image_builder.sh
```

### 烧录失败
```bash
# 检查SD卡
sudo fdisk -l

# 格式化SD卡
sudo mkfs.fat -F32 /dev/sdX1
```

### 启动失败
- 检查SD卡是否正确烧录
- 确认树莓派型号兼容性 (支持3B+/4/400)
- 检查电源供应 (推荐5V 3A)
- 查看启动日志排查问题

## 📈 性能优化

### 镜像大小优化
```bash
# 使用镜像压缩工具
./src/scripts/shrink_image_and_cleanup.sh

# 手动清理不需要的包
sudo chroot /mnt/image apt-get remove --purge -y package_name
```

### 启动速度优化
```bash
# 禁用不需要的服务
sudo systemctl disable service_name

# 优化启动脚本
# 编辑 /etc/rc.local
```

## 🔄 更新和维护

### 更新镜像
```bash
# 重新构建最新镜像
git pull origin main
./src/scripts/one_click_image_builder.sh
```

### 增量更新
```bash
# 仅更新特定组件
python3 src/scripts/auto_update_rom_sources.py
python3 src/scripts/smart_installer.py
```

---

**🎉 享受一键生成的完整树莓派游戏系统！**
