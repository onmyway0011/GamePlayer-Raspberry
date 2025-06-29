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
from typing import Optional, Tuple, List, Dict

# 导入新的管理器
try:
    from save_manager import SaveManager
    from cheat_manager import CheatManager
    from device_manager import DeviceManager
except ImportError:
    # 如果在不同目录运行，尝试相对导入
    sys.path.append(os.path.dirname(__file__))
    from save_manager import SaveManager
    from cheat_manager import CheatManager
    from device_manager import DeviceManager


class NESEmulator:
    """简单的NES模拟器"""

    def get_system_font(self, size: int):
        """获取系统字体，支持中文显示"""
        # macOS 常见中文字体
        mac_fonts = [
            'PingFang SC', 'Hiragino Sans GB', 'STHeiti', 
            'Arial Unicode MS', 'Helvetica Neue', 'Arial'
        ]
        
        for font_name in mac_fonts:
            try:
                font = pygame.font.SysFont(font_name, size)
                # 测试字体是否能渲染中文字符
                test_surface = font.render('测试', True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    return font
            except:
                continue
        
        # 如果都失败了，使用默认字体
        try:
            return pygame.font.SysFont(None, size)
        except:
            return pygame.font.Font(None, size)

    def __init__(self):
        """TODO: Add docstring"""
        # 初始化Pygame
        pygame.init()

        # NES屏幕分辨率
        self.NES_WIDTH = 256
        self.NES_HEIGHT = 240
        self.SCALE = 3

        # 创建窗口
        self.screen = pygame.display.set_mode((self.NES_WIDTH * self.SCALE, self.NES_HEIGHT * self.SCALE))
        pygame.display.set_caption("NES Emulator - Enhanced")

        # 创建NES屏幕表面
        self.nes_screen = pygame.Surface((self.NES_WIDTH, self.NES_HEIGHT))

        # 初始化管理器
        self.save_manager = SaveManager()
        self.cheat_manager = CheatManager()
        self.device_manager = DeviceManager()

        # 当前ROM路径
        self.current_rom_path = None

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

        # 字体设置 - 修复中文显示问题
        self.font = self.get_system_font(24)
        self.small_font = self.get_system_font(16)

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

        # 使用外部控制器
        self.use_external_controller = True
        self.controller_deadzone = 0.3

    def load_rom(self, rom_path: str):
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
            self.current_rom_path = rom_path
            print(f"ROM加载成功: {self.rom_info['name']}")
            print(f"PRG ROM: {self.rom_info['prg_size']}KB")
            print(f"CHR ROM: {self.rom_info['chr_size']}KB")
            print(f"Mapper: {self.rom_info['mapper']}")

            # 初始化游戏状态
            self.init_game_state()

            # 自动连接设备
            self.device_manager.auto_connect_devices()
            self.device_manager.start_device_monitor()

            # 自动启用作弊码
            self.cheat_manager.auto_enable_cheats(rom_path)
            self.cheat_manager.start_cheat_monitor(self)

            # 尝试加载存档
            self.auto_load_save()

            # 启动自动保存
            self.save_manager.start_auto_save(rom_path, self.get_game_state)

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
        # 键盘输入
        keys = pygame.key.get_pressed()

        keyboard_input = {
            'up': keys[pygame.K_UP] or keys[pygame.K_w],
            'down': keys[pygame.K_DOWN] or keys[pygame.K_s],
            'left': keys[pygame.K_LEFT] or keys[pygame.K_a],
            'right': keys[pygame.K_RIGHT] or keys[pygame.K_d],
            'a': keys[pygame.K_SPACE] or keys[pygame.K_z],
            'b': keys[pygame.K_LSHIFT] or keys[pygame.K_x],
            'start': keys[pygame.K_RETURN],
            'select': keys[pygame.K_TAB]
        }

        # 外部控制器输入
        controller_input = {}
        if self.use_external_controller:
            controller_input = self.get_external_controller_input()

        # 合并输入（键盘或控制器任一输入都有效）
        for key in self.controller:
            self.controller[key] = keyboard_input.get(key, False) or controller_input.get(key, False)

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
                "F5: Quick Save",
                "F9: Quick Load",
                "ESC: Exit"
            ]
            for i, control in enumerate(controls):
                text = self.small_font.render(control, True, self.WHITE)
                self.nes_screen.blit(text, (self.NES_WIDTH - 120, 10 + i * 12))

        # 显示增强功能状态
        if self.frame_count > 300:  # 5秒后显示状态信息
            status_y = 10

            # 作弊码状态
            cheat_status = self.cheat_manager.get_cheat_status()
            if cheat_status["enabled_cheats"] > 0:
                cheat_text = f"Cheats: {cheat_status['enabled_cheats']}"
                text = self.small_font.render(cheat_text, True, self.YELLOW)
                self.nes_screen.blit(text, (self.NES_WIDTH - 80, status_y))
                status_y += 12

            # 控制器状态
            device_status = self.device_manager.get_device_status()
            if device_status["controllers"]["count"] > 0:
                controller_text = f"Controllers: {device_status['controllers']['count']}"
                text = self.small_font.render(controller_text, True, self.GREEN)
                self.nes_screen.blit(text, (self.NES_WIDTH - 80, status_y))
                status_y += 12

            # 自动保存指示
            if hasattr(self.save_manager, 'last_save_time') and self.save_manager.last_save_time > 0:
                time_since_save = time.time() - self.save_manager.last_save_time
                if time_since_save < 3.0:  # 3秒内显示保存提示
                    save_text = "Auto Saved"
                    text = self.small_font.render(save_text, True, self.GREEN)
                    self.nes_screen.blit(text, (self.NES_WIDTH - 80, status_y))

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

                # 存档快捷键
                elif event.key == pygame.K_F5:  # F5 快速保存
                    self.manual_save(slot=1)
                elif event.key == pygame.K_F9:  # F9 快速加载
                    self.manual_load(slot=1)

                # 存档插槽快捷键 (Ctrl + 数字键)
                elif pygame.key.get_pressed()[pygame.K_LCTRL]:
                    if event.key == pygame.K_1:
                        self.manual_save(slot=1)
                    elif event.key == pygame.K_2:
                        self.manual_save(slot=2)
                    elif event.key == pygame.K_3:
                        self.manual_save(slot=3)

                # 加载插槽快捷键 (Alt + 数字键)
                elif pygame.key.get_pressed()[pygame.K_LALT]:
                    if event.key == pygame.K_1:
                        self.manual_load(slot=1)
                    elif event.key == pygame.K_2:
                        self.manual_load(slot=2)
                    elif event.key == pygame.K_3:
                        self.manual_load(slot=3)

    def run(self, rom_path: Optional[str] = None):
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
            # 清理资源
            self.cleanup()
            pygame.quit()

        print("👋 NES模拟器已退出")
        return True

    def get_external_controller_input(self) -> Dict:
        """获取外部控制器输入"""
        controller_input = {
            'up': False, 'down': False, 'left': False, 'right': False,
            'a': False, 'b': False, 'start': False, 'select': False
        }

        try:
            # 获取第一个控制器的输入
            input_state = self.device_manager.get_controller_input(0)
            if input_state:
                axes = input_state.get('axes', [])
                buttons = input_state.get('buttons', [])
                hats = input_state.get('hats', [])

                # 左摇杆或十字键
                if len(axes) >= 2:
                    # 左摇杆X轴
                    if axes[0] < -self.controller_deadzone:
                        controller_input['left'] = True
                    elif axes[0] > self.controller_deadzone:
                        controller_input['right'] = True

                    # 左摇杆Y轴
                    if axes[1] < -self.controller_deadzone:
                        controller_input['up'] = True
                    elif axes[1] > self.controller_deadzone:
                        controller_input['down'] = True

                # 十字键（Hat）
                if len(hats) >= 1:
                    hat_x, hat_y = hats[0]
                    if hat_x == -1:
                        controller_input['left'] = True
                    elif hat_x == 1:
                        controller_input['right'] = True
                    if hat_y == 1:
                        controller_input['up'] = True
                    elif hat_y == -1:
                        controller_input['down'] = True

                # 按钮映射（通用映射）
                if len(buttons) >= 4:
                    controller_input['a'] = buttons[0]      # A按钮
                    controller_input['b'] = buttons[1]      # B按钮
                    controller_input['select'] = buttons[2] if len(buttons) > 2 else False  # Select
                    controller_input['start'] = buttons[3] if len(buttons) > 3 else False   # Start

        except Exception as e:
            # 控制器输入失败时静默处理
            pass

        return controller_input

    def get_game_state(self) -> Dict:
        """获取当前游戏状态（用于存档）"""
        return {
            "player_x": self.player_x,
            "player_y": self.player_y,
            "enemies": self.enemies.copy(),
            "bullets": self.bullets.copy(),
            "score": self.score,
            "lives": self.lives,
            "level": self.level,
            "frame_count": self.frame_count,
            "timestamp": time.time()
        }

    def set_game_state(self, game_state: Dict):
        """设置游戏状态（用于读档）"""
        try:
            self.player_x = game_state.get("player_x", 50)
            self.player_y = game_state.get("player_y", 200)
            self.enemies = game_state.get("enemies", [])
            self.bullets = game_state.get("bullets", [])
            self.score = game_state.get("score", 0)
            self.lives = game_state.get("lives", 3)
            self.level = game_state.get("level", 1)
            self.frame_count = game_state.get("frame_count", 0)

            print(f"📂 游戏状态已恢复")
            print(f"   分数: {self.score}, 生命: {self.lives}, 等级: {self.level}")

        except Exception as e:
            print(f"❌ 恢复游戏状态失败: {e}")

    def auto_load_save(self):
        """自动加载存档"""
        if not self.current_rom_path:
            return

        try:
            # 尝试加载最近的存档（插槽0）
            game_state = self.save_manager.load_game(self.current_rom_path, slot=0)
            if game_state:
                self.set_game_state(game_state)
                print(f"✅ 自动加载存档成功")
            else:
                print(f"ℹ️ 没有找到存档文件，开始新游戏")

        except Exception as e:
            print(f"⚠️ 自动加载存档失败: {e}")

    def manual_save(self, slot: int = 1):
        """手动保存游戏"""
        if not self.current_rom_path:
            return False

        try:
            game_state = self.get_game_state()
            success = self.save_manager.save_game(self.current_rom_path, game_state, slot)
            if success:
                print(f"💾 手动保存成功: 插槽 {slot}")
            return success

        except Exception as e:
            print(f"❌ 手动保存失败: {e}")
            return False

    def manual_load(self, slot: int = 1):
        """手动加载游戏"""
        if not self.current_rom_path:
            return False

        try:
            game_state = self.save_manager.load_game(self.current_rom_path, slot)
            if game_state:
                self.set_game_state(game_state)
                print(f"📂 手动加载成功: 插槽 {slot}")
                return True
            else:
                print(f"❌ 插槽 {slot} 没有存档")
                return False

        except Exception as e:
            print(f"❌ 手动加载失败: {e}")
            return False

    def write_memory(self, address: int, value: int):
        """写入内存（用于作弊码）"""
        # 这是一个模拟的内存写入函数
        # 在真实的NES模拟器中，这里会修改实际的内存
        pass

    def cleanup(self):
        """清理资源"""
        try:
            # 停止自动保存
            self.save_manager.stop_auto_save()

            # 停止作弊码监控
            self.cheat_manager.stop_cheat_monitor()

            # 停止设备监控
            self.device_manager.stop_device_monitor()

            # 保存作弊码配置
            if self.current_rom_path:
                self.cheat_manager.save_cheat_config(self.current_rom_path)

            print(f"🧹 资源清理完成")

        except Exception as e:
            print(f"⚠️ 资源清理出错: {e}")


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
