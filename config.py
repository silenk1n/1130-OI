#!/usr/bin/env python3
"""
Configuration loader for the Binance monitoring system
Loads settings from environment variables or .env file
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the application"""

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', '')

    # Binance API Configuration (optional)
    BINANCE_API_KEY: str = os.getenv('BINANCE_API_KEY', '')
    BINANCE_API_SECRET: str = os.getenv('BINANCE_API_SECRET', '')

    # Application Settings
    DATA_DIR: str = os.getenv('DATA_DIR', 'data')
    CHARTS_DIR: str = os.getenv('CHARTS_DIR', 'charts')
    COLLECTION_INTERVAL: int = int(os.getenv('COLLECTION_INTERVAL', '300'))  # 5 minutes

    # Monitoring Thresholds
    FUNDING_RATE_THRESHOLD: float = float(os.getenv('FUNDING_RATE_THRESHOLD', '0.001'))  # 0.1%
    OI_RATIO_THRESHOLD: float = float(os.getenv('OI_RATIO_THRESHOLD', '2.0'))  # 2x

    @classmethod
    def validate_telegram_config(cls) -> bool:
        """Validate that Telegram configuration is set"""
        if not cls.TELEGRAM_BOT_TOKEN:
            print("❌ TELEGRAM_BOT_TOKEN is not set")
            return False
        if not cls.TELEGRAM_CHAT_ID:
            print("❌ TELEGRAM_CHAT_ID is not set")
            return False
        return True

    @classmethod
    def print_config_summary(cls):
        """Print a summary of the current configuration"""
        print("📋 Configuration Summary:")
        print(f"  • Telegram Bot: {'✅ Configured' if cls.TELEGRAM_BOT_TOKEN else '❌ Not configured'}")
        print(f"  • Telegram Chat: {'✅ Configured' if cls.TELEGRAM_CHAT_ID else '❌ Not configured'}")
        print(f"  • Binance API: {'✅ Configured' if cls.BINANCE_API_KEY else '❌ Not configured'}")
        print(f"  • Data Directory: {cls.DATA_DIR}")
        print(f"  • Collection Interval: {cls.COLLECTION_INTERVAL} seconds")
        print(f"  • Funding Rate Threshold: {cls.FUNDING_RATE_THRESHOLD:.4f}")
        print(f"  • OI Ratio Threshold: {cls.OI_RATIO_THRESHOLD:.1f}x")


def get_config() -> Config:
    """Get the configuration instance"""
    return Config


def setup_environment():
    """Setup environment and validate configuration"""
    # Load environment variables
    load_dotenv()

    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found. Using environment variables only.")
        print("   To use a .env file, copy .env.example to .env and fill in your values.")

    # Print configuration summary
    Config.print_config_summary()

    # Validate Telegram configuration
    if not Config.validate_telegram_config():
        print("\n📝 Setup Instructions:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your Telegram Bot Token and Chat ID")
        print("3. Get Bot Token from @BotFather on Telegram")
        print("4. Get Chat ID by sending a message to your bot")
        print("\nOr set environment variables:")
        print("  export TELEGRAM_BOT_TOKEN='your_bot_token'")
        print("  export TELEGRAM_CHAT_ID='your_chat_id'")
        return False

    return True


if __name__ == "__main__":
    setup_environment()