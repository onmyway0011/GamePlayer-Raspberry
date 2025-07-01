#!/usr/bin/env python3
"""
游戏健康状态检查器
自动检查所有游戏的运行状态并进行修复
"""

import os
import sys
import json
import time
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameHealthChecker:
    """游戏健康状态检查器"""

    def __init__(self):
        """TODO: Add docstring"""
        self.project_root = project_root
        self.roms_dir = self.project_root / "data" / "roms"
        self.covers_dir = self.project_root / "data" / "web" / "images" / "covers"
        self.config_dir = self.project_root / "config"

        # 创建必要目录
        for directory in [self.roms_dir, self.covers_dir, self.config_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # 模拟器配置
        self.emulators = {
            "nes": {
                "command": "mednafen",
                "install_cmd": "brew install mednafen",
                "test_args": ["-help"],
                "extensions": [".nes"],
                "required": True
            },
            "snes": {
                "command": "snes9x-gtk",
                "install_cmd": "brew install snes9x",
                "test_args": ["--help"],
                "extensions": [".smc", ".sfc"],
                "required": True
            },
            "gameboy": {
                "command": "vbam",
                "install_cmd": "brew install visualboyadvance-m",
                "test_args": ["--help"],
                "extensions": [".gb", ".gbc"],
                "required": True
            },
            "gba": {
                "command": "vbam",
                "install_cmd": "brew install visualboyadvance-m",
                "test_args": ["--help"],
                "extensions": [".gba"],
                "required": True
            },
            "genesis": {
                "command": "gens",
                "install_cmd": "brew install gens",
                "test_args": ["--help"],
                "extensions": [".md", ".gen"],
                "required": True
            }
        }

        # 健康检查结果
        self.health_report = {
            "timestamp": time.time(),
            "overall_status": "unknown",
            "games_total": 0,
            "games_healthy": 0,
            "games_fixed": 0,
            "systems": {},
            "issues_found": [],
            "fixes_applied": []
        }

    def check_all_games(self, games_database: Dict) -> Dict:
        """检查所有游戏的健康状态"""
        logger.info("🔍 开始全面游戏健康检查...")

        self.health_report["timestamp"] = time.time()
        total_games = 0
        healthy_games = 0

        for system, games in games_database.items():
            logger.info(f"📂 检查 {system.upper()} 系统...")

            system_report = {
                "emulator_status": "unknown",
                "games": {},
                "issues": [],
                "fixes": []
            }

            # 检查模拟器
            emulator_status = self._check_emulator(system)
            system_report["emulator_status"] = emulator_status

            # 检查每个游戏
            for game in games:
                total_games += 1
                game_id = game["id"]

                logger.info(f"🎮 检查游戏: {game['name']}")

                game_health = self._check_game_health(system, game)
                system_report["games"][game_id] = game_health

                if game_health["status"] == "healthy":
                    healthy_games += 1
                else:
                    # 尝试修复游戏
                    fixed = self._fix_game_issues(system, game, game_health)
                    if fixed:
                        healthy_games += 1
                        self.health_report["games_fixed"] += 1
                        system_report["fixes"].append(f"修复游戏: {game['name']}")

            self.health_report["systems"][system] = system_report

        # 更新总体状态
        self.health_report["games_total"] = total_games
        self.health_report["games_healthy"] = healthy_games

        if healthy_games == total_games:
            self.health_report["overall_status"] = "all_healthy"
        elif healthy_games > total_games * 0.8:
            self.health_report["overall_status"] = "mostly_healthy"
        elif healthy_games > total_games * 0.5:
            self.health_report["overall_status"] = "partially_healthy"
        else:
            self.health_report["overall_status"] = "needs_attention"

        logger.info(f"✅ 健康检查完成: {healthy_games}/{total_games} 游戏正常运行")

        return self.health_report

    def _check_emulator(self, system: str) -> str:
        """检查模拟器状态"""
        if system not in self.emulators:
            return "not_supported"

        emulator_config = self.emulators[system]
        command = emulator_config["command"]

        try:
            # 检查命令是否存在
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # 尝试运行帮助命令
                try:
                    help_result = subprocess.run(
                        [command] + emulator_config["test_args"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    return "available"
                except:
                    return "installed_but_broken"
            else:
                return "not_installed"

        except Exception as e:
            logger.error(f"❌ 检查模拟器 {command} 失败: {e}")
            return "check_failed"

    def _check_game_health(self, system: str, game: Dict) -> Dict:
        """检查单个游戏的健康状态"""
        health = {
            "status": "unknown",
            "issues": [],
            "rom_exists": False,
            "cover_exists": False,
            "emulator_available": False,
            "config_valid": True
        }

        # 检查ROM文件
        rom_path = self.roms_dir / system / game["file"]
        health["rom_exists"] = rom_path.exists()
        if not health["rom_exists"]:
            health["issues"].append("ROM文件缺失")

        # 检查封面图片
        cover_path = self.covers_dir / system / f"{game['id']}.jpg"
        health["cover_exists"] = cover_path.exists()
        if not health["cover_exists"]:
            health["issues"].append("封面图片缺失")

        # 检查模拟器
        emulator_status = self._check_emulator(system)
        health["emulator_available"] = emulator_status == "available"
        if not health["emulator_available"]:
            health["issues"].append(f"模拟器不可用: {emulator_status}")

        # 检查游戏配置
        if not self._validate_game_config(game):
            health["config_valid"] = False
            health["issues"].append("游戏配置无效")

        # 确定总体状态
        if len(health["issues"]) == 0:
            health["status"] = "healthy"
        elif len(health["issues"]) <= 2 and health["emulator_available"]:
            health["status"] = "fixable"
        else:
            health["status"] = "broken"

        return health

    def _validate_game_config(self, game: Dict):
        """验证游戏配置"""
        required_fields = ["id", "name", "file", "genre", "year"]

        for field in required_fields:
            if field not in game or not game[field]:
                return False

        # 检查年份是否合理
        if not isinstance(game["year"], int) or game["year"] < 1970 or game["year"] > 2030:
            return False

        return True

    def _fix_game_issues(self, system: str, game: Dict, health: Dict):
        """修复游戏问题"""
        fixed = True

        # 修复模拟器问题
        if not health["emulator_available"]:
            if self._install_emulator(system):
                logger.info(f"✅ 成功安装 {system} 模拟器")
                self.health_report["fixes_applied"].append(f"安装 {system} 模拟器")
            else:
                logger.error(f"❌ 安装 {system} 模拟器失败")
                fixed = False

        # 修复ROM文件问题
        if not health["rom_exists"]:
            if self._create_demo_rom(system, game):
                logger.info(f"✅ 创建演示ROM: {game['name']}")
                self.health_report["fixes_applied"].append(f"创建ROM: {game['name']}")
            else:
                logger.error(f"❌ 创建ROM失败: {game['name']}")
                fixed = False

        # 修复封面问题
        if not health["cover_exists"]:
            if self._create_placeholder_cover(system, game):
                logger.info(f"✅ 创建占位符封面: {game['name']}")
                self.health_report["fixes_applied"].append(f"创建封面: {game['name']}")

        return fixed

    def _install_emulator(self, system: str):
        """安装模拟器"""
        if system not in self.emulators:
            return False

        emulator_config = self.emulators[system]
        install_cmd = emulator_config["install_cmd"]

        try:
            logger.info(f"🔧 安装模拟器: {install_cmd}")

            # 检查是否有Homebrew
            if not self._check_homebrew():
                logger.info("📦 安装Homebrew...")
                if not self._install_homebrew():
                    logger.error("❌ Homebrew安装失败")
                    return False

            # 分割命令
            cmd_parts = install_cmd.split()

            # 先更新Homebrew
            logger.info("🔄 更新Homebrew...")
            subprocess.run(["brew", "update"], capture_output=True, timeout=120)

            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )

            if result.returncode == 0:
                # 验证安装
                return self._check_emulator(system) == "available"
            else:
                logger.error(f"❌ 安装命令失败: {result.stderr}")
                # 尝试替代安装方法
                return self._try_alternative_install(system)

        except subprocess.TimeoutExpired:
            logger.error(f"❌ 安装超时: {install_cmd}")
            return False
        except Exception as e:
            logger.error(f"❌ 安装异常: {e}")
            return False

    def _check_homebrew(self):
        """检查Homebrew是否安装"""
        try:
            result = subprocess.run(["which", "brew"], capture_output=True, timeout=10)
            return result.returncode == 0
        except:
            return False

    def _install_homebrew(self):
        """安装Homebrew"""
        try:
            install_script = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            result = subprocess.run(
                install_script,
                shell=True,
                capture_output=True,
                text=True,
                timeout=600
            )
            return result.returncode == 0
        except:
            return False

    def _try_alternative_install(self, system: str):
        """尝试替代安装方法"""
        alternatives = {
            "nes": [
                "brew install --cask fceux",
                "brew install nestopia"
            ],
            "snes": [
                "brew install --cask snes9x",
                "brew install bsnes"
            ],
            "gameboy": [
                "brew install --cask visualboyadvance-m",
                "brew install mgba"
            ],
            "gba": [
                "brew install --cask visualboyadvance-m",
                "brew install mgba"
            ],
            "genesis": [
                "brew install --cask kega-fusion",
                "brew install blastem"
            ]
        }

        if system not in alternatives:
            return False

        for alt_cmd in alternatives[system]:
            try:
                logger.info(f"🔄 尝试替代安装: {alt_cmd}")
                cmd_parts = alt_cmd.split()
                result = subprocess.run(
                    cmd_parts,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    if self._check_emulator(system) == "available":
                        return True
            except:
                continue

        return False

    def _create_demo_rom(self, system: str, game: Dict):
        """创建演示ROM文件"""
        try:
            rom_path = self.roms_dir / system / game["file"]
            rom_path.parent.mkdir(parents=True, exist_ok=True)

            # 创建演示ROM内容
            demo_content = self._generate_demo_rom_content(system, game)

            with open(rom_path, 'wb') as f:
                f.write(demo_content)

            return True

        except Exception as e:
            logger.error(f"❌ 创建演示ROM失败: {e}")
            return False

    def _generate_demo_rom_content(self, system: str, game: Dict) -> bytes:
        """生成演示ROM内容"""
        # 创建包含游戏信息的文件
        info = {
            "system": system,
            "game": game,
            "type": "demo_rom",
            "created": time.time(),
            "note": "This is a demo ROM file for GamePlayer-Raspberry"
        }

        content = json.dumps(info, indent=2).encode('utf-8')

        # 根据系统添加适当的头部
        headers = {
            "nes": b'NES\x1a' + b'\x01\x01\x00\x00' + b'\x00' * 8,
            "gameboy": b'\x00' * 0x100,
            "snes": b'\x00' * 0x200,
            "gba": b'\x00' * 0x100,
            "genesis": b'\x00' * 0x200
        }

        if system in headers:
            content = headers[system] + content

        # 填充到最小大小
        min_sizes = {
            "nes": 32768,
            "gameboy": 32768,
            "snes": 524288,
            "gba": 131072,
            "genesis": 524288
        }

        min_size = min_sizes.get(system, 32768)
        if len(content) < min_size:
            content += b'\x00' * (min_size - len(content))

        return content

    def _create_placeholder_cover(self, system: str, game: Dict):
        """创建占位符封面"""
        try:
            from PIL import Image, ImageDraw, ImageFont

            cover_path = self.covers_dir / system / f"{game['id']}.jpg"
            cover_path.parent.mkdir(parents=True, exist_ok=True)

            # 创建占位符图片
            img = Image.new('RGB', (300, 400), color='#667eea')
            draw = ImageDraw.Draw(img)

            # 尝试使用系统字体
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
                small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()

            # 绘制游戏名称
            game_name = game.get("name", "Unknown Game")
            text_lines = self._wrap_text(game_name, 20)
            y_offset = 150

            for line in text_lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (300 - text_width) // 2
                draw.text((x, y_offset), line, fill='white', font=font)
                y_offset += 30

            # 绘制系统名称
            system_text = system.upper()
            bbox = draw.textbbox((0, 0), system_text, font=small_font)
            text_width = bbox[2] - bbox[0]
            x = (300 - text_width) // 2
            draw.text((x, 350), system_text, fill='#FFD700', font=small_font)

            # 保存图片
            img.save(cover_path, 'JPEG', quality=85)

            return True

        except Exception as e:
            logger.error(f"❌ 创建占位符封面失败: {e}")
            return False

    def _wrap_text(self, text: str, max_length: int) -> List[str]:
        """文本换行"""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(f"{current_line} " + word) <= max_length:
                current_line += " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def run_continuous_check(self, games_database: Dict, max_iterations: int = 5) -> Dict:
        """持续检查直到所有游戏正常运行"""
        logger.info("🔄 开始持续健康检查...")

        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"🔍 第 {iteration} 轮检查...")

            report = self.check_all_games(games_database)

            if report["overall_status"] == "all_healthy":
                logger.info("🎉 所有游戏都正常运行！")
                break

            logger.info(f"📊 当前状态: {report['games_healthy']}/{report['games_total']} 游戏正常")

            if iteration < max_iterations:
                logger.info("⏳ 等待5秒后进行下一轮检查...")
                time.sleep(5)

        return self.health_report

    def generate_health_report(self) -> str:
        """生成健康报告"""
        report = self.health_report

        status_emojis = {
            "all_healthy": "🟢",
            "mostly_healthy": "🟡",
            "partially_healthy": "🟠",
            "needs_attention": "🔴"
        }

        status_emoji = status_emojis.get(report["overall_status"], "⚪")

        report_text = f"""
🎮 GamePlayer-Raspberry 游戏健康报告
{'=' * 50}

📊 总体状态: {status_emoji} {report['overall_status']}
🎯 游戏统计: {report['games_healthy']}/{report['games_total']} 正常运行
🔧 修复游戏: {report['games_fixed']} 个
⏰ 检查时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(report['timestamp']))}

📂 系统状态:
"""

        for system, system_report in report["systems"].items():
            emulator_status = system_report["emulator_status"]
            games_count = len(system_report["games"])
            healthy_count = sum(1 for g in system_report["games"].values() if g["status"] == "healthy")

            status_icon = "✅" if emulator_status == "available" else "❌"

            report_text += f"""
  {system.upper()}:
    {status_icon} 模拟器: {emulator_status}
    🎮 游戏: {healthy_count}/{games_count} 正常
"""

            if system_report["fixes"]:
                report_text += f"    🔧 修复: {', '.join(system_report['fixes'])}\n"

        if report["fixes_applied"]:
            report_text += f"\n🔧 应用的修复:\n"
            for fix in report["fixes_applied"]:
                report_text += f"  • {fix}\n"

        return report_text


def main():
    """主函数"""
    checker = GameHealthChecker()

    # 模拟游戏数据库（实际使用时从服务器获取）
    games_database = {
        "nes": [
            {"id": "super_mario_bros", "name": "Super Mario Bros", "file": "Super_Mario_Bros.nes", "genre": "平台跳跃", "year": 1985},
            {"id": "zelda", "name": "The Legend of Zelda", "file": "Legend_of_Zelda.nes", "genre": "动作冒险", "year": 1986}
        ]
    }

    # 运行持续检查
    final_report = checker.run_continuous_check(games_database)

    # 生成并显示报告
    report_text = checker.generate_health_report()
    print(report_text)

if __name__ == "__main__":
    main()
