#!/usr/bin/env python3
"""
多平台ROM自动启动器
支持NES/SNES/GB/GBA/MD等平台，自动检测并选择最优模拟器
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List

# 支持的游戏平台与模拟器
PLATFORM_EMULATORS = {
    'nes': [
        {'name': 'Nestopia', 'cmd': ['nestopia'], 'priority': 1},
        {'name': 'FCEUX', 'cmd': ['fceux'], 'priority': 2},
        {'name': 'Mesen', 'cmd': ['mesen'], 'priority': 3},
        {'name': 'VirtuaNES', 'cmd': ['virtuanes'], 'priority': 4},
        {'name': 'Mednafen', 'cmd': ['mednafen', '-nes.input.port1', 'gamepad'], 'priority': 5},
        {'name': 'RetroArch-Nestopia', 'cmd': ['retroarch', '-L', '/usr/lib/libretro/nestopia_libretro.so'], 'priority': 6},
    ],
    'snes': [
        {'name': 'Snes9x', 'cmd': ['snes9x'], 'priority': 1},
        {'name': 'bsnes', 'cmd': ['bsnes'], 'priority': 2},
        {'name': 'RetroArch-Snes9x', 'cmd': ['retroarch', '-L', '/usr/lib/libretro/snes9x_libretro.so'], 'priority': 3},
    ],
    'gb': [
        {'name': 'Gambatte', 'cmd': ['gambatte'], 'priority': 1},
        {'name': 'RetroArch-Gambatte', 'cmd': ['retroarch', '-L', '/usr/lib/libretro/gambatte_libretro.so'], 'priority': 2},
    ],
    'gba': [
        {'name': 'mGBA', 'cmd': ['mgba'], 'priority': 1},
        {'name': 'VisualBoyAdvance', 'cmd': ['visualboyadvance'], 'priority': 2},
        {'name': 'RetroArch-mGBA', 'cmd': ['retroarch', '-L', '/usr/lib/libretro/mgba_libretro.so'], 'priority': 3},
    ],
    'md': [
        {'name': 'Genesis-Plus-GX', 'cmd': ['genesis-plus-gx'], 'priority': 1},
        {'name': 'RetroArch-GenPlus', 'cmd': ['retroarch', '-L', '/usr/lib/libretro/genesis_plus_gx_libretro.so'], 'priority': 2},
    ]
}

# ROM后缀与平台映射


def detect_platform(rom_path: str) -> Optional[str]:
    """TODO: 添加文档字符串"""
    ext = Path(rom_path).suffix.lower()
    if ext in ['.nes']:
        return 'nes'
    if ext in ['.smc', '.sfc']:
        return 'snes'
    if ext in ['.gb']:
        return 'gb'
    if ext in ['.gba']:
        return 'gba'
    if ext in ['.md', '.gen', '.bin']:
        return 'md'
    return None


def get_available_emulators(platform: str) -> List[dict]:
    """TODO: 添加文档字符串"""
    emulators = PLATFORM_EMULATORS.get(platform, [])
    available = []
    for emu in emulators:
        exe = shutil.which(emu['cmd'][0])
        if exe:
            emu_copy = emu.copy()
            emu_copy['cmd'][0] = exe
            available.append(emu_copy)
    available.sort(key=lambda x: x['priority'])
    return available


def run_game(rom_path: str):
    """TODO: 添加文档字符串"""
    platform = detect_platform(rom_path)
    if not platform:
        print(f'❌ 无法识别ROM平台: {rom_path}')
        return False
    emulators = get_available_emulators(platform)
    if not emulators:
        print(f'❌ 未检测到可用的{platform.upper()}模拟器')
        return False
    for emu in emulators:
        print(f'🎮 尝试使用 {emu["name"]} 启动...')
        try:
            cmd = emu['cmd'] + [rom_path]
            proc = subprocess.Popen(cmd)
            proc.wait()
            if proc.returncode == 0:
                print(f'✅ 成功运行 {rom_path} 于 {emu["name"]}')
                return True
            else:
                print(f'⚠️ {emu["name"]} 运行失败，尝试下一个...')
        except Exception as e:
            print(f'❌ 启动 {emu["name"]} 异常: {e}')
    print('❌ 所有模拟器均无法运行该ROM')
    return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python3 universal_game_launcher.py <rom_path>')
        print('支持平台: NES(.nes), SNES(.smc/.sfc), GB(.gb), GBA(.gba), MD(.md/.gen/.bin)')
        sys.exit(1)

    rom_path = sys.argv[1]
    if rom_path in ['--help', '-h']:
        print('多平台ROM自动启动器')
        print('用法: python3 universal_game_launcher.py <rom_path>')
        print('支持平台: NES(.nes), SNES(.smc/.sfc), GB(.gb), GBA(.gba), MD(.md/.gen/.bin)')
        sys.exit(0)

    run_game(rom_path)
