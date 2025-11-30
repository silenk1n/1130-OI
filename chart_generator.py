#!/usr/bin/env python3
"""
图表生成器
为监控提醒生成价格、持仓量、费率变化的图表
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
from typing import Optional


class ChartGenerator:
    def __init__(self, output_dir: str = "charts"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # 设置中文字体（如果需要显示中文）
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

    def generate_monitoring_chart(self, symbol: str, df: pd.DataFrame,
                                funding_rate: float, oi_ratio: float) -> Optional[str]:
        """
        生成监控图表

        Args:
            symbol: 交易对名称
            df: 包含历史数据的数据框
            funding_rate: 当前资金费率
            oi_ratio: OI比率

        Returns:
            str: 图表文件路径，如果生成失败返回None
        """
        if len(df) < 5:
            print(f"数据不足，无法为 {symbol} 生成图表")
            return None

        try:
            # 创建图表
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'{symbol} 监控分析图表\n(资金费率: {funding_rate:.4f}, OI比率: {oi_ratio:.2f}x)',
                        fontsize=16, fontweight='bold')

            # 设置颜色
            colors = sns.color_palette("husl", 4)

            # 1. 价格走势图
            ax1 = axes[0, 0]
            ax1.plot(df['timestamp'], df['mark_price'],
                    color=colors[0], linewidth=2, label='标记价格')
            ax1.plot(df['timestamp'], df['index_price'],
                    color=colors[1], linewidth=2, label='指数价格', linestyle='--')
            ax1.set_title('价格走势', fontsize=14, fontweight='bold')
            ax1.set_ylabel('价格 (USDT)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # 旋转x轴标签
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

            # 2. 基差变化图
            ax2 = axes[0, 1]
            ax2.plot(df['timestamp'], df['basis_percent'],
                    color=colors[2], linewidth=2, label='基差百分比')
            ax2.axhline(y=0, color='red', linestyle='-', alpha=0.3)
            ax2.set_title('基差变化', fontsize=14, fontweight='bold')
            ax2.set_ylabel('基差百分比 (%)')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

            # 3. 持仓量变化图
            ax3 = axes[1, 0]
            ax3.plot(df['timestamp'], df['oi'],
                    color=colors[3], linewidth=2, label='持仓量')
            ax3.set_title('持仓量变化', fontsize=14, fontweight='bold')
            ax3.set_ylabel('持仓量')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)

            # 4. 资金费率变化图
            ax4 = axes[1, 1]
            ax4.plot(df['timestamp'], df['last_funding_rate'] * 100,
                    color='purple', linewidth=2, label='资金费率')
            ax4.axhline(y=0.1, color='red', linestyle='--', alpha=0.7, label='0.1%阈值')
            ax4.axhline(y=-0.1, color='red', linestyle='--', alpha=0.7)
            ax4.set_title('资金费率变化', fontsize=14, fontweight='bold')
            ax4.set_ylabel('资金费率 (%)')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)

            # 调整布局
            plt.tight_layout()

            # 保存图表
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            chart_filename = f"{symbol}_monitor_{timestamp}.png"
            chart_path = os.path.join(self.output_dir, chart_filename)

            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            print(f"图表已保存: {chart_path}")
            return chart_path

        except Exception as e:
            print(f"生成图表失败: {e}")
            return None

    def generate_detailed_analysis(self, symbol: str, df: pd.DataFrame) -> Optional[str]:
        """
        生成详细分析图表

        Args:
            symbol: 交易对名称
            df: 包含历史数据的数据框

        Returns:
            str: 图表文件路径
        """
        if len(df) < 10:
            return None

        try:
            # 创建更详细的图表
            fig, axes = plt.subplots(3, 2, figsize=(18, 15))
            fig.suptitle(f'{symbol} 详细分析报告', fontsize=18, fontweight='bold')

            # 设置颜色主题
            sns.set_palette("husl")

            # 1. 价格和基差对比
            ax1 = axes[0, 0]
            ax1.plot(df['timestamp'], df['mark_price'], label='标记价格', linewidth=2)
            ax1.plot(df['timestamp'], df['index_price'], label='指数价格', linewidth=2, linestyle='--')
            ax1.set_title('价格对比', fontsize=14, fontweight='bold')
            ax1.set_ylabel('价格')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

            # 2. 基差百分比
            ax2 = axes[0, 1]
            ax2.plot(df['timestamp'], df['basis_percent'],
                    color='orange', linewidth=2)
            ax2.axhline(y=0, color='red', linestyle='-', alpha=0.3)
            ax2.set_title('基差百分比', fontsize=14, fontweight='bold')
            ax2.set_ylabel('基差 (%)')
            ax2.grid(True, alpha=0.3)
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

            # 3. 持仓量变化
            ax3 = axes[1, 0]
            ax3.plot(df['timestamp'], df['oi'],
                    color='green', linewidth=2)
            ax3.set_title('持仓量变化', fontsize=14, fontweight='bold')
            ax3.set_ylabel('持仓量')
            ax3.grid(True, alpha=0.3)
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)

            # 4. 资金费率
            ax4 = axes[1, 1]
            ax4.plot(df['timestamp'], df['last_funding_rate'] * 100,
                    color='purple', linewidth=2)
            ax4.axhline(y=0.1, color='red', linestyle='--', alpha=0.7, label='0.1%阈值')
            ax4.axhline(y=-0.1, color='red', linestyle='--', alpha=0.7)
            ax4.set_title('资金费率', fontsize=14, fontweight='bold')
            ax4.set_ylabel('资金费率 (%)')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)

            # 5. 多空比率
            ax5 = axes[2, 0]
            ax5.plot(df['timestamp'], df['long_short_account_ratio'],
                    label='账户多空比', linewidth=2)
            ax5.plot(df['timestamp'], df['top_trader_account_ls_ratio'],
                    label='大户账户多空比', linewidth=2, linestyle='--')
            ax5.set_title('多空比率', fontsize=14, fontweight='bold')
            ax5.set_ylabel('比率')
            ax5.legend()
            ax5.grid(True, alpha=0.3)
            plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45)

            # 6. 主动买卖比
            ax6 = axes[2, 1]
            ax6.plot(df['timestamp'], df['taker_buy_sell_ratio'],
                    color='brown', linewidth=2)
            ax6.axhline(y=1, color='red', linestyle='--', alpha=0.3, label='平衡线')
            ax6.set_title('主动买卖比', fontsize=14, fontweight='bold')
            ax6.set_ylabel('买卖比率')
            ax6.legend()
            ax6.grid(True, alpha=0.3)
            plt.setp(ax6.xaxis.get_majorticklabels(), rotation=45)

            # 调整布局
            plt.tight_layout()

            # 保存图表
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            chart_filename = f"{symbol}_detailed_{timestamp}.png"
            chart_path = os.path.join(self.output_dir, chart_filename)

            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            print(f"详细图表已保存: {chart_path}")
            return chart_path

        except Exception as e:
            print(f"生成详细图表失败: {e}")
            return None


def test_chart_generation():
    """测试图表生成功能"""
    print("测试图表生成功能...")

    # 创建测试数据
    test_data = {
        'timestamp': pd.date_range('2025-11-29', periods=15, freq='5min'),
        'mark_price': [3000 + i*10 for i in range(15)],
        'index_price': [2995 + i*9 for i in range(15)],
        'basis_percent': [0.05 + i*0.01 for i in range(15)],
        'last_funding_rate': [0.0005 + i*0.0001 for i in range(15)],
        'oi': [1000000 + i*50000 for i in range(15)],
        'long_short_account_ratio': [1.5 + i*0.1 for i in range(15)],
        'top_trader_account_ls_ratio': [1.8 + i*0.08 for i in range(15)],
        'taker_buy_sell_ratio': [1.2 + i*0.05 for i in range(15)]
    }

    df = pd.DataFrame(test_data)

    generator = ChartGenerator()

    # 生成监控图表
    chart_path = generator.generate_monitoring_chart(
        symbol="TESTUSDT",
        df=df,
        funding_rate=0.0015,
        oi_ratio=2.3
    )

    if chart_path:
        print(f"监控图表生成成功: {chart_path}")

    # 生成详细分析图表
    detailed_path = generator.generate_detailed_analysis("TESTUSDT", df)

    if detailed_path:
        print(f"详细图表生成成功: {detailed_path}")


if __name__ == "__main__":
    test_chart_generation()