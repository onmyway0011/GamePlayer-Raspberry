# GamePlayer-Raspberry: 树莓派RetroPie游戏环境自动化工具集

这是一个完整的树莓派RetroPie游戏环境自动化安装和优化工具集，提供从镜像烧录到游戏生态扩展的全套解决方案。

## 🎮 功能特性

### 核心功能
- ✅ **跨平台镜像烧录**: 支持Windows/Linux/macOS的RetroPie镜像自动下载和烧录
- ✅ **ROM自动下载**: 从合法资源站自动下载游戏合集并传输到树莓派
- ✅ **HDMI优化配置**: 自动优化显示输出为1080p@60Hz，禁用过扫描
- ✅ **蓝牙设备配对**: PS4手柄和蓝牙耳机的自动配对和连接
- ✅ **系统性能调优**: SSD优化、服务精简、I/O调度器优化
- ✅ **游戏生态扩展**: 自动封面下载、主题安装、云存档同步

### 高级功能
- ✅ **沉浸式体验**: 街机控制器校准、光枪配对、GPIO灯光控制
- ✅ **零交互自动化**: 支持无人值守的批量部署
- ✅ **智能错误处理**: 完整的回滚机制和错误恢复
- ✅ **详细日志记录**: 所有操作都有完整的日志追踪

## 📋 系统要求

### 基础要求
- **树莓派**: 树莓派4B（推荐）或树莓派3B+
- **操作系统**: RetroPie 4.8+
- **存储**: 至少16GB SD卡（推荐32GB+）
- **网络**: 稳定的网络连接

### 开发环境
- **Python**: 3.7+
- **依赖库**: 见requirements.txt
- **权限**: sudo权限（用于系统配置修改）

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/GamePlayer-Raspberry.git
cd GamePlayer-Raspberry
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 基础安装流程
```bash
# 1. 镜像烧录
python retropie_installer.py

# 2. ROM下载和传输
python rom_downloader.py

# 3. HDMI配置优化
python hdmi_config.py

# 4. 游戏生态扩展
bash retropie_ecosystem_auto.sh

# 5. 沉浸式硬件配置
bash immersive_hardware_auto.sh
```

## 📁 项目结构

```
GamePlayer-Raspberry/
├── 📄 核心工具
│   ├── retropie_installer.py      # RetroPie镜像下载和烧录
│   ├── rom_downloader.py          # ROM下载和传输工具
│   ├── hdmi_config.py             # HDMI配置优化
│   └── requirements.txt           # Python依赖
│
├── 🔧 自动化脚本
│   ├── retropie_ecosystem_auto.sh # 游戏生态全自动优化
│   ├── immersive_hardware_auto.sh # 沉浸式硬件配置
│   ├── install.sh                 # Linux/macOS安装脚本
│   └── install.bat                # Windows安装脚本
│
├── 🧪 测试文件
│   ├── test_installer.py          # 安装器测试
│   ├── test_rom_downloader.py     # ROM下载器测试
│   └── test_hdmi_config.py        # HDMI配置测试
│
├── 📋 配置文件
│   ├── rom_config.json            # ROM下载配置
│   └── .gitignore                 # Git忽略文件
│
├── 📚 文档
│   ├── README.md                  # 主文档
│   ├── README_HDMI.md             # HDMI配置详细说明
│   └── LICENSE                    # 许可证
│
└── 📦 下载目录
    └── downloads/                 # 自动创建的下载目录
```

## 🛠️ 详细使用指南

### 1. RetroPie镜像安装

#### 基本使用
```bash
# 完整流程（下载+烧录）
python retropie_installer.py

# 仅检查系统依赖
python retropie_installer.py --check-only

# 仅下载镜像
python retropie_installer.py --download-only

# 列出可用磁盘
python retropie_installer.py --list-disks
```

#### 平台特定说明
- **Windows**: 自动下载镜像，提示手动使用Win32DiskImager烧录
- **Linux/macOS**: 支持自动dd命令烧录，需要sudo权限

### 2. ROM下载和传输

#### 配置设置
编辑`rom_config.json`文件：
```json
{
  "raspberry_pi": {
    "host": "192.168.1.100",
    "port": 22,
    "username": "pi",
    "password": "your_password",
    "roms_path": "/home/pi/RetroPie/roms/nes/"
  }
}
```

#### 执行下载
```bash
# 搜索并下载NES 100-in-1合集
python rom_downloader.py

# 自定义搜索
python rom_downloader.py --search "nes games collection"
```

### 3. HDMI配置优化

#### 基本配置
```bash
# 应用HDMI优化配置
python hdmi_config.py

# 预览将要应用的更改
python hdmi_config.py --dry-run

# 恢复原始配置
python hdmi_config.py --restore
```

#### 配置项说明
- `hdmi_group=1`: HDMI组1（CEA标准）
- `hdmi_mode=16`: 1080p@60Hz分辨率
- `disable_overscan=1`: 禁用过扫描实现全屏
- `gpu_mem=256`: GPU显存256MB

### 4. 游戏生态扩展

#### 全自动优化
```bash
# 一键优化所有游戏生态功能
bash retropie_ecosystem_auto.sh
```

