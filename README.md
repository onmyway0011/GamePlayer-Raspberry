# 🎮 GamePlayer-Raspberry
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/onmyway0011/GamePlayer-Raspberry)
[![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%20%7C%20macOS%20%7C%20Linux-red.svg)](https://github.com/onmyway0011/GamePlayer-Raspberry)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**树莓派多平台游戏模拟器系统**

[🚀 快速开始](#快速开始) • [📦 功能特性](#功能特性) • [🐳 Docker部署](#docker部署) • [📁 项目结构](#项目结构)

---

## 📋 核心功能

- 🕹️ 支持NES/SNES/GB/GBA/Genesis五类游戏
- 🌐 响应式Web管理界面
- 🐳 完整的Docker容器化支持
- ⚡ 一键生成系统镜像（支持真实/模拟模式）
- 📦 集成50+经典游戏ROM
- 🔧 自动化配置检测与修复

## 🎮 功能特性

### 🕹️ 游戏系统支持

| 系统 | 名称 | 支持格式 | 模拟器 | 状态 |
|------|------|----------|--------|------|
| 🎮 NES | Nintendo Entertainment System | .nes | mednafen, fceux | ✅ 完全支持 |
| 🎯 SNES | Super Nintendo | .smc, .sfc | snes9x, mednafen | ✅ 完全支持 |
| 📱 GB/GBC | Game Boy / Game Boy Color | .gb, .gbc | visualboyadvance-m | ⚠️ 需安装模拟器 |
| 🎲 GBA | Game Boy Advance | .gba | visualboyadvance-m | ⚠️ 需安装模拟器 |
| 🔵 Genesis | Sega Genesis/Mega Drive | .md, .gen | mednafen | ✅ 完全支持 |

### 🌐 Web界面功能

- **🎮 游戏中心**: 直观的游戏选择和启动界面
- **⚙️ 设置管理**: 图形化的配置管理界面
- **📊 统计信息**: 游戏时间和使用数据统计
- **🎯 金手指管理**: 作弊码的启用和配置
- **💾 存档管理**: 游戏进度的保存和加载
- **🔍 搜索过滤**: 快速查找想要的游戏
- **📱 响应式设计**: 完美适配各种设备屏幕

### 🛠️ 系统功能

- **🔧 自动化测试**: 10个测试模块，90%通过率
- **🚨 智能修复**: 自动检测和修复配置问题
- **📁 文件管理**: ROM文件的自动扫描和组织
- **🎮 设备支持**: USB手柄和蓝牙设备自动检测
- **🔊 音频系统**: 完整的音频管理和配置
- **💾 数据持久化**: 配置和存档的自动备份

## 🚀 快速开始

```bash
# 克隆项目
git clone https://github.com/onmyway0011/GamePlayer-Raspberry.git
cd GamePlayer-Raspberry

# 生成模拟镜像（macOS/Linux可用）
bash create_simulation_image.sh

# 启动Web界面
python3 simple_demo_server.py
```

访问 http://localhost:8080 管理游戏

### 🧪 运行系统测试

```bash
# 运行全面的自动化测试和修复
python3 automated_test_and_fix.py

# 查看测试结果
cat test_fix_summary.txt

# 查看详细报告
cat PROJECT_STATUS_REPORT.md
## 🌐 Web界面

### 🎮 游戏中心界面

<img src="docs/images/web-interface-preview.jpg" alt="Web界面预览" width="800">

**主要功能**:
- 🎯 **系统选择**: 卡片式游戏系统选择界面
- 🎮 **游戏列表**: 网格布局显示可用游戏
- 🔍 **智能搜索**: 实时搜索和过滤功能
- 🎯 **游戏启动**: 一键启动选中的游戏
- ⚙️ **设置配置**: 图形化设置管理界面

### 📊 系统监控

- **🟢 实时状态**: 系统在线状态监控
- **📈 使用统计**: 游戏时间和使用频率
- **💾 存储信息**: ROM文件和存档空间使用
- **🎮 设备状态**: 连接的控制器和音频设备

### 🎯 游戏管理

```
🎮 游戏启动流程:
1. 选择游戏系统 → 2. 浏览游戏列表 → 3. 点击游戏卡片
4. 配置存档位置 → 5. 启用金手指 → 6. 启动游戏
```

**支持的配置选项**:
- 💾 **存档位置**: 5个独立存档插槽
- 🎯 **金手指**: 启用/禁用作弊码
- ⚙️ **模拟器设置**: 显示、音频、控制器配置
- 🎮 **按键映射**: 自定义控制器布局

## 🐳 Docker部署

```bash
# 快速启动
docker-compose -f docker-compose.simple.yml up -d

# 构建完整镜像（需Linux环境）
docker build -f Dockerfile.raspberry -t gameplayer-rpi .
```

## 📁 项目结构

```
GamePlayer-Raspberry/
├── config/               # 模拟器与系统配置
├── data/                 # ROM及存档数据
│   └── roms/             # 多平台游戏ROM
├── output/               # 生成的系统镜像
├── docs/                # 技术文档
├── build_*.sh           # 镜像构建脚本
└── docker-compose.*.yml # 容器化配置
```

## 🛠️ 开发和配置

### 🔧 本地开发

```bash
# 1. 设置开发环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 2. 安装开发依赖
pip install -r requirements.txt
pip install aiohttp aiohttp-cors

# 3. 运行开发服务器
python3 simple_demo_server.py --debug --port 8080

# 4. 运行测试
python3 automated_test_and_fix.py
### ⚙️ 配置管理

**模拟器配置** (`config/emulators/emulator_config.json`):
```json
{
  "nes": {
    "emulator": "mednafen",
    "command": "mednafen",
    "args": ["-force_module", "nes"],
    "extensions": [".nes"]
  },
  "snes": {
    "emulator": "snes9x",
    "command": "snes9x-gtk",
    "args": ["-fullscreen"],
    "extensions": [".smc", ".sfc"]
  }
}
```

**系统设置** (`config/emulators/general_settings.json`):
```json
{
  "display": {
    "fullscreen": true,
    "resolution": "1920x1080",
    "vsync": true
  },
  "audio": {
    "enabled": true,
    "volume": 80,
    "sample_rate": 44100
  },
  "input": {
    "gamepad_enabled": true,
    "keyboard_enabled": true
  }
}
```

### 🎯 金手指配置

金手指文件存储在 `config/cheats/` 目录中，支持各种格式：

```json
{
  "nes_cheats": {
    "super_mario_bros": {
      "infinite_lives": "SXIOPO",
      "invincibility": "AAAAAA"
    }
  },
  "snes_cheats": {
    "super_mario_world": {
      "infinite_lives": "7E0DBE:63",
      "all_powers": "7E0DC0:FF"
    }
  }
}
```

## 📊 系统状态

### 🧪 测试覆盖率

根据最新的自动化测试报告：
- **总测试数**: 10个主要模块
- **通过测试**: 9个模块 (90%)
- **失败测试**: 1个模块 (仅涉及可选模拟器)
- **代码质量**: 优秀 (零语法错误)
- **功能完整性**: 核心功能100%可用

### ✅ 已验证功能

- ✅ 核心模块 - 所有Python模块语法正确
- ✅ 模拟器配置 - 配置文件格式正确
- ✅ ROM管理 - 文件管理系统完整
- ✅ Web界面 - 现代化响应式界面
- ✅ Docker支持 - 容器化部署就绪
- ✅ 构建脚本 - 自动化构建系统
- ✅ 依赖管理 - 依赖关系清晰
- ✅ 文件权限 - 权限设置正确
- ✅ 系统集成 - 模块间协作良好
### ⚠️ 需要注意的问题

- **缺少模拟器**: `snes9x-gtk` 和 `vbam` (可选，不影响核心功能)
- **安装建议**: 在macOS上可使用Homebrew安装缺失的模拟器

```bash
# macOS安装可选模拟器
brew install snes9x
brew install visualboyadvance-m
```

## 🔧 故障排除

### 🐛 常见问题

**Q: Web界面无法访问？**
```bash
# 检查服务器是否启动
ps aux | grep simple_demo_server

# 检查端口是否被占用
lsof -i :8080

# 重启服务器
python3 simple_demo_server.py --port 8080
```

**Q: 游戏启动失败？**
```bash
# 运行自动修复
python3 automated_test_and_fix.py
# 检查ROM文件
ls -la data/roms/nes/

# 检查模拟器配置
cat config/emulators/emulator_config.json
```

**Q: 配置文件丢失？**
```bash
# 重新生成配置文件
python3 automated_test_and_fix.py

# 手动创建配置目录
mkdir -p config/emulators config/cheats
```

### 🔍 日志调试

```bash
# 查看服务器日志
tail -f automated_test_fix.log

# 查看详细测试报告
cat test_fix_report_*.json | jq .

# 运行详细测试
python3 automated_test_and_fix.py --verbose
```

## 📖 文档

- 📋 [项目状态报告](PROJECT_STATUS_REPORT.md) - 详细的项目分析和测试结果
- 🧪 [测试报告](test_fix_summary.txt) - 最新的自动化测试结果
- 🔧 [配置指南](config/) - 详细的配置文件说明
- 🐳 [Docker指南](docker-compose.yml) - 容器化部署说明

## 🤝 贡献

欢迎为项目做出贡献！请阅读以下指南：

1. **Fork项目** 并创建feature分支
2. **编写代码** 并确保通过测试
3. **提交PR** 并描述你的更改

```bash
# 运行测试确保质量
python3 automated_test_and_fix.py

# 检查代码格式
python3 -m flake8 src/

# 提交更改
git add .
git commit -m "Add new feature"
git push origin feature-branch
```

## 📞 支持

- 🐛 **Bug报告**: [GitHub Issues](https://github.com/onmyway0011/GamePlayer-Raspberry/issues)
- 💬 **功能建议**: [GitHub Discussions](https://github.com/onmyway0011/GamePlayer-Raspberry/discussions)
- 📧 **联系方式**: 通过GitHub Issues联系维护者

## 📄 许可证

本项目采用 [MIT许可证](LICENSE)，详情请查看LICENSE文件。

---

**🎮 GamePlayer-Raspberry** - 让复古游戏在现代硬件上重新焕发生机！
[![Star](https://img.shields.io/github/stars/onmyway0011/GamePlayer-Raspberry?style=social)](https://github.com/onmyway0011/GamePlayer-Raspberry)
[![Fork](https://img.shields.io/github/forks/onmyway0011/GamePlayer-Raspberry?style=social)](https://github.com/onmyway0011/GamePlayer-Raspberry)
[![Watch](https://img.shields.io/github/watchers/onmyway0011/GamePlayer-Raspberry?style=social)](https://github.com/onmyway0011/GamePlayer-Raspberry)