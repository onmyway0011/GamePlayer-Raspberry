# RetroPie 系统代码索引

## 目录结构
- core/  
- roms/  
- config/  
- logs/  
- tests/  
- scripts/  
- docs/  

## 主要模块

### core/retropie_installer.py
- `RetroPieInstaller`：镜像下载、依赖检测、烧录、磁盘管理等主流程类
- `main()`：命令行入口

### core/logger_config.py
- `get_logger(name, log_file)`：统一日志获取与配置

### core/log_uploader.py
- `upload_log_to_s3(...)`：日志上传S3

### core/log_analyzer.py
- `analyze_logs()`：日志分析
- `plot_trend()`：趋势可视化
- `generate_report()`：生成分析报告
- `send_alert()`：告警推送
- `start_web_dashboard()`：Web可视化接口
- `export_to_json()`：ELK/Graylog导出
- `schedule_auto_analyze()`：定时分析

### roms/rom_downloader.py
- `ROMDownloader`：ROM下载、校验、上传主流程类

## 主要测试
- tests/test_installer.py：安装器功能测试
- tests/test_rom_downloader.py：ROM下载器测试
- tests/test_bash_scripts.py：Bash脚本语法测试
- tests/test_hdmi_config.py：HDMI配置测试

## 主要脚本
- scripts/install.sh / install.bat：一键安装脚本
- scripts/deploy.sh：自动部署脚本

## 主要文档
- docs/README.md：系统说明
- docs/PROJECT_SUMMARY.md：项目总结
- docs/LICENSE：许可证

## 主要API文档
- docs/api/core.html：核心代码API文档
- docs/api/roms.html：ROM管理API文档 