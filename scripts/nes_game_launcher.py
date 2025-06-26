#!/usr/bin/env python3
"""
NES游戏启动器
提供图形界面选择和启动NES游戏
"""

import os
import sys
import json
import subprocess
import pygame
import threading
import time
from pathlib import Path
from typing import List, Dict, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class NESGameLauncher:
    """NES游戏启动器"""
    
    def __init__(self, roms_dir: str = "/home/pi/RetroPie/roms/nes"):
        self.roms_dir = Path(roms_dir)
        self.games = []
        self.selected_index = 0
        self.running = True
        
        # 初始化Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("NES Game Launcher - GamePlayer-Raspberry")
        
        # 颜色定义
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 100, 200)
        self.GREEN = (0, 200, 0)
        self.RED = (200, 0, 0)
        self.GRAY = (128, 128, 128)
        self.YELLOW = (255, 255, 0)
        
        # 字体
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # 加载游戏列表
        self.load_games()
    
    def load_games(self):
        """加载游戏列表"""
        print("🎮 加载游戏列表...")
        
        # 确保ROM目录存在
        if not self.roms_dir.exists():
            self.roms_dir.mkdir(parents=True, exist_ok=True)
        
        # 查找ROM文件
        rom_files = list(self.roms_dir.glob("*.nes"))
        
        if not rom_files:
            print("📥 没有找到ROM文件，开始下载...")
            self.download_roms()
            rom_files = list(self.roms_dir.glob("*.nes"))
        
        # 加载ROM目录信息
        catalog_file = self.roms_dir / "rom_catalog.json"
        catalog = {}
        
        if catalog_file.exists():
            try:
                with open(catalog_file, 'r', encoding='utf-8') as f:
                    catalog = json.load(f)
            except Exception as e:
                print(f"⚠️ 加载目录失败: {e}")
        
        # 构建游戏列表
        self.games = []
        for rom_file in sorted(rom_files):
            game_info = self.get_game_info(rom_file, catalog)
            self.games.append(game_info)
        
        print(f"✅ 加载了 {len(self.games)} 个游戏")
    
    def get_game_info(self, rom_file: Path, catalog: Dict) -> Dict:
        """获取游戏信息"""
        # 从目录中查找游戏信息
        for category_info in catalog.get("categories", {}).values():
            for rom_info in category_info.get("roms", {}).values():
                if rom_info.get("filename") == rom_file.name:
                    return {
                        "name": rom_info["name"],
                        "description": rom_info["description"],
                        "genre": rom_info["genre"],
                        "year": rom_info["year"],
                        "filename": rom_file.name,
                        "path": str(rom_file),
                        "size_kb": rom_file.stat().st_size // 1024
                    }
        
        # 如果目录中没有找到，使用文件名
        return {
            "name": rom_file.stem.replace("_", " ").title(),
            "description": f"NES游戏 - {rom_file.stem}",
            "genre": "未知",
            "year": "未知",
            "filename": rom_file.name,
            "path": str(rom_file),
            "size_kb": rom_file.stat().st_size // 1024
        }
    
    def download_roms(self):
        """下载ROM文件"""
        try:
            from rom_downloader import ROMDownloader
            downloader = ROMDownloader(str(self.roms_dir))
            downloader.download_all()
            downloader.create_rom_catalog()
        except Exception as e:
            print(f"❌ ROM下载失败: {e}")
            # 创建示例ROM
            self.create_sample_roms()
    
    def create_sample_roms(self):
        """创建示例ROM文件"""
        print("📝 创建示例ROM文件...")
        
        sample_games = [
            ("Demo Game 1", "演示游戏1"),
            ("Demo Game 2", "演示游戏2"),
            ("Test ROM", "测试ROM"),
            ("Sample Platformer", "示例平台游戏"),
            ("Mini Shooter", "迷你射击游戏")
        ]
        
        for filename, title in sample_games:
            rom_file = self.roms_dir / f"{filename.lower().replace(' ', '_')}.nes"
            
            if not rom_file.exists():
                # 创建最小的NES ROM文件
                header = bytearray(16)
                header[0:4] = b'NES\x1a'
                header[4] = 1  # PRG ROM 大小
                header[5] = 1  # CHR ROM 大小
                
                prg_rom = bytearray(16384)  # 16KB PRG ROM
                chr_rom = bytearray(8192)   # 8KB CHR ROM
                
                # 添加标题信息
                title_bytes = title.encode('ascii', errors='ignore')[:16]
                prg_rom[0:len(title_bytes)] = title_bytes
                
                rom_content = bytes(header + prg_rom + chr_rom)
                
                with open(rom_file, 'wb') as f:
                    f.write(rom_content)
                
                print(f"✅ 创建示例ROM: {filename}")
    
    def draw_header(self):
        """绘制标题"""
        title_text = self.font_large.render("NES Game Launcher", True, self.WHITE)
        subtitle_text = self.font_medium.render("GamePlayer-Raspberry", True, self.GRAY)
        
        title_rect = title_text.get_rect(center=(400, 40))
        subtitle_rect = subtitle_text.get_rect(center=(400, 70))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # 绘制分隔线
        pygame.draw.line(self.screen, self.GRAY, (50, 90), (750, 90), 2)
    
    def draw_game_list(self):
        """绘制游戏列表"""
        if not self.games:
            no_games_text = self.font_medium.render("没有找到游戏文件", True, self.RED)
            text_rect = no_games_text.get_rect(center=(400, 300))
            self.screen.blit(no_games_text, text_rect)
            return
        
        # 计算显示范围
        visible_games = 8
        start_index = max(0, self.selected_index - visible_games // 2)
        end_index = min(len(self.games), start_index + visible_games)
        
        y_offset = 120
        for i in range(start_index, end_index):
            game = self.games[i]
            
            # 选中状态
            if i == self.selected_index:
                pygame.draw.rect(self.screen, self.BLUE, (50, y_offset - 5, 700, 50))
                text_color = self.WHITE
            else:
                text_color = self.WHITE
            
            # 游戏名称
            name_text = self.font_medium.render(game["name"], True, text_color)
            self.screen.blit(name_text, (60, y_offset))
            
            # 游戏信息
            info_text = f"{game['genre']} | {game['year']} | {game['size_kb']}KB"
            info_surface = self.font_small.render(info_text, True, self.GRAY)
            self.screen.blit(info_surface, (60, y_offset + 25))
            
            y_offset += 60
    
    def draw_game_details(self):
        """绘制游戏详情"""
        if not self.games or self.selected_index >= len(self.games):
            return
        
        game = self.games[self.selected_index]
        
        # 详情框
        detail_rect = pygame.Rect(50, 450, 700, 120)
        pygame.draw.rect(self.screen, (30, 30, 30), detail_rect)
        pygame.draw.rect(self.screen, self.GRAY, detail_rect, 2)
        
        # 游戏名称
        name_text = self.font_medium.render(game["name"], True, self.YELLOW)
        self.screen.blit(name_text, (60, 460))
        
        # 游戏描述
        desc_text = game["description"]
        if len(desc_text) > 60:
            desc_text = desc_text[:60] + "..."
        
        desc_surface = self.font_small.render(desc_text, True, self.WHITE)
        self.screen.blit(desc_surface, (60, 485))
        
        # 文件信息
        file_info = f"文件: {game['filename']} ({game['size_kb']}KB)"
        file_surface = self.font_small.render(file_info, True, self.GRAY)
        self.screen.blit(file_surface, (60, 505))
    
    def draw_controls(self):
        """绘制控制说明"""
        controls = [
            "↑↓ 选择游戏",
            "ENTER 启动游戏",
            "R 刷新列表",
            "Q 退出"
        ]
        
        x_offset = 60
        for control in controls:
            control_surface = self.font_small.render(control, True, self.GRAY)
            self.screen.blit(control_surface, (x_offset, 580))
            x_offset += 150
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                
                elif event.key == pygame.K_DOWN:
                    self.selected_index = min(len(self.games) - 1, self.selected_index + 1)
                
                elif event.key == pygame.K_RETURN:
                    self.launch_game()
                
                elif event.key == pygame.K_r:
                    self.load_games()
                    self.selected_index = 0
                
                elif event.key == pygame.K_q:
                    self.running = False
    
    def launch_game(self):
        """启动游戏"""
        if not self.games or self.selected_index >= len(self.games):
            return
        
        game = self.games[self.selected_index]
        print(f"🎮 启动游戏: {game['name']}")
        
        # 显示启动信息
        self.screen.fill(self.BLACK)
        loading_text = self.font_large.render(f"启动游戏: {game['name']}", True, self.WHITE)
        loading_rect = loading_text.get_rect(center=(400, 300))
        self.screen.blit(loading_text, loading_rect)
        pygame.display.flip()
        
        try:
            # 尝试使用不同的模拟器启动游戏
            emulators = [
                ["python3", "core/nesticle_installer.py", "--run", game["path"]],
                ["python3", "core/virtuanes_installer.py", "--run", game["path"]],
                ["python3", "scripts/simple_nes_player.py", game["path"]]
            ]
            
            for emulator_cmd in emulators:
                try:
                    subprocess.run(emulator_cmd, check=True, timeout=5)
                    break
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            else:
                # 如果所有模拟器都失败，显示ROM信息
                self.show_rom_info(game)
        
        except Exception as e:
            print(f"❌ 启动游戏失败: {e}")
            self.show_error(f"启动失败: {str(e)}")
    
    def show_rom_info(self, game: Dict):
        """显示ROM信息"""
        print(f"📋 显示ROM信息: {game['name']}")
        
        # 创建信息显示窗口
        info_running = True
        clock = pygame.time.Clock()
        
        while info_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                   (event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_RETURN]):
                    info_running = False
            
            self.screen.fill(self.BLACK)
            
            # 标题
            title_text = self.font_large.render("ROM 信息", True, self.WHITE)
            title_rect = title_text.get_rect(center=(400, 50))
            self.screen.blit(title_text, title_rect)
            
            # 游戏信息
            info_lines = [
                f"游戏名称: {game['name']}",
                f"描述: {game['description']}",
                f"类型: {game['genre']}",
                f"年份: {game['year']}",
                f"文件: {game['filename']}",
                f"大小: {game['size_kb']}KB",
                "",
                "按 ENTER 或 ESC 返回"
            ]
            
            y_offset = 150
            for line in info_lines:
                if line:
                    text_surface = self.font_medium.render(line, True, self.WHITE)
                    self.screen.blit(text_surface, (100, y_offset))
                y_offset += 40
            
            pygame.display.flip()
            clock.tick(60)
    
    def show_error(self, message: str):
        """显示错误信息"""
        error_running = True
        clock = pygame.time.Clock()
        
        while error_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                   (event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_RETURN]):
                    error_running = False
            
            self.screen.fill(self.BLACK)
            
            # 错误标题
            title_text = self.font_large.render("错误", True, self.RED)
            title_rect = title_text.get_rect(center=(400, 200))
            self.screen.blit(title_text, title_rect)
            
            # 错误信息
            error_text = self.font_medium.render(message, True, self.WHITE)
            error_rect = error_text.get_rect(center=(400, 300))
            self.screen.blit(error_text, error_rect)
            
            # 提示
            hint_text = self.font_small.render("按 ENTER 或 ESC 返回", True, self.GRAY)
            hint_rect = hint_text.get_rect(center=(400, 400))
            self.screen.blit(hint_text, hint_rect)
            
            pygame.display.flip()
            clock.tick(60)
    
    def run(self):
        """运行游戏启动器"""
        print("🚀 启动NES游戏启动器...")
        
        clock = pygame.time.Clock()
        
        while self.running:
            self.handle_events()
            
            # 绘制界面
            self.screen.fill(self.BLACK)
            self.draw_header()
            self.draw_game_list()
            self.draw_game_details()
            self.draw_controls()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        print("👋 游戏启动器已退出")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NES游戏启动器")
    parser.add_argument("--roms-dir", default="/home/pi/RetroPie/roms/nes", help="ROM目录路径")
    
    args = parser.parse_args()
    
    try:
        launcher = NESGameLauncher(args.roms_dir)
        launcher.run()
    except Exception as e:
        print(f"❌ 启动器运行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
