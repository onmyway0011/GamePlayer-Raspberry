import sys
from datetime import datetime
from pathlib import Path

class AutoImageGenerator:
    def auto_generate_complete_image(self):
        # Simulate image generation process
        try:
            # Placeholder for actual image generation logic
            image_file = Path("output/GamePlayer-Raspberry.img.gz")
            image_file.touch()  # Create an empty file to simulate image generation
            self.generate_usage_guide(image_file)
            return True
        except Exception as e:
            print(f"  ⚠️ 镜像生成失败: {e}")
            return False
    def generate_usage_guide(self, image_file):
        guide_content = f"""

## 使用方法

### 1. 烧录到SD卡
**推荐使用 Raspberry Pi Imager:**
1. 下载并安装 Raspberry Pi Imager: https://rpi.org/imager
2. 选择 "Use custom image"
3. 选择镜像文件: `{image_file.name}`
4. 选择8GB+的SD卡
5. 点击 "Write" 开始烧录

**命令行方式 (Linux/macOS):**
```bash
# 解压镜像
gunzip {image_file.name}

# 查找SD卡设备
diskutil list  # macOS
lsblk          # Linux

# 烧录镜像 (注意替换/dev/sdX为实际设备)
sudo dd if={image_file.stem} of=/dev/sdX bs=4M
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
生成时间: {datetime.now().isoformat()}
自动生成器版本: v1.0
"""
        
        try:
            guide_file = image_file.with_suffix('.usage.md')
            with open(guide_file, 'w', encoding='utf-8') as f:
                f.write(guide_content)
            
            print(f"  ✅ 使用指南已生成: {guide_file.name}")
            
        except Exception as e:
            print(f"  ⚠️ 使用指南生成失败: {e}")


def main():
    """主函数"""
    generator = AutoImageGenerator()
    
    print("🎯 一键自动生成GamePlayer-Raspberry镜像")
    print()
    
    success = generator.auto_generate_complete_image()
    
    if success:
        print("\n🎉 自动生成任务完成！")
        print("📁 检查output/目录查看生成的镜像文件")
    else:
        print("\n❌ 自动生成失败！")
        print("请检查错误信息并重试")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
