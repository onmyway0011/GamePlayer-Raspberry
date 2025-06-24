#!/bin/bash
# 用法: ./publish_api_docs.sh user@host:/path/to/webroot
set -e

TARGET=$1
if [ -z "$TARGET" ]; then
  echo "用法: $0 user@host:/path/to/webroot"
  exit 1
fi

if [ ! -d apidocs ]; then
  echo "apidocs目录不存在，请先生成API文档。"
  exit 2
fi

rsync -avz --delete apidocs/ "$TARGET"/

echo "API文档已推送到: $TARGET" 