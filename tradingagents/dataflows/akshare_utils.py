import akshare as ak
from typing import Annotated, Callable, Any, Optional
from pandas import DataFrame
import pandas as pd
from functools import wraps
from datetime import datetime, timedelta
import os
import sys
import numpy as np

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)
try:
    from .utils import save_output, SavePathType, decorate_all_methods, add_market_prefix, convert_symbol
except ImportError:
    from tradingagents.dataflows.utils import save_output, SavePathType, decorate_all_methods, add_market_prefix, convert_symbol

def init_stock(func: Callable) -> Callable:
    """装饰器：转换股票代码格式"""
    @wraps(func)
    def wrapper(symbol: Annotated[str, "股票代码"], *args, **kwargs) -> Any:
        symbol = convert_symbol(symbol)
        return func(symbol, *args, **kwargs)
    return wrapper

@decorate_all_methods(init_stock)
class AKShareUtils:
    def get_stock_data(
        symbol: Annotated[str, "股票代码"],
        start_date: Annotated[str, "开始日期，格式：YYYY-mm-dd"],
        end_date: Annotated[str, "结束日期，格式：YYYY-mm-dd"],
        save_path: SavePathType = None,
    ) -> DataFrame:
        """获取股票历史数据"""
        # 转换日期格式从 YYYY-mm-dd 到 YYYYmmdd
        start_date_formatted = start_date.replace('-', '')
        end_date_formatted = end_date.replace('-', '')
        
        # 获取日线数据
        stock_data = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date_formatted,
            end_date=end_date_formatted,
            adjust="qfq"  # 前复权
        )
        
        # 检查返回数据是否为空
        if stock_data is None or stock_data.empty:
            print(f"无法获取股票 {symbol} 从 {start_date} 到 {end_date} 的数据")
            return DataFrame()
        
        print(f"before: {list(stock_data.columns)}")
        # 转换列名以匹配 YFinance 格式
        stock_data = stock_data.rename(columns={
            '日期': 'Date',
            '开盘': 'Open',
            '最高': 'High',
            '最低': 'Low',
            '收盘': 'Close',
            '成交量': 'Volume',
            '换手率': 'Turnover',  # 添加换手率
            '涨跌幅': 'Change',    # 添加涨跌幅
            '涨跌额': 'Amount'     # 添加涨跌额
        })
        print(f"after rename: {list(stock_data.columns)}")
        
        # 设置日期索引
        stock_data['Date'] = pd.to_datetime(stock_data['Date'])
        stock_data = stock_data.set_index('Date')
        # 添加 Adj Close 列（A股数据已经是前复权价格）
        stock_data['Adj Close'] = stock_data['Close']
        
        print(f"final columns: {list(stock_data.columns)}, index name: {stock_data.index.name}")
        
        if save_path:
            save_output(stock_data, f"Stock data for {symbol}", save_path)
        
        print(f"after: {list(stock_data.columns)}, save_path: {save_path}")
        return stock_data

    def get_stock_info(
        symbol: Annotated[str, "股票代码"],
    ) -> dict:
        """获取股票基本信息
        
        Returns:
            dict: {
                'symbol': 股票代码,
                'name': 股票名称,
                'total_shares': 总股本,
                'float_shares': 流通股,
                'market_cap': 总市值,
                'float_market_cap': 流通市值,
                'industry': 所属行业,
                'listing_date': 上市日期,
                'latest_price': 最新价格
            }
        """
        # 获取公司基本信息
        info = ak.stock_individual_info_em(symbol=symbol)
        if info.empty:
            return {}
            
        # 将DataFrame转换为字典
        info_dict = dict(zip(info['item'], info['value']))
        
        # 转换为统一格式
        stock_info = {
            'symbol': info_dict.get('股票代码', symbol),
            'name': info_dict.get('股票简称', 'N/A'),
            'total_shares': float(info_dict.get('总股本', 0)),
            'float_shares': float(info_dict.get('流通股', 0)),
            'market_cap': float(info_dict.get('总市值', 0)),
            'float_market_cap': float(info_dict.get('流通市值', 0)),
            'industry': info_dict.get('行业', 'N/A'),
            'listing_date': info_dict.get('上市时间', 'N/A'),
            'latest_price': float(info_dict.get('最新', 0))
        }
        
        return stock_info

    def get_company_info(
        symbol: Annotated[str, "股票代码"],
        save_path: Optional[str] = None,
    ) -> DataFrame:
        """获取公司详细信息"""
        # 获取公司基本信息
        info = ak.stock_individual_info_em(symbol=symbol)
        if info.empty:
            return DataFrame()
        
        # 将DataFrame转换为字典便于查找
        info_dict = dict(zip(info['item'], info['value']))
        
        # 转换为统一格式
        company_info = {
            "Company Name": info_dict.get('股票简称', 'N/A'),
            "Industry": info_dict.get('行业', 'N/A'),
            "Total Shares": float(info_dict.get('总股本', 0)),
            "Float Shares": float(info_dict.get('流通股', 0)),
            "Market Cap": float(info_dict.get('总市值', 0)),
            "Float Market Cap": float(info_dict.get('流通市值', 0)),
            "Latest Price": float(info_dict.get('最新', 0)),
            "Listing Date": info_dict.get('上市时间', 'N/A'),
            "Country": "China"
        }
        
        company_info_df = DataFrame([company_info])
        if save_path:
            company_info_df.to_csv(save_path)
            print(f"Company info for {symbol} saved to {save_path}")
        
        return company_info_df

    def get_stock_dividends(
        symbol: Annotated[str, "股票代码"],
        save_path: Optional[str] = None,
    ) -> DataFrame:
        """获取股息数据"""
        # 获取分红数据
        dividends = ak.stock_fhps_detail_em(symbol=symbol)
        if dividends.empty:
            return DataFrame()
        
        # # 转换列名
        # dividends = dividends.rename(columns={
        #     '除权除息日': 'Date',
        #     '分红金额': 'Dividends'
        # })
        
        # 设置日期索引
        dividends['Date'] = pd.to_datetime(dividends['除权除息日'])
        dividends = dividends.set_index('Date')
        
        if save_path:
            dividends.to_csv(save_path)
            print(f"Dividends for {symbol} saved to {save_path}")
        
        return dividends

    def get_income_stmt(symbol: Annotated[str, "股票代码"]) -> DataFrame:
        """获取利润表
        
        Returns:
            DataFrame: 最新一期的利润表数据，如果获取失败返回空DataFrame
        """
        try:
            # 获取利润表
            income_stmt = ak.stock_financial_report_sina(stock=add_market_prefix(symbol), symbol="利润表")
            if income_stmt.empty:
                return DataFrame()
            
            # 获取最新的报告期
            latest_date = income_stmt['报告日'].max()
            return income_stmt[income_stmt['报告日'] == latest_date].copy()
        except Exception as e:
            print(f"获取利润表数据失败: {str(e)}")
            return DataFrame()

    def get_balance_sheet(symbol: Annotated[str, "股票代码"]) -> DataFrame:
        """获取资产负债表
        
        Returns:
            DataFrame: 最新一期的资产负债表数据，如果获取失败返回空DataFrame
        """
        try:
            # 获取资产负债表
            balance_sheet = ak.stock_balance_sheet_by_report_em(symbol=add_market_prefix(symbol))
            if balance_sheet.empty:
                return DataFrame()
            
            # 获取最新的报告期
            latest_date = balance_sheet['REPORT_DATE'].max()
            return balance_sheet[balance_sheet['REPORT_DATE'] == latest_date].copy()
        except Exception as e:
            print(f"获取资产负债表数据失败: {str(e)}")
            return DataFrame()

    def get_cash_flow(symbol: Annotated[str, "股票代码"]) -> DataFrame:
        """获取现金流量表
        
        Returns:
            DataFrame: 最新一期的现金流量表数据，如果获取失败返回空DataFrame
        """
        try:
            # 获取现金流量表
            cash_flow = ak.stock_cash_flow_sheet_by_report_em(symbol=add_market_prefix(symbol))
            if cash_flow.empty:
                return DataFrame()
            
            # 获取最新的报告期
            latest_date = cash_flow['REPORT_DATE'].max()
            return cash_flow[cash_flow['REPORT_DATE'] == latest_date].copy()
        except Exception as e:
            print(f"获取现金流量表数据失败: {str(e)}")
            return DataFrame()

    def get_analyst_recommendations(symbol: Annotated[str, "股票代码"]) -> tuple:
        """获取分析师评级
        
        Returns:
            tuple: (最多数量的评级, 该评级的数量)，如果没有数据返回 (None, 0)
            评级一般分为：买入、增持、中性、减持、卖出
        """
        try:
            # 获取分析师评级数据
            recommendations = ak.stock_institute_recommend_detail(symbol=symbol)
            if recommendations.empty:
                return None, 0
            
            # 只保留最近一个月的数据
            recommendations['评级日期'] = pd.to_datetime(recommendations['评级日期'])
            one_month_ago = pd.Timestamp.now() - pd.DateOffset(months=1)
            recent_recommendations = recommendations[recommendations['评级日期'] >= one_month_ago]
            
            if recent_recommendations.empty:
                return None, 0
            
            # 统计评级数量
            rating_counts = recent_recommendations['最新评级'].value_counts()
            if rating_counts.empty:
                return None, 0
            
            # 获取出现最多的评级
            max_rating = rating_counts.index[0]
            max_count = rating_counts.iloc[0]
            
            return max_rating, max_count
            
        except Exception as e:
            print(f"获取分析师评级数据失败: {str(e)}")
            return None, 0

