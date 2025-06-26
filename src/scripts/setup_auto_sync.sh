#!/bin/bash
set -e

# 检测操作系统
OS_TYPE=$(uname)

if [[ "$OS_TYPE" == "Darwin" ]]; then
  echo "检测到 macOS 环境，使用 brew/pip3 安装依赖..."
  # 1. 安装依赖
  brew install python3 || true
  pip3 install flask boto3 requests tqdm paramiko
else
  echo "检测到 Linux/Raspberry Pi 环境，使用 apt 安装依赖..."
  sudo apt update
  sudo apt install -y python3-pip python3-flask python3-boto3 python3-requests
  pip3 install tqdm paramiko
fi

# 2. 部署 systemd 服务（仅限 Linux/Raspberry Pi）
if [[ "$OS_TYPE" != "Darwin" ]]; then
  cat <<EOF | sudo tee /etc/systemd/system/game_sync.service
[Unit]
Description=Game Save Auto Sync

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/pi/auto_save_sync.py --watch
Restart=on-failure
User=pi

[Install]
WantedBy=multi-user.target
EOF

  sudo systemctl daemon-reload
  sudo systemctl enable game_sync
else
  echo "macOS 环境不支持 systemd 服务，跳过 systemd 部署。"
fi

# 3. 集成 EmulationStation 钩子（示例，需根据实际路径调整）
HOOK_SCRIPT="./auto_save_sync_hook.sh"
cat <<'EOS' > $HOOK_SCRIPT
#!/bin/bash
GAME_NAME="$1"
ROM_PATH="$2"
python3 ./auto_save_sync.py --pre-sync "$GAME_NAME" "$ROM_PATH"
# 启动模拟器命令应在此处
python3 ./auto_save_sync.py --post-sync "$GAME_NAME"
EOS
chmod +x $HOOK_SCRIPT

# 4. 启动 Web 配置界面（Flask）
cat <<'EOF' > web_config.py
from flask import Flask, render_template_string, request, redirect
import json
import os

app = Flask(__name__)
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "project_config.json")

HTML = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>云存档与模拟器配置</title>
</head>
<body>
  <h2>云存档与模拟器配置</h2>
  <form method="post">
    <label>模拟器类型：</label>
    <select name="emulator_type">
      <option value="retroarch" {{'selected' if config['emulator']['type']=='retroarch' else ''}}>RetroArch</option>
      <option value="snes9x" {{'selected' if config['emulator']['type']=='snes9x' else ''}}>Snes9x</option>
    </select><br><br>
    <label>金手指目录：</label><input name="cheats_dir" value="{{config['emulator']['cheats_dir']}}"><br><br>
    <label>存档目录：</label><input name="saves_dir" value="{{config['emulator']['saves_dir']}}"><br><br>
    <label>云端类型：</label>
    <select name="cloud_provider">
      <option value="cos" {{'selected' if config['cloud_save']['provider']=='cos' else ''}}>腾讯云COS</option>
      <option value="custom_api" {{'selected' if config['cloud_save']['provider']=='custom_api' else ''}}>自定义API</option>
    </select><br><br>
    <fieldset><legend>COS配置</legend>
      <label>Bucket：</label><input name="cos_bucket" value="{{config['cloud_save']['cos']['bucket']}}"><br>
      <label>Region：</label><input name="cos_region" value="{{config['cloud_save']['cos']['region']}}"><br>
      <label>SecretId：</label><input name="cos_secret_id" value="{{config['cloud_save']['cos']['secret_id']}}"><br>
      <label>SecretKey：</label><input name="cos_secret_key" value="{{config['cloud_save']['cos']['secret_key']}}"><br>
      <label>BaseURL：</label><input name="cos_base_url" value="{{config['cloud_save']['cos']['base_url']}}"><br>
    </fieldset>
    <fieldset><legend>自定义API配置</legend>
      <label>API地址：</label><input name="api_url" value="{{config['cloud_save']['custom_api']['api_url']}}"><br>
      <label>API Key：</label><input name="api_key" value="{{config['cloud_save']['custom_api']['api_key']}}"><br>
    </fieldset>
    <br><input type="submit" value="保存配置">
  </form>
</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def index():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    if request.method == "POST":
        config["emulator"]["type"] = request.form["emulator_type"]
        config["emulator"]["cheats_dir"] = request.form["cheats_dir"]
        config["emulator"]["saves_dir"] = request.form["saves_dir"]
        config["cloud_save"]["provider"] = request.form["cloud_provider"]
        config["cloud_save"]["cos"]["bucket"] = request.form["cos_bucket"]
        config["cloud_save"]["cos"]["region"] = request.form["cos_region"]
        config["cloud_save"]["cos"]["secret_id"] = request.form["cos_secret_id"]
        config["cloud_save"]["cos"]["secret_key"] = request.form["cos_secret_key"]
        config["cloud_save"]["cos"]["base_url"] = request.form["cos_base_url"]
        config["cloud_save"]["custom_api"]["api_url"] = request.form["api_url"]
        config["cloud_save"]["custom_api"]["api_key"] = request.form["api_key"]
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return redirect("/")
    return render_template_string(HTML, config=config)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
EOF

echo "自动化集成完成！可运行 python3 web_config.py 启动 Web 配置界面。" 