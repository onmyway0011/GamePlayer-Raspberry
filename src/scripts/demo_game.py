#!/usr/bin/env python3
"""
GamePlayer-Raspberry 演示游戏
一个简单的弹球游戏，展示 GUI 环境功能
"""

import pygame
import sys
import random
import math
import os

# 设置显示环境
os.environ['SDL_VIDEODRIVER'] = 'x11'

class DemoGame:
    def __init__(self):
        """初始化游戏"""
        pygame.init()
        
        # 游戏设置
        self.width = 800
        self.height = 600
        self.fps = 60
        
        # 创建游戏窗口
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("🎮 GamePlayer-Raspberry Demo Game")
        
        # 时钟
        self.clock = pygame.time.Clock()
        
        # 颜色定义
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.PURPLE = (255, 0, 255)
        self.CYAN = (0, 255, 255)
        self.ORANGE = (255, 165, 0)
        
        # 游戏对象
        self.balls = []
        self.score = 0
        self.running = True
        
        # 字体
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # 初始化球
        self.init_balls()
        
        print("🎮 GamePlayer-Raspberry Demo Game 初始化完成")
        print("🎯 游戏控制:")
        print("   - 鼠标移动: 控制重力方向")
        print("   - 空格键: 添加新球")
        print("   - R 键: 重置游戏")
        print("   - ESC 键: 退出游戏")
    
    def init_balls(self):
        """初始化球对象"""
        self.balls = []
        colors = [self.RED, self.GREEN, self.BLUE, self.YELLOW, self.PURPLE, self.CYAN, self.ORANGE]
        
        for i in range(5):
            ball = {
                'x': random.randint(50, self.width - 50),
                'y': random.randint(50, self.height - 50),
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'radius': random.randint(10, 25),
                'color': random.choice(colors),
                'trail': []
            }
            self.balls.append(ball)
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.add_ball()
                elif event.key == pygame.K_r:
                    self.reset_game()
    
    def add_ball(self):
        """添加新球"""
        colors = [self.RED, self.GREEN, self.BLUE, self.YELLOW, self.PURPLE, self.CYAN, self.ORANGE]
        ball = {
            'x': random.randint(50, self.width - 50),
            'y': random.randint(50, self.height - 50),
            'vx': random.uniform(-4, 4),
            'vy': random.uniform(-4, 4),
            'radius': random.randint(8, 20),
            'color': random.choice(colors),
            'trail': []
        }
        self.balls.append(ball)
        self.score += 10
    
    def reset_game(self):
        """重置游戏"""
        self.init_balls()
        self.score = 0
    
    def update_balls(self):
        """更新球的位置"""
        # 获取鼠标位置作为重力中心
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for ball in self.balls:
            # 计算到鼠标的距离和角度
            dx = mouse_x - ball['x']
            dy = mouse_y - ball['y']
            distance = math.sqrt(dx*dx + dy*dy)
            
            # 添加轻微的重力效果
            if distance > 0:
                gravity_strength = 0.1
                ball['vx'] += (dx / distance) * gravity_strength
                ball['vy'] += (dy / distance) * gravity_strength
            
            # 限制速度
            max_speed = 5
            speed = math.sqrt(ball['vx']**2 + ball['vy']**2)
            if speed > max_speed:
                ball['vx'] = (ball['vx'] / speed) * max_speed
                ball['vy'] = (ball['vy'] / speed) * max_speed
            
            # 更新位置
            ball['x'] += ball['vx']
            ball['y'] += ball['vy']
            
            # 边界碰撞
            if ball['x'] - ball['radius'] <= 0 or ball['x'] + ball['radius'] >= self.width:
                ball['vx'] = -ball['vx'] * 0.8  # 添加能量损失
                ball['x'] = max(ball['radius'], min(self.width - ball['radius'], ball['x']))
            
            if ball['y'] - ball['radius'] <= 0 or ball['y'] + ball['radius'] >= self.height:
                ball['vy'] = -ball['vy'] * 0.8  # 添加能量损失
                ball['y'] = max(ball['radius'], min(self.height - ball['radius'], ball['y']))
            
            # 更新轨迹
            ball['trail'].append((int(ball['x']), int(ball['y'])))
            if len(ball['trail']) > 20:
                ball['trail'].pop(0)
        
        # 球之间的碰撞检测
        for i, ball1 in enumerate(self.balls):
            for j, ball2 in enumerate(self.balls[i+1:], i+1):
                dx = ball1['x'] - ball2['x']
                dy = ball1['y'] - ball2['y']
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < ball1['radius'] + ball2['radius']:
                    # 简单的弹性碰撞
                    ball1['vx'], ball2['vx'] = ball2['vx'], ball1['vx']
                    ball1['vy'], ball2['vy'] = ball2['vy'], ball1['vy']
                    self.score += 1
    
    def draw(self):
        """绘制游戏画面"""
        # 清屏
        self.screen.fill(self.BLACK)
        
        # 绘制背景网格
        for x in range(0, self.width, 50):
            pygame.draw.line(self.screen, (20, 20, 20), (x, 0), (x, self.height))
        for y in range(0, self.height, 50):
            pygame.draw.line(self.screen, (20, 20, 20), (0, y), (self.width, y))
        
        # 绘制球的轨迹
        for ball in self.balls:
            if len(ball['trail']) > 1:
                for i in range(1, len(ball['trail'])):
                    alpha = i / len(ball['trail'])
                    color = tuple(int(c * alpha) for c in ball['color'])
                    if i < len(ball['trail']) - 1:
                        pygame.draw.line(self.screen, color, ball['trail'][i-1], ball['trail'][i], 2)
        
        # 绘制球
        for ball in self.balls:
            # 球的阴影
            shadow_pos = (int(ball['x'] + 2), int(ball['y'] + 2))
            pygame.draw.circle(self.screen, (50, 50, 50), shadow_pos, ball['radius'])
            
            # 球本体
            pygame.draw.circle(self.screen, ball['color'], (int(ball['x']), int(ball['y'])), ball['radius'])
            
            # 球的高光
            highlight_pos = (int(ball['x'] - ball['radius']//3), int(ball['y'] - ball['radius']//3))
            pygame.draw.circle(self.screen, self.WHITE, highlight_pos, ball['radius']//4)
        
        # 绘制鼠标位置指示器
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.circle(self.screen, self.WHITE, (mouse_x, mouse_y), 5, 2)
        pygame.draw.line(self.screen, self.WHITE, (mouse_x-10, mouse_y), (mouse_x+10, mouse_y), 2)
        pygame.draw.line(self.screen, self.WHITE, (mouse_x, mouse_y-10), (mouse_x, mouse_y+10), 2)
        
        # 绘制 UI
        self.draw_ui()
        
        # 更新显示
        pygame.display.flip()
    
    def draw_ui(self):
        """绘制用户界面"""
        # 标题
        title_text = self.font_large.render("🎮 GamePlayer-Raspberry", True, self.WHITE)
        self.screen.blit(title_text, (10, 10))
        
        # 分数
        score_text = self.font_medium.render(f"Score: {self.score}", True, self.YELLOW)
        self.screen.blit(score_text, (10, 60))
        
        # 球数量
        balls_text = self.font_medium.render(f"Balls: {len(self.balls)}", True, self.GREEN)
        self.screen.blit(balls_text, (10, 90))
        
        # 控制说明
        controls = [
            "Controls:",
            "Mouse: Gravity direction",
            "SPACE: Add ball",
            "R: Reset game",
            "ESC: Exit"
        ]
        
        for i, text in enumerate(controls):
            color = self.CYAN if i == 0 else self.WHITE
            control_text = self.font_small.render(text, True, color)
            self.screen.blit(control_text, (self.width - 200, 10 + i * 25))
        
        # FPS 显示
        fps_text = self.font_small.render(f"FPS: {int(self.clock.get_fps())}", True, self.WHITE)
        self.screen.blit(fps_text, (self.width - 100, self.height - 30))
    
    def run(self):
        """运行游戏主循环"""
        print("🎮 游戏开始!")
        
        while self.running:
            # 处理事件
            self.handle_events()
            
            # 更新游戏状态
            self.update_balls()
            
            # 绘制画面
            self.draw()
            
            # 控制帧率
            self.clock.tick(self.fps)
        
        print("🎮 游戏结束!")
        pygame.quit()

def main():
    """主函数"""
    try:
        # 检查显示环境
        if 'DISPLAY' not in os.environ:
            print("❌ 错误: 未设置 DISPLAY 环境变量")
            print("请确保在 X11 环境中运行此游戏")
            return 1
        
        print("🚀 启动 GamePlayer-Raspberry 演示游戏...")
        print(f"📺 显示: {os.environ.get('DISPLAY', 'unknown')}")
        
        # 创建并运行游戏
        game = DemoGame()
        game.run()
        
        return 0
        
    except pygame.error as e:
        print(f"❌ Pygame 错误: {e}")
        print("请确保在支持图形界面的环境中运行")
        return 1
    except Exception as e:
        print(f"❌ 游戏错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
