#!/usr/bin/env python3
"""
测试 stockstats_utils 的日志功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradingagents.dataflows.stockstats_utils import StockstatsUtils
from datetime import datetime, timedelta

def test_stockstats_logging():
    """测试股票统计工具的日志功能"""
    print("=" * 60)
    print("测试 StockstatsUtils 日志功能")
    print("=" * 60)
    
    # 测试参数
    symbol = "600126"  # 杭钢股份
    indicator = "rsi_14"  # RSI指标
    # curr_date = datetime.now().strftime("%Y-%m-%d")
    curr_date = "2025-06-20"
    data_dir = "./data_cache"  # 测试数据目录
    
    print(f"测试参数:")
    print(f"  Symbol: {symbol}")
    print(f"  Indicator: {indicator}")
    print(f"  Date: {curr_date}")
    print(f"  Data Directory: {data_dir}")
    print()
    
    # 测试在线模式
    print("1. 测试在线模式 (online=True):")
    try:
        result = StockstatsUtils.get_stock_stats(
            symbol=symbol,
            indicator=indicator,
            curr_date=curr_date,
            data_dir=data_dir,
            online=True
        )
        print(f"✓ 在线模式测试成功，结果: {result}")
    except Exception as e:
        print(f"✗ 在线模式测试失败: {e}")
    
    print("\n" + "-" * 40 + "\n")
    
    # 测试离线模式
    print("2. 测试离线模式 (online=False):")
    try:
        result = StockstatsUtils.get_stock_stats(
            symbol=symbol,
            indicator=indicator,
            curr_date=curr_date,
            data_dir=data_dir,
            online=False
        )
        print(f"✓ 离线模式测试成功，结果: {result}")
    except Exception as e:
        print(f"✗ 离线模式测试失败: {e}")
    
    print("\n" + "-" * 40 + "\n")
    
    # 测试无效指标
    print("3. 测试无效指标:")
    try:
        result = StockstatsUtils.get_stock_stats(
            symbol=symbol,
            indicator="invalid_indicator",
            curr_date=curr_date,
            data_dir=data_dir,
            online=True
        )
        print(f"✓ 无效指标测试成功，结果: {result}")
    except Exception as e:
        print(f"✗ 无效指标测试失败: {e}")
    
    print("\n" + "-" * 40 + "\n")
    
    # 测试无效日期
    print("4. 测试无效日期 (周末):")
    weekend_date = "2024-01-07"  # 周日
    try:
        result = StockstatsUtils.get_stock_stats(
            symbol=symbol,
            indicator=indicator,
            curr_date=weekend_date,
            data_dir=data_dir,
            online=True
        )
        print(f"✓ 周末日期测试成功，结果: {result}")
    except Exception as e:
        print(f"✗ 周末日期测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_stockstats_logging() 