# Immersive 子系统

## 系统简介
本模块负责沉浸式硬件（如灯光、音效、外设等）的自动化控制、联动、配置与日志采集，支持与主系统事件联动。

## 目录结构
```
core/         # 沉浸式硬件控制核心代码
scripts/      # 自动化脚本
docs/         # 文档与API说明
logs/         # 日志与分析报告
tests/        # 自动化测试
```

## 核心功能
- 沉浸式灯光、音效、外设自动控制
- 与主系统事件联动
- 日志采集与分析
- 自动化测试

## 主要代码片段
```bash
# 一键自动化脚本
bash scripts/immersive_hardware_auto.sh
```

## 修改记录
- 2024-06-25: 结构重构，统一日志、测试、脚本、配置目录
- 2024-06-24: 增加沉浸式硬件自动化脚本

## 核心代码展示
```bash
# scripts/immersive_hardware_auto.sh
bash scripts/immersive_hardware_auto.sh
# ... 主要功能见scripts/immersive_hardware_auto.sh
``` 