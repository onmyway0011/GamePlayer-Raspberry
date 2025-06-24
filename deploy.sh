#!/bin/bash

# GamePlayer-Raspberry 部署脚本
# 用于设置远程仓库并推送代码到GitHub

set -e

echo "🚀 GamePlayer-Raspberry 部署脚本"
echo "================================"

# 检查Git状态
if ! git status >/dev/null 2>&1; then
    echo "❌ 错误: 当前目录不是Git仓库"
    exit 1
fi

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  警告: 有未提交的更改"
    echo "请先提交所有更改:"
    echo "  git add ."
    echo "  git commit -m 'your commit message'"
    exit 1
fi

# 获取远程仓库URL
read -p "请输入GitHub仓库URL (例如: https://github.com/username/GamePlayer-Raspberry.git): " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ 错误: 请输入有效的仓库URL"
    exit 1
fi

# 添加远程仓库
echo "📡 添加远程仓库..."
git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"

# 推送代码
echo "📤 推送代码到远程仓库..."
git push -u origin master

# 推送标签
echo "🏷️  推送版本标签..."
git push origin v2.0.0

echo "✅ 部署完成！"
echo ""
echo "📋 下一步操作:"
echo "1. 在GitHub上查看您的仓库"
echo "2. 设置GitHub Pages (可选)"
echo "3. 配置GitHub Actions (可选)"
echo "4. 邀请协作者"
echo ""
echo "🔗 有用的链接:"
echo "- 仓库: $REPO_URL"
echo "- Issues: ${REPO_URL%.git}/issues"
echo "- Wiki: ${REPO_URL%.git}/wiki" 