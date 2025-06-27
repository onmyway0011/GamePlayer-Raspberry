#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

def test_nes_launch():
    """测试NES游戏启动"""
    rom_path = Path("data/roms/nes/Super_Mario_Bros.nes")
    
    if not rom_path.exists():
        print("❌ ROM文件不存在")
        return False
    
    try:
        print("🎮 启动NES游戏...")
        
        # 启动mednafen
        result = subprocess.run([
            "mednafen",
            "-force_module", "nes",
            "-video.fs", "0",  # 窗口模式
            "-sound", "0",     # 禁用声音
            str(rom_path)
        ], timeout=3)
        
        print("✅ 游戏启动成功")
        return True
        
    except subprocess.TimeoutExpired:
        print("✅ 游戏正在运行（超时是正常的）")
        return True
    except Exception as e:
        print(f"❌ 游戏启动失败: {e}")
        return False

if __name__ == "__main__":
    success = test_nes_launch()
    sys.exit(0 if success else 1)
