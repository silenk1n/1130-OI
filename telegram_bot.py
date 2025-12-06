#!/usr/bin/env python3
"""
Telegram Bot推送功能
用于发送监控提醒
"""

import requests
import os
from typing import Optional, List, Dict
from datetime import datetime


class TelegramBot:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        初始化Telegram Bot

        Args:
            bot_token: Telegram Bot Token
            chat_id: 接收消息的Chat ID
        """
        # 从环境变量获取配置，如果没有则使用参数
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')

        if not self.bot_token or not self.chat_id:
            raise ValueError("请设置TELEGRAM_BOT_TOKEN和TELEGRAM_CHAT_ID环境变量")

    def send_message(self, message: str) -> bool:
        """
        发送消息到Telegram

        Args:
            message: 要发送的消息内容

        Returns:
            bool: 发送是否成功
        """
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            print(f"Telegram消息发送成功: {message[:50]}...")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Telegram消息发送失败: {e}")
            return False

    def send_alert(self, symbol: str, funding_rate: float, oi_ratio: float, current_oi: float,
                   chart_path: str = None) -> bool:
        """
        发送监控提醒

        Args:
            symbol: 交易对
            funding_rate: 资金费率
            oi_ratio: OI比率 (最近3次均值 / 最近10次均值)
            current_oi: 当前持仓量
            chart_path: 图表文件路径（可选）

        Returns:
            bool: 发送是否成功
        """
        # 格式化消息
        if funding_rate is not None:
            funding_direction = "正" if funding_rate > 0 else "负"
            funding_percent = abs(funding_rate) * 100
        else:
            funding_direction = "N/A"
            funding_percent = 0

        message = f"🚨 <b>监控提醒</b> 🚨\n\n"
        message += f"<b>交易对:</b> {symbol}\n"
        if funding_rate is not None:
            message += f"<b>资金费率:</b> {funding_rate:.6f} ({funding_direction}{funding_percent:.3f}%)\n"
        else:
            message += f"<b>资金费率:</b> N/A\n"
        message += f"<b>持仓量比率:</b> {oi_ratio:.2f}x\n" if oi_ratio is not None else "<b>持仓量比率:</b> N/A\n"
        message += f"<b>当前持仓量:</b> {current_oi:,.0f}\n\n" if current_oi is not None else "<b>当前持仓量:</b> N/A\n\n"
        message += f"<b>触发条件:</b>\n"
        message += f"• 资金费率绝对值 > 0.1%\n"
        if oi_ratio is not None:
            message += f"• 短期持仓量激增 (3次/10次 > 2x)\n\n"
        else:
            message += f"• 小市值币种 - 仅需满足资金费率条件\n\n"
        message += f"⚠️ 注意风险控制！"

        # 如果有图表，发送带图片的消息
        if chart_path and os.path.exists(chart_path):
            return self.send_photo(chart_path, message)
        else:
            return self.send_message(message)

    def send_photo(self, photo_path: str, caption: str = "") -> bool:
        """
        发送图片到Telegram

        Args:
            photo_path: 图片文件路径
            caption: 图片说明文字

        Returns:
            bool: 发送是否成功
        """
        url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"

        try:
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption,
                    'parse_mode': 'HTML'
                }

                response = requests.post(url, files=files, data=data, timeout=30)
                response.raise_for_status()
                print(f"Telegram图片发送成功: {photo_path}")
                return True

        except requests.exceptions.RequestException as e:
            print(f"Telegram图片发送失败: {e}")
            # 如果图片发送失败，尝试发送纯文本消息
            return self.send_message(caption)

    def send_combined_alerts(self, alerts: List[Dict]) -> bool:
        """
        发送合并的警报消息，按照资金费率绝对值从高到低排序

        Args:
            alerts: 警报列表，每个警报是一个字典，包含:
                - symbol: 交易对名称
                - funding_rate: 资金费率（可能为None）
                - oi_ratio: OI比率（可能为None）
                - current_oi: 当前持仓量（可能为None）
                - market_cap: 市值（可能为None）

        Returns:
            bool: 发送是否成功
        """
        if not alerts:
            print("没有警报需要发送")
            return True

        # 按照资金费率绝对值从高到低排序
        # 注意：funding_rate可能为None，需要处理
        def get_funding_rate_abs(alert):
            funding_rate = alert.get('funding_rate')
            if funding_rate is None:
                return -float('inf')  # None值排在最后
            return abs(funding_rate)

        sorted_alerts = sorted(alerts, key=get_funding_rate_abs, reverse=True)

        # 构建合并消息
        message_parts = [
            "🚨 <b>合并监控警报</b> 🚨\n\n",
            f"📊 发现 {len(alerts)} 个异常交易对\n",
            f"⏰ 报告时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n",
            "<b>交易对详情（按资金费率绝对值排序）:</b>\n"
        ]

        for i, alert in enumerate(sorted_alerts, 1):
            symbol = alert.get('symbol', 'N/A')
            funding_rate = alert.get('funding_rate')
            oi_ratio = alert.get('oi_ratio')
            current_oi = alert.get('current_oi')
            market_cap = alert.get('market_cap')

            # 格式化资金费率
            if funding_rate is not None:
                funding_rate_str = f"{funding_rate:.6f}"
                funding_rate_pct = funding_rate * 100
                funding_direction = "正" if funding_rate > 0 else "负"
                funding_info = f"{funding_rate_str} ({funding_direction}{funding_rate_pct:.3f}%)"
            else:
                funding_info = "N/A"

            # 格式化OI比率
            oi_ratio_str = f"{oi_ratio:.2f}x" if oi_ratio is not None else "N/A"

            # 格式化当前持仓量
            if current_oi is not None:
                current_oi_str = f"{current_oi:,.0f}"
            else:
                current_oi_str = "N/A"

            # 格式化市值（如果有）
            market_cap_info = ""
            if market_cap is not None:
                if market_cap >= 1000000000:  # 超过10亿美元
                    market_cap_str = f"${market_cap/1000000000:.2f}B"
                elif market_cap >= 1000000:   # 超过100万美元
                    market_cap_str = f"${market_cap/1000000:.2f}M"
                else:
                    market_cap_str = f"${market_cap:,.0f}"
                market_cap_info = f" | 市值: {market_cap_str}"

            # 构建单行信息
            line = f"{i}. <code>{symbol}</code>\n"
            line += f"   资金费率: {funding_info}\n"
            line += f"   OI比率: {oi_ratio_str}"
            if market_cap_info:
                line += market_cap_info
            line += "\n"

            message_parts.append(line)

        message_parts.extend([
            f"\n<b>触发条件:</b>\n",
            f"• 资金费率绝对值 > 0.1%\n",
            f"• 大市值币种需同时满足持仓量比率 > 2x\n",
            f"• 小市值币种只需满足资金费率条件\n\n",
            f"⚠️ 注意风险控制！"
        ])

        message = "".join(message_parts)
        return self.send_message(message)


def test_telegram_bot():
    """测试Telegram Bot功能"""
    try:
        bot = TelegramBot()
        success = bot.send_message("🔔 测试消息: Binance监控系统正常运行")
        if success:
            print("Telegram Bot测试成功！")
        else:
            print("Telegram Bot测试失败！")
    except ValueError as e:
        print(f"Telegram Bot配置错误: {e}")
        print("请设置环境变量:")
        print("export TELEGRAM_BOT_TOKEN='你的Bot Token'")
        print("export TELEGRAM_CHAT_ID='你的Chat ID'")


if __name__ == "__main__":
    test_telegram_bot()