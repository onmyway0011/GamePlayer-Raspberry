from flask import Flask, redirect, render_template_string, request
import json
import os

app = Flask(__name__)
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "project_config.json")

HTML = """
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
"""

@app.route("/", methods=["GET", "POST"])

def index():
    """
    处理根路由("/")的GET和POST请求，用于展示和更新模拟器配置。

    GET请求:
        - 读取并返回当前配置文件内容
        - 渲染配置页面模板

    POST请求:
        - 接收表单数据并更新配置项:
            - 模拟器类型(emulator_type)
            - 作弊码目录(cheats_dir)
            - 存档目录(saves_dir)
            - 云存储相关配置(provider/bucket/region等)
        - 将更新后的配置写入文件
        - 重定向到根路由

    返回:
        - GET: 渲染的HTML模板
        - POST: 重定向响应
    """
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
