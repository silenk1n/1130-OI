#!/bin/zsh

# Binance永续合约监控系统 - tmux 启动脚本

echo "启动Binance永续合约监控系统（使用tmux）..."
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

echo ""
echo "创建tmux会话..."

# 检查是否已在tmux会话中运行
if [ -n "$TMUX" ]; then
    echo "⚠️ 已在tmux会话中，直接启动监控系统..."
    python3 binance_monitor_auto.py
else
    # 创建新的tmux会话
    tmux new-session -d -s binance_monitor "source venv/bin/activate && python3 binance_monitor_auto.py"

    echo "✅ 监控系统已在tmux会话中启动"
    echo ""
    echo "管理命令:"
    echo "  连接会话: tmux attach -t binance_monitor"
    echo "  查看会话: tmux ls"
    echo "  分离会话: 按 Ctrl+B, 然后按 D"
    echo "  停止会话: tmux kill-session -t binance_monitor"
    echo ""
    echo "现在可以安全断开SSH连接，系统将继续运行"
fi