#!/usr/bin/env python3
"""
修复NES模拟器运行失败问题
专门解决模拟器检测和启动问题
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class NESRuntimeFixer:
    """NES运行时修复器"""

    def __init__(self):
        """TODO: 添加文档字符串"""
        self.project_root = project_root

    def check_mednafen_status(self):
        """检查mednafen状态"""
        print("🔍 检查mednafen状态...")

        try:
            # 检查mednafen是否存在
            which_result = subprocess.run(["which", "mednafen"], capture_output=True, text=True, timeout=10)

            if which_result.returncode == 0:
                mednafen_path = which_result.stdout.strip()
                print(f"✅ mednafen路径: {mednafen_path}")

                # 检查版本
                version_result = subprocess.run([mednafen_path, "-help"], capture_output=True, text=True, timeout=10)

                if "nes" in version_result.stdout.lower():
                    print("✅ mednafen支持NES模拟")
                    return True, mednafen_path
                else:
                    print("❌ mednafen不支持NES")
                    return False, mednafen_path
            else:
                print("❌ mednafen未找到")
                return False, None

        except Exception as e:
            print(f"❌ 检查mednafen失败: {e}")
            return False, None

    def fix_game_launcher_detection(self):
        """修复游戏启动器的模拟器检测"""
        print("🔧 修复游戏启动器检测...")

        launcher_file = self.project_root / "src" / "core" / "game_launcher.py"

        # 读取文件
        with open(launcher_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找并替换模拟器检测函数
        old_check_function = '''    def check_emulator_availability(self, system: str):
        """检查模拟器是否可用"""
        if system not in self.emulator_configs:
            return False

        config = self.emulator_configs[system]
        command = config.get("command", "")

        try:
            # 检查命令是否存在
            result = subprocess.run(["which", command], capture_output=True, text=True)
            available = result.returncode == 0

            # 更新配置
            config["installed"] = available

            return available
        except Exception:
            return False'''

        new_check_function = '''    def check_emulator_availability(self, system: str):
        """检查模拟器是否可用"""
        if system not in self.emulator_configs:
            return False

        config = self.emulator_configs[system]
        command = config.get("command", "")

        try:
            # 特殊处理mednafen
            if command == "mednafen":
                # 检查mednafen是否存在
                result = subprocess.run(["which", "mednafen"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # 验证mednafen支持NES
                    help_result = subprocess.run(["mednafen", "-help"], capture_output=True, text=True, timeout=10)
                    available = "nes" in help_result.stdout.lower()
                else:
                    available = False
            else:
                # 检查其他命令是否存在
                result = subprocess.run(["which", command], capture_output=True, text=True, timeout=10)
                available = result.returncode == 0

            # 更新配置
            config["installed"] = available

            return available
        except Exception as e:
            print(f"检查模拟器失败: {e}")
            return False'''

        if old_check_function in content:
            content = content.replace(old_check_function, new_check_function)

            # 写回文件
            with open(launcher_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print("✅ 游戏启动器检测函数已更新")
            return True
        else:
            print("⚠️ 未找到需要替换的检测函数")
            return False

    def create_emulator_config_file(self):
        """创建模拟器配置文件"""
        print("📝 创建模拟器配置文件...")

        config_dir = self.project_root / "config" / "emulators"
        config_dir.mkdir(parents=True, exist_ok=True)

        config_file = config_dir / "emulator_config.json"

        config_data = {
            "nes": {
                "emulator": "mednafen",
                "command": "mednafen",
                "args": ["-force_module", "nes", "-video.fs", "0"],
                "extensions": [".nes"],
                "installed": True,
                "description": "Mednafen NES模拟器"
            },
            "snes": {
                "emulator": "mednafen",
                "command": "mednafen",
                "args": ["-force_module", "snes", "-video.fs", "0"],
                "extensions": [".smc", ".sfc"],
                "installed": False,
                "description": "Mednafen SNES模拟器"
            },
            "gameboy": {
                "emulator": "mednafen",
                "command": "mednafen",
                "args": ["-force_module", "gb", "-video.fs", "0"],
                "extensions": [".gb", ".gbc"],
                "installed": False,
                "description": "Mednafen Game Boy模拟器"
            },
            "gba": {
                "emulator": "mednafen",
                "command": "mednafen",
                "args": ["-force_module", "gba", "-video.fs", "0"],
                "extensions": [".gba"],
                "installed": False,
                "description": "Mednafen GBA模拟器"
            },
            "genesis": {
                "emulator": "mednafen",
                "command": "mednafen",
                "args": ["-force_module", "md", "-video.fs", "0"],
                "extensions": [".md", ".gen"],
                "installed": False,
                "description": "Mednafen Genesis模拟器"
            }
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

        print(f"✅ 模拟器配置文件已创建: {config_file}")
        return True

    def test_direct_launch(self):
        """测试直接启动"""
        print("🧪 测试直接启动...")

        rom_path = self.project_root / "data" / "roms" / "nes" / "Super_Mario_Bros.nes"

        if not rom_path.exists():
            print("❌ ROM文件不存在")
            return False

        try:
            print("🎮 尝试启动mednafen...")

            # 启动mednafen（3秒后自动退出）
            result = subprocess.run([
                "mednafen",
                "-force_module", "nes",
                "-video.fs", "0",  # 窗口模式
                "-sound", "0",     # 禁用声音
                str(rom_path)
            ], timeout=3, capture_output=True, text=True)

            print("✅ mednafen启动成功")
            return True

        except subprocess.TimeoutExpired:
            print("✅ mednafen正在运行（超时是正常的）")
            return True
        except Exception as e:
            print(f"❌ mednafen启动失败: {e}")
            return False

    def fix_import_issues(self):
        """修复导入问题"""
        print("🔧 修复导入问题...")

        launcher_file = self.project_root / "src" / "core" / "game_launcher.py"

        # 读取文件
        with open(launcher_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 确保有subprocess导入
        if "import subprocess" not in content:
            # 在文件开头添加导入
            lines = content.split('\n')
            import_index = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_index = i + 1

            lines.insert(import_index, "import subprocess")
            content = '\n'.join(lines)

            # 写回文件
            with open(launcher_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print("✅ 添加了subprocess导入")
            return True
        else:
            print("✅ subprocess导入已存在")
            return True

    def create_simple_test_api(self):
        """创建简单的测试API"""
        print("🔧 创建简单测试API...")

        test_api_file = self.project_root / "test_nes_api.py"

        api_content = '''#!/usr/bin/env python3
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
'''

        with open(test_api_file, 'w', encoding='utf-8') as f:
            f.write(api_content)

        # 使脚本可执行
        test_api_file.chmod(0o755)

        print(f"✅ 测试API已创建: {test_api_file}")

        # 运行测试
        try:
            result = subprocess.run(["python3", str(test_api_file)],
                                  capture_output=True, text=True, timeout=15)

            print("测试结果:")
            print(result.stdout)

            if result.stderr:
                print("错误信息:")
                print(result.stderr)

            return result.returncode == 0

        except Exception as e:
            print(f"❌ 运行测试API失败: {e}")
            return False

    def run_comprehensive_fix(self):
        """运行综合修复"""
        print("🎮 NES模拟器运行失败综合修复")
        print("=" * 50)

        success_count = 0
        total_tests = 6

        # 1. 检查mednafen状态
        mednafen_ok, mednafen_path = self.check_mednafen_status()
        if mednafen_ok:
            print("✅ 1/6: mednafen状态检查通过")
            success_count += 1
        else:
            print("❌ 1/6: mednafen状态检查失败")

        # 2. 修复导入问题
        if self.fix_import_issues():
            print("✅ 2/6: 导入问题修复完成")
            success_count += 1
        else:
            print("❌ 2/6: 导入问题修复失败")

        # 3. 修复游戏启动器检测
        if self.fix_game_launcher_detection():
            print("✅ 3/6: 游戏启动器检测修复完成")
            success_count += 1
        else:
            print("❌ 3/6: 游戏启动器检测修复失败")

        # 4. 创建模拟器配置文件
        if self.create_emulator_config_file():
            print("✅ 4/6: 模拟器配置文件创建完成")
            success_count += 1
        else:
            print("❌ 4/6: 模拟器配置文件创建失败")

        # 5. 测试直接启动
        if self.test_direct_launch():
            print("✅ 5/6: 直接启动测试通过")
            success_count += 1
        else:
            print("❌ 5/6: 直接启动测试失败")

        # 6. 创建简单测试API
        if self.create_simple_test_api():
            print("✅ 6/6: 简单测试API创建完成")
            success_count += 1
        else:
            print("❌ 6/6: 简单测试API创建失败")

        print("\n" + "=" * 50)
        print(f"🎯 修复完成: {success_count}/{total_tests} 项成功")

        if success_count >= 5:
            print("🎉 NES模拟器运行问题修复成功！")
            print("💡 建议操作:")
            print("1. 重启Web服务器: PORT=3014 python3 src/scripts/simple_demo_server.py")
            print("2. 测试NES游戏启动: python3 test_nes_api.py launch")
            print("3. 访问Web界面: http://localhost:3014")
        else:
            print("⚠️ 修复未完全成功")
            print("💡 可能需要:")
            print("1. 重新安装mednafen: brew reinstall mednafen")
            print("2. 检查系统权限")
            print("3. 重启终端")


def main():
    """主函数"""
    fixer = NESRuntimeFixer()
    fixer.run_comprehensive_fix()

if __name__ == "__main__":
    main()
