#!/bin/zsh

# Binance永续合约数据采集系统启动脚本

echo "启动Binance永续合约数据采集系统..."
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
echo "系统已准备就绪！"
echo ""
echo "使用方法:"
echo "1. 单次数据采集: python3 binance_oi_monitor.py"
echo "2. 数据分析: python3 binance_oi_monitor.py"
echo "3. 定时采集: python3 binance_oi_monitor.py"
echo ""

# 显示当前数据文件数量
file_count=$(ls -1 data/*.csv 2>/dev/null | wc -l)
echo "当前数据文件数量: $file_count"

# 直接启动自动化监控系统
echo "启动自动化监控系统..."
python3 binance_monitor_auto.py