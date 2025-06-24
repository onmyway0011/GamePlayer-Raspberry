#!/usr/bin/env python3
"""
树莓派HDMI配置优化脚本

这是一个专门用于优化树莓派HDMI输出的Python脚本。
自动修改 /boot/config.txt 配置文件，实现最佳的显示效果。

主要功能：
- 强制HDMI输出为1080p@60Hz
- 禁用过扫描（overscan）实现全屏显示
- 增加GPU显存至256MB提升性能
- 自动备份和恢复配置文件
- 支持预览模式和回滚操作
- 完整的配置验证和错误处理

配置项说明：
- hdmi_group=1: HDMI组1（CEA标准）
- hdmi_mode=16: 1080p@60Hz分辨率
- hdmi_force_hotplug=1: 强制HDMI热插拔检测
- hdmi_drive=2: HDMI驱动强度
- disable_overscan=1: 禁用过扫描
- gpu_mem=256: GPU显存256MB

系统要求：
- 树莓派系统
- Python 3.7+
- sudo权限（用于修改/boot/config.txt）

作者: AI Assistant
版本: 2.0.0
许可证: MIT
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hdmi_config.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HDMIConfigurator:
    """
    HDMI配置器类
    
    提供完整的树莓派HDMI配置优化功能，包括：
    - 配置文件读取和解析
    - 自动备份和恢复
    - HDMI参数优化
    - 配置验证和预览
    - 错误处理和回滚
    
    属性:
        config_path (Path): 配置文件路径
        backup_path (Path): 备份文件路径
        hdmi_configs (Dict): HDMI配置项字典
    """
    
    def __init__(self, config_path: str = "/boot/config.txt"):
        """
        初始化HDMI配置器
        
        Args:
            config_path (str): 配置文件路径
        """
        self.config_path = Path(config_path)
        self.backup_path = self.config_path.with_suffix('.txt.backup')
        
        # HDMI配置项
        self.hdmi_configs = {
            # 强制HDMI输出为1080p@60Hz
            "hdmi_group": "1",
            "hdmi_mode": "16",
            "hdmi_force_hotplug": "1",
            "hdmi_drive": "2",
            
            # 禁用过扫描
            "disable_overscan": "1",
            
            # GPU显存配置
            "gpu_mem": "256",
            
            # 其他优化配置
            "hdmi_ignore_cec_init": "1",
            "hdmi_ignore_cec": "1",
            "config_hdmi_boost": "4"
        }
        
    def check_permissions(self) -> bool:
        """检查文件权限"""
        if not self.config_path.exists():
            logger.error(f"配置文件不存在: {self.config_path}")
            return False
        
        if not os.access(self.config_path, os.R_OK | os.W_OK):
            logger.error(f"没有配置文件读写权限: {self.config_path}")
            logger.info("请使用 sudo 运行此脚本")
            return False
        
        return True
    
    def backup_config(self) -> bool:
        """备份原始配置文件"""
        try:
            if not self.backup_path.exists():
                shutil.copy2(self.config_path, self.backup_path)
                logger.info(f"配置文件已备份到: {self.backup_path}")
            else:
                logger.info(f"备份文件已存在: {self.backup_path}")
            return True
        except Exception as e:
            logger.error(f"备份配置文件失败: {e}")
            return False
    
    def read_config(self) -> List[str]:
        """读取配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception as e:
            logger.error(f"读取配置文件失败: {e}")
            return []
    
    def write_config(self, lines: List[str]) -> bool:
        """写入配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            logger.info("配置文件写入成功")
            return True
        except Exception as e:
            logger.error(f"写入配置文件失败: {e}")
            return False
    
    def parse_config_line(self, line: str) -> Optional[Dict[str, str]]:
        """解析配置行"""
        line = line.strip()
        
        # 跳过注释和空行
        if not line or line.startswith('#'):
            return None
        
        # 解析 key=value 格式
        if '=' in line:
            key, value = line.split('=', 1)
            return {
                'key': key.strip(),
                'value': value.strip(),
                'line': line
            }
        
        return None
    
    def find_config_line(self, lines: List[str], key: str) -> Optional[int]:
        """查找配置项的行号"""
        for i, line in enumerate(lines):
            parsed = self.parse_config_line(line)
            if parsed and parsed['key'] == key:
                return i
        return None
    
    def update_config(self, lines: List[str], key: str, value: str) -> List[str]:
        """更新配置项"""
        line_index = self.find_config_line(lines, key)
        
        if line_index is not None:
            # 更新现有配置
            lines[line_index] = f"{key}={value}\n"
            logger.info(f"更新配置: {key}={value}")
        else:
            # 添加新配置
            lines.append(f"{key}={value}\n")
            logger.info(f"添加配置: {key}={value}")
        
        return lines
    
    def apply_hdmi_configs(self) -> bool:
        """应用HDMI配置"""
        logger.info("开始应用HDMI配置...")
        
        # 读取现有配置
        lines = self.read_config()
        if not lines:
            return False
        
        # 应用每个配置项
        for key, value in self.hdmi_configs.items():
            lines = self.update_config(lines, key, value)
        
        # 写入配置文件
        return self.write_config(lines)
    
    def restore_backup(self) -> bool:
        """恢复备份配置"""
        if not self.backup_path.exists():
            logger.error("备份文件不存在")
            return False
        
        try:
            shutil.copy2(self.backup_path, self.config_path)
            logger.info("已恢复原始配置")
            return True
        except Exception as e:
            logger.error(f"恢复配置失败: {e}")
            return False
    
    def show_current_config(self) -> None:
        """显示当前配置"""
        logger.info("当前HDMI相关配置:")
        
        lines = self.read_config()
        if not lines:
            return
        
        hdmi_keys = set(self.hdmi_configs.keys())
        
        for line in lines:
            parsed = self.parse_config_line(line)
            if parsed and parsed['key'] in hdmi_keys:
                print(f"  {parsed['key']}={parsed['value']}")
    
    def show_changes(self) -> None:
        """显示将要应用的更改"""
        logger.info("将要应用的HDMI配置:")
        for key, value in self.hdmi_configs.items():
            print(f"  {key}={value}")
        
        print("\n配置说明:")
        print("  hdmi_group=1: HDMI组1（CEA标准）")
        print("  hdmi_mode=16: 1080p@60Hz")
        print("  hdmi_force_hotplug=1: 强制HDMI热插拔检测")
        print("  hdmi_drive=2: HDMI驱动强度")
        print("  disable_overscan=1: 禁用过扫描")
        print("  gpu_mem=256: GPU显存256MB")
        print("  hdmi_ignore_cec_init=1: 忽略CEC初始化")
        print("  hdmi_ignore_cec=1: 忽略CEC")
        print("  config_hdmi_boost=4: HDMI信号增强")
    
    def validate_config(self) -> bool:
        """验证配置"""
        logger.info("验证配置...")
        
        # 检查关键配置项
        required_configs = {
            'hdmi_group': '1',
            'hdmi_mode': '16',
            'gpu_mem': '256'
        }
        
        lines = self.read_config()
        if not lines:
            return False
        
        for key, expected_value in required_configs.items():
            line_index = self.find_config_line(lines, key)
            if line_index is None:
                logger.warning(f"缺少配置项: {key}")
                continue
            
            parsed = self.parse_config_line(lines[line_index])
            if parsed and parsed['value'] != expected_value:
                logger.warning(f"配置项 {key} 值不匹配: 期望 {expected_value}, 实际 {parsed['value']}")
        
        logger.info("配置验证完成")
        return True
    
    def run(self, dry_run: bool = False, restore: bool = False) -> bool:
        """运行配置程序"""
        logger.info("=== 树莓派HDMI配置优化工具 ===")
        
        # 检查权限
        if not self.check_permissions():
            return False
        
        # 恢复备份
        if restore:
            return self.restore_backup()
        
        # 显示当前配置
        self.show_current_config()
        
        # 显示将要应用的更改
        self.show_changes()
        
        if dry_run:
            logger.info("模拟运行模式，不会实际修改配置文件")
            return True
        
        # 确认操作
        confirm = input("\n确认应用这些配置？(y/N): ")
        if confirm.lower() != 'y':
            logger.info("操作已取消")
            return False
        
        # 备份配置
        if not self.backup_config():
            return False
        
        # 应用配置
        if not self.apply_hdmi_configs():
            return False
        
        # 验证配置
        self.validate_config()
        
        logger.info("=== 配置完成 ===")
        logger.info("请重启树莓派以应用新配置")
        logger.info("重启命令: sudo reboot")
        
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="树莓派HDMI配置优化工具")
    parser.add_argument("--config", default="/boot/config.txt", help="配置文件路径")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，不实际修改文件")
    parser.add_argument("--restore", action="store_true", help="恢复原始配置")
    parser.add_argument("--show", action="store_true", help="显示当前配置")
    
    args = parser.parse_args()
    
    configurator = HDMIConfigurator(args.config)
    
    if args.show:
        configurator.show_current_config()
        return
    
    if args.restore:
        configurator.run(restore=True)
        return
    
    success = configurator.run(dry_run=args.dry_run)
    
    if success:
        print("\n🎉 HDMI配置优化完成！")
        if not args.dry_run:
            print("请重启树莓派以应用新配置")
    else:
        print("\n❌ 配置失败，请查看日志文件")

if __name__ == "__main__":
    main() 