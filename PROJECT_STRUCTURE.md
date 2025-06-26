# 🏗️ GamePlayer-Raspberry 项目结构

## 📁 完整目录结构

```
GamePlayer-Raspberry/
├── 📄 README.md                          # 项目主文档
├── 📄 requirements.txt                   # Python 依赖包列表
├── 📄 project_config.json               # 全局项目配置
├── 📄 rom_config.json                   # ROM 下载配置
├── 📄 web_config.py                     # Web 配置界面
├── 🐳 Dockerfile                        # Docker 容器配置
├── 🐳 Dockerfile.raspberry              # 树莓派专用 Docker 配置
├── 📄 inject_drivers_to_img.sh          # 镜像驱动注入脚本
├── 📄 publish_api_docs.sh               # API 文档发布脚本
├── 📄 project_file_tree.txt             # 项目文件树
├── 📄 auto_refactor_structure.sh        # 自动重构脚本
│
├── 🎯 core/                              # 核心功能模块
│   ├── 📄 base_installer.py             # 安装器抽象基类
│   ├── 🖥️ hdmi_config.py                # HDMI 显示配置优化
│   ├── 🎮 nesticle_installer.py         # Nesticle 95 模拟器安装器
│   ├── 🎯 virtuanes_installer.py        # VirtuaNES 0.97 模拟器安装器
│   ├── 🔧 retropie_installer.py         # RetroPie 系统安装器
│   └── 📦 rom_downloader.py             # ROM 下载管理工具
│
├── ⚙️ config/                            # 配置文件目录
│   ├── 📄 project_config.json           # 主配置文件
│   ├── 📄 rom_config.json               # ROM 下载配置
│   ├── 📄 requirements.txt              # 依赖包配置
│   ├── 🔧 install.sh                    # Linux/macOS 安装脚本
│   ├── 🔧 install.bat                   # Windows 安装脚本
│   └── 🔧 firstboot_setup.service       # 首次启动服务配置
│
├── 🧪 tests/                             # 测试套件 (44/44 通过)
│   ├── 📄 test_nesticle_installer.py    # Nesticle 安装器测试
│   ├── 📄 test_virtuanes_installer.py   # VirtuaNES 安装器测试
│   ├── 📄 test_retropie_installer.py    # RetroPie 安装器测试
│   ├── 📄 test_rom_downloader.py        # ROM 下载器测试
│   ├── 📄 test_installer.py             # 通用安装器测试
│   └── 📁 logs/                         # 测试日志
│
├── 🤖 scripts/                           # 自动化脚本
│   ├── 🎮 auto_nesticle_integration.sh  # Nesticle 自动集成
│   ├── 🎯 auto_virtuanes_integration.sh # VirtuaNES 自动集成
│   ├── 💾 auto_save_sync.py             # 存档同步工具
│   ├── 🔄 auto_migrate_to_pi.sh         # 自动迁移到树莓派
│   ├── 🎨 retropie_ecosystem_auto.sh    # RetroPie 生态自动化
│   ├── 🎪 immersive_hardware_auto.sh    # 沉浸式硬件配置
│   ├── 💿 batch_burn_sd.sh              # 批量 SD 卡烧录
│   ├── 🐳 docker_build_and_run.sh       # Docker 构建运行
│   ├── 🔧 docker_auto_fix_and_build.sh  # Docker 自动修复构建
│   ├── 🚀 docker_full_auto_ci.sh        # Docker 完整 CI
│   ├── 🎬 docker_start.sh               # Docker 启动脚本
│   ├── 📦 shrink_image_and_cleanup.sh   # 镜像压缩清理
│   ├── 🔗 setup_auto_sync.sh            # 自动同步设置
│   ├── 🎮 demo_nesticle_integration.sh  # Nesticle 演示集成
│   └── 🔄 auto_save_sync_hook.sh        # 存档同步钩子
│
├── 🏗️ systems/                          # 子系统模块
│   ├── 📄 __init__.py                   # Python 包初始化
│   │
│   ├── 🖥️ hdmi/                         # HDMI 配置子系统
│   │   ├── 📄 README.md                 # HDMI 子系统说明
│   │   ├── 🎯 core/
│   │   │   └── 📄 hdmi_config.py        # HDMI 配置核心
│   │   ├── 🧪 tests/
│   │   │   └── 📄 test_hdmi_config.py   # HDMI 配置测试
│   │   └── 📚 docs/                     # HDMI 文档
│   │       ├── 📄 INDEX.md              # 文档索引
│   │       ├── 📄 README_HDMI.md        # HDMI 详细说明
│   │       └── 🌐 api/                  # API 文档
│   │
│   ├── 🔧 retropie/                     # RetroPie 子系统
│   │   ├── 📄 README.md                 # RetroPie 子系统说明
│   │   ├── 🎯 core/                     # 核心功能
│   │   │   ├── 📄 retropie_installer.py # RetroPie 安装器
│   │   │   ├── 📊 log_analyzer.py       # 日志分析器
│   │   │   ├── 📤 log_uploader.py       # 日志上传器
│   │   │   └── ⚙️ logger_config.py      # 日志配置
│   │   ├── 🎮 roms/                     # ROM 管理
│   │   │   └── 📄 rom_downloader.py     # ROM 下载器
│   │   ├── ⚙️ config/                   # 配置文件
│   │   │   ├── 📄 requirements.txt      # 依赖配置
│   │   │   ├── 📄 rom_config.json       # ROM 配置
│   │   │   └── 📄 log_upload_config.json # 日志上传配置
│   │   ├── 🔧 scripts/                  # 部署脚本
│   │   │   ├── 🚀 deploy.sh             # 部署脚本
│   │   │   ├── 🔧 install.sh            # Linux 安装
│   │   │   └── 🔧 install.bat           # Windows 安装
│   │   ├── 🧪 tests/                    # 测试文件
│   │   │   ├── 📄 report.xml            # 测试报告
│   │   │   └── 🧪 tests/                # 测试套件
│   │   └── 📚 docs/                     # 文档目录
│   │       ├── 📄 INDEX.md              # 文档索引
│   │       ├── 📄 LICENSE               # 许可证
│   │       ├── 📄 PROJECT_SUMMARY.md    # 项目总结
│   │       ├── 📄 README.md             # 详细说明
│   │       └── 🌐 api/                  # API 文档
│   │
│   ├── 🎨 ecosystem/                    # 生态系统工具
│   │   ├── 📄 README.md                 # 生态系统说明
│   │   └── 🔧 scripts/
│   │       └── 📄 retropie_ecosystem_auto.sh # 生态自动化
│   │
│   └── 🎪 immersive/                    # 沉浸式硬件
│       ├── 📄 README.md                 # 沉浸式硬件说明
│       └── 🔧 scripts/
│           └── 📄 immersive_hardware_auto.sh # 硬件自动化
│
├── 📚 docs/                             # 项目文档
│   ├── 📄 LICENSE                       # 项目许可证
│   ├── 📄 DIR_TREE.md                   # 目录树文档
│   ├── 📄 README_HDMI.md                # HDMI 配置说明
│   └── 📄 NESTICLE_INTEGRATION_SUMMARY.md # Nesticle 集成总结
│
├── 📥 downloads/                        # 下载文件存储
│   ├── 🎮 roms/                         # ROM 文件
│   ├── 🎯 nesticle/                     # Nesticle 相关文件
│   └── 💿 retropie-buster-4.8-rpi4_400.img # RetroPie 镜像
│
└── 📊 logs/                             # 运行日志
    ├── 📄 gameplayer_*.log              # 主程序日志
    ├── 📄 hdmi_config.log               # HDMI 配置日志
    ├── 📄 retropie_installer.log        # RetroPie 安装日志
    ├── 📄 rom_downloader.log            # ROM 下载日志
    ├── 📄 nesticle_installer.log        # Nesticle 安装日志
    ├── 📄 virtuanes_installer.log       # VirtuaNES 安装日志
    ├── 📄 pylint_report.log             # 代码质量报告
    ├── 📁 log_reports/                  # 日志报告
    └── 📁 logs/                         # 历史日志
```