if __name__ == "__main__":
    # 设置显示选项
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_rows', 10)
    pd.set_option('display.float_format', lambda x: '{:,.2f}'.format(x) if isinstance(x, (float, int)) else str(x))
    
    # 测试代码
    try:
        # 测试股票代码
        symbol = "600519"  # 贵州茅台
        
        print("\n1. 测试市场标识前缀")
        print(f"原始代码: {symbol}")
        print(f"带市场标识: {add_market_prefix(symbol)}")
        
        test_symbols = ["600519", "000002", "002415", "300059", "688001"]
        print("\n不同市场股票代码测试:")
        for s in test_symbols:
            print(f"{s} -> {add_market_prefix(s)}")
        
        print("\n2. 测试获取股票基本信息")
        stock_info = AKShareUtils.get_stock_info(symbol)
        print("股票基本信息:")
        print(f"股票代码: {stock_info['symbol']}")
        print(f"股票名称: {stock_info['name']}")
        print(f"最新价格: {stock_info['latest_price']:.2f}")
        print(f"总股本: {stock_info['total_shares']:,.0f}")
        print(f"流通股: {stock_info['float_shares']:,.0f}")
        print(f"总市值: {stock_info['market_cap']:,.2f}")
        print(f"流通市值: {stock_info['float_market_cap']:,.2f}")
        print(f"所属行业: {stock_info['industry']}")
        print(f"上市日期: {stock_info['listing_date']}")
        
        print("\n3. 测试获取历史行情数据")
        # 获取最近30天的数据
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        stock_data = AKShareUtils.get_stock_data(symbol, start_date, end_date)
        print("\n历史行情数据前5行:")
        print(stock_data.head())
        
        print("\n4. 测试获取公司详细信息")
        company_info = AKShareUtils.get_company_info(symbol)
        print("\n公司详细信息:")
        print(company_info)
        
        print("\n5. 测试获取分红数据")
        dividends = AKShareUtils.get_stock_dividends(symbol)
        print("\n最近的分红记录:")
        if not dividends.empty:
            print(dividends.head())
        else:
            print("无分红记录")
        
        print("\n6. 测试获取财务报表数据")
        print("\n6.1 利润表:")
        income_stmt = AKShareUtils.get_income_stmt(symbol)
        if not income_stmt.empty:
            print(income_stmt.head())
        else:
            print("无法获取利润表数据")
        
        print("\n6.2 资产负债表:")
        balance_sheet = AKShareUtils.get_balance_sheet(symbol)
        if not balance_sheet.empty:
            print(balance_sheet.head())
        else:
            print("无法获取资产负债表数据")
        
        print("\n6.3 现金流量表:")
        cash_flow = AKShareUtils.get_cash_flow(symbol)
        if not cash_flow.empty:
            print(cash_flow.head())
        else:
            print("无法获取现金流量表数据")
        
        print("\n7. 测试获取分析师评级")
        rating, count = AKShareUtils.get_analyst_recommendations(symbol)
        print(f"最近一个月的主流评级: {rating}")
        print(f"该评级的分析师数量: {count}")
        
        # 获取原始评级数据用于展示
        recommendations = ak.stock_institute_recommend_detail(symbol=symbol)
        if not recommendations.empty:
            recommendations['评级日期'] = pd.to_datetime(recommendations['评级日期'])
            one_month_ago = pd.Timestamp.now() - pd.DateOffset(months=1)
            recent_recommendations = recommendations[recommendations['评级日期'] >= one_month_ago]
            
            if not recent_recommendations.empty:
                print("\n最近一个月的评级分布:")
                rating_dist = recent_recommendations['最新评级'].value_counts()
                for rating_type, count in rating_dist.items():
                    print(f"{rating_type}: {count}个")
            else:
                print("\n最近一个月没有评级数据")
        else:
            print("无法获取分析师评级数据")

    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        import traceback
        print(traceback.format_exc()) 