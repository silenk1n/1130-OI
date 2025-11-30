# Binance永续合约监控系统

这是一个长期运行的Binance永续合约数据监控系统，每5分钟自动采集数据，每半小时生成分析报告。

## 功能特性

- 📊 **自动数据采集**: 每5分钟采集50个交易量最大的USDT永续合约数据
- 📈 **智能分析**: 每半小时生成价格、基差、资金费率、持仓量变化分析报告
- 🔄 **长期运行**: 支持后台运行和自动重启
- 📝 **完整日志**: 详细的运行日志和错误记录
- 🛡️ **稳定可靠**: 完善的错误处理和恢复机制

采集的数据包括：
- **标记价格 (Mark Price)** - 当前标记价格
- **指数价格 (Index Price)** - 基础指数价格
- **基差 (Basis)** - 标记价格与指数价格之差
- **基差百分比 (Basis Percent)** - 基差占指数价格的百分比
- **最新资金费率 (Last Funding Rate)** - 最近一次资金费率
- **持仓量 (Open Interest)** - 总持仓量
- **账户多空比 (Long/Short Account Ratio)** - 多头与空头账户比例
- **大户账户多空比 (Top Trader Account LS Ratio)** - 大户账户多空比例
- **大户持仓多空比 (Top Trader Position LS Ratio)** - 大户持仓多空比例
- **主动买卖比 (Taker Buy/Sell Ratio)** - 主动买入卖出比例

## Files

### 1. `binance_data_snapshot.py`
Main script for fetching data snapshots for individual symbols or multiple symbols.

**Usage:**
```python
from binance_data_snapshot import BinanceDataSnapshot

# Initialize
snapshot = BinanceDataSnapshot()

# Get data for single symbol
data = snapshot.get_data_snapshot("BTCUSDT")

# Get data for multiple symbols
symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
data = snapshot.get_multiple_symbols_snapshot(symbols)
```

### 2. `binance_symbols.py`
Utility script to get available USDT perpetual trading pairs.

**Usage:**
```python
from binance_symbols import get_usdt_perpetual_symbols, get_top_symbols_by_volume

# Get all USDT perpetual symbols
all_symbols = get_usdt_perpetual_symbols()

# Get top symbols by 24h trading volume
top_symbols = get_top_symbols_by_volume(20)
```

### 3. `data_analysis_example.py`
Example script demonstrating data analysis and insights.

**Usage:**
```bash
python3 data_analysis_example.py
```

## 安装和使用

### 快速开始

使用启动脚本（推荐）：
```bash
./start_collector.sh
```

### 手动安装

1. 创建虚拟环境并安装依赖：
```bash
python3 -m venv venv
source venv/bin/activate
pip install pandas requests schedule
```

2. 运行脚本：
```bash
# 单次数据采集
python3 data_collector.py

# 数据分析
python3 data_analyzer.py

# 定时采集（每5分钟）
python3 scheduler.py

# 监控系统（需要Telegram配置）
python3 monitor.py

# 监控系统测试（无需Telegram）
python3 monitor_test.py

# 监控演示
python3 monitor_demo.py
```

## 监控系统

### 监控条件

系统会监控以下条件，当同时满足时发送Telegram提醒：

1. **资金费率条件**: 资金费率绝对值 > 0.1%
   - `|last_funding_rate| > 0.001`

2. **持仓量条件**: 短期持仓量激增
   - `最近3次OI均值 / 最近10次OI均值 > 2`

### Telegram Bot配置

1. 创建Telegram Bot并获取Token
2. 获取你的Chat ID
3. 设置环境变量：
```bash
export TELEGRAM_BOT_TOKEN="你的Bot Token"
export TELEGRAM_CHAT_ID="你的Chat ID"
```

详细配置说明：
```bash
python3 config_example.py
```

### 图表功能

系统会自动为每个监控提醒生成分析图表，包含：
- 价格走势对比
- 基差变化
- 持仓量变化
- 资金费率变化（包含0.1%阈值线）

查看推送示例：
```bash
python3 push_demo.py
```

### 监控调度器

启动完整的监控调度器（每5分钟执行一次数据采集和监控）：
```bash
python3 monitor_scheduler.py
```

## API Endpoints Used

- **Mark Price & Funding Rate**: `/fapi/v1/premiumIndex`
- **Index Price**: `/fapi/v1/indexInfo`
- **Funding Rate History**: `/fapi/v1/fundingRate`
- **Open Interest**: `/fapi/v1/openInterest`
- **Long/Short Ratios**: `/futures/data/globalLongShortAccountRatio`, `/futures/data/topLongShortAccountRatio`, `/futures/data/topLongShortPositionRatio`
- **Taker Buy/Sell Ratio**: `/futures/data/takerlongshortRatio`

## Data Interpretation

### Basis Analysis
- **Positive Basis**: Mark price > Index price (contango)
- **Negative Basis**: Mark price < Index price (backwardation)

### Funding Rate Analysis
- **Positive Funding**: Longs pay shorts
- **Negative Funding**: Shorts pay longs

### Long/Short Ratios
- **Ratio > 1**: More long positions than short positions
- **Ratio < 1**: More short positions than long positions

### Taker Buy/Sell Ratio
- **Ratio > 1**: More taker buy volume than sell volume
- **Ratio < 1**: More taker sell volume than buy volume

## 长期运行配置

### 快速启动
```bash
# 启动监控服务
./start_monitor.sh

# 停止监控服务
./stop_monitor.sh

# 检查服务状态
./check_status.sh
```

### 服务器部署

#### 方案1: 使用systemd服务（Linux服务器）
1. 复制服务文件：`sudo cp binance-monitor.service /etc/systemd/system/`
2. 重新加载配置：`sudo systemctl daemon-reload`
3. 启用服务：`sudo systemctl enable binance-monitor.service`
4. 启动服务：`sudo systemctl start binance-monitor.service`

#### 方案2: 使用nohup后台运行
```bash
nohup python monitor_service.py > monitor_service.log 2>&1 &
echo $! > monitor_service.pid
```

### 监控报告
系统每半小时自动生成：
- **24小时长期趋势报告** - 过去24小时主要变化
- **6小时短期趋势报告** - 最近6小时快速变化

## 故障排除

- **服务无法启动**: 检查依赖和网络连接
- **数据采集失败**: 检查API调用频率和网络
- **服务意外停止**: 使用systemd服务会自动重启

## Rate Limiting

The scripts include built-in delays to avoid hitting Binance API rate limits. For production use, consider implementing more sophisticated rate limiting and error handling.

## Disclaimer

This tool is for educational and research purposes only. Always verify data from official sources before making trading decisions.