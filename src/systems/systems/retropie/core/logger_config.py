"""日志配置模块"""
import logging
import logging.handlers
import os
from datetime import datetime

LOG_DIR = os.path.abspath(os.getenv('LOG_DIR', 'logs'))
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, f'gameplayer_{datetime.now().strftime("%Y%m%d")}.log')


def get_logger(name: str = 'GamePlayer', level: int = logging.INFO) -> logging.Logger:
    """获取带有本地轮转和S3上传的日志记录器"""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s] %(message)s')
    file_handler = logging.handlers.TimedRotatingFileHandler(LOG_FILE, when='midnight', backupCount=30, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    # S3上传Handler可选
    s3_config = os.getenv('S3_LOG_CONFIG')
    if s3_config:
        try:
            import boto3
            import json
            s3_info = json.loads(s3_config)
            class S3UploadHandler(logging.Handler):
                def emit(self, record):
                    try:
                        s3 = boto3.client('s3', endpoint_url=s3_info.get('endpoint'))
                        log_entry = self.format(record)
                        key = f"{s3_info.get('prefix', 'logs/')}{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name}.log"
                        s3.put_object(Bucket=s3_info['bucket'], Key=key, Body=log_entry.encode('utf-8'))
                    except Exception as exc:
                        print(f'S3日志上传失败: {exc}')
            s3_handler = S3UploadHandler()
            s3_handler.setFormatter(formatter)
            logger.addHandler(s3_handler)
        except Exception as exc:
            print(f'S3日志Handler初始化失败: {exc}')
    return logger 