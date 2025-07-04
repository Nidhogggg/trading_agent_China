import akshare as ak
import pandas as pd
from typing import Annotated, Optional
from datetime import datetime
from functools import wraps
import numpy as np
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)
try:
    from .utils import add_market_prefix, convert_symbol
except ImportError:
    from tradingagents.dataflows.utils import add_market_prefix, convert_symbol

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

class AKShareFinanceUtils:
    @staticmethod
    @convert_symbol
    def get_balance_sheet(
        symbol: Annotated[str, "股票代码"],
        freq: Annotated[str, "报告频率：annual/quarterly"] = "annual",
        report_date: Optional[str] = None,
        filter_empty: bool = True
    ) -> pd.DataFrame:
        """获取资产负债表数据
        
        Args:
            symbol: 股票代码
            freq: 报告频率，annual 或 quarterly
            report_date: 报告日期，格式：YYYYMMDD，如果为 None 则获取最新报告
            filter_empty: 是否过滤空值列
        
        Returns:
            pd.DataFrame: 包含资产负债表主要字段的DataFrame
        """
        try:
            # 获取资产负债表数据
            df = ak.stock_financial_report_sina(stock=add_market_prefix(symbol), symbol="资产负债表")
            if df.empty:
                return pd.DataFrame()
            
            # 转换报告日期为datetime格式并排序
            df['报告日'] = pd.to_datetime(df['报告日'])
            df = df.sort_values('报告日', ascending=False)
            
            # 根据频率筛选数据
            if freq == "annual":
                df = df[df['报告日'].dt.month == 12]  # 只保留年报数据
            
            # 如果指定了报告日期，筛选对应数据
            if report_date:
                df = df[df['报告日'].dt.strftime('%Y%m%d') == report_date]
            
            # 计算一些常用财务比率
            try:
                # 流动比率 = 流动资产合计 / 流动负债合计
                if '流动资产合计' in df.columns and '流动负债合计' in df.columns:
                    df['流动比率'] = df['流动资产合计'].astype(float) / df['流动负债合计'].astype(float)
                
                # 速动比率 = (流动资产合计 - 存货) / 流动负债合计
                if '流动资产合计' in df.columns and '存货' in df.columns and '流动负债合计' in df.columns:
                    df['速动比率'] = (df['流动资产合计'].astype(float) - df['存货'].astype(float)) / df['流动负债合计'].astype(float)
                
                # 资产负债率 = 负债合计 / 资产总计
                if '负债合计' in df.columns and '资产总计' in df.columns:
                    df['资产负债率(%)'] = df['负债合计'].astype(float) / df['资产总计'].astype(float) * 100
            except Exception as e:
                print(f"Warning: Error calculating financial ratios: {str(e)}")
            
            # 过滤空值列
            if filter_empty:
                df = AKShareFinanceUtils.filter_non_empty_data(df)
            
            return df
            
        except Exception as e:
            print(f"Error getting balance sheet data: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    @convert_symbol
    def get_income_statement(
        symbol: Annotated[str, "股票代码"],
        freq: Annotated[str, "报告频率：annual/quarterly"] = "annual",
        report_date: Optional[str] = None,
        filter_empty: bool = True
    ) -> pd.DataFrame:
        """获取利润表数据
        
        Args:
            symbol: 股票代码
            freq: 报告频率，annual 或 quarterly
            report_date: 报告日期，格式：YYYYMMDD，如果为 None 则获取最新报告
            filter_empty: 是否过滤空值列
        
        Returns:
            pd.DataFrame: 包含利润表主要字段的DataFrame
        """
        try:
            # 获取利润表数据
            df = ak.stock_financial_report_sina(stock=add_market_prefix(symbol), symbol="利润表")
            if df.empty:
                return pd.DataFrame()
            
            # 转换报告日期为datetime格式并排序
            df['报告日'] = pd.to_datetime(df['报告日'])
            df = df.sort_values('报告日', ascending=False)
            
            # 根据频率筛选数据
            if freq == "annual":
                df = df[df['报告日'].dt.month == 12]  # 只保留年报数据
            
            # 如果指定了报告日期，筛选对应数据
            if report_date:
                df = df[df['报告日'].dt.strftime('%Y%m%d') == report_date]
            
            # 计算一些常用财务比率
            try:
                # 毛利率 = (营业收入 - 营业成本) / 营业收入
                if '营业收入' in df.columns and '营业成本' in df.columns:
                    revenue = df['营业收入'].astype(float)
                    cost = df['营业成本'].astype(float)
                    df['毛利率(%)'] = (revenue - cost) / revenue * 100
                
                # 营业利润率 = 营业利润 / 营业收入
                if '营业利润' in df.columns and '营业收入' in df.columns:
                    op_profit = df['营业利润'].astype(float)
                    df['营业利润率(%)'] = op_profit / revenue * 100
                
                # 净利润率 = 净利润 / 营业收入
                if '净利润' in df.columns and '营业收入' in df.columns:
                    net_profit = df['净利润'].astype(float)
                    df['净利润率(%)'] = net_profit / revenue * 100
                
                # 费用率 = (销售费用 + 管理费用 + 研发费用) / 营业收入
                if all(x in df.columns for x in ['销售费用', '管理费用', '研发费用', '营业收入']):
                    total_expenses = (df['销售费用'].astype(float) + 
                                   df['管理费用'].astype(float) + 
                                   df['研发费用'].astype(float))
                    df['费用率(%)'] = total_expenses / revenue * 100
                
                # 研发投入比 = 研发费用 / 营业收入
                if '研发费用' in df.columns and '营业收入' in df.columns:
                    rd_expense = df['研发费用'].astype(float)
                    df['研发投入比(%)'] = rd_expense / revenue * 100
                
            except Exception as e:
                print(f"Warning: Error calculating financial ratios: {str(e)}")
            
            # 过滤空值列
            if filter_empty:
                df = AKShareFinanceUtils.filter_non_empty_data(df)
            
            return df
            
        except Exception as e:
            print(f"Error getting income statement data: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    @convert_symbol
    def get_cash_flow(
        symbol: Annotated[str, "股票代码"],
        freq: Annotated[str, "报告频率：annual/quarterly"] = "annual",
        report_date: Optional[str] = None,
        filter_empty: bool = True
    ) -> pd.DataFrame:
        """获取现金流量表数据
        
        Args:
            symbol: 股票代码
            freq: 报告频率，annual 或 quarterly
            report_date: 报告日期，格式：YYYYMMDD，如果为 None 则获取最新报告
            filter_empty: 是否过滤空值列
        
        Returns:
            pd.DataFrame: 包含现金流量表主要字段的DataFrame
        """
        try:
            # 获取现金流量表数据
            df = ak.stock_financial_report_sina(stock=add_market_prefix(symbol), symbol="现金流量表")
            if df.empty:
                return pd.DataFrame()
            
            # 转换报告日期为datetime格式并排序
            df['报告日'] = pd.to_datetime(df['报告日'])
            df = df.sort_values('报告日', ascending=False)
            
            # 根据频率筛选数据
            if freq == "annual":
                df = df[df['报告日'].dt.month == 12]  # 只保留年报数据
            
            # 如果指定了报告日期，筛选对应数据
            if report_date:
                df = df[df['报告日'].dt.strftime('%Y%m%d') == report_date]
            
            # 计算一些常用现金流指标
            try:
                # 经营活动现金流量净额占比
                if all(x in df.columns for x in ['经营活动产生的现金流量净额', '投资活动产生的现金流量净额', '筹资活动产生的现金流量净额']):
                    op_cash = df['经营活动产生的现金流量净额'].astype(float)
                    inv_cash = df['投资活动产生的现金流量净额'].astype(float)
                    fin_cash = df['筹资活动产生的现金流量净额'].astype(float)
                    total_cash = abs(op_cash) + abs(inv_cash) + abs(fin_cash)
                    df['经营活动现金流占比(%)'] = op_cash / total_cash * 100
                    df['投资活动现金流占比(%)'] = inv_cash / total_cash * 100
                    df['筹资活动现金流占比(%)'] = fin_cash / total_cash * 100
                
                # 现金收入比 = 销售商品、提供劳务收到的现金 / 营业收入
                if '销售商品、提供劳务收到的现金' in df.columns:
                    sales_cash = df['销售商品、提供劳务收到的现金'].astype(float)
                    df['现金收入比'] = sales_cash
                
                # 现金流量比率 = 经营活动产生的现金流量净额 / 流动负债合计
                if '经营活动产生的现金流量净额' in df.columns:
                    op_cash_flow = df['经营活动产生的现金流量净额'].astype(float)
                    df['经营活动现金流量净额'] = op_cash_flow
                
            except Exception as e:
                print(f"Warning: Error calculating cash flow ratios: {str(e)}")
            
            # 过滤空值列
            if filter_empty:
                df = AKShareFinanceUtils.filter_non_empty_data(df)
            
            return df
            
        except Exception as e:
            print(f"Error getting cash flow statement data: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    @convert_symbol
    def get_financial_indicators(
        symbol: Annotated[str, "股票代码"],
        start_year: Optional[str] = None
    ) -> pd.DataFrame:
        """获取主要财务指标数据
        
        Args:
            symbol: 股票代码
            start_year: 开始年份，格式：YYYY，如果为 None 则获取最近 4 年数据
        
        Returns:
            pd.DataFrame: 包含主要财务指标的DataFrame
        """
        try:
            # 如果没有指定开始年份，则获取最近4年的数据
            if start_year is None:
                start_year = str(pd.Timestamp.now().year - 4)
            
            # 获取财务指标数据
            df = ak.stock_financial_analysis_indicator(symbol=symbol, start_year=start_year)
            if df.empty:
                return pd.DataFrame()
            
            # 转换日期格式并排序
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.sort_values('日期', ascending=False)
            
            # 计算同比变化
            try:
                # 获取最新两期数据
                latest_data = df.iloc[0]
                if len(df) > 1:
                    prev_data = df.iloc[1]
                    
                    # 计算主要指标的同比变化
                    yoy_metrics = [
                        '摊薄每股收益(元)',
                        '净资产收益率(%)',
                        '营业利润率(%)',
                        '销售净利率(%)',
                        '总资产周转率(次)'
                    ]
                    
                    for metric in yoy_metrics:
                        if metric in latest_data.index and metric in prev_data.index:
                            try:
                                curr_value = float(latest_data[metric])
                                prev_value = float(prev_data[metric])
                                if prev_value != 0:
                                    yoy_change = ((curr_value - prev_value) / prev_value * 100)
                                    df.loc[df.index[0], f'{metric}_同比变化(%)'] = round(yoy_change, 2)
                            except (ValueError, TypeError):
                                df.loc[df.index[0], f'{metric}_同比变化(%)'] = None
                
            except Exception as e:
                print(f"Warning: Error calculating YoY changes: {str(e)}")
            
            return df
            
        except Exception as e:
            print(f"Error getting financial indicators: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def format_financial_report(
        balance_sheet: pd.DataFrame,
        income_stmt: pd.DataFrame,
        cash_flow: pd.DataFrame,
        report_date: Optional[str] = None
    ) -> dict:
        """将三张财务报表格式化为统一的格式"""
        if report_date:
            # 筛选指定日期的数据
            balance_sheet = balance_sheet[balance_sheet['报告日'].dt.strftime('%Y%m%d') == report_date]
            income_stmt = income_stmt[income_stmt['报告日'].dt.strftime('%Y%m%d') == report_date]
            cash_flow = cash_flow[cash_flow['报告日'].dt.strftime('%Y%m%d') == report_date]
            
        return {
            "资产负债表": balance_sheet.to_dict('records')[0] if not balance_sheet.empty else {},
            "利润表": income_stmt.to_dict('records')[0] if not income_stmt.empty else {},
            "现金流量表": cash_flow.to_dict('records')[0] if not cash_flow.empty else {}
        }

    @staticmethod
    def get_finance_analysis(symbol: str, curr_date: str) -> str:
        """获取财务分析数据，包括主要财务指标等
        
        Args:
            symbol: 股票代码
            curr_date: 当前日期，格式：YYYY-MM-DD
        
        Returns:
            str: 财务分析报告（markdown格式）
        """
        try:
            # 
            curr_date = pd.to_datetime(curr_date)
            start_year = str(curr_date.year - 1)
            # 1. 获取主要财务指标
            finance_indicator = AKShareFinanceUtils.get_financial_indicators(symbol)
            if finance_indicator.empty:
                return "无法获取财务指标数据"
            
            # 2. 获取历史财务数据
            fin_abstract = ak.stock_financial_abstract(symbol=symbol)
            
            # 确保数据按日期降序排序
            finance_indicator['日期'] = pd.to_datetime(finance_indicator['日期'])
            finance_indicator = finance_indicator.sort_values('日期', ascending=False)
            
            # 获取最新两期数据
            latest_data = None
            prev_data = None
            if len(finance_indicator) > 0:
                latest_data = finance_indicator.iloc[0]
                if len(finance_indicator) > 1:
                    prev_data = finance_indicator.iloc[1]
            
            if latest_data is None:
                return "无法获取最新财务指标数据"
            
            # 生成分析报告
            report = "## 财务分析报告\n\n"
            
            # 1. 盈利能力分析
            report += "### 1. 盈利能力分析\n"
            profit_metrics = {
                "摊薄每股收益(元)": "每股收益",
                "净资产收益率(%)": "ROE",
                "总资产利润率(%)": "ROA",
                "销售净利率(%)": "销售净利率",
                "营业利润率(%)": "营业利润率"
            }
            
            for key, name in profit_metrics.items():
                value = latest_data.get(key, 'N/A')
                yoy = latest_data.get(f"{key}_同比变化(%)", 'N/A')
                if yoy != 'N/A':
                    yoy = f"{yoy:+.2f}%"
                report += f"- {name}: {value} (同比变化: {yoy})\n"
            
            # 2. 运营效率分析
            report += "\n### 2. 运营效率分析\n"
            operation_metrics = {
                "总资产周转率(次)": "总资产周转率",
                "应收账款周转率(次)": "应收账款周转率",
                "存货周转率(次)": "存货周转率",
                "流动资产周转率(次)": "流动资产周转率"
            }
            
            for key, name in operation_metrics.items():
                value = latest_data.get(key, 'N/A')
                yoy = latest_data.get(f"{key}_同比变化(%)", 'N/A')
                if yoy != 'N/A':
                    yoy = f"{yoy:+.2f}%"
                report += f"- {name}: {value} (同比变化: {yoy})\n"
            
            # 3. 偿债能力分析
            report += "\n### 3. 偿债能力分析\n"
            debt_metrics = {
                "资产负债率(%)": "资产负债率",
                "流动比率": "流动比率",
                "速动比率": "速动比率",
                "现金比率(%)": "现金比率"
            }
            
            for key, name in debt_metrics.items():
                value = latest_data.get(key, 'N/A')
                yoy = latest_data.get(f"{key}_同比变化(%)", 'N/A')
                if yoy != 'N/A':
                    yoy = f"{yoy:+.2f}%"
                report += f"- {name}: {value} (同比变化: {yoy})\n"
            
            # 4. 成长能力分析
            report += "\n### 4. 成长能力分析\n"
            growth_metrics = {
                "主营业务收入增长率(%)": "营收增长率",
                "净利润增长率(%)": "净利润增长率",
                "净资产增长率(%)": "净资产增长率",
                "总资产增长率(%)": "总资产增长率"
            }
            
            for key, name in growth_metrics.items():
                value = latest_data.get(key, 'N/A')
                report += f"- {name}: {value}\n"
            
            # 5. 现金流分析
            report += "\n### 5. 现金流分析\n"
            cash_metrics = {
                "经营现金净流量对销售收入比率(%)": "经营现金收入比",
                "资产的经营现金流量回报率(%)": "现金流回报率",
                "经营现金净流量与净利润的比率(%)": "现金净利率",
                "每股经营性现金流(元)": "每股经营现金流"
            }
            
            for key, name in cash_metrics.items():
                value = latest_data.get(key, 'N/A')
                yoy = latest_data.get(f"{key}_同比变化(%)", 'N/A')
                if yoy != 'N/A':
                    yoy = f"{yoy:+.2f}%"
                report += f"- {name}: {value} (同比变化: {yoy})\n"
            
            # 6. 历史业绩趋势
            if not fin_abstract.empty:
                report += "\n### 6. 历史业绩趋势\n"
                # 获取最近的年度数据
                annual_data = fin_abstract[fin_abstract['选项'] == '常用指标']
                if not annual_data.empty:
                    # 获取归母净利润数据
                    net_profit = annual_data[annual_data['指标'] == '归母净利润'].iloc[0]
                    # 获取营业总收入数据
                    revenue = annual_data[annual_data['指标'] == '营业总收入'].iloc[0]
                    
                    report += "最近四年业绩数据：\n\n"
                    report += "| 年份 | 营业总收入(亿元) | 同比增长 | 归母净利润(亿元) | 同比增长 |\n"
                    report += "|------|----------------|----------|----------------|----------|\n"
                    
                    # 获取最近4年的年报数据
                    years = sorted([col for col in net_profit.index if col.endswith('1231')][0:4], reverse=True)
                    for i, year in enumerate(years):
                        try:
                            curr_revenue = float(revenue[year]) / 1e8  # 转换为亿元
                            curr_profit = float(net_profit[year]) / 1e8  # 转换为亿元
                            
                            if i < len(years) - 1:  # 不是最后一年，可以计算同比
                                prev_year = years[i + 1]
                                rev_growth = (float(revenue[year]) / float(revenue[prev_year]) - 1) * 100
                                profit_growth = (float(net_profit[year]) / float(net_profit[prev_year]) - 1) * 100
                                report += f"| {year[:4]} | {curr_revenue:.2f} | {rev_growth:+.2f}% | {curr_profit:.2f} | {profit_growth:+.2f}% |\n"
                            else:  # 最后一年，没有同比数据
                                report += f"| {year[:4]} | {curr_revenue:.2f} | - | {curr_profit:.2f} | - |\n"
                        except (ValueError, TypeError, ZeroDivisionError):
                            report += f"| {year[:4]} | N/A | N/A | N/A | N/A |\n"
            
            return report

        except Exception as e:
            print(f"Error getting finance analysis data: {str(e)}")
            return "获取财务分析数据失败"

    @staticmethod
    def filter_non_empty_data(df: pd.DataFrame, threshold: float = 0.0) -> pd.DataFrame:
        """过滤掉全为nan或0的列，只保留有意义的数据
        
        Args:
            df: 原始DataFrame
            threshold: 数值阈值，小于此值的视为空值
        
        Returns:
            pd.DataFrame: 过滤后的DataFrame
        """
        if df.empty:
            return df
        
        # 对于数值列，过滤掉全为nan或0的列
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        non_empty_cols = []
        
        for col in df.columns:
            if col in numeric_cols:
                # 数值列：过滤掉全为nan或小于阈值的列
                if not df[col].isna().all() and (df[col].abs() > threshold).any():
                    non_empty_cols.append(col)
            else:
                # 非数值列：过滤掉全为nan的列
                if not df[col].isna().all():
                    non_empty_cols.append(col)
        
        return df[non_empty_cols]

if __name__ == "__main__":
    # 设置显示选项
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_rows', 20)
    pd.set_option('display.float_format', lambda x: '{:,.2f}'.format(x) if isinstance(x, (float, int)) else str(x))
    
    try:
        # 测试股票代码
        symbol = "600886"  # 国投电力
        curr_date = datetime.now().strftime("%Y-%m-%d")
        
        print("\n1. 测试获取资产负债表")
        print("\n1.1 年度数据:")
        balance_sheet_annual = AKShareFinanceUtils.get_balance_sheet(symbol, freq="annual")
        if not balance_sheet_annual.empty:
            print(balance_sheet_annual.head())
        else:
            print("无法获取年度资产负债表数据")
            
        print("\n1.2 季度数据:")
        balance_sheet_quarterly = AKShareFinanceUtils.get_balance_sheet(symbol, freq="quarterly")
        if not balance_sheet_quarterly.empty:
            print(balance_sheet_quarterly.head())
        else:
            print("无法获取季度资产负债表数据")
        
        print("\n2. 测试获取利润表")
        print("\n2.1 年度数据:")
        income_stmt_annual = AKShareFinanceUtils.get_income_statement(symbol, freq="annual")
        if not income_stmt_annual.empty:
            print(income_stmt_annual.head())
        else:
            print("无法获取年度利润表数据")
            
        print("\n2.2 季度数据:")
        income_stmt_quarterly = AKShareFinanceUtils.get_income_statement(symbol, freq="quarterly")
        if not income_stmt_quarterly.empty:
            print(income_stmt_quarterly.head())
        else:
            print("无法获取季度利润表数据")
        
        print("\n3. 测试获取现金流量表")
        print("\n3.1 年度数据:")
        cash_flow_annual = AKShareFinanceUtils.get_cash_flow(symbol, freq="annual")
        if not cash_flow_annual.empty:
            print(cash_flow_annual.head())
        else:
            print("无法获取年度现金流量表数据")
            
        print("\n3.2 季度数据:")
        cash_flow_quarterly = AKShareFinanceUtils.get_cash_flow(symbol, freq="quarterly")
        if not cash_flow_quarterly.empty:
            print(cash_flow_quarterly.head())
        else:
            print("无法获取季度现金流量表数据")
        
        print("\n4. 测试获取财务指标")
        financial_indicators = AKShareFinanceUtils.get_financial_indicators(symbol)
        if not financial_indicators.empty:
            print(financial_indicators.head())
        else:
            print("无法获取财务指标数据")
        
        print("\n5. 测试财务报表格式化")
        formatted_report = AKShareFinanceUtils.format_financial_report(
            balance_sheet_annual,
            income_stmt_annual,
            cash_flow_annual
        )
        print("\n5.1 资产负债表数据:")
        for key, value in formatted_report['资产负债表'].items():
            print(f"{key}: {value}")
            
        print("\n5.2 利润表数据:")
        for key, value in formatted_report['利润表'].items():
            print(f"{key}: {value}")
            
        print("\n5.3 现金流量表数据:")
        for key, value in formatted_report['现金流量表'].items():
            print(f"{key}: {value}")
        
        print("\n6. 测试获取财务分析报告")
        analysis_report = AKShareFinanceUtils.get_finance_analysis(symbol, curr_date)
        print(analysis_report)

    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        import traceback
        print(traceback.format_exc()) 