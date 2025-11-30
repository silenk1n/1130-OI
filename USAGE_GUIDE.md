# Binance永续合约监控系统 - 使用指南

## 📖 目录

- [快速开始](#快速开始)
- [详细配置](#详细配置)
- [程序功能](#程序功能)
- [监控系统](#监控系统)
- [数据分析](#数据分析)
- [长期运行](#长期运行)
- [故障排除](#故障排除)

## 🚀 快速开始

### 方式一：使用启动脚本（推荐）

```bash
# 1. 下载项目
cd /path/to/project

# 2. 运行启动脚本
./start_collector.sh
```

启动脚本会自动：
- 创建Python虚拟环境
- 安装所有依赖包
- 创建数据目录
- 启动融合版本主程序

### 方式二：手动安装

```bash
# 1. 创建虚拟环境
python3 -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动程序
python3 binance_oi_monitor.py
```

## ⚙️ 详细配置

### Telegram Bot配置

#### 步骤1：创建Telegram Bot

1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按照提示设置Bot名称和用户名
4. 保存Bot Token（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

#### 步骤2：获取Chat ID

**方法一：通过API获取**

1. 向你的Bot发送任意消息
2. 在浏览器中访问：
   ```
   https://api.telegram.org/bot<YourBOTToken>/getUpdates
   ```
3. 在JSON响应中找到 `chat.id` 字段

**方法二：使用配置向导**

```bash
python3 setup.py
```

#### 步骤3：配置环境变量

**使用.env文件（推荐）**

```bash
# 复制示例文件
cp .env.example .env

# 编辑配置文件
nano .env
```

在 `.env` 文件中填入：
```env
TELEGRAM_BOT_TOKEN=你的Bot Token
TELEGRAM_CHAT_ID=你的Chat ID
```

**使用环境变量**

```bash
export TELEGRAM_BOT_TOKEN="你的Bot Token"
export TELEGRAM_CHAT_ID="你的Chat ID"
```

## 🎯 程序功能

### 融合版本主程序

```bash
python3 binance_oi_monitor.py
```

**交互式菜单选项：**

1. **单次数据采集**
   - 采集10个主要交易对的数据
   - 保存到 `data/` 目录
   - 适合测试和快速使用

2. **数据分析报告**
   - 生成24小时趋势报告
   - 显示价格、基差、资金费率、持仓量变化排名
   - 需要先有数据文件

3. **启动定时采集**
   - 每5分钟自动采集数据
   - 长期运行模式
   - 按 Ctrl+C 停止

4. **查看可用交易对**
   - 显示所有USDT永续合约交易对
   - 显示前20个交易对

5. **退出**
   - 退出程序

### 独立功能模块

#### 数据采集

```bash
# 单次数据采集
python3 data_collector.py

# 采集指定交易对
python3 -c "
from data_collector import DataCollector
collector = DataCollector()
collector.collect_data_for_symbols(['BTCUSDT', 'ETHUSDT'])
"
```

#### 数据分析

```bash
# 生成分析报告
python3 data_analyzer.py

# 自定义时间范围分析
python3 -c "
from data_analyzer import DataAnalyzer
analyzer = DataAnalyzer()
analyzer.generate_report(6)  # 6小时报告
"
```

#### 定时调度

```bash
# 启动定时采集
python3 scheduler.py

# 后台运行
nohup python3 scheduler.py > scheduler.log 2>&1 &
```

## 🔔 监控系统

### 监控条件

系统监控以下条件，当**同时满足**时发送Telegram提醒：

1. **资金费率条件**
   - `|last_funding_rate| > 0.001` (0.1%)
   - 表示资金费率绝对值超过0.1%

2. **持仓量条件**
   - `最近3次OI均值 / 最近10次OI均值 > 2`
   - 表示持仓量短期激增2倍以上

### 运行监控

```bash
# 单次监控检查
python3 monitor.py

# 集成到定时调度中
# 在 scheduler.py 中自动运行
```

### 监控提醒示例

当监控条件触发时，系统会发送：

- **文字提醒**：包含交易对、资金费率、OI比率、当前OI
- **分析图表**：包含价格、基差、持仓量、资金费率走势

## 📊 数据分析

### 数据指标说明

#### 基础指标
- **标记价格 (Mark Price)**：永续合约的标记价格
- **指数价格 (Index Price)**：基础资产的指数价格
- **基差 (Basis)**：标记价格与指数价格之差
- **基差百分比**：基差占指数价格的百分比

#### 资金费率
- **最新资金费率**：最近一次的资金费率
- **资金费率趋势**：资金费率的变化方向

#### 持仓量
- **持仓量 (OI)**：合约的总持仓量
- **持仓量变化**：持仓量的增减情况

#### 多空比
- **账户多空比**：所有账户的多空比例
- **大户账户多空比**：大户账户的多空比例
- **大户持仓多空比**：大户持仓的多空比例

#### 主动买卖比
- **主动买卖比**：主动买入与卖出的比例

### 分析报告解读

#### 价格变化排名
- **涨幅Top 10**：过去24小时价格涨幅最大的交易对
- **跌幅Top 10**：过去24小时价格跌幅最大的交易对

#### 基差变化排名
- **基差扩大Top 10**：基差百分比增加最多的交易对
- **基差缩小Top 10**：基差百分比减少最多的交易对

#### 资金费率变化排名
- **费率上升Top 10**：资金费率上升最多的交易对
- **费率下降Top 10**：资金费率下降最多的交易对

#### 持仓量变化排名
- **持仓增长Top 10**：持仓量增长百分比最大的交易对
- **持仓减少Top 10**：持仓量减少百分比最大的交易对

## 🚀 长期运行

### 使用systemd服务（Linux）

1. **安装服务文件**
   ```bash
   sudo cp binance-monitor.service /etc/systemd/system/
   sudo systemctl daemon-reload
   ```

2. **启用和启动服务**
   ```bash
   sudo systemctl enable binance-monitor.service
   sudo systemctl start binance-monitor.service
   ```

3. **查看服务状态**
   ```bash
   sudo systemctl status binance-monitor.service
   journalctl -u binance-monitor.service -f
   ```

4. **停止服务**
   ```bash
   sudo systemctl stop binance-monitor.service
   ```

### 使用nohup后台运行

```bash
# 启动后台服务
nohup python3 scheduler.py > scheduler.log 2>&1 &
echo $! > scheduler.pid

# 查看日志
tail -f scheduler.log

# 停止服务
kill $(cat scheduler.pid)
```

### 使用screen/tmux

```bash
# 使用screen
screen -S binance_monitor
python3 scheduler.py
# 按 Ctrl+A, D 分离会话

# 重新连接
screen -r binance_monitor
```

## 🔧 故障排除

### 常见问题

#### 1. 依赖安装失败

```bash
# 更新pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 如果仍有问题，尝试逐个安装
pip install requests pandas schedule python-binance python-dotenv
```

#### 2. Telegram Bot配置错误

**错误信息：** `Telegram Bot配置错误`

**解决方法：**
1. 检查Bot Token格式是否正确
2. 确认Chat ID是否正确
3. 确保Bot已启动并可以接收消息
4. 检查网络连接

#### 3. 数据采集失败

**错误信息：** `API请求失败`

**解决方法：**
1. 检查网络连接
2. 确认Binance API服务正常
3. 检查API限流设置
4. 添加重试机制

#### 4. 程序意外停止

**解决方法：**
1. 使用systemd服务自动重启
2. 使用nohup后台运行
3. 添加错误日志和监控

### 日志查看

```bash
# 查看系统日志
journalctl -u binance-monitor.service

# 查看程序日志
tail -f scheduler.log

# 查看数据目录
ls -la data/
```

### 性能优化

1. **调整采集频率**
   - 修改 `config.py` 中的 `COLLECTION_INTERVAL`
   - 默认5分钟，可根据需要调整

2. **调整监控阈值**
   - 修改资金费率阈值：`FUNDING_RATE_THRESHOLD`
   - 修改OI比率阈值：`OI_RATIO_THRESHOLD`

3. **限制采集交易对数量**
   - 在 `data_collector.py` 中修改 `collect_top_symbols_data` 的limit参数

## 📁 数据文件说明

### 数据目录结构

```
data/
├── BTCUSDT.csv
├── ETHUSDT.csv
├── ADAUSDT.csv
└── ...
```

### CSV文件格式

每个交易对的CSV文件包含以下列：

| 列名 | 说明 | 数据类型 |
|------|------|----------|
| timestamp | 时间戳 | datetime |
| mark_price | 标记价格 | float |
| index_price | 指数价格 | float |
| basis | 基差 | float |
| basis_percent | 基差百分比 | float |
| last_funding_rate | 最新资金费率 | float |
| next_funding_time | 下次资金费率时间 | int |
| oi | 持仓量 | float |
| long_short_account_ratio | 账户多空比 | float |
| top_trader_account_ls_ratio | 大户账户多空比 | float |
| top_trader_position_ls_ratio | 大户持仓多空比 | float |
| taker_buy_sell_ratio | 主动买卖比 | float |

## 📈 图表说明

系统为每个监控提醒生成4个图表：

1. **价格走势对比**
   - 标记价格 vs 指数价格
   - 显示价格差异和趋势

2. **基差变化**
   - 基差百分比变化趋势
   - 显示基差扩大或缩小

3. **持仓量变化**
   - 持仓量历史变化
   - 显示持仓量激增点

4. **资金费率变化**
   - 资金费率历史变化
   - 包含0.1%阈值线

---

**更多帮助：**
- 查看源代码注释
- 查看README.md文档
- 提交Issue获取支持

**项目维护者**: [你的名字]
**最后更新**: 2025-11-30
**版本**: v2.0 (融合版本)