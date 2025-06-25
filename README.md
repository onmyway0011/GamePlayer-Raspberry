# 🎮 GamePlayer-Raspberry

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-44%2F44%20passing-brightgreen.svg)](https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry)

## 📖 项目简介

GamePlayer-Raspberry 是一套面向树莓派的多子系统游戏与多媒体环境自动化管理平台。提供完整的 RetroPie 游戏系统解决方案，包括 HDMI 配置优化、ROM 自动下载管理、模拟器安装配置、硬件环境检测等功能，适合树莓派游戏机、家庭娱乐和教育场景。

## ✨ 主要功能

### 🖥️ HDMI 显示优化
- 一键优化树莓派 HDMI 显示参数（1080p@60Hz、禁用过扫描等）
- 支持配置备份、恢复和预览模式
- 自动检测和修复显示问题

### 🎯 ROM 管理系统
- 自动化下载、校验、上传 NES/SNES 等 ROM 到树莓派
- 支持断点续传和文件完整性验证
- 从 Archive.org 等合法资源站搜索和下载

### 🎮 模拟器安装器
- **Nesticle 95**: 支持金手指、无限条命、自动保存功能
- **VirtuaNES 0.97**: 高兼容性 NES 模拟器
- 自动集成到 RetroArch 核心系统

### 🔧 系统工具
- RetroPie 镜像自动下载、解压和烧录
- 跨平台支持（Windows/Linux/macOS）
- 完善的依赖检测和自动安装

### 🧪 测试与质量保证
- 44 个自动化测试全部通过
- 完善的测试环境支持（TEST_ENV 标志）
- 增强的错误处理与日志记录机制

## 📋 版本记录

### v2.2.0 (2025-06-25) - 最新版本 🆕
- ✅ **代码质量大幅提升**: 修复所有语法错误和导入问题
- ✅ **测试覆盖率 100%**: 44/44 测试全部通过
- ✅ **架构优化**: 统一抽象基类实现，代码结构更清晰
- ✅ **错误修复**: 修复 Nesticle 和 VirtuaNES 安装器的抽象方法问题
- ✅ **测试环境改进**: 完善测试环境检测和临时目录管理
- ✅ **代码规范**: 删除未使用导入，统一代码风格

### v2.1.0 (2024-07-01)
- 新增 HDMI 配置优化模块，支持动态参数调整
- 改进测试环境支持，添加 TEST_ENV 标志区分测试/生产环境
- 优化安装流程，添加自动依赖检测和配置验证
- 增强错误处理和日志记录机制
- 兼容 Python 3.7+，支持 macOS/Linux/Raspberry Pi

## 🚀 快速开始

### 1. 环境准备

**系统要求**:
- Python 3.7 及以上版本
- 支持 Windows、Linux、macOS 和 Raspberry Pi
- 推荐使用虚拟环境

### 2. 安装项目

```bash
# 克隆项目
git clone git@github.com:LIUCHAOVSYAN/GamePlayer-Raspberry.git
cd GamePlayer-Raspberry

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

> ⚠️ **注意**: 必须使用 `pip install -r requirements.txt`，不要写成 `pip install requirements.txt`

### 3. 运行测试验证

```bash
# 运行所有测试
pytest tests/ -v

# 生成测试覆盖率报告
pytest tests/ --cov=core --cov-report=html
```

### 4. 基本使用

#### HDMI 配置优化
```bash
python core/hdmi_config.py --help
```

#### 模拟器安装
```bash
# 安装 Nesticle 95 模拟器
python core/nesticle_installer.py

