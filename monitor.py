#!/usr/bin/env python3
"""
资金费率和持仓量监控系统
监控条件：
1. 资金费率绝对值 > 0.1% (|last_funding_rate| > 0.001)
2. 最近3次OI均值 / 最近10次OI均值 > 2
"""

import pandas as pd
import os
import glob
from typing import Dict, List, Tuple, Optional
from telegram_bot import TelegramBot
from chart_generator import ChartGenerator


class FundingOIMonitor:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.bot = TelegramBot()
        self.chart_generator = ChartGenerator()

    def load_symbol_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """加载单个交易对的历史数据"""
        csv_file = os.path.join(self.data_dir, f"{symbol}.csv")

        if not os.path.exists(csv_file):
            return None

        try:
            df = pd.read_csv(csv_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            return df
        except Exception as e:
            print(f"加载 {symbol} 数据失败: {e}")
            return None

    def calculate_oi_ratio(self, df: pd.DataFrame) -> Optional[float]:
        """
        计算持仓量比率：最近3次均值 / 最近10次均值

        Args:
            df: 包含oi列的数据框

        Returns:
            float: OI比率，如果数据不足返回None
        """
        if len(df) < 10:
            return None

        # 获取最近的数据点
        recent_data = df.tail(10)

        # 计算最近3次OI均值
        recent_3_avg = recent_data.tail(3)['oi'].mean()

        # 计算最近10次OI均值
        recent_10_avg = recent_data['oi'].mean()

        # 避免除零
        if recent_10_avg == 0:
            return None

        return recent_3_avg / recent_10_avg

    def check_conditions(self, symbol: str) -> Tuple[bool, Optional[float], Optional[float], Optional[float]]:
        """
        检查交易对是否满足监控条件

        Args:
            symbol: 交易对名称

        Returns:
            Tuple[bool, float, float, float]:
                (是否满足条件, 资金费率, OI比率, 当前OI)
        """
        df = self.load_symbol_data(symbol)
        if df is None or len(df) < 10:
            return False, None, None, None

        # 获取最新数据
        latest = df.iloc[-1]
        funding_rate = latest['last_funding_rate']
        current_oi = latest['oi']

        # 检查资金费率条件
        funding_condition = abs(funding_rate) > 0.001

        # 计算OI比率
        oi_ratio = self.calculate_oi_ratio(df)
        if oi_ratio is None:
            return False, funding_rate, None, current_oi

        # 检查OI条件
        oi_condition = oi_ratio > 2.0

        # 返回结果
        return (funding_condition and oi_condition, funding_rate, oi_ratio, current_oi)

    def monitor_all_symbols(self) -> List[Dict]:
        """
        监控所有交易对

        Returns:
            List[Dict]: 满足条件的交易对列表
        """
        csv_files = glob.glob(os.path.join(self.data_dir, "*.csv"))
        symbols = [os.path.basename(f).replace('.csv', '') for f in csv_files]

        alerts = []

        print(f"开始监控 {len(symbols)} 个交易对...")

        for symbol in symbols:
            try:
                condition_met, funding_rate, oi_ratio, current_oi = self.check_conditions(symbol)

                if condition_met:
                    alert_info = {
                        'symbol': symbol,
                        'funding_rate': funding_rate,
                        'oi_ratio': oi_ratio,
                        'current_oi': current_oi
                    }
                    alerts.append(alert_info)

                    print(f"🚨 发现符合条件的交易对: {symbol}")
                    print(f"   资金费率: {funding_rate:.6f}")
                    print(f"   OI比率: {oi_ratio:.2f}x" if oi_ratio is not None else "   OI比率: N/A")
                    print(f"   当前OI: {current_oi:,.0f}")

            except Exception as e:
                print(f"监控 {symbol} 时出错: {e}")
                continue

        return alerts

    def send_alerts(self, alerts: List[Dict]) -> int:
        """
        发送Telegram提醒

        Args:
            alerts: 提醒列表

        Returns:
            int: 成功发送的提醒数量
        """
        success_count = 0

        for alert in alerts:
            try:
                # 为每个提醒生成图表
                df = self.load_symbol_data(alert['symbol'])
                chart_path = None

                if df is not None and len(df) >= 5:
                    chart_path = self.chart_generator.generate_monitoring_chart(
                        symbol=alert['symbol'],
                        df=df,
                        funding_rate=alert['funding_rate'],
                        oi_ratio=alert['oi_ratio']
                    )

                # 发送提醒（包含图表）
                success = self.bot.send_alert(
                    symbol=alert['symbol'],
                    funding_rate=alert['funding_rate'],
                    oi_ratio=alert['oi_ratio'],
                    current_oi=alert['current_oi'],
                    chart_path=chart_path
                )
                if success:
                    success_count += 1
            except Exception as e:
                print(f"发送 {alert['symbol']} 提醒失败: {e}")

        return success_count

    def run_monitoring(self) -> Tuple[int, int]:
        """
        运行一次完整的监控

        Returns:
            Tuple[int, int]: (发现的提醒数量, 成功发送的提醒数量)
        """
        print("\n" + "="*60)
        print("资金费率和持仓量监控系统")
        print("="*60)

        # 发现符合条件的交易对
        alerts = self.monitor_all_symbols()

        if alerts:
            print(f"\n发现 {len(alerts)} 个符合条件的交易对，正在发送提醒...")

            # 发送Telegram提醒
            success_count = self.send_alerts(alerts)

            print(f"提醒发送完成: {success_count}/{len(alerts)} 成功")
            return len(alerts), success_count
        else:
            print("\n✅ 未发现符合条件的交易对")
            return 0, 0


def main():
    """主函数"""
    try:
        monitor = FundingOIMonitor()
        alerts_found, alerts_sent = monitor.run_monitoring()

        print(f"\n监控完成: 发现 {alerts_found} 个提醒，发送 {alerts_sent} 个提醒")

    except Exception as e:
        print(f"监控系统运行失败: {e}")
        print("请检查Telegram Bot配置")


if __name__ == "__main__":
    main()