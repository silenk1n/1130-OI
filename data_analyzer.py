#!/usr/bin/env python3
"""
数据比对分析工具
用于分析历史数据的变化趋势
"""

import pandas as pd
import os
import glob
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class DataAnalyzer:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir

    def load_symbol_data(self, symbol: str) -> pd.DataFrame:
        """加载单个交易对的历史数据"""
        csv_file = os.path.join(self.data_dir, f"{symbol}.csv")

        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"数据文件不存在: {csv_file}")

        df = pd.read_csv(csv_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        return df

    def get_available_symbols(self) -> List[str]:
        """获取所有可用的交易对"""
        csv_files = glob.glob(os.path.join(self.data_dir, "*.csv"))
        symbols = [os.path.basename(f).replace('.csv', '') for f in csv_files]
        return sorted(symbols)

    def analyze_changes(self, symbol: str, hours: int = 24) -> Dict[str, any]:
        """分析指定时间段内的数据变化"""
        try:
            df = self.load_symbol_data(symbol)

            if len(df) < 2:
                return {"error": "数据不足"}

            # 计算时间范围
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_data = df[df['timestamp'] >= cutoff_time]

            if len(recent_data) < 2:
                return {"error": "指定时间段内数据不足"}

            # 获取最新和最旧的数据点
            latest = recent_data.iloc[-1]
            oldest = recent_data.iloc[0]

            # 计算变化
            changes = {
                'symbol': symbol,
                'period_hours': hours,
                'data_points': len(recent_data),
                'mark_price_change': latest['mark_price'] - oldest['mark_price'],
                'mark_price_change_pct': ((latest['mark_price'] - oldest['mark_price']) / oldest['mark_price']) * 100,
                'basis_change': latest['basis'] - oldest['basis'],
                'basis_percent_change': latest['basis_percent'] - oldest['basis_percent'],
                'funding_rate_change': latest['last_funding_rate'] - oldest['last_funding_rate'],
                'oi_change': latest['oi'] - oldest['oi'],
                'oi_change_pct': ((latest['oi'] - oldest['oi']) / oldest['oi']) * 100 if oldest['oi'] != 0 else 0,
                'account_ratio_change': latest['long_short_account_ratio'] - oldest['long_short_account_ratio'],
                'taker_ratio_change': latest['taker_buy_sell_ratio'] - oldest['taker_buy_sell_ratio'],
                'latest_timestamp': latest['timestamp'],
                'oldest_timestamp': oldest['timestamp']
            }

            return changes

        except Exception as e:
            return {"error": str(e)}

    def find_extreme_changes(self, hours: int = 24, top_n: int = 10) -> Dict[str, List[Dict]]:
        """查找变化最大的交易对"""
        symbols = self.get_available_symbols()
        all_changes = []

        print(f"分析 {len(symbols)} 个交易对在过去 {hours} 小时内的变化...")

        for symbol in symbols:
            changes = self.analyze_changes(symbol, hours)
            if 'error' not in changes:
                all_changes.append(changes)

        # 按不同指标排序
        results = {
            'price_increase': sorted(all_changes, key=lambda x: x['mark_price_change_pct'], reverse=True)[:top_n],
            'price_decrease': sorted(all_changes, key=lambda x: x['mark_price_change_pct'])[:top_n],
            'basis_increase': sorted(all_changes, key=lambda x: x['basis_percent_change'], reverse=True)[:top_n],
            'basis_decrease': sorted(all_changes, key=lambda x: x['basis_percent_change'])[:top_n],
            'funding_increase': sorted(all_changes, key=lambda x: x['funding_rate_change'], reverse=True)[:top_n],
            'funding_decrease': sorted(all_changes, key=lambda x: x['funding_rate_change'])[:top_n],
            'oi_increase': sorted(all_changes, key=lambda x: x['oi_change_pct'], reverse=True)[:top_n],
            'oi_decrease': sorted(all_changes, key=lambda x: x['oi_change_pct'])[:top_n]
        }

        return results

    def generate_report(self, hours: int = 24):
        """生成分析报告"""
        print(f"\n{'='*60}")
        print(f"Binance永续合约数据分析报告")
        print(f"时间范围: 过去 {hours} 小时")
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        extreme_changes = self.find_extreme_changes(hours)

        # 价格变化分析
        print(f"\n📈 价格涨幅Top 10:")
        for i, change in enumerate(extreme_changes['price_increase'], 1):
            print(f"  {i:2d}. {change['symbol']}: +{change['mark_price_change_pct']:.2f}%")

        print(f"\n📉 价格跌幅Top 10:")
        for i, change in enumerate(extreme_changes['price_decrease'], 1):
            print(f"  {i:2d}. {change['symbol']}: {change['mark_price_change_pct']:.2f}%")

        # 基差变化分析
        print(f"\n📊 基差扩大Top 10:")
        for i, change in enumerate(extreme_changes['basis_increase'], 1):
            print(f"  {i:2d}. {change['symbol']}: +{change['basis_percent_change']:.4f}%")

        print(f"\n📊 基差缩小Top 10:")
        for i, change in enumerate(extreme_changes['basis_decrease'], 1):
            print(f"  {i:2d}. {change['symbol']}: {change['basis_percent_change']:.4f}%")

        # 资金费率变化分析
        print(f"\n💰 资金费率上升Top 10:")
        for i, change in enumerate(extreme_changes['funding_increase'], 1):
            print(f"  {i:2d}. {change['symbol']}: +{change['funding_rate_change']:.6f}")

        print(f"\n💰 资金费率下降Top 10:")
        for i, change in enumerate(extreme_changes['funding_decrease'], 1):
            print(f"  {i:2d}. {change['symbol']}: {change['funding_rate_change']:.6f}")

        # 持仓量变化分析
        print(f"\n📦 持仓量增长Top 10:")
        for i, change in enumerate(extreme_changes['oi_increase'], 1):
            print(f"  {i:2d}. {change['symbol']}: +{change['oi_change_pct']:.2f}%")

        print(f"\n📦 持仓量减少Top 10:")
        for i, change in enumerate(extreme_changes['oi_decrease'], 1):
            print(f"  {i:2d}. {change['symbol']}: {change['oi_change_pct']:.2f}%")


def main():
    """主函数"""
    analyzer = DataAnalyzer()

    # 检查可用数据
    symbols = analyzer.get_available_symbols()
    print(f"发现 {len(symbols)} 个交易对的数据文件")

    if not symbols:
        print("没有找到数据文件，请先运行数据采集器")
        return

    # 生成24小时分析报告
    analyzer.generate_report(24)


if __name__ == "__main__":
    main()