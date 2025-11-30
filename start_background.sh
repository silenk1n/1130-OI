#!/bin/zsh

# Binance永续合约监控系统后台启动脚本

echo "启动Binance永续合约监控系统（后台运行）..."
echo "========================================"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
if ! python3 -c "import pandas" &>/dev/null; then
    echo "安装依赖包..."
    pip install -r requirements.txt
fi

# 创建数据目录
mkdir -p data

# 创建日志目录
mkdir -p logs

echo ""
echo "启动后台监控进程..."

# 使用nohup后台运行，并保存PID
echo "启动时间: $(date)" > logs/startup.log
nohup python3 binance_monitor_auto.py >> logs/monitor.log 2>&1 &
MONITOR_PID=$!
echo $MONITOR_PID > logs/monitor.pid

echo "✅ 监控系统已启动（PID: $MONITOR_PID）"
echo "📝 日志文件: logs/monitor.log"
echo "🔢 PID文件: logs/monitor.pid"
echo ""
echo "管理命令:"
echo "  查看日志: tail -f logs/monitor.log"
echo "  查看状态: ps -p $MONITOR_PID"
echo "  停止系统: kill $MONITOR_PID"
echo "  重启系统: ./restart_monitor.sh"
echo ""
echo "系统将在后台持续运行，即使断开SSH连接也不会停止"

# 显示最近日志
echo "最近日志:"
tail -5 logs/monitor.log 2>/dev/null || echo "(暂无日志)"