import akshare as ak
import pandas as pd
from typing import Annotated, List, Dict, Optional
from datetime import datetime, timedelta
from functools import wraps

def convert_symbol(func):
    """装饰器：转换股票代码格式"""
    @wraps(func)
    def wrapper(symbol: str, *args, **kwargs):
        # 移除可能的市场后缀
        symbol = symbol.split('.')[0]
        # 确保是6位数字
        if len(symbol) != 6:
            raise ValueError(f"Invalid A-share stock symbol: {symbol}")
        return func(symbol, *args, **kwargs)
    return wrapper

class AKShareSpecialUtils:
    @staticmethod
    @convert_symbol
    def get_dragon_tiger_list(
        symbol: Annotated[str, "股票代码"],
        start_date: Annotated[str, "开始日期 YYYY-MM-DD"],
        end_date: Annotated[str, "结束日期 YYYY-MM-DD"]
    ) -> str:
        """获取个股龙虎榜数据"""
        try:
            df = ak.stock_lhb_detail_em(symbol=symbol)
            df = df[
                (df['交易日期'] >= start_date) & 
                (df['交易日期'] <= end_date)
            ]
        except:
            return "未找到龙虎榜数据"

        if df.empty:
            return "该时间段内无龙虎榜数据"

        report = ["## 龙虎榜数据\n"]
        
        for _, row in df.iterrows():
            report.append(f"### {row['交易日期']}")
            report.append(f"上榜原因: {row['上榜原因']}")
            report.append(f"解读: {row['解读']}")
            report.append(f"收盘价: {row['收盘价']} 涨跌幅: {row['涨跌幅']}%")
            report.append(f"成交额: {row['成交额']} 成交量: {row['成交量']}")
            report.append("\n买入金额最大的前5名营业部:")
            for i in range(1, 6):
                if f'买方营业部_{i}' in row and pd.notna(row[f'买方营业部_{i}']):
                    report.append(f"- {row[f'买方营业部_{i}']} 买入: {row[f'买方买入金额_{i}']}万")
            report.append("\n卖出金额最大的前5名营业部:")
            for i in range(1, 6):
                if f'卖方营业部_{i}' in row and pd.notna(row[f'卖方营业部_{i}']):
                    report.append(f"- {row[f'卖方营业部_{i}']} 卖出: {row[f'卖方卖出金额_{i}']}万")
            report.append("\n")

        return "\n".join(report)

    @staticmethod
    @convert_symbol
    def get_block_trades(
        symbol: Annotated[str, "股票代码"],
        start_date: Annotated[str, "开始日期 YYYY-MM-DD"],
        end_date: Annotated[str, "结束日期 YYYY-MM-DD"]
    ) -> str:
        """获取大宗交易数据"""
        try:
            df = ak.stock_dzjy_detail_em(symbol=symbol)
            df = df[
                (df['交易日期'] >= start_date) & 
                (df['交易日期'] <= end_date)
            ]
        except:
            return "未找到大宗交易数据"

        if df.empty:
            return "该时间段内无大宗交易数据"

        report = ["## 大宗交易数据\n"]
        
        for _, row in df.iterrows():
            report.append(f"### {row['交易日期']}")
            report.append(f"成交价: {row['成交价']} 折溢价率: {row['折溢价率']}%")
            report.append(f"成交量(万股): {row['成交量']} 成交额(万元): {row['成交额']}")
            if '买方营业部' in row and pd.notna(row['买方营业部']):
                report.append(f"买方营业部: {row['买方营业部']}")
            if '卖方营业部' in row and pd.notna(row['卖方营业部']):
                report.append(f"卖方营业部: {row['卖方营业部']}")
            report.append("\n")

        return "\n".join(report)

    @staticmethod
    @convert_symbol
    def get_margin_trading(
        symbol: Annotated[str, "股票代码"],
        start_date: Annotated[str, "开始日期 YYYY-MM-DD"],
        end_date: Annotated[str, "结束日期 YYYY-MM-DD"]
    ) -> str:
        """获取融资融券数据"""
        try:
            df = ak.stock_margin_detail_em(symbol=symbol)
            df = df[
                (df['交易日期'] >= start_date) & 
                (df['交易日期'] <= end_date)
            ]
        except:
            return "未找到融资融券数据"

        if df.empty:
            return "该时间段内无融资融券数据"

        report = ["## 融资融券数据\n"]
        
        for _, row in df.iterrows():
            report.append(f"### {row['交易日期']}")
            report.append(f"收盘价: {row['收盘价']} 涨跌幅: {row['涨跌幅']}%")
            report.append("\n融资数据:")
            report.append(f"- 余额(万元): {row['融资余额']} 买入额: {row['融资买入额']} 偿还额: {row['融资偿还额']}")
            report.append("\n融券数据:")
            report.append(f"- 余量(股): {row['融券余量']} 卖出量: {row['融券卖出量']} 偿还量: {row['融券偿还量']}")
            report.append(f"- 余额(万元): {row['融券余额']}")
            report.append(f"\n融资融券余额(万元): {row['融资融券余额']}")
            report.append("\n")

        return "\n".join(report)

    @staticmethod
    @convert_symbol
    def get_north_south_flow(
        symbol: Annotated[str, "股票代码"],
        start_date: Annotated[str, "开始日期 YYYY-MM-DD"],
        end_date: Annotated[str, "结束日期 YYYY-MM-DD"]
    ) -> str:
        """获取个股北向资金数据"""
        try:
            df = ak.stock_hsgt_individual_em(symbol=symbol)
            df = df[
                (df['日期'] >= start_date) & 
                (df['日期'] <= end_date)
            ]
        except:
            return "未找到北向资金数据"

        if df.empty:
            return "该时间段内无北向资金数据"

        report = ["## 北向资金数据\n"]
        
        for _, row in df.iterrows():
            report.append(f"### {row['日期']}")
            report.append(f"收盘价: {row['收盘价']} 涨跌幅: {row['涨跌幅']}%")
            report.append(f"持股数量(万股): {row['持股数量']} 持股市值(万元): {row['持股市值']}")
            report.append(f"持股占比: {row['持股占比']}% 持股市值变化(万元): {row['市值变化']}")
            report.append(f"持股数量变化(万股): {row['持股变动']}")
            report.append("\n")

        return "\n".join(report)

    @staticmethod
    def get_industry_analysis(
        industry: Annotated[str, "行业名称"],
        date: Annotated[str, "日期 YYYY-MM-DD"]
    ) -> str:
        """获取行业资金流向分析"""
        try:
            # 获取行业资金流向
            df_flow = ak.stock_sector_fund_flow_hist("板块资金流", date)
            # 获取行业涨跌幅
            df_perf = ak.stock_sector_detail(sector="行业")
        except:
            return "未找到行业分析数据"

        report = ["## 行业分析数据\n"]

        # 处理资金流向数据
        if not df_flow.empty:
            industry_flow = df_flow[df_flow['板块名称'] == industry]
            if not industry_flow.empty:
                row = industry_flow.iloc[0]
                report.append(f"### 资金流向 ({date})")
                report.append(f"净额(万元): {row['净额']} 净占比: {row['净占比']}%")
                report.append(f"主力净额(万元): {row['主力净额']} 主力净占比: {row['主力净占比']}%")
                report.append(f"超大单净额(万元): {row['超大单净额']} 超大单净占比: {row['超大单净占比']}%")
                report.append("\n")

        # 处理行业整体表现数据
        if not df_perf.empty:
            industry_perf = df_perf[df_perf['行业名称'] == industry]
            if not industry_perf.empty:
                row = industry_perf.iloc[0]
                report.append("### 行业整体表现")
                report.append(f"平均涨跌幅: {row['涨跌幅']}%")
                report.append(f"总市值(亿): {row['总市值']} 流通市值(亿): {row['流通市值']}")
                report.append(f"换手率: {row['换手率']}% 上涨家数: {row['上涨家数']} 下跌家数: {row['下跌家数']}")
                report.append("\n")

        return "\n".join(report)

    @staticmethod
    def format_special_report(
        dragon_tiger: str = "",
        block_trades: str = "",
        margin_trading: str = "",
        north_flow: str = "",
        industry_analysis: str = ""
    ) -> str:
        """格式化特殊数据报告"""
        report_parts = []
        
        if dragon_tiger:
            report_parts.append(dragon_tiger)
        if block_trades:
            report_parts.append(block_trades)
        if margin_trading:
            report_parts.append(margin_trading)
        if north_flow:
            report_parts.append(north_flow)
        if industry_analysis:
            report_parts.append(industry_analysis)
            
        if not report_parts:
            return "无特殊数据"
            
        return "\n\n".join(report_parts) 