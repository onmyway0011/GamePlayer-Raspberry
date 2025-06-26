# 🎮 ROM 使用指南

## 📋 概述

GamePlayer-Raspberry 项目现在包含了完整的 NES ROM 自动下载和管理系统，可以自动获取推荐的开源和免费 ROM 文件，并集成到树莓派镜像中。

## 🚀 快速开始

### 自动下载 ROM

```bash
# 下载所有推荐 ROM
python3 scripts/rom_downloader.py

# 下载特定分类
python3 scripts/rom_downloader.py --category homebrew

# 指定输出目录
python3 scripts/rom_downloader.py --output /path/to/roms
```

### ROM 管理

```bash
# 列出所有 ROM
python3 scripts/rom_manager.py list

# 验证 ROM 文件
python3 scripts/rom_manager.py verify

# 清理无效 ROM
python3 scripts/rom_manager.py clean

# 备份 ROM
python3 scripts/rom_manager.py backup /path/to/backup

# 恢复 ROM
python3 scripts/rom_manager.py restore /path/to/backup
```

## 📦 ROM 分类

### 🏠 自制游戏 (Homebrew)
现代开发者制作的高质量 NES 游戏：
- **Micro Mages**: 现代 NES 平台游戏杰作
- **Blade Buster**: 横版射击游戏
- **Twin Dragons**: 双人合作动作游戏

### 🌍 公有领域游戏 (Public Domain)
无版权限制的经典游戏：
- **Tetris Clone**: 俄罗斯方块克隆版
- **Snake Game**: 贪吃蛇游戏

### 🧪 演示 ROM (Demo ROMs)
用于测试模拟器功能：
- **NESTest**: NES 模拟器测试 ROM
- **Color Test**: 颜色显示测试

## 📁 目录结构

```
/home/pi/RetroPie/roms/nes/
├── *.nes                    # NES ROM 文件
├── rom_catalog.json         # ROM 目录信息
├── playlists/              # 播放列表
│   ├── homebrew.m3u        # 自制游戏列表
│   ├── public_domain.m3u   # 公有领域游戏
│   └── demo_roms.m3u       # 演示ROM列表
└── README.md               # ROM 信息文档
```

## 🔧 集成到镜像

ROM 下载功能已完全集成到镜像构建过程中：

### 智能安装器集成
```bash
# 运行智能安装器（自动下载 ROM）
python3 scripts/smart_installer.py
```

### 镜像构建集成
```bash
# 构建包含 ROM 的镜像
python3 scripts/raspberry_image_builder.py
```

### 全自动构建
```bash
# 一键构建（包含 ROM 下载）
./scripts/auto_build_and_deploy.sh
```

## 🎯 使用方法

### 在 RetroPie 中使用

1. **通过 EmulationStation**:
   - 启动 RetroPie
   - 选择 "Nintendo Entertainment System"
   - 选择要玩的游戏

2. **通过命令行**:
   ```bash
   # 使用 Nesticle 模拟器
   cd /opt/retropie/emulators/nesticle
   ./nesticle /home/pi/RetroPie/roms/nes/game.nes
   
   # 使用 VirtuaNES 模拟器
   cd /opt/retropie/emulators/virtuanes
   ./virtuanes /home/pi/RetroPie/roms/nes/game.nes
   ```

3. **通过 RetroArch**:
   ```bash
   retroarch -L /path/to/nes_core.so /home/pi/RetroPie/roms/nes/game.nes
   ```

### 播放列表使用

```bash
# 查看可用播放列表
python3 scripts/rom_manager.py playlists

# 创建自定义播放列表
python3 scripts/rom_manager.py playlist "我的最爱" game1.nes game2.nes game3.nes
```

## 🛠️ 高级功能

### 自定义 ROM 源

编辑 `scripts/rom_downloader.py` 中的 `recommended_roms` 字典：

```python
"custom_category": {
    "name": "自定义分类",
    "description": "我的自定义ROM",
    "roms": {
        "my_game": {
            "name": "我的游戏",
            "description": "自定义游戏描述",
            "url": "https://example.com/my_game.nes",
            "size_kb": 32,
            "genre": "动作",
            "year": 2025,
            "free": True
        }
    }
}
```

### 备用 ROM 系统

当网络下载失败时，系统会自动创建备用 ROM 文件：

```python
# 自动生成的备用 ROM 包含：
- 有效的 NES 文件头
- 基本的 PRG ROM 和 CHR ROM 数据
- 游戏标题信息
- 最小可运行结构
```

### ROM 验证

系统会自动验证 ROM 文件的完整性：

```bash
# 验证 ROM 文件格式
python3 scripts/rom_manager.py verify

# 输出示例：
# ✅ game1.nes - 有效的NES ROM
# ❌ invalid.nes - 无效的文件格式
```

## 📊 配置选项

在 `config/packages.json` 中配置 ROM 相关设置：

```json
{
  "rom_configuration": {
    "download_enabled": true,
    "rom_directory": "/home/pi/RetroPie/roms/nes",
    "backup_directory": "/home/pi/RetroPie/roms/backup",
    "max_rom_size_mb": 10,
    "categories": {
      "homebrew": {
        "enabled": true,
        "priority": 1
      }
    }
  }
}
```

## 🔐 法律声明

### 包含的 ROM 类型

所有自动下载的 ROM 文件均为：
- ✅ **开源自制游戏**: 现代开发者创作的免费游戏
- ✅ **公有领域作品**: 无版权限制的经典游戏
- ✅ **测试用 ROM**: 用于模拟器测试的演示文件
- ✅ **备用 ROM**: 系统生成的最小测试文件

### 使用须知

- 🚫 **不包含商业游戏**: 不会下载任何受版权保护的商业游戏
- ✅ **完全合法**: 所有 ROM 文件都可以合法分发和使用
- 📝 **遵守许可**: 请遵守各个游戏的开源许可协议
- 🌍 **地区法律**: 请确保遵守当地法律法规

## 🐛 故障排除

### 常见问题

1. **下载失败**:
   ```bash
   # 检查网络连接
   ping github.com
   
   # 手动重试下载
   python3 scripts/rom_downloader.py --category demo_roms
   ```

2. **ROM 文件损坏**:
   ```bash
   # 验证 ROM 文件
   python3 scripts/rom_manager.py verify
   
   # 清理无效文件
   python3 scripts/rom_manager.py clean
   ```

3. **权限问题**:
   ```bash
   # 修复权限
   sudo chown -R pi:pi /home/pi/RetroPie/roms/nes/
   chmod 644 /home/pi/RetroPie/roms/nes/*.nes
   ```

### 日志查看

```bash
# 查看下载日志
tail -f image_builder.log

# 查看安装日志
tail -f smart_installer.log
```

## 📞 技术支持

如有问题，请：
1. 查看项目 README.md
2. 检查 GitHub Issues
3. 运行诊断命令：
   ```bash
   python3 scripts/rom_manager.py verify
   python3 -m pytest tests/test_rom_integration.py -v
   ```

---

**构建时间**: 2025-06-26  
**版本**: 1.0.0  
**状态**: ✅ 完成