## 📋 核心模块说明

### 🎯 core/ - 核心功能模块
- **base_installer.py**: 所有安装器的抽象基类，提供统一接口
- **hdmi_config.py**: 树莓派 HDMI 显示优化，支持 1080p@60Hz 配置
- **nesticle_installer.py**: Nesticle 95 模拟器安装器，支持金手指和自动保存
- **virtuanes_installer.py**: VirtuaNES 0.97 模拟器安装器，高兼容性
- **retropie_installer.py**: RetroPie 系统安装器，支持跨平台
- **rom_downloader.py**: ROM 下载管理工具，支持断点续传

### 🧪 tests/ - 测试套件
- **44/44 测试全部通过**，覆盖率 100%
- 包含单元测试、集成测试和功能测试
- 支持测试环境和生产环境分离

### 🤖 scripts/ - 自动化脚本
- **批量部署**: 支持无人值守批量 SD 卡烧录
- **Docker 集成**: 完整的容器化部署方案
- **自动化集成**: 一键安装和配置各种模拟器
- **存档同步**: 本地和云端存档自动同步

### 🏗️ systems/ - 子系统架构
- **模块化设计**: 每个子系统独立开发和测试
- **标准化接口**: 统一的配置和部署方式
- **文档完整**: 每个子系统都有详细文档和 API 说明

## 🔧 技术特性

### 🏗️ 架构优势
- **抽象基类设计**: 确保所有安装器接口一致
- **模块化架构**: 支持独立开发、测试和部署
- **配置驱动**: 通过 JSON 配置文件灵活控制
- **跨平台支持**: Windows、Linux、macOS、Raspberry Pi

### 🧪 质量保证
- **100% 测试覆盖**: 44/44 测试全部通过
- **代码质量检查**: Pylint 静态分析
- **持续集成**: 自动化测试和部署
- **错误恢复**: 自动重试和回滚机制

### 🚀 生产特性
- **批量部署**: 适合大规模生产环境
- **自动化流程**: 最小化人工干预
- **配置备份**: 自动备份重要配置
- **安全性**: 权限检查和安全操作
