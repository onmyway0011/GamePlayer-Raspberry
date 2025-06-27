#!/usr/bin/env python3
"""
音频管理器
处理游戏音频、音效、背景音乐等
"""

import os
import sys
import json
import time
import threading
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import pygame
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except (ImportError, pygame.error) as e:
    print(f"⚠️ 音频系统不可用: {e}")
    pygame = None
    AUDIO_AVAILABLE = False


class AudioManager:
    """音频管理器"""

    def __init__(self, audio_dir: str = "data/audio"):
        """TODO: Add docstring"""
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.audio_available = AUDIO_AVAILABLE

        # 音频配置
        self.sample_rate = 44100
        self.buffer_size = 1024
        self.channels = 2
        self.audio_enabled = True
        self.master_volume = 0.7
        self.sfx_volume = 0.8
        self.music_volume = 0.6

        # 音频文件缓存
        self.sound_cache = {}
        self.music_cache = {}

        # 当前播放状态
        self.current_music = None
        self.music_playing = False
        self.sfx_enabled = True

        # 音频线程
        self.audio_thread = None
        self.audio_thread_running = False

        # 初始化音频系统
        self._initialize_audio()

        print(f"🔊 音频管理器初始化完成")
        print(f"📁 音频目录: {self.audio_dir}")
        print(f"🎵 采样率: {self.sample_rate}Hz")
        print(f"🔊 缓冲区: {self.buffer_size}")

    def _initialize_audio(self):
        """初始化音频系统"""
        try:
            if pygame and pygame.mixer:
                # 初始化pygame音频
                pygame.mixer.pre_init(
                    frequency=self.sample_rate,
                    size=-16,
                    channels=self.channels,
                    buffer=self.buffer_size
                )
                pygame.mixer.init()

                # 设置音量
                pygame.mixer.music.set_volume(self.music_volume)

                print("✅ Pygame音频系统初始化成功")

        except Exception as e:
            print(f"⚠️ 音频系统初始化失败: {e}")
            self.audio_enabled = False

    def create_default_sounds(self):
        """创建默认音效"""
        sounds_dir = self.audio_dir / "sounds"
        sounds_dir.mkdir(exist_ok=True)

        # 创建简单的音效文件（使用代码生成）
        self._generate_beep_sound(sounds_dir / "beep.wav", 800, 0.1)
        self._generate_beep_sound(sounds_dir / "select.wav", 1000, 0.05)
        self._generate_beep_sound(sounds_dir / "start.wav", 600, 0.2)
        self._generate_beep_sound(sounds_dir / "error.wav", 200, 0.3)
        self._generate_beep_sound(sounds_dir / "success.wav", 1200, 0.15)

        print("🎵 默认音效文件已创建")

    def _generate_beep_sound(self, filename: Path, frequency: int, duration: float):
        """生成简单的蜂鸣音效"""
        try:
            import numpy as np
            import wave

            # 生成正弦波
            sample_rate = 44100
            frames = int(duration * sample_rate)

            # 创建正弦波数据
            wave_data = np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames))

            # 添加淡入淡出效果
            fade_frames = int(0.01 * sample_rate)  # 10ms淡入淡出
            if fade_frames > 0:
                fade_in = np.linspace(0, 1, fade_frames)
                fade_out = np.linspace(1, 0, fade_frames)

                wave_data[:fade_frames] *= fade_in
                wave_data[-fade_frames:] *= fade_out

            # 转换为16位整数
            wave_data = (wave_data * 32767).astype(np.int16)

            # 保存为WAV文件
            with wave.open(str(filename), 'w') as wav_file:
                wav_file.setnchannels(1)  # 单声道
                wav_file.setsampwidth(2)  # 16位
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(wave_data.tobytes())

        except ImportError:
            print("⚠️ numpy未安装，无法生成音效文件")
        except Exception as e:
            print(f"⚠️ 生成音效失败: {e}")

    def load_sound(self, sound_name: str, file_path: str = None):
        """加载音效文件"""
        if not self.audio_enabled or not pygame:
            return False

        try:
            if file_path is None:
                file_path = self.audio_dir / "sounds" / f"{sound_name}.wav"

            if not Path(file_path).exists():
                print(f"⚠️ 音效文件不存在: {file_path}")
                return False

            sound = pygame.mixer.Sound(str(file_path))
            sound.set_volume(self.sfx_volume * self.master_volume)
            self.sound_cache[sound_name] = sound

            print(f"🎵 音效已加载: {sound_name}")
            return True

        except Exception as e:
            print(f"❌ 加载音效失败: {e}")
            return False

    def play_sound(self, sound_name: str, volume: float = 1.0):
        """播放音效"""
        if not self.audio_enabled or not self.sfx_enabled or not pygame:
            return False

        try:
            # 如果音效未加载，尝试加载
            if sound_name not in self.sound_cache:
                if not self.load_sound(sound_name):
                    return False

            sound = self.sound_cache[sound_name]
            sound.set_volume(volume * self.sfx_volume * self.master_volume)
            sound.play()

            return True

        except Exception as e:
            print(f"❌ 播放音效失败: {e}")
            return False

    def load_music(self, music_name: str, file_path: str = None):
        """加载背景音乐"""
        if not self.audio_enabled or not pygame:
            return False

        try:
            if file_path is None:
                # 支持多种音频格式
                for ext in ['.mp3', '.ogg', '.wav']:
                    potential_path = self.audio_dir / "music" / f"{music_name}{ext}"
                    if potential_path.exists():
                        file_path = potential_path
                        break

            if not file_path or not Path(file_path).exists():
                print(f"⚠️ 音乐文件不存在: {music_name}")
                return False

            self.music_cache[music_name] = str(file_path)
            print(f"🎵 音乐已加载: {music_name}")
            return True

        except Exception as e:
            print(f"❌ 加载音乐失败: {e}")
            return False

    def play_music(self, music_name: str, loops: int = -1, fade_in: float = 0.0):
        """播放背景音乐"""
        if not self.audio_enabled or not pygame:
            return False

        try:
            # 如果音乐未加载，尝试加载
            if music_name not in self.music_cache:
                if not self.load_music(music_name):
                    return False

            music_path = self.music_cache[music_name]

            # 停止当前音乐
            if self.music_playing:
                pygame.mixer.music.stop()

            # 加载并播放新音乐
            pygame.mixer.music.load(music_path)

            if fade_in > 0:
                pygame.mixer.music.play(loops, fade_ms=int(fade_in * 1000))
            else:
                pygame.mixer.music.play(loops)

            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

            self.current_music = music_name
            self.music_playing = True

            print(f"🎵 开始播放音乐: {music_name}")
            return True

        except Exception as e:
            print(f"❌ 播放音乐失败: {e}")
            return False

    def stop_music(self, fade_out: float = 0.0):
        """停止背景音乐"""
        if not self.audio_enabled or not pygame:
            return

        try:
            if fade_out > 0:
                pygame.mixer.music.fadeout(int(fade_out * 1000))
            else:
                pygame.mixer.music.stop()

            self.music_playing = False
            self.current_music = None

            print("🔇 音乐已停止")

        except Exception as e:
            print(f"❌ 停止音乐失败: {e}")

    def pause_music(self):
        """暂停音乐"""
        if not self.audio_enabled or not pygame:
            return

        try:
            pygame.mixer.music.pause()
            print("⏸️ 音乐已暂停")
        except Exception as e:
            print(f"❌ 暂停音乐失败: {e}")

    def resume_music(self):
        """恢复音乐"""
        if not self.audio_enabled or not pygame:
            return

        try:
            pygame.mixer.music.unpause()
            print("▶️ 音乐已恢复")
        except Exception as e:
            print(f"❌ 恢复音乐失败: {e}")

    def set_master_volume(self, volume: float):
        """设置主音量"""
        self.master_volume = max(0.0, min(1.0, volume))

        # 更新所有音效音量
        for sound in self.sound_cache.values():
            sound.set_volume(self.sfx_volume * self.master_volume)

        # 更新音乐音量
        if pygame and pygame.mixer:
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

        print(f"🔊 主音量设置为: {self.master_volume:.1%}")

    def set_sfx_volume(self, volume: float):
        """设置音效音量"""
        self.sfx_volume = max(0.0, min(1.0, volume))

        # 更新所有音效音量
        for sound in self.sound_cache.values():
            sound.set_volume(self.sfx_volume * self.master_volume)

        print(f"🎵 音效音量设置为: {self.sfx_volume:.1%}")

    def set_music_volume(self, volume: float):
        """设置音乐音量"""
        self.music_volume = max(0.0, min(1.0, volume))

        # 更新音乐音量
        if pygame and pygame.mixer:
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

        print(f"🎼 音乐音量设置为: {self.music_volume:.1%}")

    def toggle_sfx(self):
        """切换音效开关"""
        self.sfx_enabled = not self.sfx_enabled
        print(f"🎵 音效 {'开启' if self.sfx_enabled else '关闭'}")
        return self.sfx_enabled

    def get_audio_status(self) -> Dict[str, Any]:
        """获取音频状态"""
        return {
            "audio_enabled": self.audio_enabled,
            "master_volume": self.master_volume,
            "sfx_volume": self.sfx_volume,
            "music_volume": self.music_volume,
            "sfx_enabled": self.sfx_enabled,
            "music_playing": self.music_playing,
            "current_music": self.current_music,
            "loaded_sounds": list(self.sound_cache.keys()),
            "loaded_music": list(self.music_cache.keys())
        }

    def save_audio_config(self, config_file: str = None):
        """保存音频配置"""
        if config_file is None:
            config_file = self.audio_dir / "audio_config.json"

        config = {
            "master_volume": self.master_volume,
            "sfx_volume": self.sfx_volume,
            "music_volume": self.music_volume,
            "sfx_enabled": self.sfx_enabled,
            "sample_rate": self.sample_rate,
            "buffer_size": self.buffer_size,
            "channels": self.channels
        }

        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"💾 音频配置已保存: {config_file}")
        except Exception as e:
            print(f"❌ 保存音频配置失败: {e}")

    def load_audio_config(self, config_file: str = None):
        """加载音频配置"""
        if config_file is None:
            config_file = self.audio_dir / "audio_config.json"

        try:
            if Path(config_file).exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)

                self.master_volume = config.get("master_volume", 0.7)
                self.sfx_volume = config.get("sfx_volume", 0.8)
                self.music_volume = config.get("music_volume", 0.6)
                self.sfx_enabled = config.get("sfx_enabled", True)

                print(f"📂 音频配置已加载: {config_file}")
            else:
                print("⚠️ 音频配置文件不存在，使用默认配置")

        except Exception as e:
            print(f"❌ 加载音频配置失败: {e}")

    def cleanup(self):
        """清理音频资源"""
        try:
            if pygame and pygame.mixer:
                pygame.mixer.music.stop()
                pygame.mixer.stop()
                pygame.mixer.quit()

            self.sound_cache.clear()
            self.music_cache.clear()
            self.audio_thread_running = False

            print("🧹 音频资源已清理")

        except Exception as e:
            print(f"❌ 清理音频资源失败: {e}")

# 全局音频管理器实例
audio_manager = None


def get_audio_manager() -> AudioManager:
    """获取全局音频管理器实例"""
    global audio_manager
    if audio_manager is None:
        audio_manager = AudioManager()
    return audio_manager


def initialize_audio_system():
    """初始化音频系统"""
    manager = get_audio_manager()
    manager.load_audio_config()
    manager.create_default_sounds()

    # 加载默认音效
    default_sounds = ["beep", "select", "start", "error", "success"]
    for sound in default_sounds:
        manager.load_sound(sound)

    return manager

if __name__ == "__main__":
    # 测试音频系统
    print("🎵 测试音频系统...")

    manager = initialize_audio_system()

    # 测试音效
    print("🔊 测试音效...")
    manager.play_sound("beep")
    time.sleep(0.5)
    manager.play_sound("select")
    time.sleep(0.5)
    manager.play_sound("success")

    # 显示状态
    status = manager.get_audio_status()
    print(f"📊 音频状态: {status}")

    # 清理
    time.sleep(2)
    manager.cleanup()
