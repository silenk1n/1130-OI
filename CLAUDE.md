# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Binance perpetual contracts monitoring system written in Python. It automatically collects data from all USDT perpetual contracts (~530+ pairs) every 5 minutes, analyzes funding rates and open interest changes, and sends Telegram alerts when specific conditions are met.

## Key Architecture

### Core Components

1. **Main Entry Points**:
   - `binance_monitor_auto.py` - Fully automated version (recommended)
   - `binance_oi_monitor.py` - Interactive version with menu system
   - `start_collector.sh` - One-click startup script

2. **Core Modules**:
   - `data_collector.py` - Data collection from Binance API
   - `monitor.py` - Funding rate and open interest monitoring
   - `telegram_bot.py` - Telegram notifications
   - `data_analyzer.py` - Data analysis and reporting
   - `scheduler.py` - Scheduled task execution
   - `chart_generator.py` - Visualization charts
   - `config.py` - Configuration management
   - `setup.py` - Interactive configuration setup

3. **Data Flow**:
   - Collection: Binance API → CSV files in `data/` directory
   - Monitoring: CSV data → Analysis → Telegram alerts
   - Visualization: CSV data → Matplotlib charts → `charts/` directory
   - Reporting: Periodic status reports via Telegram

### Monitoring Logic

The system uses different monitoring strategies based on market capitalization:

- **Large-cap coins** (market cap ≥ $100M): BOTH conditions required:
  1. `|funding_rate| > 0.1%`
  2. `recent_3_avg_oi / recent_10_avg_oi > 2`

- **Small-cap coins** (market cap < $100M): EITHER condition triggers

- **Unknown market cap**: Treated as small-cap

## Development Commands

### Setup and Installation

```bash
# One-click setup (recommended)
./start_collector.sh

# Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Telegram Bot Token and Chat ID
```

### Running the Application

```bash
# Automated version (recommended)
python3 binance_monitor_auto.py

# Interactive version
python3 binance_oi_monitor.py

# Individual modules
python3 data_collector.py      # Single data collection
python3 monitor.py            # Single monitoring check
python3 scheduler.py          # Start scheduled collection
python3 data_analyzer.py      # Generate analysis report
python3 setup.py              # Interactive configuration
```

### Testing and Verification

```bash
# Check configuration
python3 config.py

# Test Telegram Bot
python3 -c "from telegram_bot import TelegramBot; bot = TelegramBot(); print('Bot configured')"

# Test data collection for specific symbols
python3 -c "from data_collector import DataCollector; collector = DataCollector(); collector.collect_data_for_symbols(['BTCUSDT', 'ETHUSDT'])"
```

### Production Deployment

```bash
# Systemd service (Linux)
sudo cp binance-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable binance-monitor.service
sudo systemctl start binance-monitor.service

# Background running with nohup
nohup python3 scheduler.py > scheduler.log 2>&1 &
echo $! > scheduler.pid
```

## Configuration

### Required Configuration

1. **Telegram Bot Token**: From @BotFather
2. **Telegram Chat ID**: From `https://api.telegram.org/bot<YourBOTToken>/getUpdates`

### Configuration Files

- `.env.example` - Template configuration file
- `.env` - Actual configuration (gitignored)
- `config.py` - Configuration loader class

### Environment Variables

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
DATA_DIR=data                    # Data storage directory
CHARTS_DIR=charts                # Charts storage directory
COLLECTION_INTERVAL=300          # Data collection interval in seconds (5 minutes)
FUNDING_RATE_THRESHOLD=0.001     # 0.1% funding rate threshold
OI_RATIO_THRESHOLD=2.0           # 2x open interest ratio threshold
MARKET_CAP_THRESHOLD=100000000   # $100M market cap threshold
```

## Data Structure

### Data Directory (`data/`)

- Contains CSV files for each trading pair (e.g., `BTCUSDT.csv`)
- Each file contains timestamped data with 12 metrics:
  - Mark price, index price, basis, basis percentage
  - Funding rate, open interest (OI)
  - Long/short ratios (account, top trader)
  - Taker buy/sell ratio

### Charts Directory (`charts/`)

- Contains generated charts for monitoring alerts
- Each alert generates 4 charts:
  - Price comparison (mark vs index)
  - Basis percentage trend
  - Open interest history
  - Funding rate history with threshold line

## Git Workflow

- Main branch: `main`
- Remote: `https://github.com/silenk1n/OI_alert.git`
- Gitignored: `.env`, `data/`, `charts/`, `venv/`
- Use `PUSH_GUIDE.md` for GitHub authentication help

## Claude Code Permissions

The `.claude/settings.local.json` allows Claude Code to:
- Execute Python and pip commands
- Run git operations (commit, push, add)
- Use system commands (curl, source, chmod, find)

## Important Notes

1. **API Rate Limiting**: The system includes delays to avoid Binance API rate limits
2. **Error Handling**: Built-in retry mechanisms and comprehensive logging
3. **Long-running**: Designed for continuous operation with automatic recovery
4. **Modular Design**: Clear separation of concerns for easy maintenance
5. **Production Ready**: Includes service files and deployment guides

## Troubleshooting

- **Telegram alerts not working**: Verify Bot Token and Chat ID in `.env`
- **Data collection failing**: Check network connectivity to Binance API
- **Service not starting**: Ensure all dependencies are installed (`pip install -r requirements.txt`)
- **Permission errors**: Check file permissions for `data/` and `charts/` directories