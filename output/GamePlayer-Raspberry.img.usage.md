

## 使用方法

### 1. 烧录到SD卡
**推荐使用 Raspberry Pi Imager:**
1. 下载并安装 Raspberry Pi Imager: https://rpi.org/imager
2. 选择 "Use custom image"
3. 选择镜像文件: `GamePlayer-Raspberry.img.gz`
4. 选择8GB+的SD卡
5. 点击 "Write" 开始烧录

**命令行方式 (Linux/macOS):**
```bash
# 解压镜像
gunzip GamePlayer-Raspberry.img.gz

# 查找SD卡设备
diskutil list  # macOS
lsblk          # Linux

# 烧录镜像 (注意替换/dev/sdX为实际设备)
sudo dd if=GamePlayer-Raspberry.img of=/dev/sdX bs=4M
sync
```

### 2. 启动树莓派
1. 将SD卡插入树莓派
2. 连接HDMI显示器
3. 连接网络 (有线或WiFi)
4. 接通电源启动

### 3. 访问游戏
- **Web界面**: http://树莓派IP:8080
- **SSH连接**: ssh pi@树莓派IP
- **默认密码**: raspberry

### 4. 游戏控制
- **移动**: 方向键 或 WASD
- **A按钮**: 空格 或 Z
- **B按钮**: Shift 或 X
- **开始**: Enter
- **选择**: Tab
- **退出游戏**: ESC

## 技术规格
- **兼容硬件**: Raspberry Pi 3B+, 4, 400
- **最小SD卡**: 8GB
- **推荐SD卡**: 16GB+ (Class 10)
- **网络**: 有线以太网或WiFi
- **显示**: HDMI输出

## 故障排除
- **无法启动**: 检查SD卡烧录是否完整
- **无法连接**: 检查网络配置
- **游戏无响应**: 按ESC返回主菜单
- **性能问题**: 确保使用高速SD卡

---
生成时间: 2025-07-09T10:59:10.683425
自动生成器版本: v1.0
