#!/usr/bin/env python3
"""
监控系统调度器
每5分钟执行一次数据采集和监控
"""

import time
import schedule
from datetime import datetime
from data_collector import run_collection_cycle
from monitor import FundingOIMonitor


def monitoring_job():
    """监控任务函数"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 执行监控任务...")

    try:
        # 第一步：数据采集
        print("📊 执行数据采集...")
        success, errors = run_collection_cycle()
        print(f"数据采集完成: {success} 成功, {errors} 失败")

        # 第二步：监控分析
        print("🔍 执行监控分析...")
        monitor = FundingOIMonitor()
        alerts_found, alerts_sent = monitor.run_monitoring()

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 监控任务完成: 发现 {alerts_found} 个提醒，发送 {alerts_sent} 个提醒")

    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 监控任务失败: {e}")


def run_monitor_scheduler():
    """运行监控调度器"""
    print("Binance永续合约监控系统调度器")
    print("=" * 60)
    print("调度器已启动，每5分钟自动执行数据采集和监控")
    print("监控条件:")
    print("• 资金费率绝对值 > 0.1%")
    print("• 短期持仓量激增 (最近3次/最近10次 > 2x)")
    print("按 Ctrl+C 停止调度器")
    print("=" * 60)

    # 设置定时任务
    schedule.every(5).minutes.do(monitoring_job)

    # 立即执行一次
    monitoring_job()

    # 主循环
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 监控调度器已停止")
            break
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 调度器错误: {e}")
            time.sleep(60)  # 出错后等待1分钟再继续


if __name__ == "__main__":
    run_monitor_scheduler()