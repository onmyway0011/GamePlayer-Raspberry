#!/bin/bash
# 项目清理和状态报告脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🧹 GamePlayer-Raspberry 项目清理和状态报告"
echo "============================================="

# 1. 清理Python缓存文件
log_info "1. 清理Python缓存文件..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.pyd" -delete 2>/dev/null || true
log_success "✅ Python缓存文件清理完成"

# 2. 清理临时文件
log_info "2. 清理临时文件..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*.backup" -delete 2>/dev/null || true
find . -name "*~" -delete 2>/dev/null || true
log_success "✅ 临时文件清理完成"

# 3. 清理日志文件
log_info "3. 清理旧日志文件..."
find . -name "*.log" -size +10M -delete 2>/dev/null || true
find . -name "build.log" -delete 2>/dev/null || true
log_success "✅ 日志文件清理完成"

# 4. 清理空目录
log_info "4. 清理空目录..."
find . -type d -empty -not -path "./.git/*" -delete 2>/dev/null || true
log_success "✅ 空目录清理完成"

# 5. 检查Docker状态
log_info "5. 检查Docker环境状态..."
if docker info >/dev/null 2>&1; then
    log_success "✅ Docker运行正常"
    
    # 检查容器状态
    if docker ps | grep -q "gameplayer-test"; then
        log_success "✅ 测试容器正在运行"
        echo "   📡 访问地址: http://localhost:8080"
    else
        log_warning "⚠️ 测试容器未运行"
    fi
    
    # 显示镜像信息
    echo "   🐳 Docker镜像:"
    docker images | grep -E "(python|gameplayer)" | head -5
else
    log_error "❌ Docker未运行"
fi

# 6. 项目结构验证
log_info "6. 验证项目结构..."
required_dirs=("src" "config" "docs" "tests" "build" "data" "tools")
missing_dirs=()

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        log_success "✅ $dir/ 目录存在"
    else
        missing_dirs+=("$dir")
        log_error "❌ $dir/ 目录缺失"
    fi
done

# 7. 检查关键文件
log_info "7. 检查关键文件..."
key_files=("README.md" "requirements.txt" "setup.py" "quick_start.sh")
for file in "${key_files[@]}"; do
    if [ -f "$file" ]; then
        log_success "✅ $file 存在"
    else
        log_error "❌ $file 缺失"
    fi
done

# 8. 生成状态报告
log_info "8. 生成状态报告..."
report_file="data/logs/project_status_$(date +%Y%m%d_%H%M%S).md"
mkdir -p "$(dirname "$report_file")"

cat > "$report_file" << EOF
# GamePlayer-Raspberry 项目状态报告

**生成时间:** $(date '+%Y-%m-%d %H:%M:%S')

## 📁 项目结构状态

### ✅ 已完成的重构
- 项目结构已重新组织为专业化目录结构
- 源代码移动到 \`src/\` 目录
- 配置文件整理到 \`config/\` 目录
- 文档集中到 \`docs/\` 目录
- 测试文件组织到 \`tests/\` 目录

### 📂 目录结构
\`\`\`
$(tree -L 2 -I '__pycache__|*.pyc|.git' . 2>/dev/null || find . -type d -not -path "./.git*" | head -20 | sort)
\`\`\`

## 🐳 Docker环境状态

### 容器状态
\`\`\`
$(docker ps 2>/dev/null || echo "Docker未运行")
\`\`\`

### 镜像状态
\`\`\`
$(docker images 2>/dev/null | head -5 || echo "Docker未运行")
\`\`\`

## 🧹 清理结果

- ✅ Python缓存文件已清理
- ✅ 临时文件已清理  
- ✅ 日志文件已清理
- ✅ 空目录已清理

## 📊 项目统计

- **总文件数:** $(find . -type f -not -path "./.git/*" | wc -l)
- **Python文件数:** $(find . -name "*.py" -not -path "./.git/*" | wc -l)
- **Shell脚本数:** $(find . -name "*.sh" -not -path "./.git/*" | wc -l)
- **Docker文件数:** $(find . -name "Dockerfile*" -not -path "./.git/*" | wc -l)

## 🎯 下一步建议

1. 运行完整的Docker构建测试
2. 执行单元测试验证功能
3. 更新文档和README
4. 提交代码变更

---
*报告由 cleanup_and_report.sh 自动生成*
EOF

log_success "✅ 状态报告已生成: $report_file"

# 9. 总结
echo ""
echo "🎉 项目清理和检查完成！"
echo "📊 状态报告: $report_file"
echo ""

if [ ${#missing_dirs[@]} -eq 0 ]; then
    log_success "✅ 项目结构完整"
else
    log_warning "⚠️ 缺失目录: ${missing_dirs[*]}"
fi

echo "🚀 建议下一步操作:"
echo "   1. 查看状态报告: cat $report_file"
echo "   2. 运行Docker测试: src/scripts/quick_docker_test.sh"
echo "   3. 执行单元测试: python -m pytest tests/"
echo "   4. 启动完整环境: ./quick_start.sh"
echo ""
