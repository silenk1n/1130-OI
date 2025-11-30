#!/usr/bin/env python3
"""
Binance永续合约数据采集器
每5分钟自动获取所有USDT永续合约交易对数据并保存到CSV文件
"""

import csv
import os
import time
from datetime import datetime
from typing import Dict, List
from binance_data_snapshot import BinanceDataSnapshot
from binance_symbols import get_usdt_perpetual_symbols


class DataCollector:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.snapshot = BinanceDataSnapshot()

        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)

    def save_to_csv(self, symbol: str, data: Dict[str, any]):
        """将数据保存到CSV文件"""
        csv_file = os.path.join(self.data_dir, f"{symbol}.csv")

        # CSV文件头
        fieldnames = [
            'timestamp',
            'mark_price',
            'index_price',
            'basis',
            'basis_percent',
            'last_funding_rate',
            'next_funding_time',
            'oi',
            'long_short_account_ratio',
            'top_trader_account_ls_ratio',
            'top_trader_position_ls_ratio',
            'taker_buy_sell_ratio'
        ]

        # 检查文件是否存在，如果不存在则写入表头
        file_exists = os.path.isfile(csv_file)

        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            # 准备要写入的数据
            row_data = {
                'timestamp': data['timestamp'],
                'mark_price': data['mark_price'],
                'index_price': data['index_price'],
                'basis': data['basis'],
                'basis_percent': data['basis_percent'],
                'last_funding_rate': data['last_funding_rate'],
                'next_funding_time': data['next_funding_time'],
                'oi': data['oi'],
                'long_short_account_ratio': data['long_short_account_ratio'],
                'top_trader_account_ls_ratio': data['top_trader_account_ls_ratio'],
                'top_trader_position_ls_ratio': data['top_trader_position_ls_ratio'],
                'taker_buy_sell_ratio': data['taker_buy_sell_ratio']
            }

            writer.writerow(row_data)

    def collect_data_for_symbols(self, symbols: List[str]):
        """为指定的交易对列表收集数据"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始收集 {len(symbols)} 个交易对的数据...")

        success_count = 0
        error_count = 0

        for symbol in symbols:
            try:
                # 获取数据快照
                data = self.snapshot.get_data_snapshot(symbol)

                # 保存到CSV
                self.save_to_csv(symbol, data)

                success_count += 1
                print(f"  ✓ {symbol}: 数据已保存")

                # 添加延迟避免API限制
                time.sleep(0.1)

            except Exception as e:
                error_count += 1
                print(f"  ✗ {symbol}: 错误 - {e}")

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 数据收集完成: {success_count} 成功, {error_count} 失败")
        return success_count, error_count

    def collect_all_data(self):
        """收集所有USDT永续合约交易对的数据"""
        symbols = get_usdt_perpetual_symbols()
        return self.collect_data_for_symbols(symbols)

    def collect_top_symbols_data(self, limit: int = 50):
        """收集交易量前N的交易对数据"""
        from binance_symbols import get_top_symbols_by_volume
        symbols = get_top_symbols_by_volume(limit)
        return self.collect_data_for_symbols(symbols)


def run_collection_cycle():
    """运行一次数据收集周期"""
    collector = DataCollector()

    # 收集前50个交易量最大的交易对数据
    success, errors = collector.collect_top_symbols_data(50)

    return success, errors


def main():
    """主函数 - 单次运行测试"""
    print("Binance永续合约数据采集器")
    print("=" * 50)

    collector = DataCollector()

    # 测试收集前10个交易对的数据
    test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "XRPUSDT",
                   "DOGEUSDT", "BNBUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT"]

    print(f"测试收集 {len(test_symbols)} 个交易对的数据...")
    success, errors = collector.collect_data_for_symbols(test_symbols)

    print(f"\n测试完成: {success} 成功, {errors} 失败")
    print(f"数据已保存到 {collector.data_dir}/ 目录")


if __name__ == "__main__":
    main()