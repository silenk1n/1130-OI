#!/usr/bin/env python3
"""
Binance永续合约自动监控系统
一体化版本 - 只需运行一次，自动完成所有功能

功能：
1. 自动数据采集（每5分钟）
2. 自动监控分析（每5分钟）
3. 自动推送提醒（满足条件时）
4. 运行状态报告（每30分钟）
5. 启动成功通知（首次运行）
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
from dotenv import load_dotenv


class Config:
    """配置管理类"""

    def __init__(self):
        # 加载环境变量
        load_dotenv()

        # Telegram配置
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

        # 应用设置
        self.DATA_DIR = os.getenv('DATA_DIR', 'data')
        self.CHARTS_DIR = os.getenv('CHARTS_DIR', 'charts')
        self.COLLECTION_INTERVAL = int(os.getenv('COLLECTION_INTERVAL', '300'))  # 5分钟

        # 监控阈值
        self.FUNDING_RATE_THRESHOLD = float(os.getenv('FUNDING_RATE_THRESHOLD', '0.001'))  # 0.1%
        self.OI_RATIO_THRESHOLD = float(os.getenv('OI_RATIO_THRESHOLD', '2.0'))  # 2x
        self.MARKET_CAP_THRESHOLD = float(os.getenv('MARKET_CAP_THRESHOLD', '100000000'))  # 1亿美元

        # 确保目录存在
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.CHARTS_DIR, exist_ok=True)

    def validate_telegram_config(self) -> bool:
        """验证Telegram配置"""
        if not self.TELEGRAM_BOT_TOKEN:
            print("❌ TELEGRAM_BOT_TOKEN 未配置")
            return False
        if not self.TELEGRAM_CHAT_ID:
            print("❌ TELEGRAM_CHAT_ID 未配置")
            return False
        return True


class TelegramBot:
    """Telegram Bot推送类"""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}"

    def send_message(self, message: str) -> bool:
        """发送文本消息"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.config.TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            success = response.status_code == 200
            if success:
                print(f"Telegram消息发送成功: {message[:50]}...")
            return success
        except Exception as e:
            print(f"发送Telegram消息失败: {e}")
            return False

    def send_startup_notification(self) -> bool:
        """发送启动成功通知"""
        message = (
            "🚀 <b>Binance永续合约监控系统已启动</b>\n\n"
            "✅ 系统状态：运行中\n"
            "📊 数据采集：每5分钟（所有USDT永续合约）\n"
            "🔔 监控提醒：实时推送\n"
            "📈 状态报告：每30分钟\n\n"
            f"启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "系统将持续监控所有USDT永续合约的资金费率和持仓量变化"
        )
        return self.send_message(message)

    def send_status_report(self, stats: Dict) -> bool:
        """发送运行状态报告"""
        message = (
            "📊 <b>系统运行状态报告</b>\n\n"
            f"⏰ 报告时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"📈 数据采集：{stats['collection_success']} 成功, {stats['collection_errors']} 失败\n"
            f"🔔 监控提醒：{stats['alerts_found']} 发现, {stats['alerts_sent']} 发送\n"
            f"💾 数据文件：{stats['data_files']} 个\n"
            f"📦 数据大小：{stats['data_size']}\n"
            f"🧹 上次清理：{stats['last_cleanup_time']}\n"
            f"💰 监控交易对：{stats['total_symbols']} 个\n"
            f"🔄 运行时长：{stats['uptime']}\n"
            f"📡 系统状态：{'✅ 正常' if stats['system_healthy'] else '⚠️ 异常'}\n\n"
            "下次报告：30分钟后"
        )
        return self.send_message(message)

    def send_alert(self, symbol: str, funding_rate: float, oi_ratio: float, current_oi: float, market_cap: Optional[float] = None) -> bool:
        """发送监控提醒"""
        funding_rate_pct = funding_rate * 100

        # 构建市值信息
        market_cap_info = ""
        if market_cap is not None:
            if market_cap >= 1000000000:  # 超过10亿美元
                market_cap_str = f"${market_cap/1000000000:.2f}B"
            elif market_cap >= 1000000:   # 超过100万美元
                market_cap_str = f"${market_cap/1000000:.2f}M"
            else:
                market_cap_str = f"${market_cap:,.0f}"

            market_cap_info = f"\n💰 市值：{market_cap_str}"

            # 添加市值分类说明
            if market_cap < 100000000:  # 小于1亿美元
                market_cap_info += " (小市值币种 - 满足任一条件触发)"
            else:
                market_cap_info += " (大市值币种 - 需同时满足两个条件)"

        # 处理持仓量比率显示
        oi_ratio_info = f"{oi_ratio:.2f}x" if oi_ratio is not None else "N/A"

        message = (
            "🚨 <b>监控提醒：发现异常交易对</b>\n\n"
            f"💰 交易对：<code>{symbol}</code>\n"
            f"📊 资金费率：{funding_rate_pct:.4f}%\n"
            f"📈 持仓量比率：{oi_ratio_info}\n"
            f"📦 当前持仓量：{current_oi:,.0f}"
            f"{market_cap_info}\n\n"
            f"⏰ 发现时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "💡 建议：关注资金费率变化和持仓量趋势"
        )
        return self.send_message(message)


