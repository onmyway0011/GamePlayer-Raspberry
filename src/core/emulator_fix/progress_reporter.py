#!/usr/bin/env python3
"""
进度报告器 - 提供进度显示和报告生成功能
"""

import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any
from .logger_setup import get_logger

logger = get_logger("progress")


class ProgressReporter:
    """进度报告器"""

    def __init__(self):
        """初始化进度报告器"""
        self.current_task: Optional[str] = None
        self.total_items: int = 0
        self.completed_items: int = 0
        self.start_time: Optional[float] = None
        self.is_running: bool = False
        self._progress_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start_progress(self, task_name: str, total_items: int) -> None:
        """开始进度显示"""
        self.current_task = task_name
        self.total_items = total_items
        self.completed_items = 0
        self.start_time = time.time()
        self.is_running = True
        self._stop_event.clear()

        logger.info(f"🚀 开始: {task_name} (共 {total_items} 项)")

        # 启动进度显示线程
        self._progress_thread = threading.Thread(target=self._progress_loop, daemon=True)
        self._progress_thread.start()

    def update_progress(self, completed: Optional[int] = None, message: Optional[str] = None) -> None:
        """更新进度"""
        if completed is not None:
            self.completed_items = completed
        else:
            self.completed_items += 1

        if message:
            logger.debug(f"📝 {message}")

    def finish_progress(self) -> None:
        """结束进度显示"""
        if not self.is_running:
            return

        self.is_running = False
        self._stop_event.set()

        if self._progress_thread and self._progress_thread.is_alive():
            self._progress_thread.join(timeout=1.0)

        # 显示最终结果
        if self.start_time:
            duration = time.time() - self.start_time
            logger.info(f"✅ 完成: {self.current_task} ({self.completed_items}/{self.total_items}) - 耗时: {duration:.2f}s")

        self._reset()

    def _progress_loop(self) -> None:
        """进度显示循环"""
        while not self._stop_event.wait(2.0):  # 每2秒更新一次
            if not self.is_running:
                break

            self._display_progress()

    def _display_progress(self) -> None:
        """显示进度"""
        if not self.is_running or self.total_items == 0:
            return

        percentage = (self.completed_items / self.total_items) * 100

        # 计算剩余时间
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        if self.completed_items > 0:
            avg_time_per_item = elapsed_time / self.completed_items
            remaining_items = self.total_items - self.completed_items
            eta = remaining_items * avg_time_per_item
            eta_text = f"剩余: {eta:.0f}s"
        else:
            eta_text = "计算中..."

        # 创建进度条
        bar_length = 30
        filled_length = int(bar_length * percentage / 100)
        bar = "█" * f"{filled_length}░" * (bar_length - filled_length)

        logger.info(f"📊 {self.current_task}: [{bar}] {percentage:.1f}% ({self.completed_items}/{self.total_items}) - {eta_text}")

    def _reset(self) -> None:
        """重置状态"""
        self.current_task = None
        self.total_items = 0
        self.completed_items = 0
        self.start_time = None
        self.is_running = False
        self._progress_thread = None

    def generate_html_report(self, session) -> str:
        """生成HTML报告"""
        if not session:
            return self._generate_empty_report()

        summary = session
        if hasattr(session, 'session_id'):
            # 如果是FixSession对象，获取摘要
            from .state_manager import get_state_manager
            state_manager = get_state_manager()
            summary = state_manager.get_session_summary(session)

        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>游戏模拟器修复报告</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .header h1 {
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }
        .header .subtitle {
            color: #7f8c8d;
            font-size: 1.2em;
            margin-top: 10px;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            font-size: 1.1em;
        }
        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .summary-card .unit {
            font-size: 0.9em;
            opacity: 0.8;
        }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .progress-bar {
            background: #ecf0f1;
            border-radius: 10px;
            overflow: hidden;
            height: 20px;
            margin: 10px 0;
        }
        .progress-fill {
            background: linear-gradient(90deg, #2ecc71, #27ae60);
            height: 100%;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.8em;
        }
        .status-good { color: #27ae60; }
        .status-warning { color: #f39c12; }
        .status-error { color: #e74c3c; }
        .timestamp {
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }
        .emoji {
            font-size: 1.2em;
            margin-right: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 游戏模拟器修复报告</h1>
            <div class="subtitle">GamePlayer-Raspberry 系统修复详情</div>
        </div>

        <div class="summary">
            <div class="summary-card">
                <h3>📊 总执行时间</h3>
                <div class="value">{duration:.1f}</div>
                <div class="unit">秒</div>
            </div>
            <div class="summary-card">
                <h3>📝 修复项目</h3>
                <div class="value">{total_items}</div>
                <div class="unit">个</div>
            </div>
            <div class="summary-card">
                <h3>✅ 成功完成</h3>
                <div class="value">{completed_items}</div>
                <div class="unit">个</div>
            </div>
            <div class="summary-card">
                <h3>🎯 成功率</h3>
                <div class="value">{success_rate:.1f}</div>
                <div class="unit">%</div>
            </div>
        </div>

        <div class="section">
            <h2>📈 修复进度</h2>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress_percentage:.1f}%">
                    {progress_percentage:.1f}%
                </div>
            </div>
            <p>修复进度: {completed_items} / {total_items} 项完成</p>
        </div>

        <div class="section">
            <h2>🔍 修复详情</h2>
            <div class="details">
                <p><span class="emoji">🎮</span><strong>会话ID:</strong> {session_id}</p>
                <p><span class="emoji">⏰</span><strong>开始时间:</strong> {start_time}</p>
                <p><span class="emoji">🏁</span><strong>结束时间:</strong> {end_time}</p>
                <p><span class="emoji">⚡</span><strong>执行时长:</strong> {duration:.2f} 秒</p>
            </div>
        </div>

        <div class="section">
            <h2>📋 修复结果</h2>
            <div class="results">
                {results_html}
            </div>
        </div>

        <div class="timestamp">
            <p>报告生成时间: {report_time}</p>
            <p>🎮 GamePlayer-Raspberry v4.6.0 - 企业级代码质量版本</p>
        </div>
    </div>
</body>
</html>
        """

        # 生成结果HTML
        results_html = self._generate_results_html(summary)

        # 格式化时间
        start_time = summary.get('start_time', 'N/A')
        end_time = summary.get('end_time', 'N/A')

        return html_template.format(
            session_id=summary.get('session_id', 'unknown'),
            duration=summary.get('duration', 0) or 0,
            total_items=summary.get('total_items', 0),
            completed_items=summary.get('completed_items', 0),
            failed_items=summary.get('failed_items', 0),
            progress_percentage=summary.get('progress_percentage', 0),
            success_rate=summary.get('success_rate', 0),
            start_time=start_time,
            end_time=end_time,
            results_html=results_html,
            report_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

    def _generate_results_html(self, summary: Dict[str, Any]) -> str:
        """生成结果HTML"""
        total = summary.get('total_items', 0)
        completed = summary.get('completed_items', 0)
        failed = summary.get('failed_items', 0)

        if total == 0:
            return "<p>没有执行任何修复操作。</p>"

        results = []

        if completed > 0:
            results.append(f'<p class="status-good"><span class="emoji">✅</span><strong>成功完成:</strong> {completed} 个项目</p>')

        if failed > 0:
            results.append(f'<p class="status-error"><span class="emoji">❌</span><strong>修复失败:</strong> {failed} 个项目</p>')

        skipped = total - completed - failed
        if skipped > 0:
            results.append(f'<p class="status-warning"><span class="emoji">⏭️</span><strong>跳过执行:</strong> {skipped} 个项目</p>')

        # 添加建议
        if failed == 0:
            results.append('<p class="status-good"><span class="emoji">🎉</span><strong>恭喜!</strong> 所有问题都已成功修复，系统现在可以正常运行游戏了。</p>')
        else:
            results.append('<p class="status-warning"><span class="emoji">⚠️</span><strong>注意:</strong> 部分问题修复失败，请检查日志文件获取详细信息。</p>')

        return '\n'.join(results)

    def _generate_empty_report(self) -> str:
        """生成空报告"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>游戏模拟器修复报告</title>
</head>
<body>
    <h1>🎮 游戏模拟器修复报告</h1>
    <p>没有可用的修复会话数据。</p>
</body>
</html>
        """

if __name__ == "__main__":
    # 测试进度报告器
    import time

    reporter = ProgressReporter()

    # 测试进度显示
    reporter.start_progress("测试任务", 5)

    for i in range(5):
        time.sleep(1)
        reporter.update_progress(message=f"完成项目 {i+1}")

    reporter.finish_progress()

    print("✅ 进度报告器测试完成")
