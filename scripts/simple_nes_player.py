#!/usr/bin/env python3
"""
简单的NES ROM播放器
显示ROM信息和基本的游戏界面模拟
"""

import sys
import pygame
import time
import random
from pathlib import Path

class SimpleNESPlayer:
    """简单的NES播放器"""
    
    def __init__(self, rom_path: str):
        self.rom_path = Path(rom_path)
        self.running = True
        
        # 初始化Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((512, 480))  # NES分辨率的2倍
        pygame.display.set_caption(f"NES Player - {self.rom_path.stem}")
        
        # 颜色定义
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.GRAY = (128, 128, 128)
        
        # NES调色板（简化版）
        self.nes_palette = [
            (84, 84, 84), (0, 30, 116), (8, 16, 144), (48, 0, 136),
            (68, 0, 100), (92, 0, 48), (84, 4, 0), (60, 24, 0),
            (32, 42, 0), (8, 58, 0), (0, 64, 0), (0, 60, 0),
            (0, 50, 60), (0, 0, 0), (0, 0, 0), (0, 0, 0)
        ]
        
        # 字体
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # 游戏状态
        self.game_time = 0
        self.score = 0
        self.level = 1
        
        # 加载ROM信息
        self.rom_info = self.load_rom_info()
        
        # 创建游戏对象
        self.player_x = 50
        self.player_y = 200
        self.enemies = []
        self.bullets = []
        
        # 生成敌人
        for i in range(5):
            self.enemies.append({
                'x': 400 + i * 80,
                'y': 100 + (i % 3) * 60,
                'dx': -1,
                'dy': 0
            })
    
    def load_rom_info(self):
        """加载ROM信息"""
        if not self.rom_path.exists():
            return {"error": "ROM文件不存在"}
        
        try:
            with open(self.rom_path, 'rb') as f:
                header = f.read(16)
            
            if len(header) < 16 or header[0:4] != b'NES\x1a':
                return {"error": "无效的NES ROM文件"}
            
            prg_size = header[4] * 16  # KB
            chr_size = header[5] * 8   # KB
            
            return {
                "name": self.rom_path.stem.replace("_", " ").title(),
                "prg_size": prg_size,
                "chr_size": chr_size,
                "total_size": self.rom_path.stat().st_size,
                "valid": True
            }
            
        except Exception as e:
            return {"error": f"读取ROM失败: {e}"}
    
    def draw_rom_info(self):
        """绘制ROM信息"""
        y_offset = 10
        
        # ROM名称
        name_text = self.font_large.render(self.rom_info.get("name", "未知游戏"), True, self.WHITE)
        self.screen.blit(name_text, (10, y_offset))
        y_offset += 40
        
        if "error" in self.rom_info:
            error_text = self.font_medium.render(f"错误: {self.rom_info['error']}", True, self.RED)
            self.screen.blit(error_text, (10, y_offset))
            return
        
        # ROM信息
        info_lines = [
            f"PRG ROM: {self.rom_info['prg_size']}KB",
            f"CHR ROM: {self.rom_info['chr_size']}KB",
            f"文件大小: {self.rom_info['total_size'] // 1024}KB",
            f"游戏时间: {self.game_time // 60}:{self.game_time % 60:02d}",
            f"分数: {self.score}",
            f"等级: {self.level}"
        ]
        
        for line in info_lines:
            text_surface = self.font_small.render(line, True, self.WHITE)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 20
    
    def draw_game_simulation(self):
        """绘制游戏模拟"""
        # 绘制游戏区域边框
        game_rect = pygame.Rect(10, 150, 492, 320)
        pygame.draw.rect(self.screen, self.GRAY, game_rect, 2)
        
        # 绘制玩家
        player_rect = pygame.Rect(self.player_x, self.player_y, 20, 20)
        pygame.draw.rect(self.screen, self.GREEN, player_rect)
        
        # 绘制敌人
        for enemy in self.enemies:
            enemy_rect = pygame.Rect(enemy['x'], enemy['y'], 15, 15)
            pygame.draw.rect(self.screen, self.RED, enemy_rect)
        
        # 绘制子弹
        for bullet in self.bullets:
            bullet_rect = pygame.Rect(bullet['x'], bullet['y'], 5, 5)
            pygame.draw.rect(self.screen, self.YELLOW, bullet_rect)
        
        # 绘制背景元素（模拟像素艺术）
        for i in range(0, 500, 50):
            for j in range(150, 470, 50):
                color = self.nes_palette[random.randint(0, 15)]
                if random.random() < 0.1:  # 10%概率绘制背景像素
                    pygame.draw.rect(self.screen, color, (i, j, 5, 5))
    
    def draw_controls(self):
        """绘制控制说明"""
        controls = [
            "WASD: 移动",
            "SPACE: 射击",
            "ESC: 退出"
        ]
        
        y_offset = 480 - len(controls) * 20
        for control in controls:
            text_surface = self.font_small.render(control, True, self.GRAY)
            self.screen.blit(text_surface, (400, y_offset))
            y_offset += 20
    
    def update_game(self):
        """更新游戏状态"""
        self.game_time += 1
        
        # 更新敌人位置
        for enemy in self.enemies:
            enemy['x'] += enemy['dx']
            enemy['y'] += enemy['dy']
            
            # 边界检测
            if enemy['x'] <= 10 or enemy['x'] >= 480:
                enemy['dx'] = -enemy['dx']
            if enemy['y'] <= 150 or enemy['y'] >= 450:
                enemy['dy'] = random.choice([-1, 0, 1])
        
        # 更新子弹位置
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            
            # 移除超出边界的子弹
            if bullet['x'] < 0 or bullet['x'] > 512 or bullet['y'] < 0 or bullet['y'] > 480:
                self.bullets.remove(bullet)
        
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
                'x': 500,
                'y': random.randint(150, 400),
                'dx': -1,
                'dy': random.choice([-1, 0, 1])
            })
        
        # 升级
        if self.score > 0 and self.score % 100 == 0:
            self.level = self.score // 100 + 1
    
    def handle_events(self):
        """处理事件"""
        keys = pygame.key.get_pressed()
        
        # 玩家移动
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player_y = max(150, self.player_y - 3)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player_y = min(450, self.player_y + 3)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player_x = max(10, self.player_x - 3)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player_x = min(480, self.player_x + 3)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                elif event.key == pygame.K_SPACE:
                    # 发射子弹
                    self.bullets.append({
                        'x': self.player_x + 20,
                        'y': self.player_y + 10,
                        'dx': 5,
                        'dy': 0
                    })
    
    def run(self):
        """运行播放器"""
        print(f"🎮 启动NES播放器: {self.rom_path.name}")
        
        if "error" in self.rom_info:
            print(f"❌ {self.rom_info['error']}")
        
        clock = pygame.time.Clock()
        frame_count = 0
        
        while self.running:
            self.handle_events()
            
            # 每秒更新60次游戏状态
            if frame_count % 1 == 0:
                self.update_game()
            
            # 绘制界面
            self.screen.fill(self.BLACK)
            self.draw_rom_info()
            self.draw_game_simulation()
            self.draw_controls()
            
            pygame.display.flip()
            clock.tick(60)
            frame_count += 1
        
        pygame.quit()
        print("👋 NES播放器已退出")

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python3 simple_nes_player.py <rom_file>")
        sys.exit(1)
    
    rom_path = sys.argv[1]
    
    try:
        player = SimpleNESPlayer(rom_path)
        player.run()
    except Exception as e:
        print(f"❌ 播放器运行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
