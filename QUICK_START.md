# Binance永续合约监控系统 - 快速开始指南

## 🚀 5分钟快速部署

### 步骤1：下载项目

```bash
# 克隆项目或下载ZIP文件
cd /path/to/project
```

### 步骤2：一键启动

```bash
# 运行启动脚本（推荐）
./start_collector.sh
```

启动脚本会自动完成：
- ✅ 创建Python虚拟环境
- ✅ 安装所有依赖包
- ✅ 创建数据目录
- ✅ 启动融合版本主程序

### 步骤3：选择操作

在交互式菜单中选择：

```
请选择操作:
1. 单次数据采集     ← 推荐先测试
2. 数据分析报告
3. 启动定时采集     ← 长期运行
4. 查看可用交易对
5. 退出
```

## 📱 Telegram Bot快速配置

### 1. 创建Bot（1分钟）

1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot`
3. 设置Bot名称（如：`MyBinanceMonitor`）
4. 设置Bot用户名（如：`my_binance_monitor_bot`）
5. **保存Token**（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 2. 获取Chat ID（30秒）

1. 向你的Bot发送任意消息
2. 访问：`https://api.telegram.org/bot<你的Token>/getUpdates`
3. 复制 `chat.id` 字段的值

### 3. 配置（30秒）

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置
nano .env
```

填入：
```env
TELEGRAM_BOT_TOKEN=你的Token
TELEGRAM_CHAT_ID=你的Chat ID
```

## 🎯 核心功能快速体验

### 测试数据采集

```bash
python3 binance_oi_monitor.py
# 选择 1. 单次数据采集
```

### 查看分析报告

```bash
python3 binance_oi_monitor.py
# 选择 2. 数据分析报告
```

### 启动长期监控

```bash
python3 binance_oi_monitor.py
# 选择 3. 启动定时采集
```

## ⚡ 常用命令速查

### 快速启动
```bash
./start_collector.sh          # 一键启动
python3 binance_oi_monitor.py # 融合版本
```

### 独立功能
```bash
python3 data_collector.py     # 数据采集
python3 monitor.py           # 监控检查
python3 scheduler.py         # 定时采集
```

### 配置管理
```bash
python3 setup.py             # 配置向导
python3 config.py            # 配置检查
```

## 🔧 故障快速排查

### 问题1：启动失败
```bash
# 检查依赖
pip install -r requirements.txt

# 检查Python版本
python3 --version
```

### 问题2：Telegram不工作
```bash
# 检查配置
python3 config.py

# 测试Bot
python3 -c "from telegram_bot import TelegramBot; bot = TelegramBot(); print('配置检查完成')"
```

### 问题3：数据采集失败
```bash
# 检查网络
ping api.binance.com

# 检查数据目录
ls -la data/
```

## 📊 监控条件说明

### 触发条件（同时满足）

1. **资金费率** > 0.1% 或 < -0.1%
2. **持仓量激增**：最近3次均值 > 最近10次均值的2倍

### 监控示例

当以下情况发生时发送提醒：
- BTCUSDT 资金费率：0.15%（超过0.1%）
- BTCUSDT 持仓量：最近3次均值是最近10次均值的2.5倍

## 🚀 生产环境部署

### 使用systemd（推荐）

```bash
# 安装服务
sudo cp binance-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable binance-monitor.service
sudo systemctl start binance-monitor.service

# 查看状态
sudo systemctl status binance-monitor.service
```

### 使用nohup

```bash
# 后台运行
nohup python3 scheduler.py > scheduler.log 2>&1 &

# 查看日志
tail -f scheduler.log
```

## 📞 获取帮助

- **详细文档**：查看 `README.md` 和 `USAGE_GUIDE.md`
- **配置帮助**：运行 `python3 setup.py`
- **问题反馈**：提交Issue

---

**提示**：首次使用建议先运行"单次数据采集"测试功能，确认正常后再启动"定时采集"。

**版本**: v2.0 (融合版本)
**更新日期**: 2025-11-30