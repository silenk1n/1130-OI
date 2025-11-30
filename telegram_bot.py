#!/usr/bin/env python3
"""
Telegram Bot推送功能
用于发送监控提醒
"""

import requests
import os
from typing import Optional


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
        funding_direction = "正" if funding_rate > 0 else "负"
        funding_percent = abs(funding_rate) * 100

        message = f"🚨 <b>监控提醒</b> 🚨\n\n"
        message += f"<b>交易对:</b> {symbol}\n"
        message += f"<b>资金费率:</b> {funding_rate:.6f} ({funding_direction}{funding_percent:.3f}%)\n"
        message += f"<b>持仓量比率:</b> {oi_ratio:.2f}x\n"
        message += f"<b>当前持仓量:</b> {current_oi:,.0f}\n\n"
        message += f"<b>触发条件:</b>\n"
        message += f"• 资金费率绝对值 > 0.1%\n"
        message += f"• 短期持仓量激增 (3次/10次 > 2x)\n\n"
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