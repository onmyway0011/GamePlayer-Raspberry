#!/usr/bin/env python3
"""
简化的ROM下载器 - 创建示例ROM文件
"""
import os
import json
from pathlib import Path

def create_sample_roms():
    """创建示例ROM文件"""
    base_dir = Path("data/roms")
    systems = {
        "nes": [".nes"],
        "snes": [".smc"],
        "gameboy": [".gb"],
        "gba": [".gba"],
        "genesis": [".md"]
    }
    
    # 创建目录
    for system in systems:
        (base_dir / system).mkdir(parents=True, exist_ok=True)
    
    # 示例游戏名称
    games = [
        "Adventure Quest", "Space Fighter", "Puzzle Master", "Racing Pro",
        "Ninja Warrior", "Magic Kingdom", "Robot Battle", "Super Platform",
        "Card Master", "Sports Champion", "Mystery Castle", "Ocean Explorer",
        "Sky Racer", "Dragon Legend", "Pixel Fighter", "Time Traveler"
    ]
    
    # 生成最小有效ROM
    def create_nes_rom(name):
        header = bytearray(16)
        header[0:4] = b'NES\x1a'
        header[4] = 1  # 16KB PRG
        header[5] = 1  # 8KB CHR
        prg = bytearray(16384)
        chr = bytearray(8192)
        # 设置重置向量
        prg[0x3FFC] = 0x00
        prg[0x3FFD] = 0x80
        return bytes(header + prg + chr)
    
    total_created = 0
    for system, exts in systems.items():
        for i, game in enumerate(games):
            if i >= 10:  # 每个系统10个游戏
                break
            filename = f"{game.lower().replace(' ', '_')}{exts[0]}"
            filepath = base_dir / system / filename
            
            if not filepath.exists():
                # 为所有系统创建NES格式的ROM（简化）
                rom_data = create_nes_rom(game)
                with open(filepath, 'wb') as f:
                    f.write(rom_data)
                total_created += 1
                print(f"✅ 创建: {filepath}")
    
    print(f"\n🎮 创建了 {total_created} 个示例ROM文件")
    
    # 生成ROM目录
    catalog = {"systems": {}}
    for system in systems:
        roms = []
        for rom_file in (base_dir / system).glob("*"):
            roms.append({
                "name": rom_file.stem.replace("_", " ").title(),
                "filename": rom_file.name,
                "size": rom_file.stat().st_size
            })
        catalog["systems"][system] = {"count": len(roms), "roms": roms}
    
    with open(base_dir / "catalog.json", 'w') as f:
        json.dump(catalog, f, indent=2)

if __name__ == "__main__":
    create_sample_roms()
