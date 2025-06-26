"""日志分析与可视化工具模块"""
import os
import re
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from threading import Thread
import time

LOG_DIR = 'logs'
REPORT_DIR = 'log_reports'
os.makedirs(REPORT_DIR, exist_ok=True)

def parse_log_line(line) -> None:
    """解析单行日志"""
    m = re.match(r'\[(.*?)\]\[(.*?)\]\[(.*?)\] (.*)', line)
    if m:
        return {
            'time': m.group(1),
            'level': m.group(2),
            'module': m.group(3),
            'msg': m.group(4)
        }
    return None

def analyze_logs(keyword=None, anomaly_patterns=None) -> None:
    """分析日志，支持关键字和异常模式检索"""
    stats = defaultdict(Counter)
    errors = []
    warnings = []
    all_times = []
    keyword_hits = []
    anomaly_hits = []
    for fname in os.listdir(LOG_DIR):
        if not fname.endswith('.log'):
            continue
        with open(os.path.join(LOG_DIR, fname), encoding='utf-8') as f:
            for line in f:
                entry = parse_log_line(line)
                if not entry:
                    continue
                stats[entry['module']][entry['level']] += 1
                if entry['level'] == 'ERROR':
                    errors.append(entry)
                if entry['level'] == 'WARNING':
                    warnings.append(entry)
                try:
                    all_times.append(datetime.strptime(entry['time'], '%Y-%m-%d %H:%M:%S'))
                except ValueError:
                    pass
                if keyword and keyword in entry['msg']:
                    keyword_hits.append(entry)
                if anomaly_patterns:
                    for pat in anomaly_patterns:
                        if re.search(pat, entry['msg']):
                            anomaly_hits.append(entry)
    return stats, errors, warnings, all_times, keyword_hits, anomaly_hits

def plot_trend(all_times) -> None:
    """生成日志活跃趋势图"""
    if not all_times:
        return None
    days = [dt.date() for dt in all_times]
    count = Counter(days)
    dates = sorted(count)
    values = [count[d] for d in dates]
    plt.figure(figsize=(8, 4))
    plt.plot(dates, values, marker='o')
    plt.title('日志活跃趋势')
    plt.xlabel('日期')
    plt.ylabel('日志条数')
    plt.tight_layout()
    img_path = os.path.join(REPORT_DIR, 'trend.png')
    plt.savefig(img_path)
    plt.close()
    return img_path

