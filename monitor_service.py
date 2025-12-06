#!/usr/bin/env python3
"""
Binance永续合约监控服务
长期运行的数据采集和分析服务
每半小时生成分析报告
"""

import time
import schedule
import logging
import sys
import os
from datetime import datetime, timedelta
from data_collector import run_collection_cycle
from data_analyzer import DataAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor_service.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class MonitorService:
    def __init__(self):
        self.analyzer = DataAnalyzer()
        self.setup_schedule()

    def setup_schedule(self):
        """设置定时任务"""
        # 每15分钟采集数据
        schedule.every(15).minutes.do(self.collect_data_job)

        # 每半小时生成报告
        schedule.every(30).minutes.do(self.generate_report_job)

        # 每天凌晨清理旧日志
        schedule.every().day.at("00:00").do(self.cleanup_job)

    def collect_data_job(self):
        """数据采集任务"""
        try:
            logger.info("开始执行数据采集任务...")
            success, errors = run_collection_cycle()
            logger.info(f"数据采集完成: {success} 成功, {errors} 失败")
        except Exception as e:
            logger.error(f"数据采集任务失败: {e}")

    def generate_report_job(self):
        """生成报告任务"""
        try:
            logger.info("开始生成分析报告...")

            # 生成24小时分析报告
            self.analyzer.generate_report(24)

            # 同时生成6小时短期报告
            print("\n" + "="*60)
            print("短期分析报告 (6小时)")
            print("="*60)
            self.analyzer.generate_report(6)

            logger.info("分析报告生成完成")

        except Exception as e:
            logger.error(f"生成报告任务失败: {e}")

    def cleanup_job(self):
        """清理任务"""
        try:
            # 清理7天前的日志文件
            cutoff_time = datetime.now() - timedelta(days=7)
            log_file = 'monitor_service.log'

            if os.path.exists(log_file):
                file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                if file_time < cutoff_time:
                    os.remove(log_file)
                    logger.info("已清理旧日志文件")

        except Exception as e:
            logger.error(f"清理任务失败: {e}")

    def run(self):
        """运行监控服务"""
        logger.info("Binance永续合约监控服务启动")
        logger.info("服务配置:")
        logger.info("  - 每5分钟采集数据")
        logger.info("  - 每半小时生成报告")
        logger.info("  - 按 Ctrl+C 停止服务")

        # 立即执行一次初始任务
        self.collect_data_job()
        self.generate_report_job()

        # 主循环
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("监控服务已停止")
                break
            except Exception as e:
                logger.error(f"监控服务错误: {e}")
                time.sleep(60)  # 出错后等待1分钟再继续

def main():
    """主函数"""
    service = MonitorService()
    service.run()

if __name__ == "__main__":
    main()