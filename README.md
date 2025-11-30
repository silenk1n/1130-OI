# Binance永续合约监控系统

这是一个长期运行的Binance永续合约数据监控系统，每5分钟自动采集数据，每半小时生成分析报告。

## 🚀 新版本更新

**自动化版本已发布！** `binance_monitor_auto.py` 现在包含所有功能：
- ✅ 一键启动，完全自动化
- ✅ 自动数据采集（每5分钟，**所有USDT永续合约**）
- ✅ 自动监控分析（每5分钟）
- ✅ 自动推送提醒（满足条件时）
- ✅ 运行状态报告（每30分钟）
- ✅ 启动成功通知（首次运行）

## 功能特性

- 📊 **自动数据采集**: 每5分钟采集**所有USDT永续合约**数据（约530+个交易对）
- 📈 **智能分析**: 每半小时生成价格、基差、资金费率、持仓量变化分析报告
- 🔔 **智能监控**: 监控资金费率和持仓量变化，满足条件时发送Telegram提醒
- 📊 **图表生成**: 自动为监控提醒生成分析图表
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

## 核心程序文件

### 🎯 自动化版本主程序

**`binance_monitor_auto.py`** - 自动化版本主程序，一键启动所有功能

**功能:**
- 自动数据采集（每5分钟，**所有USDT永续合约**）
- 自动监控分析（每5分钟）
- 自动推送提醒（满足条件时）
- 运行状态报告（每30分钟）
- 启动成功通知（首次运行）

**使用方法:**
```bash
python3 binance_monitor_auto.py
```

### 🎯 融合版本主程序

**`binance_oi_monitor.py`** - 融合版本主程序，包含所有核心功能

**功能:**
- 单次数据采集
- 数据分析报告
- 定时数据采集调度
- 交互式菜单系统

**使用方法:**
```bash
python3 binance_oi_monitor.py
```

### 📊 独立功能模块

**`data_collector.py`** - 数据采集器
- 从Binance API获取永续合约数据
- 保存到CSV文件

**`monitor.py`** - 资金费率和持仓量监控系统
- 监控资金费率 > 0.1%
- 监控持仓量短期激增
- 发送Telegram提醒

**`telegram_bot.py`** - Telegram Bot推送功能
- 发送监控提醒
- 支持图片附件

**`data_analyzer.py`** - 数据分析器
- 生成24小时趋势报告
- 分析价格、基差、资金费率、持仓量变化

**`scheduler.py`** - 定时数据采集调度器
- 每5分钟自动采集数据
- 长期运行支持

**`chart_generator.py`** - 图表生成器
- 为监控提醒生成分析图表
- 包含价格、基差、持仓量、资金费率图表

### 🔧 工具和配置

**`config.py`** - 配置管理
- 加载环境变量和设置
- 验证Telegram Bot配置

**`setup.py`** - 交互式配置设置
- 引导用户完成配置
- 创建.env文件

**`binance_data_snapshot.py`** - Binance数据快照获取
- 获取单个或多个交易对数据快照

**`binance_symbols.py`** - 交易对管理工具
- 获取USDT永续合约交易对
- 按交易量排序

## 安装和使用

### 🚀 快速开始

**推荐方式 - 使用启动脚本：**
```bash
./start_collector.sh
```

启动脚本会自动：
- 创建虚拟环境
- 安装依赖包
- 创建数据目录
- 启动**自动化监控系统**

### 📦 手动安装

1. **创建虚拟环境并安装依赖：**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **配置Telegram Bot（必需，用于监控提醒和状态报告）：**
```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的配置
# TELEGRAM_BOT_TOKEN=你的Bot Token
# TELEGRAM_CHAT_ID=你的Chat ID
```

3. **运行程序：**

**自动化版本（强烈推荐）：**
```bash
python3 binance_monitor_auto.py
```

**融合版本（交互式）：**
```bash
python3 binance_oi_monitor.py
```

