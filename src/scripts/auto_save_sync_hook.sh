#!/bin/bash
GAME_NAME="$1"
ROM_PATH="$2"
python3 ./auto_save_sync.py --pre-sync "$GAME_NAME" "$ROM_PATH"
# 启动模拟器命令应在此处
python3 ./auto_save_sync.py --post-sync "$GAME_NAME"
