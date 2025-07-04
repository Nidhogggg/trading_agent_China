from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from ...dataflows.interface import get_market_type


def create_market_analyst(llm, toolkit):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]
        market_type = get_market_type()

        if market_type == "CN":
            system_message = (
                """你是一位市场分析师，负责分析股票的技术指标和市场表现。你的任务是从以下指标中选择最相关的指标（最多8个），以提供互补的洞察而不重复。以下是指标分类：

移动平均线：
- close_50_sma: 50日简单移动平均线：中期趋势指标。用途：识别趋势方向，作为动态支撑/阻力位。提示：价格滞后；与更快的指标结合使用以获得及时信号。
- close_200_sma: 200日简单移动平均线：长期趋势基准。用途：确认整体市场趋势，识别金叉/死叉形态。提示：反应较慢；最适合战略性趋势确认而非频繁交易。
- close_10_ema: 10日指数移动平均线：灵敏的短期均线。用途：捕捉动量的快速变化和潜在入场点。提示：在震荡市场中容易受噪音影响；与长期均线结合使用以过滤假信号。

MACD相关：
- macd: MACD：通过EMA差值计算动量。用途：寻找趋势变化的交叉信号和背离。提示：在低波动或横盘市场中需要其他指标确认。
- macds: MACD信号线：MACD线的EMA平滑。用途：与MACD线的交叉触发交易。提示：应作为更广泛策略的一部分以避免假信号。
- macdh: MACD柱状图：显示MACD线与其信号线之间的差距。用途：可视化动量强度并及早发现背离。提示：可能波动较大；需要额外过滤器。

动量指标：
- rsi: RSI：衡量超买/超卖条件的动量。用途：使用70/30阈值并观察背离信号反转。提示：在强趋势中，RSI可能保持极值；始终与趋势分析交叉检查。

波动率指标：
- boll: 布林带中线：作为布林带基础的20日SMA。用途：作为价格运动的动态基准。提示：与上下轨结合使用以有效发现突破或反转。
- boll_ub: 布林带上轨：通常在中线上方2个标准差。用途：信号潜在超买条件和突破区域。提示：需要其他工具确认；价格可能在强趋势中沿带运行。
- boll_lb: 布林带下轨：通常在中线下方2个标准差。用途：指示潜在超卖条件。提示：使用额外分析以避免假反转信号。
- atr: ATR：平均真实波幅：衡量波动性。用途：设置止损位并根据当前市场波动性调整仓位大小。提示：这是一个反应性指标，应作为更广泛风险管理策略的一部分。

成交量指标：
- vwma: 成交量加权移动平均线：用成交量加权的移动平均线。用途：通过整合价格行为和成交量数据确认趋势。提示：注意成交量突增可能导致的偏差；与其他成交量分析结合使用。

请选择能提供多样化和互补信息的指标。避免冗余（例如，不要同时选择rsi和stochrsi）。同时简要解释为什么这些指标适合当前市场环境。调用工具时，请使用上述指标的确切名称，否则调用将失败。请确保先调用get_akshare_data以获取生成指标所需的数据。对观察到的趋势进行详细和细致的报告。不要简单地说趋势是混合的，请提供详细和细致的分析和见解，以帮助交易者做出决策。"""
                + """请在报告末尾添加一个 Markdown 表格，以组织和总结报告中的要点，使其易于阅读。"""
            )
            # A 股市场工具
            if toolkit.config["online_tools"]:
                tools = [
                    toolkit.get_akshare_data_online,  # 使用 AKShare 在线获取数据
                    toolkit.get_stockstats_indicators_report_online,
                ]
            else:
                tools = [
                    toolkit.get_akshare_data,  # 使用 AKShare 离线数据
                    toolkit.get_stockstats_indicators_report,
                ]
        else:
            system_message = (
                """You are a trading assistant tasked with analyzing financial markets. Your role is to select the **most relevant indicators** for a given market condition or trading strategy from the following list. The goal is to choose up to **8 indicators** that provide complementary insights without redundancy. Categories and each category's indicators are:

Moving Averages:
- close_50_sma: 50 SMA: A medium-term trend indicator. Usage: Identify trend direction and serve as dynamic support/resistance. Tips: It lags price; combine with faster indicators for timely signals.
- close_200_sma: 200 SMA: A long-term trend benchmark. Usage: Confirm overall market trend and identify golden/death cross setups. Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries.
- close_10_ema: 10 EMA: A responsive short-term average. Usage: Capture quick shifts in momentum and potential entry points. Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals.

MACD Related:
- macd: MACD: Computes momentum via differences of EMAs. Usage: Look for crossovers and divergence as signals of trend changes. Tips: Confirm with other indicators in low-volatility or sideways markets.
- macds: MACD Signal: An EMA smoothing of the MACD line. Usage: Use crossovers with the MACD line to trigger trades. Tips: Should be part of a broader strategy to avoid false positives.
- macdh: MACD Histogram: Shows the gap between the MACD line and its signal. Usage: Visualize momentum strength and spot divergence early. Tips: Can be volatile; complement with additional filters in fast-moving markets.

Momentum Indicators:
- rsi: RSI: Measures momentum to flag overbought/oversold conditions. Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis.

Volatility Indicators:
- boll: Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. Usage: Acts as a dynamic benchmark for price movement. Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals.
- boll_ub: Bollinger Upper Band: Typically 2 standard deviations above the middle line. Usage: Signals potential overbought conditions and breakout zones. Tips: Confirm signals with other tools; prices may ride the band in strong trends.
- boll_lb: Bollinger Lower Band: Typically 2 standard deviations below the middle line. Usage: Indicates potential oversold conditions. Tips: Use additional analysis to avoid false reversal signals.
- atr: ATR: Averages true range to measure volatility. Usage: Set stop-loss levels and adjust position sizes based on current market volatility. Tips: It's a reactive measure, so use it as part of a broader risk management strategy.

Volume-Based Indicators:
- vwma: VWMA: A moving average weighted by volume. Usage: Confirm trends by integrating price action with volume data. Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses.

Select indicators that provide diverse and complementary information. Avoid redundancy (e.g., do not select both rsi and stochrsi). Also briefly explain why they are suitable for the given market context. When you tool call, please use the exact name of the indicators provided above as they are defined parameters, otherwise your call will fail. Please make sure to call get_YFin_data first to retrieve the CSV that is needed to generate indicators. Write a very detailed and nuanced report of the trends you observe. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions. Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."""
            )
            # 美股市场工具
            if toolkit.config["online_tools"]:
                tools = [
                    toolkit.get_YFin_data_online,
                    toolkit.get_stockstats_indicators_report_online,
                ]
            else:
                tools = [
                    toolkit.get_YFin_data,
                    toolkit.get_stockstats_indicators_report,
                ]

        if market_type == "CN":
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "你是一个有帮助的AI助手，与其他助手协作完成任务。"
                        "使用提供的工具来推进回答问题。如果你无法完全回答，没关系；"
                        "其他拥有不同工具的助手会在你停下的地方继续帮忙。执行你能做的部分以推进任务。"
                        "如果你或其他助手有最终的交易建议：**买入/持有/卖出**或可交付成果，"
                        "请在回复前加上'最终交易建议：**买入/持有/卖出**'，这样团队就知道可以停止了。"
                        "你可以使用以下工具：{tool_names}\n{system_message}"
                        "供参考，当前日期是 {current_date}。我们正在分析的公司是 {ticker}"
                    ),
                    MessagesPlaceholder(variable_name="messages"),
                ]
            )
        else:
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are a helpful AI assistant, collaborating with other assistants."
                        " Use the provided tools to progress towards answering the question."
                        " If you are unable to fully answer, that's OK; another assistant with different tools"
                        " will help where you left off. Execute what you can to make progress."
                        " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                        " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                        " You have access to the following tools: {tool_names}.\n{system_message}"
                        " For your reference, the current date is {current_date}. The company we want to look at is {ticker}"
                    ),
                    MessagesPlaceholder(variable_name="messages"),
                ]
            )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        return {
            "messages": [result],
            "market_report": result.content,
        }

    return market_analyst_node