**独立功能模块：**
```bash
# 单次数据采集
python3 data_collector.py

# 数据分析报告
python3 data_analyzer.py

# 定时采集（每5分钟）
python3 scheduler.py

# 监控系统（需要Telegram配置）
python3 monitor.py

# 配置设置
python3 setup.py
```

## 🔔 监控系统

### 自动化版本功能

**`binance_monitor_auto.py`** 提供完全自动化的监控体验：

1. **启动成功通知**
   - 系统启动后立即发送Telegram通知
   - 包含系统状态和运行计划

2. **自动数据采集**
   - 每5分钟采集**所有USDT永续合约**（约530+个交易对）
   - 自动保存到CSV文件

3. **自动监控分析**
   - 每5分钟检查所有交易对
   - 自动发现符合条件的交易对

4. **自动推送提醒**
   - 发现异常时立即发送Telegram提醒
   - 包含详细的分析数据

5. **运行状态报告**
   - 每30分钟发送系统运行状态
   - 包含采集统计、监控统计、运行时长
   - **与监控提醒完全独立**

### 监控条件

系统会监控以下条件，当**同时满足**时发送Telegram提醒：

1. **资金费率条件**: 资金费率绝对值 > 0.1%
   - `|last_funding_rate| > 0.001`

2. **持仓量条件**: 短期持仓量激增
   - `最近3次OI均值 / 最近10次OI均值 > 2`

### 📱 Telegram Bot配置

1. **创建Telegram Bot**
   - 在Telegram中搜索 @BotFather
   - 发送 `/newbot` 命令
   - 按照提示创建Bot并获取Token

2. **获取Chat ID**
   - 向你的Bot发送任意消息
   - 访问 `https://api.telegram.org/bot<YourBOTToken>/getUpdates`
   - 在响应中找到 `chat.id` 字段

3. **配置环境变量**

**方法一：使用.env文件**
```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件
nano .env

# 填入你的配置
TELEGRAM_BOT_TOKEN=你的Bot Token
TELEGRAM_CHAT_ID=你的Chat ID
```

**方法二：设置环境变量**
```bash
export TELEGRAM_BOT_TOKEN="你的Bot Token"
export TELEGRAM_CHAT_ID="你的Chat ID"
```

**方法三：使用配置向导**
```bash
python3 setup.py
```

### 📊 图表功能

系统会自动为每个监控提醒生成分析图表，包含：
- **价格走势对比** - 标记价格 vs 指数价格
- **基差变化** - 基差百分比变化趋势
- **持仓量变化** - 持仓量历史变化
- **资金费率变化** - 包含0.1%阈值线

### ⚙️ 监控调度器

启动完整的监控调度器（每5分钟执行一次数据采集和监控）：
```bash
python3 scheduler.py
```

或者使用融合版本：
```bash
python3 binance_oi_monitor.py
# 选择选项3: 启动定时采集
```

## 🔗 API Endpoints Used

- **Mark Price & Funding Rate**: `/fapi/v1/premiumIndex`
- **Index Price**: `/fapi/v1/indexInfo`
- **Funding Rate History**: `/fapi/v1/fundingRate`
- **Open Interest**: `/fapi/v1/openInterest`
- **Long/Short Ratios**: `/futures/data/globalLongShortAccountRatio`, `/futures/data/topLongShortAccountRatio`, `/futures/data/topLongShortPositionRatio`
- **Taker Buy/Sell Ratio**: `/futures/data/takerlongshortRatio`

## 📊 数据分析

### 基差分析 (Basis Analysis)
- **正基差 (Positive Basis)**: 标记价格 > 指数价格 (正价差)
- **负基差 (Negative Basis)**: 标记价格 < 指数价格 (逆价差)

### 资金费率分析 (Funding Rate Analysis)
- **正资金费率 (Positive Funding)**: 多头支付空头
- **负资金费率 (Negative Funding)**: 空头支付多头