def generate_report(stats, errors, warnings, trend_img, keyword_hits, anomaly_hits, keyword=None, anomaly_patterns=None) -> None:
    """生成Markdown格式的日志分析报告"""
    report_path = os.path.join(REPORT_DIR, f'log_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f'# 日志分析报告\n\n')
        f.write(f'生成时间: {datetime.now()}\n\n')
        f.write('## 各模块日志级别统计\n')
        for module, counter in stats.items():
            f.write(f'- **{module}**: ' + ', '.join([f'{k}: {v}' for k, v in counter.items()]) + '\n')
        f.write('\n## 错误统计\n')
        f.write(f'- 错误总数: {len(errors)}\n')
        for e in errors[-10:]:
            f.write(f'  - [{e["time"]}] {e["module"]}: {e["msg"]}\n')
        f.write('\n## 警告统计\n')
        f.write(f'- 警告总数: {len(warnings)}\n')
        for w in warnings[-10:]:
            f.write(f'  - [{w["time"]}] {w["module"]}: {w["msg"]}\n')
        if trend_img:
            f.write(f'\n## 日志活跃趋势\n![]({os.path.basename(trend_img)})\n')
        if keyword:
            f.write(f'\n## 关键字检索: {keyword}\n命中条数: {len(keyword_hits)}\n')
            for hit in keyword_hits[-10:]:
                f.write(f'  - [{hit["time"]}] {hit["module"]}: {hit["msg"]}\n')
        if anomaly_patterns:
            f.write(f'\n## 异常模式识别: {anomaly_patterns}\n命中条数: {len(anomaly_hits)}\n')
            for hit in anomaly_hits[-10:]:
                f.write(f'  - [{hit["time"]}] {hit["module"]}: {hit["msg"]}\n')
    return report_path

def send_alert(errors, warnings, anomaly_hits) -> None:
    """通过Webhook发送日志告警"""
    webhook = os.environ.get('LOG_ALERT_WEBHOOK')
    if not webhook:
        return
    import requests
    msg = f'日志告警\n错误数: {len(errors)}\n警告数: {len(warnings)}\n异常模式命中: {len(anomaly_hits)}\n'
    msg += '\n'.join([f'{e["time"]} {e["module"]}: {e["msg"]}' for e in errors[-3:]])
    data = {"msgtype": "text", "text": {"content": msg}}
    try:
        requests.post(webhook, json=data, timeout=5)
    except requests.RequestException as exc:
        print(f'告警发送失败: {exc}')

def start_web_dashboard() -> None:
    """启动Flask Web服务，提供日志可视化接口"""
    from flask import Flask, jsonify, request, send_from_directory
    app = Flask(__name__)

    @app.route('/logs')
    def logs() -> None:
        keyword = request.args.get('keyword')
        anomaly = request.args.get('anomaly')
        anomaly_patterns = [anomaly] if anomaly else None
        _, _, _, _, keyword_hits, anomaly_hits = analyze_logs(keyword, anomaly_patterns)
        return jsonify({
            'keyword_hits': keyword_hits,
            'anomaly_hits': anomaly_hits
        })

    @app.route('/trend')
    def trend() -> None:
        _, _, _, all_times, _, _ = analyze_logs()
        img_path = plot_trend(all_times)
        return send_from_directory(REPORT_DIR, os.path.basename(img_path))

    @app.route('/report')
    def report() -> None:
        files = sorted([f for f in os.listdir(REPORT_DIR) if f.endswith('.md')], reverse=True)
        if not files:
            return 'No report', 404
        with open(os.path.join(REPORT_DIR, files[0]), encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/markdown; charset=utf-8'}

    app.run(port=5001)

def export_to_json() -> None:
    """导出所有日志为ELK/Graylog可用的JSON"""
    all_entries = []
    for fname in os.listdir(LOG_DIR):
        if not fname.endswith('.log'):
            continue
        with open(os.path.join(LOG_DIR, fname), encoding='utf-8') as f:
            for line in f:
                entry = parse_log_line(line)
                if entry:
                    all_entries.append(entry)
    out_path = os.path.join(REPORT_DIR, f'elk_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)
    print(f'ELK/Graylog导出文件: {out_path}')

def schedule_auto_analyze(interval_min=10) -> None:
    """定时自动分析日志"""
    def loop() -> None:
        while True:
            print(f"[AutoAnalyze] {datetime.now()} 自动分析...")
            stats, errors, warnings, all_times, keyword_hits, anomaly_hits = analyze_logs()
            trend_img = plot_trend(all_times)
            generate_report(stats, errors, warnings, trend_img, keyword_hits, anomaly_hits)
            send_alert(errors, warnings, anomaly_hits)
            time.sleep(interval_min * 60)
    Thread(target=loop, daemon=True).start()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='日志分析与可视化工具')
    parser.add_argument('--keyword', help='关键字检索')
    parser.add_argument('--anomaly', nargs='*', help='异常模式正则')
    parser.add_argument('--web', action='store_true', help='启动Web可视化')
    parser.add_argument('--elk', action='store_true', help='导出ELK/Graylog JSON')
    parser.add_argument('--auto', action='store_true', help='定时自动分析')
    args = parser.parse_args()

    if args.web:
        start_web_dashboard()
    elif args.elk:
        export_to_json()
    else:
        anomaly_patterns = args.anomaly if args.anomaly else None
        stats, errors, warnings, all_times, keyword_hits, anomaly_hits = analyze_logs(args.keyword, anomaly_patterns)
        trend_img = plot_trend(all_times)
        report_path = generate_report(stats, errors, warnings, trend_img, keyword_hits, anomaly_hits, args.keyword, anomaly_patterns)
        print(f'日志分析报告已生成: {report_path}')
        send_alert(errors, warnings, anomaly_hits)
        if args.auto:
            schedule_auto_analyze()
            while True:
                time.sleep(3600) 