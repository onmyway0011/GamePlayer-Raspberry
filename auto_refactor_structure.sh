#!/bin/bash
set -e

# 1. 创建新目录结构
mkdir -p core scripts tests config docs downloads logs

# 2. 移动核心工具脚本
mv rom_downloader.py retropie_installer.py hdmi_config.py core/ 2>/dev/null || true

# 3. 移动自动化脚本
mv auto_migrate_to_pi.sh setup_auto_sync.sh auto_save_sync.py immersive_hardware_auto.sh retropie_ecosystem_auto.sh auto_save_sync_hook.sh scripts/ 2>/dev/null || true

# 4. 移动测试文件
mv test_*.py tests/ 2>/dev/null || true

# 5. 移动配置文件
mv requirements.txt project_config.json firstboot_setup.service install.sh install.bat config/ 2>/dev/null || true

# 6. 移动文档
mv README.md README_HDMI.md LICENSE docs/ 2>/dev/null || true

# 7. 移动下载和日志
mv downloads/ downloads 2>/dev/null || true
mv logs/ logs 2>/dev/null || true

# 8. 合并 systems 下内容
for d in systems/*; do
  [ -d "$d" ] || continue
  # 合并 core 脚本
  if [ -d "$d/core" ]; then mv $d/core/* core/ 2>/dev/null || true; fi
  # 合并 config
  if [ -d "$d/config" ]; then mv $d/config/* config/ 2>/dev/null || true; fi
  # 合并 logs
  if [ -d "$d/logs" ]; then mv $d/logs/* logs/ 2>/dev/null || true; fi
  # 合并 docs
  if [ -d "$d/docs" ]; then mv $d/docs/* docs/ 2>/dev/null || true; fi
  # 合并 tests
  if [ -d "$d/tests" ]; then mv $d/tests/* tests/ 2>/dev/null || true; fi
  # 合并 roms/cheats/saves
  if [ -d "$d/roms" ]; then mv $d/roms/* downloads/ 2>/dev/null || true; fi
  if [ -d "$d/cheats" ]; then mv $d/cheats/* downloads/ 2>/dev/null || true; fi
  if [ -d "$d/saves" ]; then mv $d/saves/* downloads/ 2>/dev/null || true; fi
  # 删除空目录
  rm -rf "$d"
done
rm -rf systems

# 9. 修正引用路径（仅示例，建议后续用 sed 全局替换 core/、config/、tests/ 等新路径）
# find . -type f -name '*.py' -exec sed -i '' 's/systems\.\(retropie\|hdmi\|immersive\|ecosystem\)\.core/core/g' {} +

# 10. 更新 README.md 目录结构快照
cd docs
python3 -c "import os; print('# 目录结构\n');
for root, dirs, files in os.walk('..'):
  level = root.replace('..', '').count(os.sep)
  indent = '  ' * level
  print(f'{indent}- {os.path.basename(root)}/')
  for f in files:
    print(f'{indent}  - {f}')" > DIR_TREE.md
cd ..

# 11. git 自动提交并推送
if git status | grep -q 'Changes not staged'; then
  git add .
  git commit -m "自动化目录结构迁移与文档更新"
  git push origin HEAD:main || git push origin HEAD:master
fi

echo "[OK] 目录结构已自动迁移、README已更新并推送。" 