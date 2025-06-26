# HDMI 子系统

## 系统简介
本模块负责树莓派HDMI显示相关的自动化配置、分辨率/刷新率优化、EDID管理、HDMI热插拔检测、日志采集与分析等。

## 目录结构
```
core/         # HDMI配置与控制核心代码
config/       # 配置文件
logs/         # 日志与分析报告
scripts/      # 自动化脚本
tests/        # 自动化测试
docs/         # 文档与API说明
```

## 核心功能
- HDMI参数自动检测与优化（hdmi_config.py）
- EDID读取与管理
- HDMI热插拔事件监控
- 日志采集与分析
- 自动化测试

## 主要代码片段
```python
# HDMI配置与检测
from .core.hdmi_config import detect_hdmi, optimize_resolution
info = detect_hdmi()
optimize_resolution(info)
```

## 修改记录
- 2024-06-25: 结构重构，统一日志、测试、脚本、配置目录
- 2024-06-24: 增加HDMI热插拔检测与日志分析
- 2024-06-23: 支持EDID读取与分辨率优化

## 核心代码展示
```python
# core/hdmi_config.py
from logger_config import get_logger
logger = get_logger("hdmi_config", "hdmi_config.log")
# ... 主要功能见core/hdmi_config.py
``` 