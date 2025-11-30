#!/usr/bin/env python3
"""
定时数据采集调度器
每5分钟自动运行数据采集
"""

import time
import schedule
from datetime import datetime
from data_collector import run_collection_cycle


def job():
    """定时任务函数"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 执行定时数据采集...")

    try:
        success, errors = run_collection_cycle()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 采集完成: {success} 成功, {errors} 失败")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 采集失败: {e}")


def run_scheduler():
    """运行调度器"""
    print("Binance永续合约数据采集调度器")
    print("=" * 50)
    print("调度器已启动，每5分钟自动采集数据")
    print("按 Ctrl+C 停止调度器")
    print("=" * 50)

    # 设置定时任务
    schedule.every(5).minutes.do(job)

    # 立即执行一次
    job()

    # 主循环
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 调度器已停止")
            break
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 调度器错误: {e}")
            time.sleep(60)  # 出错后等待1分钟再继续


if __name__ == "__main__":
    run_scheduler()