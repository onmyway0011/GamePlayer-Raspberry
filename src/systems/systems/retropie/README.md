# RetroPie 子系统

## 系统简介
本模块负责Raspberry Pi下RetroPie的自动化安装、ROM管理、日志采集与分析、云同步等核心功能，支持一键部署、批量ROM下载、日志可视化与告警。

## 目录结构
```
core/         # 主要业务逻辑（安装器、日志、ROM下载等）
config/       # 配置文件（如log_upload_config.json、requirements.txt等）
logs/         # 日志与分析报告
roms/         # ROM下载与管理
scripts/      # 安装、部署等Shell脚本
tests/        # 自动化测试
```

## 核心功能
- 一键安装与环境配置（retropie_installer.py）
- ROM自动下载与管理（rom_downloader.py）
- 日志采集、分析、可视化与云同步（logger_config.py, log_analyzer.py, log_uploader.py）
- 自动化测试与报告生成

## 主要代码片段
```python
# 日志分析与可视化
from .core.log_analyzer import analyze_logs, plot_trend, generate_report
stats, errors, warnings, all_times, keyword_hits, anomaly_hits = analyze_logs()
trend_img = plot_trend(all_times)
report_path = generate_report(stats, errors, warnings, trend_img, keyword_hits, anomaly_hits)
```

## 修改记录
- 2024-06-25: 结构重构，统一日志、测试、脚本、配置目录
- 2024-06-24: 集成API文档自动发布与推送脚本
- 2024-06-23: 增加日志云同步与可视化分析
- 2024-06-22: 支持ROM批量下载与管理 