# 树莓派HDMI配置优化工具

这是一个Python脚本，用于自动修改树莓派的`/boot/config.txt`配置文件，实现HDMI输出优化。

## 功能特性

- ✅ **强制HDMI输出**: 设置为1080p@60Hz
- ✅ **禁用过扫描**: 实现全屏显示
- ✅ **增加GPU显存**: 设置为256MB
- ✅ **自动备份**: 修改前自动备份原始配置
- ✅ **配置验证**: 验证配置项是否正确应用
- ✅ **安全恢复**: 支持恢复原始配置
- ✅ **模拟运行**: 支持预览将要应用的更改

## 配置项说明

### HDMI输出配置
- `hdmi_group=1`: HDMI组1（CEA标准）
- `hdmi_mode=16`: 1080p@60Hz分辨率
- `hdmi_force_hotplug=1`: 强制HDMI热插拔检测
- `hdmi_drive=2`: HDMI驱动强度

### 显示优化
- `disable_overscan=1`: 禁用过扫描，实现全屏显示

### 性能优化
- `gpu_mem=256`: GPU显存设置为256MB

### 其他优化
- `hdmi_ignore_cec_init=1`: 忽略CEC初始化
- `hdmi_ignore_cec=1`: 忽略CEC功能
- `config_hdmi_boost=4`: HDMI信号增强

## 使用方法

### 1. 查看当前配置
```bash
python hdmi_config.py --show
```

### 2. 模拟运行（预览更改）
```bash
python hdmi_config.py --dry-run
```

### 3. 应用配置（需要sudo权限）
```bash
sudo python hdmi_config.py
```

### 4. 恢复原始配置
```bash
sudo python hdmi_config.py --restore
```

### 5. 指定配置文件路径
```bash
sudo python hdmi_config.py --config /path/to/config.txt
```

## 使用流程

1. **查看当前配置**: 了解现有的HDMI设置
2. **模拟运行**: 预览将要应用的更改
3. **确认应用**: 输入'y'确认应用配置
4. **重启系统**: 重启树莓派以应用新配置

## 安全特性

### 自动备份
- 修改前自动备份原始配置文件到`/boot/config.txt.backup`
- 备份文件包含时间戳，避免覆盖

### 权限检查
- 检查文件读写权限
- 提示使用sudo运行

### 配置验证
- 验证关键配置项是否正确应用
- 显示配置验证结果

## 故障排除

### 常见问题

1. **权限错误**
   ```bash
   # 确保使用sudo运行
   sudo python hdmi_config.py
   ```

2. **配置文件不存在**
   ```bash
   # 检查配置文件路径
   ls -la /boot/config.txt
   ```

3. **HDMI无输出**
   ```bash
   # 恢复原始配置
   sudo python hdmi_config.py --restore
   ```

4. **配置未生效**
   ```bash
   # 重启树莓派
   sudo reboot
   ```

### 手动恢复
如果脚本无法运行，可以手动恢复：
```bash
sudo cp /boot/config.txt.backup /boot/config.txt
sudo reboot
```

## 技术细节

### HDMI模式说明
- `hdmi_group=1`: CEA标准（电视）
- `hdmi_mode=16`: 1920x1080@60Hz

### GPU显存说明
- 默认显存通常为64MB或128MB
- 增加到256MB可提升图形性能
- 显存从系统内存中分配

### 过扫描说明
- 过扫描是电视显示技术，会在图像周围添加黑边
- 禁用过扫描可实现像素完美显示

## 兼容性

- **操作系统**: Raspberry Pi OS (基于Debian)
- **Python版本**: 3.7+
- **树莓派型号**: 所有支持HDMI的型号

## 日志文件

脚本会生成详细的日志文件`hdmi_config.log`，包含：
- 配置读取和写入操作
- 备份和恢复操作
- 错误和警告信息

## 开发信息

- **作者**: AI Assistant
- **许可证**: MIT
- **版本**: 1.0.0

## 更新日志

### v1.0.0
- 初始版本发布
- 支持HDMI输出优化
- 支持配置备份和恢复
- 支持模拟运行模式
- 完整的配置验证功能

# 检查本次优化是否有变更
if grep -q "已批量抓取" "$LOGFILE" || grep -q "已切换到主题" "$LOGFILE" || grep -q "已映射到云端" "$LOGFILE"; then
    # 有变更才推送
    # ...（推送代码见上）
fi

OPTIMIZED=0
while [ $OPTIMIZED -eq 0 ]; do
    OPTIMIZED=1

    # 检查封面
    for SYS in "${PLATFORMS[@]}"; do
        if [ ! -d "$ROM_ROOT/$SYS/media" ] || [ ! -f "$ROM_ROOT/$SYS/gamelist.xml" ]; then
            # 自动生成profile并抓取
            # ...（如上）
            OPTIMIZED=0
        fi
    done

    # 检查主题
    if ! grep -q 'RetroPie-Material' "$THEME_CFG"; then
        # 自动切换
        # ...（如上）
        OPTIMIZED=0
    fi

    # 检查Netplay
    for SYS in "${PLATFORMS[@]}"; do
        CFG="/opt/retropie/configs/$SYS/retroarch.cfg"
        if [ -f "$CFG" ] && ! grep -q 'netplay_ip_port = "55435"' "$CFG"; then
            # 自动配置
            # ...（如上）
            OPTIMIZED=0
        fi
    done

    # 检查云存档
    for SYS in "${PLATFORMS[@]}"; do
        SAVES="$ROM_ROOT/$SYS/saves"
        if [ ! -L "$SAVES" ]; then
            # 自动软链
            # ...（如上）
            OPTIMIZED=0
        fi
    done

    if [ $OPTIMIZED -eq 1 ]; then
        log "所有优化项已完成，无需进一步优化。"
    else
        log "检测到未完成优化项，继续自动优化..."
    fi
done 