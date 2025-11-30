#!/usr/bin/env python3
"""
Setup script for Binance monitoring system
Helps users configure their Telegram bot settings
"""

import os
import sys


def setup_configuration():
    """Interactive setup for configuration"""
    print("🔧 Binance Monitoring System Setup")
    print("=" * 50)

    # Check if .env file already exists
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        choice = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if choice != 'y':
            print("Setup cancelled.")
            return

    # Get Telegram Bot Token
    print("\n📱 Telegram Bot Configuration:")
    print("1. Create a bot with @BotFather on Telegram")
    print("2. Send /newbot command and follow instructions")
    print("3. Copy the bot token provided by @BotFather")

    bot_token = input("\nEnter your Telegram Bot Token: ").strip()

    if not bot_token:
        print("❌ Bot token is required. Setup cancelled.")
        return

    # Get Chat ID
    print("\n💬 Telegram Chat ID:")
    print("1. Start a chat with your bot")
    print("2. Send any message to the bot")
    print("3. Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")
    print("4. Look for 'chat' object and copy the 'id' value")

    chat_id = input("\nEnter your Telegram Chat ID: ").strip()

    if not chat_id:
        print("❌ Chat ID is required. Setup cancelled.")
        return

    # Create .env file
    env_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={bot_token}
TELEGRAM_CHAT_ID={chat_id}

# Optional: Additional configuration
# BINANCE_API_KEY=your_binance_api_key_here
# BINANCE_API_SECRET=your_binance_api_secret_here
# DATA_DIR=data
# CHARTS_DIR=charts
# COLLECTION_INTERVAL=300
# FUNDING_RATE_THRESHOLD=0.001
# OI_RATIO_THRESHOLD=2.0
"""

    try:
        with open('.env', 'w') as f:
            f.write(env_content)

        print(f"\n✅ Configuration saved to .env file")
        print(f"📋 Bot Token: {bot_token[:10]}...{bot_token[-5:]}")
        print(f"📋 Chat ID: {chat_id}")
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Test the configuration: python config.py")
        print("2. Start data collection: python scheduler.py")
        print("3. Run monitoring: python monitor.py")

    except Exception as e:
        print(f"❌ Error saving configuration: {e}")


def test_configuration():
    """Test the current configuration"""
    print("🧪 Testing Configuration...")

    try:
        from config import setup_environment

        if setup_environment():
            print("✅ Configuration is valid!")

            # Test Telegram bot
            try:
                from telegram_bot import TelegramBot
                bot = TelegramBot()
                print("✅ Telegram Bot configuration is valid")
            except Exception as e:
                print(f"❌ Telegram Bot test failed: {e}")
        else:
            print("❌ Configuration is incomplete")

    except ImportError as e:
        print(f"❌ Configuration test failed: {e}")


def main():
    """Main setup function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            test_configuration()
        elif sys.argv[1] == 'setup':
            setup_configuration()
        else:
            print("Usage:")
            print("  python setup.py setup    - Interactive setup")
            print("  python setup.py test     - Test configuration")
    else:
        print("Binance Monitoring System Setup")
        print("\nCommands:")
        print("  python setup.py setup    - Interactive setup")
        print("  python setup.py test     - Test configuration")


if __name__ == "__main__":
    main()