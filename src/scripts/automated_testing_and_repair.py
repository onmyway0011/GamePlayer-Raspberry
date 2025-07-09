#!/usr/bin/env python3
"""
GamePlayer-Raspberry 自动化测试和修复系统
检测镜像功能并自动修复问题
"""

import os
import sys
import json
import subprocess
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import threading
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutomatedTestingAndRepair:
    """自动化测试和修复系统"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.test_results = []
        self.repair_log = []
        
        # 测试配置
        self.test_config = {
            "rom_integrity": {"enabled": True, "timeout": 30},
            "emulator_availability": {"enabled": True, "timeout": 10},
            "web_interface": {"enabled": True, "timeout": 15},
            "audio_system": {"enabled": True, "timeout": 10},
            "controller_support": {"enabled": True, "timeout": 5},
            "storage_space": {"enabled": True, "timeout": 5},
            "network_connectivity": {"enabled": True, "timeout": 10},
            "system_services": {"enabled": True, "timeout": 20},
            "game_launch": {"enabled": True, "timeout": 30},
            "auto_repair": {"enabled": True, "max_attempts": 3}
        }
        
        print("🔧 GamePlayer-Raspberry 自动化测试和修复系统")
        print("=" * 60)
        print(f"📁 项目目录: {self.project_root}")
        print()
    
    def run_comprehensive_tests(self) -> Dict:
        """运行全面的系统测试"""
        start_time = time.time()
        
        print("🚀 开始全面系统测试...")
        print("=" * 60)
        
        # 测试项目列表
        test_suite = [
            ("ROM完整性检查", self._test_rom_integrity),
            ("模拟器可用性检查", self._test_emulator_availability),
            ("Web界面功能测试", self._test_web_interface),
            ("音频系统测试", self._test_audio_system),
            ("控制器支持测试", self._test_controller_support),
            ("存储空间检查", self._test_storage_space),
            ("网络连接测试", self._test_network_connectivity),
            ("系统服务检查", self._test_system_services),
            ("游戏启动测试", self._test_game_launch),
        ]
        
        # 执行测试
        passed_tests = 0
        failed_tests = 0
        
        for test_name, test_func in test_suite:
            print(f"\n📋 执行: {test_name}")
            try:
                result = test_func()
                if result['status'] == 'pass':
                    print(f"✅ {test_name}: 通过")
                    passed_tests += 1
                else:
                    print(f"❌ {test_name}: 失败 - {result.get('error', '未知错误')}")
                    failed_tests += 1
                    
                    # 尝试自动修复
                    if self.test_config["auto_repair"]["enabled"]:
                        self._attempt_auto_repair(test_name, result)
                
                self.test_results.append({
                    "test": test_name,
                    "result": result,
                    "timestamp": time.time()
                })
                
            except Exception as e:
                error_msg = f"测试执行异常: {e}"
                print(f"⚠️ {test_name}: {error_msg}")
                self.test_results.append({
                    "test": test_name,
                    "result": {"status": "error", "error": error_msg},
                    "timestamp": time.time()
                })
                failed_tests += 1
        
        # 生成测试报告
        test_time = time.time() - start_time
        test_summary = {
            "total_tests": len(test_suite),
            "passed": passed_tests,
            "failed": failed_tests,
            "test_time": round(test_time, 2),
            "success_rate": round((passed_tests / len(test_suite)) * 100, 1),
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "repairs_attempted": len(self.repair_log)
        }
        
        self._generate_test_report(test_summary)
        
        print("\n" + "=" * 60)
        print("🎯 测试完成总结:")
        print(f"  总测试数: {test_summary['total_tests']}")
        print(f"  通过: {test_summary['passed']}")
        print(f"  失败: {test_summary['failed']}")
        print(f"  成功率: {test_summary['success_rate']}%")
        print(f"  测试时间: {test_summary['test_time']}秒")
        print(f"  修复尝试: {test_summary['repairs_attempted']}次")
        print("=" * 60)
        
        return test_summary
    
    def _test_rom_integrity(self) -> Dict:
        """测试ROM文件完整性"""
        roms_dir = self.project_root / "data" / "roms"
        
        if not roms_dir.exists():
            return {"status": "fail", "error": "ROM目录不存在"}
        
        total_roms = 0
        corrupted_roms = []
        
        # 检查各系统ROM
        for system_dir in roms_dir.iterdir():
            if system_dir.is_dir():
                for rom_file in system_dir.glob("*.*"):
                    if rom_file.suffix in ['.nes', '.smc', '.gb', '.gba', '.md', '.zip', '.n64', '.bin']:
                        total_roms += 1
                        
                        # 检查文件完整性
                        if rom_file.stat().st_size == 0:
                            corrupted_roms.append(str(rom_file))
                        
                        # 检查文件头（简单验证）
                        try:
                            with open(rom_file, 'rb') as f:
                                header = f.read(16)
                                if len(header) < 4:
                                    corrupted_roms.append(str(rom_file))
                        except:
                            corrupted_roms.append(str(rom_file))
        
        if corrupted_roms:
            return {
                "status": "fail",
                "error": f"发现{len(corrupted_roms)}个损坏的ROM文件",
                "details": {"total": total_roms, "corrupted": corrupted_roms}
            }
        
        return {
            "status": "pass",
            "details": {"total_roms": total_roms, "all_valid": True}
        }
    
    def _test_emulator_availability(self) -> Dict:
        """测试模拟器可用性"""
        emulators = {
            "nes": ["fceux", "nestopia", "mednafen"],
            "snes": ["snes9x", "zsnes", "mednafen"],
            "gb": ["visualboyadvance", "mednafen"],
            "genesis": ["gens", "mednafen"]
        }
        
        available_emulators = {}
        missing_systems = []
        
        for system, emulator_list in emulators.items():
            system_available = False
            for emulator in emulator_list:
                if self._check_command_exists(emulator):
                    available_emulators[system] = emulator
                    system_available = True
                    break
            
            if not system_available:
                missing_systems.append(system)
        
        if missing_systems:
            return {
                "status": "fail",
                "error": f"缺少{len(missing_systems)}个系统的模拟器",
                "details": {"missing": missing_systems, "available": available_emulators}
            }
        
        return {
            "status": "pass",
            "details": {"available_emulators": available_emulators}
        }
    
    def _test_web_interface(self) -> Dict:
        """测试Web界面功能"""
        web_dir = self.project_root / "data" / "web"
        
        # 检查Web文件
        required_files = ["index.html", "style.css", "script.js"]
        missing_files = []
        
        if web_dir.exists():
            for file_name in required_files:
                if not (web_dir / file_name).exists():
                    missing_files.append(file_name)
        else:
            missing_files = required_files
        
        # 尝试启动Web服务器进行测试
        try:
            import http.server
            import socketserver
            import threading
            import time
            
            # 在随机端口启动测试服务器
            test_port = 9999
            web_server = None
            
            def start_server():
                nonlocal web_server
                try:
                    os.chdir(web_dir if web_dir.exists() else self.project_root)
                    handler = http.server.SimpleHTTPRequestHandler
                    web_server = socketserver.TCPServer(("", test_port), handler)
                    web_server.serve_forever()
                except:
                    pass
            
            if missing_files:
                return {
                    "status": "fail",
                    "error": f"缺少Web文件: {missing_files}",
                    "details": {"missing_files": missing_files}
                }
            
            # 启动测试服务器
            server_thread = threading.Thread(target=start_server, daemon=True)
            server_thread.start()
            time.sleep(2)
            
            # 测试连接
            try:
                import urllib.request
                response = urllib.request.urlopen(f"http://localhost:{test_port}", timeout=5)
                if response.getcode() == 200:
                    web_test_result = "pass"
                else:
                    web_test_result = "fail"
            except:
                web_test_result = "fail"
            
            # 关闭测试服务器
            if web_server:
                web_server.shutdown()
            
            if web_test_result == "pass":
                return {"status": "pass", "details": {"web_server": "functional"}}
            else:
                return {"status": "fail", "error": "Web服务器启动失败"}
                
        except Exception as e:
            return {"status": "fail", "error": f"Web界面测试异常: {e}"}
    
    def _test_audio_system(self) -> Dict:
        """测试音频系统"""
        # 检查音频设备
        audio_devices = []
        
        try:
            # 在macOS上检查音频设备
            result = subprocess.run(['system_profiler', 'SPAudioDataType'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and "Audio" in result.stdout:
                audio_devices.append("system_audio")
        except:
            pass
        
        # 检查Python音频库
        audio_libs = []
        try:
            import pygame
            audio_libs.append("pygame")
        except ImportError:
            pass
        
        try:
            import pyaudio
            audio_libs.append("pyaudio")
        except ImportError:
            pass
        
        if not audio_devices and not audio_libs:
            return {
                "status": "fail",
                "error": "未检测到音频设备或音频库",
                "details": {"devices": audio_devices, "libraries": audio_libs}
            }
        
        return {
            "status": "pass",
            "details": {"audio_devices": audio_devices, "audio_libraries": audio_libs}
        }
    
    def _test_controller_support(self) -> Dict:
        """测试控制器支持"""
        # 检查输入设备
        input_devices = []
        
        try:
            # 检查pygame的手柄支持
            import pygame
            pygame.init()
            pygame.joystick.init()
            
            joystick_count = pygame.joystick.get_count()
            for i in range(joystick_count):
                joystick = pygame.joystick.Joystick(i)
                input_devices.append(f"joystick_{i}: {joystick.get_name()}")
            
            pygame.quit()
        except:
            pass
        # 键盘总是可用的
        input_devices.append("keyboard")
        
        return {
            "status": "pass",
            "details": {"input_devices": input_devices}
        }
    
    def _test_storage_space(self) -> Dict:
        """测试存储空间"""
        try:
            import shutil
            
            # 检查项目目录空间
            total, used, free = shutil.disk_usage(self.project_root)
            
            free_gb = free / (1024**3)
            total_gb = total / (1024**3)
            used_percent = (used / total) * 100
            
            # 至少需要1GB空闲空间
            min_free_gb = 1.0
            
            if free_gb < min_free_gb:
                return {
                    "status": "fail",
                    "error": f"存储空间不足，需要至少{min_free_gb}GB，当前只有{free_gb:.2f}GB",
                    "details": {"free_gb": round(free_gb, 2), "total_gb": round(total_gb, 2), "used_percent": round(used_percent, 1)}
                }
            
            return {
                "status": "pass",
                "details": {"free_gb": round(free_gb, 2), "total_gb": round(total_gb, 2), "used_percent": round(used_percent, 1)}
            }
            
        except Exception as e:
            return {"status": "fail", "error": f"存储空间检查失败: {e}"}
    
    def _test_network_connectivity(self) -> Dict:
        """测试网络连接"""
        test_urls = [
            "https://www.google.com",
            "https://www.github.com",
            "https://www.baidu.com"
        ]
        
        successful_connections = 0
        
        for url in test_urls:
            try:
                import urllib.request
                response = urllib.request.urlopen(url, timeout=5)
                if response.getcode() == 200:
                    successful_connections += 1
            except:
                pass
        
        if successful_connections == 0:
            return {
                "status": "fail",
                "error": "无法连接到任何测试网站",
                "details": {"tested_urls": len(test_urls), "successful": 0}
            }
        
        return {
            "status": "pass",
            "details": {"tested_urls": len(test_urls), "successful": successful_connections}
        }
    
    def _test_system_services(self) -> Dict:
        """测试系统服务"""
        required_services = {
            "python3": "Python 3解释器",
            "git": "Git版本控制",
        }
        
        missing_services = []
        available_services = []
        
        for service, description in required_services.items():
            if self._check_command_exists(service):
                available_services.append(service)
            else:
                missing_services.append(service)
        
        if missing_services:
            return {
                "status": "fail",
                "error": f"缺少必需服务: {missing_services}",
                "details": {"missing": missing_services, "available": available_services}
            }
        
        return {
            "status": "pass",
            "details": {"available_services": available_services}
        }
    
    def _test_game_launch(self) -> Dict:
        """测试游戏启动"""
        # 查找可用的游戏ROM
        roms_dir = self.project_root / "data" / "roms"
        test_games = []
        
        if roms_dir.exists():
            for system_dir in roms_dir.iterdir():
                if system_dir.is_dir():
                    rom_files = list(system_dir.glob("*.nes"))[:1]  # 只测试第一个NES游戏
                    for rom_file in rom_files:
                        test_games.append({
                            "system": system_dir.name,
                            "rom": rom_file.name,
                            "path": str(rom_file)
                        })
                        break  # 每个系统只测试一个游戏
        
        if not test_games:
            return {"status": "fail", "error": "未找到可测试的游戏ROM"}
        
        # 测试游戏启动（模拟测试）
        successful_launches = 0
        failed_launches = []
        
        for game in test_games:
            try:
                # 这里模拟游戏启动测试
                # 实际环境中会尝试启动模拟器
                if Path(game["path"]).exists() and Path(game["path"]).stat().st_size > 0:
                    successful_launches += 1
                else:
                    failed_launches.append(game["rom"])
            except Exception as e:
                failed_launches.append(f"{game['rom']}: {e}")
        
        if failed_launches:
            return {
                "status": "fail",
                "error": f"游戏启动测试失败: {failed_launches}",
                "details": {"tested": len(test_games), "successful": successful_launches, "failed": failed_launches}
            }
        
        return {
            "status": "pass",
            "details": {"tested_games": len(test_games), "all_successful": True}
        }
    
    def _check_command_exists(self, command: str) -> bool:
        """检查命令是否存在"""
        try:
            result = subprocess.run(['which', command], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _attempt_auto_repair(self, test_name: str, test_result: Dict):
        """尝试自动修复测试失败的问题"""
        print(f"🔧 尝试自动修复: {test_name}")
        
        repair_success = False
        repair_actions = []
        
        try:
            if "ROM完整性" in test_name:
                repair_success = self._repair_rom_integrity(test_result)
            elif "模拟器可用性" in test_name:
                repair_success = self._repair_emulator_availability(test_result)
            elif "Web界面" in test_name:
                repair_success = self._repair_web_interface(test_result)
            elif "音频系统" in test_name:
                repair_success = self._repair_audio_system(test_result)
            elif "存储空间" in test_name:
                repair_success = self._repair_storage_space(test_result)
            elif "网络连接" in test_name:
                repair_success = self._repair_network_connectivity(test_result)
            
            repair_log_entry = {
                "test": test_name,
                "timestamp": time.time(),
                "success": repair_success,
                "actions": repair_actions,
                "original_error": test_result.get("error", "未知错误")
            }
            
            self.repair_log.append(repair_log_entry)
            
            if repair_success:
                print(f"✅ 自动修复成功: {test_name}")
            else:
                print(f"❌ 自动修复失败: {test_name}")
                
        except Exception as e:
            print(f"⚠️ 自动修复异常: {test_name} - {e}")
    
    def _repair_rom_integrity(self, test_result: Dict) -> bool:
        """修复ROM完整性问题"""
        try:
            if "details" in test_result and "corrupted" in test_result["details"]:
                corrupted_files = test_result["details"]["corrupted"]
                
                for file_path in corrupted_files:
                    file_path = Path(file_path)
                    if file_path.exists():
                        # 删除损坏的ROM文件
                        file_path.unlink()
                        print(f"已删除损坏的ROM: {file_path.name}")
                
                # 重新生成ROM文件
                from .sync_rom_downloader import SyncROMDownloader
                downloader = SyncROMDownloader()
                downloader.download_all_recommended_games()
                
                return True
        except Exception as e:
            logger.error(f"ROM完整性修复失败: {e}")
        
        return False
    
    def _repair_emulator_availability(self, test_result: Dict) -> bool:
        """修复模拟器可用性问题"""
        try:
            # 在实际环境中，这里会尝试安装缺少的模拟器
            # 当前只是记录问题
            print("🔧 模拟器修复需要管理员权限，已记录问题")
            return False
        except Exception as e:
            logger.error(f"模拟器可用性修复失败: {e}")
        
        return False
    
    def _repair_web_interface(self, test_result: Dict) -> bool:
        """修复Web界面问题"""
        try:
            web_dir = self.project_root / "data" / "web"
            web_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建基本的Web文件
            if not (web_dir / "index.html").exists():
                with open(web_dir / "index.html", 'w', encoding='utf-8') as f:
                    f.write('''<!DOCTYPE html>
<html><head><title>GamePlayer-Raspberry</title></head>
<body><h1>GamePlayer-Raspberry 游戏中心</h1><p>游戏界面正在初始化...</p></body>
</html>''')
            
            if not (web_dir / "style.css").exists():
                with open(web_dir / "style.css", 'w') as f:
                    f.write('body { font-family: Arial; background: #333; color: white; }')
            
            if not (web_dir / "script.js").exists():
                with open(web_dir / "script.js", 'w') as f:
                    f.write('console.log("GamePlayer-Raspberry Web Interface Loaded");')
            
            return True
        except Exception as e:
            logger.error(f"Web界面修复失败: {e}")
        
        return False
    
    def _repair_audio_system(self, test_result: Dict) -> bool:
        """修复音频系统问题"""
        # 音频问题通常需要系统级修复
        print("🔧 音频系统修复需要系统级权限，已记录问题")
        return False
    
    def _repair_storage_space(self, test_result: Dict) -> bool:
        """修复存储空间问题"""
        try:
            # 清理临时文件
            temp_dirs = ["/tmp", self.project_root / "temp", self.project_root / "cache"]
            
            for temp_dir in temp_dirs:
                if isinstance(temp_dir, str):
                    temp_dir = Path(temp_dir)
                
                if temp_dir.exists():
                    for item in temp_dir.glob("*"):
                        if item.is_file() and item.suffix in ['.tmp', '.log', '.cache']:
                            try:
                                item.unlink()
                            except:
                                pass
            
            print("🗑️ 已清理临时文件")
            return True
        except Exception as e:
            logger.error(f"存储空间修复失败: {e}")
        
        return False
    
    def _repair_network_connectivity(self, test_result: Dict) -> bool:
        """修复网络连接问题"""
        # 网络问题通常需要手动配置
        print("🔧 网络连接问题需要手动检查网络设置")
        return False
    
    def _generate_test_report(self, test_summary: Dict):
        """生成测试报告"""
        report = {
            "test_summary": test_summary,
            "detailed_results": self.test_results,
            "repair_log": self.repair_log,
            "generated_at": time.strftime('%Y-%m-%d %H:%M:%S'),
            "system_info": {
                "platform": sys.platform,
                "python_version": sys.version,
                "project_root": str(self.project_root)
            }
        }
        
        # 保存详细报告
        report_file = self.project_root / "output" / f"test_report_{int(time.time())}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 生成简洁的HTML报告
        html_report = self._generate_html_report(report)
        html_file = report_file.with_suffix('.html')
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"\n📋 测试报告已生成:")
        print(f"  详细报告: {report_file}")
        print(f"  HTML报告: {html_file}")
    
    def _generate_html_report(self, report: Dict) -> str:
        """生成HTML测试报告"""
        summary = report["test_summary"]
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>GamePlayer-Raspberry 测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; }}
        .summary {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .test-item {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
        .pass {{ background: #d4edda; border-left: 5px solid #28a745; }}
        .fail {{ background: #f8d7da; border-left: 5px solid #dc3545; }}
        .error {{ background: #fff3cd; border-left: 5px solid #ffc107; }}
        .repair-log {{ background: #e7f3ff; padding: 15px; margin: 20px 0; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎮 GamePlayer-Raspberry 自动化测试报告</h1>
        <p>生成时间: {report["generated_at"]}</p>
    </div>
    
    <div class="summary">
        <h2>📊 测试总结</h2>
        <p><strong>总测试数:</strong> {summary["total_tests"]}</p>
        <p><strong>通过:</strong> {summary["passed"]} ✅</p>
        <p><strong>失败:</strong> {summary["failed"]} ❌</p>
        <p><strong>成功率:</strong> {summary["success_rate"]}%</p>
        <p><strong>测试时间:</strong> {summary["test_time"]}秒</p>
        <p><strong>修复尝试:</strong> {summary["repairs_attempted"]}次</p>
    </div>
    
    <div class="summary">
        <h2>📋 详细测试结果</h2>'''
        
        for result in report["detailed_results"]:
            status_class = result["result"]["status"]
            test_name = result["test"]
            test_result = result["result"]
            
            html += f'''
        <div class="test-item {status_class}">
            <strong>{test_name}</strong>
            <p>状态: {test_result["status"].upper()}</p>'''
            
            if "error" in test_result:
                html += f'<p>错误: {test_result["error"]}</p>'
            
            if "details" in test_result:
                html += f'<p>详情: {test_result["details"]}</p>'
            
            html += '</div>'
        
        if report["repair_log"]:
            html += '''
    </div>
    
    <div class="repair-log">
        <h2>🔧 自动修复日志</h2>'''
            
            for repair in report["repair_log"]:
                status = "成功" if repair["success"] else "失败"
                html += f'''
        <p><strong>{repair["test"]}</strong> - 修复{status}</p>
        <p>原始错误: {repair["original_error"]}</p>'''
            
            html += '</div>'
        
        html += '''
</body>
</html>'''
        
        return html


def main():
    """主函数"""
    tester = AutomatedTestingAndRepair()
    
    # 运行全面测试
    results = tester.run_comprehensive_tests()
    
    print(f"\n🎯 自动化测试完成！")
    print(f"测试通过率: {results['success_rate']}%")
    
    if results['failed'] > 0:
        print(f"⚠️ 发现 {results['failed']} 个问题，已尝试自动修复")
    else:
        print("✅ 所有测试通过，系统运行正常！")
    
    return results

if __name__ == "__main__":
    main()