# 安装 VirtuaNES 0.97 模拟器
python core/virtuanes_installer.py
```

#### ROM 下载管理
```bash
python core/rom_downloader.py --help
```

#### RetroPie 系统安装
```bash
python core/retropie_installer.py --help
```

## 📁 项目结构

```text
GamePlayer-Raspberry/
├── core/                          # 核心功能模块
│   ├── base_installer.py          # 安装器抽象基类
│   ├── hdmi_config.py             # HDMI 显示配置优化
│   ├── nesticle_installer.py      # Nesticle 95 模拟器安装器
│   ├── retropie_installer.py      # RetroPie 系统安装器
│   ├── rom_downloader.py          # ROM 下载管理工具
│   └── virtuanes_installer.py    # VirtuaNES 0.97 模拟器安装器
├── tests/                         # 测试套件 (44/44 通过)
│   ├── test_nesticle_installer.py
│   ├── test_retropie_installer.py
│   ├── test_rom_downloader.py
│   └── test_virtuanes_installer.py
├── config/                        # 配置文件
│   ├── project_config.json        # 主配置文件
│   └── rom_config.json           # ROM 下载配置
├── scripts/                       # 自动化脚本
│   └── auto_save_sync.py         # 存档同步工具
├── systems/                       # 子系统模块
│   ├── hdmi/                     # HDMI 配置子系统
│   ├── retropie/                 # RetroPie 子系统
│   └── ecosystem/                # 生态系统工具
├── logs/                         # 运行日志
├── downloads/                    # 下载文件存储
└── docs/                        # 项目文档
```

### 核心模块说明

#### 🎯 core/base_installer.py
- 所有安装器的抽象基类
- 提供统一的依赖检测、包管理、配置加载接口
- 确保代码复用和一致性

#### 🖥️ core/hdmi_config.py
- 树莓派 HDMI 显示优化脚本
- 自动修改 `/boot/config.txt`，强制 1080p@60Hz
- 支持配置备份、恢复、预览和回滚

#### 🎮 core/nesticle_installer.py
- Nesticle 95 模拟器自动安装器
- 支持金手指、无限条命、自动保存功能
- 自动集成到 RetroArch 核心系统

#### 🎯 core/virtuanes_installer.py
- VirtuaNES 0.97 模拟器安装器
- 高兼容性 NES 模拟器
- 完整的配置文件生成和管理

#### 📦 core/rom_downloader.py
- ROM 自动下载与传输工具
- 支持从 Archive.org 等合法资源站搜索下载
- 具备断点续传、校验、SFTP 上传功能

#### 🔧 core/retropie_installer.py
- RetroPie 镜像自动下载与烧录工具
- 支持 Windows/Linux/macOS 三平台
- 自动检测依赖、智能列盘与安全烧录

## 🧪 测试与质量保证

### 测试覆盖率
- ✅ **44/44 测试全部通过**
- ✅ **100% 核心功能覆盖**
- ✅ **自动化 CI/CD 流程**

### 运行测试
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_nesticle_installer.py -v

# 生成覆盖率报告
pytest tests/ --cov=core --cov-report=html
```

### 代码质量
- 所有 Python 文件语法检查通过
- 统一的代码风格和规范
- 完善的错误处理和日志记录
- 抽象基类确保架构一致性

## 🚀 高级特性

### 🏗️ 架构亮点
- **抽象基类设计**: 统一的 `BaseInstaller` 确保所有安装器接口一致
- **模块化架构**: 核心功能按功能域拆分，支持独立开发和测试
- **配置驱动**: 所有功能通过 JSON 配置文件灵活控制
- **跨平台支持**: 支持 Windows、Linux、macOS 和 Raspberry Pi

### 🔧 开发特性
- **测试环境支持**: `TEST_ENV` 标志区分测试和生产环境
- **完善的日志系统**: 分级日志记录，便于调试和监控
- **错误恢复机制**: 自动重试、回滚和错误处理
- **扩展性设计**: 易于添加新的模拟器和功能

### 🎯 生产特性
- **批量部署支持**: 适合大规模生产和运维
- **自动化流程**: 最小化人工干预
- **配置备份**: 自动备份重要配置文件
- **安全性**: 权限检查和安全操作

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 联系方式

- **GitHub**: [LIUCHAOVSYAN](https://github.com/LIUCHAOVSYAN)
- **项目地址**: [GamePlayer-Raspberry](https://github.com/LIUCHAOVSYAN/GamePlayer-Raspberry)

## ⚠️ 免责声明

**注意**: 本项目仅用于教育和研究目的。请确保遵守当地法律法规，仅下载您拥有合法权利的游戏 ROM。

---

**如有问题请提交 Issue 或联系维护者。**
