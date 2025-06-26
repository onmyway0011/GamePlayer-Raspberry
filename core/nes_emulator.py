#!/usr/bin/env python3
"""
简单的NES模拟器核心
基于Pygame实现的基础NES模拟器，支持运行NES ROM文件
"""

import os
import sys
import pygame
import struct
import time
import threading
from pathlib import Path
from typing import Optional, Tuple, List

class NESEmulator:
    """简单的NES模拟器"""
    
    def __init__(self):
        # 初始化Pygame
        pygame.init()
        
        # NES屏幕分辨率
        self.NES_WIDTH = 256
        self.NES_HEIGHT = 240
        self.SCALE = 3
        
        # 创建窗口
        self.screen = pygame.display.set_mode((self.NES_WIDTH * self.SCALE, self.NES_HEIGHT * self.SCALE))
        pygame.display.set_caption("NES Emulator")
        
        # 创建NES屏幕表面
        self.nes_screen = pygame.Surface((self.NES_WIDTH, self.NES_HEIGHT))
        
        # 颜色定义
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        
        # NES调色板（简化版）
        self.nes_palette = [
            (84, 84, 84), (0, 30, 116), (8, 16, 144), (48, 0, 136),
            (68, 0, 100), (92, 0, 48), (84, 4, 0), (60, 24, 0),
            (32, 42, 0), (8, 58, 0), (0, 64, 0), (0, 60, 0),
            (0, 50, 60), (0, 0, 0), (0, 0, 0), (0, 0, 0),
            (152, 150, 152), (8, 76, 196), (48, 50, 236), (92, 30, 228),
            (136, 20, 176), (160, 20, 100), (152, 34, 32), (120, 60, 0),
            (84, 90, 0), (40, 114, 0), (8, 124, 0), (0, 118, 40),
            (0, 102, 120), (0, 0, 0), (0, 0, 0), (0, 0, 0)
        ]
        
        # 游戏状态
        self.running = False
        self.paused = False
        self.rom_loaded = False
        self.rom_data = None
        self.rom_info = {}
        
        # 模拟的游戏对象
        self.player_x = 50
        self.player_y = 200
        self.enemies = []
        self.bullets = []
        self.score = 0
        self.lives = 3
        self.level = 1
        
        # 时钟
        self.clock = pygame.time.Clock()
        self.frame_count = 0
        
        # 字体
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 16)
        
        # 控制器状态
        self.controller = {
            'up': False,
            'down': False,
            'left': False,
            'right': False,
            'a': False,
            'b': False,
            'start': False,
            'select': False
        }
    
    def load_rom(self, rom_path: str) -> bool:
        """加载ROM文件"""
        try:
            rom_file = Path(rom_path)
            if not rom_file.exists():
                print(f"ROM文件不存在: {rom_path}")
                return False
            
            with open(rom_file, 'rb') as f:
                self.rom_data = f.read()
            
            # 解析ROM头部
            if len(self.rom_data) < 16:
                print("ROM文件太小")
                return False
            
            header = self.rom_data[:16]
            if header[:4] != b'NES\x1a':
                print("不是有效的NES ROM文件")
                return False
            
            # 解析ROM信息
            self.rom_info = {
                'name': rom_file.stem,
                'prg_size': header[4] * 16,  # KB
                'chr_size': header[5] * 8,   # KB
                'flags6': header[6],
                'flags7': header[7],
                'mapper': ((header[7] & 0xF0) | (header[6] >> 4)),
                'mirroring': 'vertical' if (header[6] & 1) else 'horizontal'
            }
            
            self.rom_loaded = True
            print(f"ROM加载成功: {self.rom_info['name']}")
            print(f"PRG ROM: {self.rom_info['prg_size']}KB")
            print(f"CHR ROM: {self.rom_info['chr_size']}KB")
            print(f"Mapper: {self.rom_info['mapper']}")
            
            # 初始化游戏状态
            self.init_game_state()
            
            return True
            
        except Exception as e:
            print(f"ROM加载失败: {e}")
            return False
    
    def init_game_state(self):
        """初始化游戏状态"""
        # 重置游戏对象
        self.player_x = 50
        self.player_y = 200
        self.enemies = []
        self.bullets = []
        self.score = 0
        self.lives = 3
        self.level = 1
        
        # 生成初始敌人
        for i in range(5):
            self.enemies.append({
                'x': 200 + i * 60,
                'y': 50 + (i % 3) * 50,
                'dx': -1,
                'dy': 0,
                'type': i % 3
            })
    
    def update_controller(self):
        """更新控制器状态"""
        keys = pygame.key.get_pressed()
        
        self.controller['up'] = keys[pygame.K_UP] or keys[pygame.K_w]
        self.controller['down'] = keys[pygame.K_DOWN] or keys[pygame.K_s]
        self.controller['left'] = keys[pygame.K_LEFT] or keys[pygame.K_a]
        self.controller['right'] = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        self.controller['a'] = keys[pygame.K_SPACE] or keys[pygame.K_z]
        self.controller['b'] = keys[pygame.K_LSHIFT] or keys[pygame.K_x]
        self.controller['start'] = keys[pygame.K_RETURN]
        self.controller['select'] = keys[pygame.K_TAB]
    
    def update_game_logic(self):
        """更新游戏逻辑"""
        if not self.rom_loaded or self.paused:
            return
        
        # 玩家移动
        if self.controller['left']:
            self.player_x = max(10, self.player_x - 3)
        if self.controller['right']:
            self.player_x = min(self.NES_WIDTH - 30, self.player_x + 3)
        if self.controller['up']:
            self.player_y = max(10, self.player_y - 3)
        if self.controller['down']:
            self.player_y = min(self.NES_HEIGHT - 30, self.player_y + 3)
        
        # 射击
        if self.controller['a'] and self.frame_count % 10 == 0:
            self.bullets.append({
                'x': self.player_x + 15,
                'y': self.player_y,
                'dx': 5,
                'dy': 0
            })
        
        # 更新子弹
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            
            if bullet['x'] > self.NES_WIDTH or bullet['x'] < 0:
                self.bullets.remove(bullet)
        
        # 更新敌人
        for enemy in self.enemies:
            enemy['x'] += enemy['dx']
            enemy['y'] += enemy['dy']
            
            # 边界检测
            if enemy['x'] <= 10 or enemy['x'] >= self.NES_WIDTH - 20:
                enemy['dx'] = -enemy['dx']
            if enemy['y'] <= 10 or enemy['y'] >= self.NES_HEIGHT - 20:
                enemy['dy'] = -enemy['dy']
        
        # 碰撞检测
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if (abs(bullet['x'] - enemy['x']) < 15 and 
                    abs(bullet['y'] - enemy['y']) < 15):
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 10
                    break
        
        # 重新生成敌人
        if len(self.enemies) < 3:
            self.enemies.append({
                'x': self.NES_WIDTH - 20,
                'y': 50 + (len(self.enemies) % 3) * 50,
                'dx': -1,
                'dy': 0,
                'type': len(self.enemies) % 3
            })
        
        # 升级
        if self.score > 0 and self.score % 100 == 0 and self.frame_count % 60 == 0:
            self.level = self.score // 100 + 1
    
    def render_game(self):
        """渲染游戏画面"""
        # 清空屏幕
        self.nes_screen.fill(self.BLACK)
        
        if not self.rom_loaded:
            # 显示"请加载ROM"信息
            text = self.font.render("Please load a ROM file", True, self.WHITE)
            text_rect = text.get_rect(center=(self.NES_WIDTH//2, self.NES_HEIGHT//2))
            self.nes_screen.blit(text, text_rect)
        else:
            # 绘制游戏内容
            self.render_game_objects()
            self.render_ui()
        
        # 缩放到屏幕
        scaled_surface = pygame.transform.scale(self.nes_screen, 
                                              (self.NES_WIDTH * self.SCALE, self.NES_HEIGHT * self.SCALE))
        self.screen.blit(scaled_surface, (0, 0))
        
        pygame.display.flip()
    
    def render_game_objects(self):
        """渲染游戏对象"""
        # 绘制背景网格
        for x in range(0, self.NES_WIDTH, 32):
            for y in range(0, self.NES_HEIGHT, 32):
                if (x + y) % 64 == 0:
                    pygame.draw.rect(self.nes_screen, (20, 20, 20), (x, y, 32, 32))
        
        # 绘制玩家
        player_color = self.GREEN if not self.paused else self.YELLOW
        pygame.draw.rect(self.nes_screen, player_color, (self.player_x, self.player_y, 20, 20))
        pygame.draw.rect(self.nes_screen, self.WHITE, (self.player_x + 5, self.player_y + 5, 10, 10))
        
        # 绘制敌人
        for enemy in self.enemies:
            enemy_colors = [self.RED, (255, 128, 0), (255, 0, 255)]
            color = enemy_colors[enemy['type']]
            pygame.draw.rect(self.nes_screen, color, (enemy['x'], enemy['y'], 15, 15))
        
        # 绘制子弹
        for bullet in self.bullets:
            pygame.draw.rect(self.nes_screen, self.YELLOW, (bullet['x'], bullet['y'], 5, 5))
    
    def render_ui(self):
        """渲染用户界面"""
        # 分数
        score_text = self.small_font.render(f"SCORE: {self.score}", True, self.WHITE)
        self.nes_screen.blit(score_text, (10, 10))
        
        # 生命
        lives_text = self.small_font.render(f"LIVES: {self.lives}", True, self.WHITE)
        self.nes_screen.blit(lives_text, (10, 25))
        
        # 等级
        level_text = self.small_font.render(f"LEVEL: {self.level}", True, self.WHITE)
        self.nes_screen.blit(level_text, (10, 40))
        
        # ROM信息
        if self.rom_info:
            rom_text = self.small_font.render(f"ROM: {self.rom_info['name']}", True, self.WHITE)
            self.nes_screen.blit(rom_text, (10, self.NES_HEIGHT - 20))
        
        # 暂停提示
        if self.paused:
            pause_text = self.font.render("PAUSED", True, self.YELLOW)
            pause_rect = pause_text.get_rect(center=(self.NES_WIDTH//2, self.NES_HEIGHT//2))
            self.nes_screen.blit(pause_text, pause_rect)
        
        # 控制提示
        if self.frame_count < 300:  # 显示5秒
            controls = [
                "WASD/Arrows: Move",
                "Space/Z: Fire",
                "P: Pause",
                "ESC: Exit"
            ]
            for i, control in enumerate(controls):
                text = self.small_font.render(control, True, self.WHITE)
                self.nes_screen.blit(text, (self.NES_WIDTH - 120, 10 + i * 15))
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.rom_loaded:
                    self.init_game_state()
    
    def run(self, rom_path: Optional[str] = None) -> bool:
        """运行模拟器"""
        print("🎮 启动NES模拟器...")
        
        if rom_path:
            if not self.load_rom(rom_path):
                print("ROM加载失败")
                return False
        
        self.running = True
        
        try:
            while self.running:
                self.handle_events()
                self.update_controller()
                self.update_game_logic()
                self.render_game()
                
                self.clock.tick(60)  # 60 FPS
                self.frame_count += 1
        
        except KeyboardInterrupt:
            print("\n用户中断")
        
        except Exception as e:
            print(f"模拟器运行错误: {e}")
            return False
        
        finally:
            pygame.quit()
        
        print("👋 NES模拟器已退出")
        return True

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="简单NES模拟器")
    parser.add_argument("rom", nargs="?", help="ROM文件路径")
    parser.add_argument("--fullscreen", action="store_true", help="全屏模式")
    
    args = parser.parse_args()
    
    emulator = NESEmulator()
    
    if args.fullscreen:
        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    
    success = emulator.run(args.rom)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
