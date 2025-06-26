# 新项目结构

## 目录说明

### 📁 src/ - 源代码
- `core/` - 核心模块 (NES模拟器、存档管理、金手指等)
- `scripts/` - 脚本工具 (安装器、ROM管理等)
- `web/` - Web相关文件
- `systems/` - 系统集成模块

### ⚙️ config/ - 配置文件
- `docker/` - Docker相关配置
- `system/` - 系统配置文件

### 📖 docs/ - 文档
- `guides/` - 使用指南
- `api/` - API文档  
- `reports/` - 分析报告

### 🧪 tests/ - 测试
- `unit/` - 单元测试
- `integration/` - 集成测试
- `fixtures/` - 测试数据

### 🏗️ build/ - 构建
- `docker/` - Docker构建文件
- `scripts/` - 构建脚本
- `output/` - 构建输出

### 💾 data/ - 数据
- `roms/` - 游戏ROM文件
- `saves/` - 游戏存档
- `cheats/` - 金手指配置
- `logs/` - 日志文件

### 🛠️ tools/ - 工具
- `dev/` - 开发工具
- `deploy/` - 部署工具

### 🎨 assets/ - 资源
- `images/` - 图片资源
- `fonts/` - 字体文件
- `sounds/` - 音频文件

## 主要改进

1. **清晰的分层结构** - 按功能分类组织文件
2. **标准化命名** - 使用业界标准的目录名称
3. **逻辑分离** - 源码、配置、文档、测试分离
4. **易于维护** - 结构清晰，便于查找和维护

## 迁移说明

- 原有文件已按新结构重新组织
- 备份文件保存在 `backup_old_structure/` 目录
- 导入路径可能需要手动调整
