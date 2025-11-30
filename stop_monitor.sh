#!/bin/zsh

# 停止Binance永续合约监控系统

echo "停止Binance永续合约监控系统..."

PID_FILE="logs/monitor.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ 未找到PID文件，系统可能未运行"
    exit 1
fi

MONITOR_PID=$(cat "$PID_FILE")

if ps -p "$MONITOR_PID" > /dev/null 2>&1; then
    echo "正在停止进程 (PID: $MONITOR_PID)..."
    kill "$MONITOR_PID"

    # 等待进程停止
    for i in {1..10}; do
        if ! ps -p "$MONITOR_PID" > /dev/null 2>&1; then
            echo "✅ 监控系统已停止"
            rm "$PID_FILE"
            exit 0
        fi
        sleep 1
    done

    # 如果正常停止失败，强制停止
    echo "强制停止进程..."
    kill -9 "$MONITOR_PID"
    rm "$PID_FILE"
    echo "✅ 监控系统已强制停止"
else
    echo "❌ 进程 (PID: $MONITOR_PID) 不存在"
    rm "$PID_FILE"
fi