### 多空比分析 (Long/Short Ratios)
- **比率 > 1**: 多头仓位多于空头仓位
- **比率 < 1**: 空头仓位多于多头仓位

### 主动买卖比分析 (Taker Buy/Sell Ratio)
- **比率 > 1**: 主动买入量多于主动卖出量
- **比率 < 1**: 主动卖出量多于主动买入量

### 数据分析报告

系统每半小时自动生成分析报告，包含：
- **价格涨幅/跌幅Top 10**
- **基差扩大/缩小Top 10**
- **资金费率上升/下降Top 10**
- **持仓量增长/减少Top 10**

查看报告：
```bash
python3 binance_oi_monitor.py
# 选择选项2: 数据分析报告
```

## 🚀 长期运行配置

### 快速启动

**使用启动脚本（推荐）：**
```bash
./start_collector.sh
```

### 服务器部署

#### 方案1: 使用systemd服务（Linux服务器）

1. **复制服务文件：**
```bash
sudo cp binance-monitor.service /etc/systemd/system/
```

2. **重新加载配置：**
```bash
sudo systemctl daemon-reload
```

3. **启用服务：**
```bash
sudo systemctl enable binance-monitor.service
```

4. **启动服务：**
```bash
sudo systemctl start binance-monitor.service
```

5. **查看服务状态：**
```bash
sudo systemctl status binance-monitor.service
```

#### 方案2: 使用nohup后台运行
```bash
# 启动后台服务
nohup python3 scheduler.py > scheduler.log 2>&1 &
echo $! > scheduler.pid

# 查看日志
tail -f scheduler.log

# 停止服务
kill $(cat scheduler.pid)
```

### 📈 监控报告

系统每半小时自动生成：
- **24小时长期趋势报告** - 过去24小时主要变化
- **6小时短期趋势报告** - 最近6小时快速变化

报告内容包括：
- 价格变化排名
- 基差变化排名
- 资金费率变化排名
- 持仓量变化排名

## 🔧 故障排除

### 常见问题

- **服务无法启动**: 检查依赖和网络连接
- **数据采集失败**: 检查API调用频率和网络
- **Telegram提醒未发送**: 检查Bot Token和Chat ID配置
- **服务意外停止**: 使用systemd服务会自动重启

### 依赖包

**必需依赖:**
```bash
pip install -r requirements.txt
```

**requirements.txt 内容:**
```
requests>=2.25.1
pandas>=1.3.0
schedule>=1.1.0
python-binance>=1.0.16
python-dotenv>=0.19.0
```

### API限流

脚本内置延迟以避免触发Binance API限流。生产环境中建议实现更复杂的限流和错误处理机制。

## 📋 项目结构

```
binance_oi_monitor/
├── binance_monitor_auto.py    # 🆕 自动化版本主程序（推荐）
├── binance_oi_monitor.py      # 融合版本主程序
├── data_collector.py          # 数据采集器
├── monitor.py                 # 资金费率监控
├── telegram_bot.py            # Telegram推送
├── data_analyzer.py           # 数据分析器
├── scheduler.py               # 定时调度器
├── chart_generator.py         # 图表生成器
├── config.py                  # 配置管理
├── setup.py                   # 配置设置
├── binance_data_snapshot.py   # 数据快照
├── binance_symbols.py         # 交易对管理
├── start_collector.sh         # 启动脚本
├── binance-monitor.service    # systemd服务文件
├── requirements.txt           # 依赖包列表
├── .env.example               # 环境变量示例
├── data/                      # 数据目录
├── charts/                    # 图表目录
├── README.md                  # 说明文档
├── USAGE_GUIDE.md             # 使用指南
└── QUICK_START.md             # 快速开始
```

## ⚠️ 免责声明

本工具仅供教育和研究目的使用。在做出交易决策前，请始终从官方来源验证数据。

---

**项目维护者**: [你的名字]
**最后更新**: 2025-11-30
**版本**: v2.0 (融合版本)