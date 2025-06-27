#!/usr/bin/env python3
"""
简单的NES测试API
"""

import subprocess
import json
from pathlib import Path

def test_nes_emulator():
    """测试NES模拟器"""
    try:
        # 检查mednafen
        result = subprocess.run(["which", "mednafen"], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            mednafen_path = result.stdout.strip()
            print(f"✅ mednafen路径: {mednafen_path}")
            
            # 检查NES支持
            help_result = subprocess.run(["mednafen", "-help"], capture_output=True, text=True, timeout=10)
            
            if "nes" in help_result.stdout.lower():
                print("✅ mednafen支持NES")
                return {"success": True, "emulator": "mednafen", "path": mednafen_path}
            else:
                print("❌ mednafen不支持NES")
                return {"success": False, "error": "mednafen不支持NES"}
        else:
            print("❌ mednafen未找到")
            return {"success": False, "error": "mednafen未安装"}
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return {"success": False, "error": str(e)}

def launch_nes_game(rom_file="Super_Mario_Bros.nes"):
    """启动NES游戏"""
    try:
        rom_path = Path("data/roms/nes") / rom_file
        
        if not rom_path.exists():
            return {"success": False, "error": f"ROM文件不存在: {rom_path}"}
        
        # 启动mednafen
        cmd = [
            "mednafen",
            "-force_module", "nes",
            "-video.fs", "0",  # 窗口模式
            str(rom_path)
        ]
        
        print(f"🎮 启动命令: {' '.join(cmd)}")
        
        # 后台启动
        process = subprocess.Popen(cmd)
        
        return {
            "success": True, 
            "message": "游戏启动成功",
            "pid": process.pid,
            "command": cmd
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "launch":
        result = launch_nes_game()
    else:
        result = test_nes_emulator()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