class BinanceDataCollector:
    """Binance数据采集器"""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = "https://fapi.binance.com"
        self.futures_data_url = "https://fapi.binance.com/futures/data"

    def get_mark_price(self, symbol: str) -> Dict[str, Any]:
        """获取标记价格和资金费率"""
        url = f"{self.base_url}/fapi/v1/premiumIndex"
        params = {"symbol": symbol}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"获取 {symbol} 标记价格失败: {e}")
            return {}

    def get_open_interest(self, symbol: str) -> Dict[str, Any]:
        """获取持仓量"""
        url = f"{self.base_url}/fapi/v1/openInterest"
        params = {"symbol": symbol}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"获取 {symbol} 持仓量失败: {e}")
            return {}

    def get_funding_rate(self, symbol: str) -> Dict[str, Any]:
        """获取最新资金费率"""
        url = f"{self.base_url}/fapi/v1/fundingRate"
        params = {"symbol": symbol, "limit": 1}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data[0] if data else {}
        except Exception as e:
            print(f"获取 {symbol} 资金费率失败: {e}")
            return {}

    def get_all_usdt_perpetual_symbols(self) -> List[str]:
        """获取所有USDT永续合约交易对"""
        url = f"{self.base_url}/fapi/v1/exchangeInfo"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            usdt_symbols = []
            for symbol_info in data["symbols"]:
                if (symbol_info["quoteAsset"] == "USDT" and
                    symbol_info["contractType"] == "PERPETUAL" and
                    symbol_info["status"] == "TRADING"):
                    usdt_symbols.append(symbol_info["symbol"])

            print(f"获取到 {len(usdt_symbols)} 个USDT永续合约交易对")
            return sorted(usdt_symbols)
        except Exception as e:
            print(f"获取交易对信息失败: {e}")
            # 返回一些主要交易对作为备用
            return ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", "XRPUSDT", "DOTUSDT", "DOGEUSDT", "AVAXUSDT", "MATICUSDT"]

    def get_market_cap(self, symbol: str) -> Optional[float]:
        """获取币种市值（美元）
        注意：这是一个简化实现，实际使用时需要更准确的市值数据源
        """
        # 从交易对中提取基础币种
        base_asset = symbol.replace("USDT", "")

        # 这里使用一个简化的市值估算方法
        # 实际生产环境中应该使用专业的市值数据API
        try:
            # 获取现货价格
            spot_url = "https://api.binance.com/api/v3/ticker/price"
            params = {"symbol": symbol}
            response = requests.get(spot_url, params=params, timeout=5)

            if response.status_code == 200:
                price_data = response.json()
                price = float(price_data['price'])

                # 简化的流通量估算（实际应该从专业API获取）
                # 这里使用一个预设的流通量映射
                supply_map = {
                    "BTC": 19500000,   # 比特币流通量
                    "ETH": 120000000,  # 以太坊流通量
                    "BNB": 150000000,  # BNB流通量
                    "ADA": 35000000000, # Cardano流通量
                    "SOL": 400000000,  # Solana流通量
                    "XRP": 54000000000, # XRP流通量
                    "DOT": 1200000000, # Polkadot流通量
                    "DOGE": 140000000000, # Dogecoin流通量
                    "AVAX": 360000000, # Avalanche流通量
                    "MATIC": 10000000000, # Polygon流通量
                }

                # 如果币种在映射中，计算市值
                if base_asset in supply_map:
                    market_cap = price * supply_map[base_asset]
                    return market_cap
                else:
                    # 对于不在映射中的币种，返回None表示未知
                    return None

        except Exception as e:
            print(f"获取 {symbol} 市值失败: {e}")
            return None

        return None

    def get_data_snapshot(self, symbol: str) -> Dict[str, Any]:
        """获取完整数据快照"""
        # 获取标记价格和资金费率
        mark_data = self.get_mark_price(symbol)
        mark_price = float(mark_data.get("markPrice", 0)) if mark_data else 0
        index_price = float(mark_data.get("indexPrice", 0)) if mark_data else 0

        # 计算基差
        basis = mark_price - index_price
        basis_percent = (basis / index_price) * 100 if index_price != 0 else 0

        # 获取资金费率
        funding_data = self.get_funding_rate(symbol)

        # 获取持仓量
        oi_data = self.get_open_interest(symbol)

        # 编译完整快照
        snapshot = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "mark_price": mark_price,
            "index_price": index_price,
            "basis": basis,
            "basis_percent": basis_percent,
            "last_funding_rate": float(funding_data.get("fundingRate", 0)) if funding_data else 0,
            "next_funding_time": funding_data.get("fundingTime", 0) if funding_data else 0,
            "oi": float(oi_data.get("openInterest", 0)) if oi_data else 0
        }

        return snapshot

    def save_to_csv(self, symbol: str, data: Dict[str, any]):
        """将数据保存到CSV文件"""
        csv_file = os.path.join(self.config.DATA_DIR, f"{symbol}.csv")

        # CSV文件头
        fieldnames = [
            'timestamp',
            'mark_price',
            'index_price',
            'basis',
            'basis_percent',
            'last_funding_rate',
            'next_funding_time',
            'oi'
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
                'oi': data['oi']
            }

            writer.writerow(row_data)

    def collect_data(self) -> Tuple[int, int]:
        """收集数据"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始数据采集...")

        symbols = self.get_all_usdt_perpetual_symbols()
        success_count = 0
        error_count = 0

        print(f"开始采集 {len(symbols)} 个交易对的数据...")

        for i, symbol in enumerate(symbols, 1):
            try:
                # 获取数据快照
                data = self.get_data_snapshot(symbol)

                # 保存到CSV
                self.save_to_csv(symbol, data)

                success_count += 1
                if i % 20 == 0 or i == len(symbols):
                    print(f"  [{i}/{len(symbols)}] ✓ {symbol}: 数据已保存")

                # 添加延迟避免API限制
                time.sleep(0.1)

            except Exception as e:
                error_count += 1
                print(f"  ✗ {symbol}: 错误 - {e}")

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 数据采集完成: {success_count} 成功, {error_count} 失败")
        return success_count, error_count


class Monitor:
    """监控器"""

    def __init__(self, config: Config, telegram_bot: TelegramBot, data_collector: BinanceDataCollector):
        self.config = config
        self.telegram_bot = telegram_bot
        self.data_collector = data_collector

    def load_symbol_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """加载单个交易对的历史数据"""
        csv_file = os.path.join(self.config.DATA_DIR, f"{symbol}.csv")

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
        """计算持仓量比率：最近3次均值 / 最近10次均值"""
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

    def check_conditions(self, symbol: str) -> Tuple[bool, Optional[float], Optional[float], Optional[float], Optional[float]]:
        """检查交易对是否满足监控条件"""
        # 先获取市值
        market_cap = self.data_collector.get_market_cap(symbol)

        # 获取最新数据
        df = self.load_symbol_data(symbol)
        if df is None or len(df) == 0:
            # 没有数据时，无法判断
            return False, None, None, None, market_cap

        # 获取最新数据
        latest = df.iloc[-1]
        funding_rate = latest['last_funding_rate']
        current_oi = latest['oi']

        # 检查资金费率条件
        funding_condition = abs(funding_rate) > self.config.FUNDING_RATE_THRESHOLD

        # 判断条件：
        # 1. 对于市值 < 1亿美元的交易对：只需要满足资金费率条件
        # 2. 对于市值 >= 1亿美元的交易对：需要同时满足资金费率和持仓量条件
        # 3. 对于市值未知的交易对：默认按小市值币种处理（只需要满足资金费率条件）
        if market_cap is None or market_cap < self.config.MARKET_CAP_THRESHOLD:
            # 小市值币种或市值未知币种：只需要满足资金费率条件
            condition_met = funding_condition
            oi_ratio = None  # 小市值币种不需要OI比率
        else:
            # 大市值币种：需要同时满足资金费率和持仓量条件
            # 检查是否有足够数据计算OI比率
            if len(df) < 10:
                # 数据不足，无法计算OI比率
                condition_met = False
                oi_ratio = None
            else:
                # 计算OI比率
                oi_ratio = self.calculate_oi_ratio(df)
                if oi_ratio is None:
                    condition_met = False
                else:
                    # 检查OI条件
                    oi_condition = oi_ratio > self.config.OI_RATIO_THRESHOLD
                    condition_met = funding_condition and oi_condition

        # 返回结果
        return (condition_met, funding_rate, oi_ratio, current_oi, market_cap)

    def monitor_all_symbols(self) -> List[Dict]:
        """监控所有交易对"""
        csv_files = glob.glob(os.path.join(self.config.DATA_DIR, "*.csv"))
        symbols = [os.path.basename(f).replace('.csv', '') for f in csv_files]

        alerts = []

        print(f"开始监控 {len(symbols)} 个交易对...")

        for symbol in symbols:
            try:
                condition_met, funding_rate, oi_ratio, current_oi, market_cap = self.check_conditions(symbol)

                if condition_met:
                    alert_info = {
                        'symbol': symbol,
                        'funding_rate': funding_rate,
                        'oi_ratio': oi_ratio,
                        'current_oi': current_oi,
                        'market_cap': market_cap
                    }
                    alerts.append(alert_info)

                    print(f"🚨 发现符合条件的交易对: {symbol}")
                    print(f"   资金费率: {funding_rate:.6f}")
                    print(f"   OI比率: {oi_ratio:.2f}x")
                    print(f"   当前OI: {current_oi:,.0f}")
                    if market_cap:
                        print(f"   市值: ${market_cap:,.0f}")

                    # 发送提醒
                    success = self.telegram_bot.send_alert(symbol, funding_rate, oi_ratio, current_oi, market_cap)
                    if success:
                        print(f"✅ Telegram警报发送成功: {symbol}")
                    else:
                        print(f"❌ Telegram警报发送失败: {symbol}")

            except Exception as e:
                print(f"监控 {symbol} 时出错: {e}")
                continue

        return alerts


class AutoMonitorSystem:
    """自动监控系统"""

    def __init__(self):
        self.config = Config()
        self.telegram_bot = TelegramBot(self.config)
        self.data_collector = BinanceDataCollector(self.config)
        self.monitor = Monitor(self.config, self.telegram_bot, self.data_collector)

        # 运行统计
        self.start_time = datetime.now()
        self.collection_success_total = 0
        self.collection_errors_total = 0
        self.alerts_found_total = 0
        self.alerts_sent_total = 0

        # 文件管理
        self.data_size_threshold = 800 * 1024 * 1024  # 800MB
        self.last_cleanup_time = None

        # 状态标志
        self.system_started = False

    def calculate_data_size(self) -> int:
        """计算数据目录总大小（字节）"""
        total_size = 0
        for file_path in glob.glob(os.path.join(self.config.DATA_DIR, "*.csv")):
            try:
                total_size += os.path.getsize(file_path)
            except OSError:
                continue
        return total_size

    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def cleanup_old_data(self) -> Dict[str, any]:
        """清理旧数据，保留最近的数据"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始数据清理...")

        csv_files = glob.glob(os.path.join(self.config.DATA_DIR, "*.csv"))
        files_processed = 0
        files_cleaned = 0
        total_rows_removed = 0

        for csv_file in csv_files:
            try:
                # 读取CSV文件
                df = pd.read_csv(csv_file)
                original_rows = len(df)

                if original_rows <= 1000:  # 如果数据量不大，跳过清理
                    files_processed += 1
                    continue

                # 保留最近1000行数据
                df_cleaned = df.tail(1000)
                rows_removed = original_rows - len(df_cleaned)

                if rows_removed > 0:
                    # 保存清理后的数据
                    df_cleaned.to_csv(csv_file, index=False)
                    files_cleaned += 1
                    total_rows_removed += rows_removed
                    print(f"  ✓ {os.path.basename(csv_file)}: 保留 {len(df_cleaned)} 行，删除 {rows_removed} 行")

                files_processed += 1

            except Exception as e:
                print(f"  ✗ {os.path.basename(csv_file)}: 清理失败 - {e}")
                continue

        self.last_cleanup_time = datetime.now()

        result = {
            'files_processed': files_processed,
            'files_cleaned': files_cleaned,
            'total_rows_removed': total_rows_removed,
            'cleanup_time': self.last_cleanup_time.strftime('%Y-%m-%d %H:%M:%S')
        }

        print(f"数据清理完成: 处理 {files_processed} 个文件，清理 {files_cleaned} 个文件，删除 {total_rows_removed} 行数据")
        return result

    def check_and_cleanup_data(self) -> Optional[Dict[str, any]]:
        """检查数据大小并执行清理"""
        current_size = self.calculate_data_size()

        if current_size >= self.data_size_threshold:
            print(f"数据大小 {self.format_file_size(current_size)} 超过阈值 {self.format_file_size(self.data_size_threshold)}，执行清理...")

            # 发送清理通知
            self.telegram_bot.send_message(
                f"🧹 <b>数据清理通知</b>\n\n"
                f"数据目录大小已达到 {self.format_file_size(current_size)}，\n"
                f"超过阈值 {self.format_file_size(self.data_size_threshold)}，\n"
                f"正在执行自动清理..."
            )

            # 执行清理
            cleanup_result = self.cleanup_old_data()

            # 发送清理完成通知
            new_size = self.calculate_data_size()
            self.telegram_bot.send_message(
                f"✅ <b>数据清理完成</b>\n\n"
                f"处理文件: {cleanup_result['files_processed']} 个\n"
                f"清理文件: {cleanup_result['files_cleaned']} 个\n"
                f"删除数据行: {cleanup_result['total_rows_removed']} 行\n"
                f"清理前大小: {self.format_file_size(current_size)}\n"
                f"清理后大小: {self.format_file_size(new_size)}\n"
                f"清理时间: {cleanup_result['cleanup_time']}"
            )

            return cleanup_result

        return None

    def get_system_stats(self) -> Dict:
        """获取系统统计信息"""
        # 计算运行时长
        uptime = datetime.now() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        # 统计数据文件
        data_files = len(glob.glob(os.path.join(self.config.DATA_DIR, "*.csv")))

        # 计算数据大小
        data_size = self.calculate_data_size()
        data_size_str = self.format_file_size(data_size)

        # 获取总交易对数量
        total_symbols = len(self.data_collector.get_all_usdt_perpetual_symbols())

        return {
            'collection_success': self.collection_success_total,
            'collection_errors': self.collection_errors_total,
            'alerts_found': self.alerts_found_total,
            'alerts_sent': self.alerts_sent_total,
            'data_files': data_files,
            'data_size': data_size_str,
            'data_size_bytes': data_size,
            'total_symbols': total_symbols,
            'uptime': uptime_str,
            'system_healthy': True,
            'last_cleanup_time': self.last_cleanup_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_cleanup_time else '从未清理'
        }

    def collection_job(self):
        """数据采集任务"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 执行数据采集...")

        try:
            success, errors = self.data_collector.collect_data()
            self.collection_success_total += success
            self.collection_errors_total += errors

            # 检查并执行数据清理（如果需要）
            self.check_and_cleanup_data()

            # 采集完成后立即执行监控
            self.monitoring_job()

        except Exception as e:
            print(f"数据采集失败: {e}")

    def monitoring_job(self):
        """监控任务"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 执行监控检查...")

        try:
            alerts = self.monitor.monitor_all_symbols()
            self.alerts_found_total += len(alerts)
            self.alerts_sent_total += len(alerts)  # 简化：每个发现都发送

            if alerts:
                print(f"发现 {len(alerts)} 个符合条件的交易对，已发送提醒")
            else:
                print("✅ 未发现符合条件的交易对")

        except Exception as e:
            print(f"监控检查失败: {e}")

    def status_report_job(self):
        """状态报告任务"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 生成状态报告...")

        try:
            stats = self.get_system_stats()
            success = self.telegram_bot.send_status_report(stats)

            if success:
                print("✅ 状态报告发送成功")
            else:
                print("❌ 状态报告发送失败")

        except Exception as e:
            print(f"状态报告生成失败: {e}")

    def setup_schedule(self):
        """设置定时任务"""
        # 每5分钟执行数据采集和监控
        schedule.every(5).minutes.do(self.collection_job)

        # 每30分钟执行状态报告
        schedule.every(30).minutes.do(self.status_report_job)

        print("定时任务设置完成:")
        print("  📊 数据采集: 每5分钟（所有USDT永续合约）")
        print("  🔔 监控检查: 每5分钟")
        print("  📈 状态报告: 每30分钟")

    def run(self):
        """运行自动监控系统"""
        print("🚀 Binance永续合约自动监控系统")
        print("=" * 50)

        # 验证配置
        if not self.config.validate_telegram_config():
            print("❌ Telegram配置错误，请检查 .env 文件")
            return

        # 发送启动通知
        print("发送启动通知...")
        if self.telegram_bot.send_startup_notification():
            print("✅ 启动通知发送成功")
        else:
            print("❌ 启动通知发送失败")

        # 设置定时任务
        self.setup_schedule()

        # 立即执行一次数据采集和监控
        print("\n执行首次数据采集和监控...")
        self.collection_job()

        print("\n" + "=" * 50)
        print("系统已启动，开始自动运行...")
        print("按 Ctrl+C 停止系统")
        print("=" * 50)

        self.system_started = True

        # 主循环
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 系统已停止")
                break
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 系统错误: {e}")
                time.sleep(60)  # 出错后等待1分钟再继续


def main():
    """主函数"""
    try:
        system = AutoMonitorSystem()
        system.run()
    except Exception as e:
        print(f"系统启动失败: {e}")
        print("请检查配置和网络连接")


if __name__ == "__main__":
    main()