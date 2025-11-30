#!/usr/bin/env python3
"""
Binance永续合约持仓量监控系统
融合版本 - 包含数据采集、分析和定时调度功能
"""

import requests
import json
import time
import csv
import os
import pandas as pd
import schedule
import glob
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta


class BinanceDataSnapshot:
    """Binance永续合约数据快照类"""

    def __init__(self):
        self.base_url = "https://fapi.binance.com"
        self.futures_data_url = "https://fapi.binance.com/futures/data"

    def get_mark_price(self, symbol: str) -> Dict[str, Any]:
        """获取标记价格和资金费率"""
        url = f"{self.base_url}/fapi/v1/premiumIndex"
        params = {"symbol": symbol}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching mark price for {symbol}: {e}")
            return {}

    def get_index_price(self, symbol: str) -> Optional[float]:
        """获取指数价格"""
        mark_data = self.get_mark_price(symbol)
        if mark_data and "indexPrice" in mark_data:
            return float(mark_data["indexPrice"])

        # 备用方法
        url = f"{self.base_url}/fapi/v1/indexInfo"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data:
                if item.get("symbol") == symbol:
                    return float(item.get("indexPrice", 0))
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching index price for {symbol}: {e}")
            return None

    def calculate_basis(self, mark_price: float, index_price: float) -> Dict[str, float]:
        """计算基差和基差百分比"""
        if index_price == 0:
            return {"basis": 0, "basis_percent": 0}

        basis = mark_price - index_price
        basis_percent = (basis / index_price) * 100

        return {
            "basis": basis,
            "basis_percent": basis_percent
        }

    def get_funding_rate(self, symbol: str) -> Dict[str, Any]:
        """获取最新资金费率"""
        url = f"{self.base_url}/fapi/v1/fundingRate"
        params = {"symbol": symbol, "limit": 1}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data[0] if data else {}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching funding rate for {symbol}: {e}")
            return {}

    def get_open_interest(self, symbol: str) -> Dict[str, Any]:
        """获取持仓量"""
        url = f"{self.base_url}/fapi/v1/openInterest"
        params = {"symbol": symbol}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching open interest for {symbol}: {e}")
            return {}

    def get_long_short_ratio(self, symbol: str, period: str = "5m", limit: int = 1) -> Dict[str, Any]:
        """获取多空比数据"""

        def fetch_ratio(endpoint: str) -> List[Dict]:
            url = f"{self.futures_data_url}/{endpoint}"
            params = {
                "symbol": symbol,
                "period": period,
                "limit": limit
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {endpoint} for {symbol}: {e}")
                return []

        # 获取所有比率类型
        account_ratio = fetch_ratio("globalLongShortAccountRatio")
        top_account_ratio = fetch_ratio("topLongShortAccountRatio")
        top_position_ratio = fetch_ratio("topLongShortPositionRatio")

        return {
            "long_short_account_ratio": account_ratio[0] if account_ratio else {},
            "top_trader_account_ls_ratio": top_account_ratio[0] if top_account_ratio else {},
            "top_trader_position_ls_ratio": top_position_ratio[0] if top_position_ratio else {}
        }

    def get_taker_buy_sell_ratio(self, symbol: str, period: str = "5m", limit: int = 1) -> Dict[str, Any]:
        """获取主动买卖比"""
        url = f"{self.futures_data_url}/takerlongshortRatio"
        params = {
            "symbol": symbol,
            "period": period,
            "limit": limit
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data[0] if data else {}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching taker buy/sell ratio for {symbol}: {e}")
            return {}

    def get_data_snapshot(self, symbol: str) -> Dict[str, Any]:
        """获取完整数据快照"""
        print(f"获取 {symbol} 的数据快照...")

        # 获取标记价格和资金费率
        mark_data = self.get_mark_price(symbol)
        mark_price = float(mark_data.get("markPrice", 0)) if mark_data else 0

        # 获取指数价格
        index_price = self.get_index_price(symbol) or 0

        # 计算基差
        basis_data = self.calculate_basis(mark_price, index_price)

        # 获取资金费率
        funding_data = self.get_funding_rate(symbol)

        # 获取持仓量
        oi_data = self.get_open_interest(symbol)

        # 获取多空比
        ratio_data = self.get_long_short_ratio(symbol)

        # 获取主动买卖比
        taker_data = self.get_taker_buy_sell_ratio(symbol)

        # 编译完整快照
        snapshot = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "mark_price": mark_price,
            "index_price": index_price,
            "basis": basis_data["basis"],
            "basis_percent": basis_data["basis_percent"],
            "last_funding_rate": float(funding_data.get("fundingRate", 0)) if funding_data else 0,
            "next_funding_time": funding_data.get("fundingTime", 0) if funding_data else 0,
            "oi": float(oi_data.get("openInterest", 0)) if oi_data else 0,
            "long_short_account_ratio": float(ratio_data.get("long_short_account_ratio", {}).get("longShortRatio", 0)) if ratio_data.get("long_short_account_ratio") else 0,
            "top_trader_account_ls_ratio": float(ratio_data.get("top_trader_account_ls_ratio", {}).get("longShortRatio", 0)) if ratio_data.get("top_trader_account_ls_ratio") else 0,
            "top_trader_position_ls_ratio": float(ratio_data.get("top_trader_position_ls_ratio", {}).get("longShortRatio", 0)) if ratio_data.get("top_trader_position_ls_ratio") else 0,
            "taker_buy_sell_ratio": float(taker_data.get("buySellRatio", 0)) if taker_data else 0
        }

        return snapshot

    def get_multiple_symbols_snapshot(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """获取多个交易对的数据快照"""
        snapshots = {}

        for symbol in symbols:
            snapshot = self.get_data_snapshot(symbol)
            snapshots[symbol] = snapshot

            # 添加延迟避免API限制
            time.sleep(0.1)

        return snapshots


def get_usdt_perpetual_symbols():
    """获取所有USDT永续合约交易对"""
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        usdt_symbols = []
        for symbol_info in data["symbols"]:
            if (symbol_info["quoteAsset"] == "USDT" and
                symbol_info["contractType"] == "PERPETUAL" and
                symbol_info["status"] == "TRADING"):
                usdt_symbols.append(symbol_info["symbol"])

        return sorted(usdt_symbols)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange info: {e}")
        return []


def get_top_symbols_by_volume(limit: int = 20):
    """获取按24小时交易量排序的前N个交易对"""
    url = "https://fapi.binance.com/fapi/v1/ticker/24hr"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # 过滤USDT永续合约并按交易量排序
        usdt_symbols = []
        for ticker in data:
            if ticker["symbol"].endswith("USDT"):
                usdt_symbols.append({
                    "symbol": ticker["symbol"],
                    "volume": float(ticker["quoteVolume"])
                })

        # 按交易量降序排序
        usdt_symbols.sort(key=lambda x: x["volume"], reverse=True)

        return [symbol["symbol"] for symbol in usdt_symbols[:limit]]

    except requests.exceptions.RequestException as e:
        print(f"Error fetching 24hr ticker data: {e}")
        return []


class DataCollector:
    """数据采集器"""

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

    def collect_data_for_symbols(self, symbols: List[str]) -> Tuple[int, int]:
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

    def collect_all_data(self) -> Tuple[int, int]:
        """收集所有USDT永续合约交易对的数据"""
        symbols = get_usdt_perpetual_symbols()
        return self.collect_data_for_symbols(symbols)

    def collect_top_symbols_data(self, limit: int = 50) -> Tuple[int, int]:
        """收集交易量前N的交易对数据"""
        symbols = get_top_symbols_by_volume(limit)
        return self.collect_data_for_symbols(symbols)


def run_collection_cycle():
    """运行一次数据收集周期"""
    collector = DataCollector()

    # 收集前50个交易量最大的交易对数据
    success, errors = collector.collect_top_symbols_data(50)

    return success, errors


class DataAnalyzer:
    """数据分析器"""

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


def scheduler_job():
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
    schedule.every(5).minutes.do(scheduler_job)

    # 立即执行一次
    scheduler_job()

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


def main():
    """主函数 - 提供交互式菜单"""
    print("Binance永续合约持仓量监控系统")
    print("=" * 50)

    while True:
        print("\n请选择操作:")
        print("1. 单次数据采集")
        print("2. 数据分析报告")
        print("3. 启动定时采集")
        print("4. 查看可用交易对")
        print("5. 退出")

        choice = input("请输入选择 (1-5): ").strip()

        if choice == "1":
            print("\n执行单次数据采集...")
            collector = DataCollector()
            test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "XRPUSDT",
                           "DOGEUSDT", "BNBUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT"]
            print(f"测试收集 {len(test_symbols)} 个交易对的数据...")
            success, errors = collector.collect_data_for_symbols(test_symbols)
            print(f"\n测试完成: {success} 成功, {errors} 失败")
            print(f"数据已保存到 {collector.data_dir}/ 目录")

        elif choice == "2":
            print("\n生成数据分析报告...")
            analyzer = DataAnalyzer()
            symbols = analyzer.get_available_symbols()
            if not symbols:
                print("没有找到数据文件，请先运行数据采集")
            else:
                print(f"发现 {len(symbols)} 个交易对的数据文件")
                analyzer.generate_report(24)

        elif choice == "3":
            print("\n启动定时数据采集...")
            run_scheduler()

        elif choice == "4":
            print("\n获取可用交易对...")
            symbols = get_usdt_perpetual_symbols()
            print(f"总USDT永续合约交易对数量: {len(symbols)}")
            print("\n前20个交易对:")
            for symbol in symbols[:20]:
                print(f"  {symbol}")

        elif choice == "5":
            print("退出系统")
            break

        else:
            print("无效选择，请重新输入")


if __name__ == "__main__":
    main()