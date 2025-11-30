#!/bin/zsh

# 重启Binance永续合约监控系统

echo "重启Binance永续合约监控系统..."

# 先停止（如果正在运行）
if [ -f "stop_monitor.sh" ]; then
    ./stop_monitor.sh
else
    echo "⚠️ 未找到停止脚本，跳过停止步骤"
fi

# 等待2秒确保进程完全停止
sleep 2

# 重新启动
if [ -f "start_background.sh" ]; then
    ./start_background.sh
else
    echo "❌ 未找到启动脚本"
    exit 1
fi