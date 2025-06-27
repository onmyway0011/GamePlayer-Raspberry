"""日志上传模块"""
import os
import json
from datetime import datetime
import glob


def upload_logs_to_s3(config_path='systems/retropie/config/log_upload_config.json'):
    """上传本地日志到S3兼容对象存储"""
    try:
        import boto3
    except ImportError:
        print('boto3未安装，无法上传日志')
        return
    if not os.path.exists(config_path):
        print(f'未找到配置文件: {config_path}')
        return
    with open(config_path, encoding='utf-8') as f:
        config = json.load(f)
    s3 = boto3.client('s3', endpoint_url=config.get('endpoint'))
    log_dir = config.get('log_dir', 'logs')
    prefix = config.get('prefix', 'logs/')
    for log_file in glob.glob(os.path.join(log_dir, '*.log')):
        key = f"{prefix}{os.path.basename(log_file)}"
        try:
            s3.upload_file(log_file, config['bucket'], key)
            print(f'已上传: {log_file} -> s3://{config["bucket"]}/{key}')
        except Exception as exc:
            print(f'上传失败: {log_file}, 错误: {exc}')

if __name__ == '__main__':
    import json
    if not os.path.exists('log_upload_config.json'):
        print('请先配置log_upload_config.json')
        exit(1)
    with open('log_upload_config.json') as f:
        cfg = json.load(f)
    today = datetime.now().strftime('%Y-%m-%d')
    for log_file in os.listdir('logs'):
        if today in log_file:
            upload_logs_to_s3(
                os.path.join('systems/retropie/config', 'log_upload_config.json')
            )