#### 功能包括
- 自动封面和元数据下载（Skraper）
- 主题批量安装和自动切换
- Netplay局域网联机配置
- 云存档同步（Google Drive/Dropbox）

### 5. 沉浸式硬件配置

#### 硬件支持
```bash
# 配置沉浸式外设
bash immersive_hardware_auto.sh
```

#### 支持的外设
- PS4手柄蓝牙配对
- 蓝牙耳机A2DP连接
- 街机控制器校准
- Sinden光枪配对
- Wii体感控制器
- GPIO灯光控制（WS2812B）
- 震动反馈引擎

## 🔧 高级配置

### 系统性能调优

#### 自动调优脚本
```bash
# 系统级性能优化
bash system_tuneup.sh
```

#### 优化项目
- SSD替换和优化
- 系统服务精简
- I/O调度器切换为kyber
- CPU超频和散热设置
- 外置GPU扩展

### 网络和存储优化

#### 网络配置
- 自动WiFi配置
- 网络性能优化
- 远程访问设置

#### 存储优化
- 自动SSD检测和迁移
- 存储性能优化
- 备份策略配置

## 🐛 故障排除

### 常见问题

#### 1. 权限错误
```bash
# Linux/macOS权限问题
sudo python retropie_installer.py

# Windows管理员权限
# 以管理员身份运行命令提示符
```

#### 2. 网络连接问题
```bash
# 检查网络连接
ping -c 1 www.google.com

# 检查DNS解析
nslookup retropie.org.uk
```

#### 3. 磁盘空间不足
```bash
# 检查磁盘空间
df -h

# 清理临时文件
rm -rf downloads/*.tmp
```

#### 4. 蓝牙配对失败
```bash
# 重启蓝牙服务
sudo systemctl restart bluetooth

# 清除蓝牙缓存
sudo rm -rf /var/lib/bluetooth/*
```

### 日志文件
所有工具都会生成详细的日志文件：
- `retropie_installer.log`: 镜像安装日志
- `rom_downloader.log`: ROM下载日志
- `hdmi_config.log`: HDMI配置日志
- `retropie_ecosystem_auto.log`: 生态优化日志

## 📊 性能基准

### 测试环境
- **硬件**: 树莓派4B 4GB
- **存储**: SanDisk Extreme 32GB
- **网络**: 千兆以太网

### 性能指标
- **镜像下载**: ~15分钟（1GB镜像）
- **ROM传输**: ~5分钟（100个ROM）
- **系统启动**: ~30秒
- **游戏加载**: ~2-5秒

## 🔄 版本历史

### v2.0.0 (2024-06-24)
- 🎉 **重大更新**: 完整的游戏环境自动化工具集
- ✨ **新功能**: 
  - 沉浸式硬件自动配置
  - 零交互全自动优化
  - 智能错误处理和回滚
  - 云存档同步功能
- 🔧 **优化**: 
  - 代码文档结构优化
  - 错误处理机制改进
  - 日志系统完善
- 🐛 **修复**: 
  - Pylance静态分析错误
  - 变量定义问题
  - 导入语句优化

### v1.5.0 (2024-06-20)
- ✨ **新功能**: 
  - 游戏生态扩展脚本
  - 自动封面和元数据下载
  - 主题批量安装
  - Netplay配置
- 🔧 **优化**: 
  - 系统性能调优
  - 网络配置优化
  - 存储性能提升

### v1.2.0 (2024-06-15)
- ✨ **新功能**: 
  - HDMI配置优化
  - 蓝牙设备自动配对
  - ROM下载和传输
- 🔧 **优化**: 
  - 跨平台兼容性
  - 错误处理机制
  - 日志记录系统

### v1.0.0 (2024-06-10)
- 🎉 **初始版本**: 
  - RetroPie镜像下载和烧录
  - 跨平台支持
  - 基础自动化功能

## 🤝 贡献指南

### 提交Issue
1. 检查现有Issue避免重复
2. 提供详细的错误信息和环境描述
3. 附上相关的日志文件

### 提交Pull Request
1. Fork项目并创建功能分支
2. 遵循代码风格和文档规范
3. 添加必要的测试用例
4. 更新相关文档

### 代码规范
- 使用Google风格的Python文档字符串
- 遵循PEP 8代码风格
- 添加类型注解
- 包含错误处理

## 📄 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件。

## 🙏 致谢

- [RetroPie](https://retropie.org.uk/) - 优秀的树莓派游戏系统
- [Archive.org](https://archive.org/) - 提供ROM资源
- [Skraper](https://www.skraper.net/) - 游戏封面和元数据工具
- 开源社区 - 提供各种工具和库

## 📞 支持

- 📧 **邮箱**: support@example.com
- 💬 **讨论**: [GitHub Discussions](https://github.com/yourusername/GamePlayer-Raspberry/discussions)
- 🐛 **问题**: [GitHub Issues](https://github.com/yourusername/GamePlayer-Raspberry/issues)
- 📖 **文档**: [Wiki](https://github.com/yourusername/GamePlayer-Raspberry/wiki)

---

**注意**: 本项目仅用于教育和研究目的。请确保遵守当地法律法规，仅下载您拥有合法权利的游戏ROM。 