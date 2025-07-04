from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from ...dataflows.interface import get_market_type


def create_fundamentals_analyst(llm, toolkit):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]
        market_type = get_market_type()

        if market_type == "CN":
            system_message = (
                "你是一位专业的基本面分析师，负责对公司进行深入的基本面分析。请撰写一份全面的分析报告，重点关注以下方面：\n\n"
                "1. 财务分析：\n"
                "   - 资产负债表分析：资产质量、负债结构、资本充足性\n"
                "   - 现金流量表分析：经营、投资、筹资活动现金流\n"
                "   - 利润表分析：收入增长、盈利能力、费用控制\n"
                "   - 主要财务指标：ROE、ROA、毛利率、净利率等\n\n"
                "2. 行业地位：\n"
                "   - 市场份额和竞争优势\n"
                "   - 行业集中度和竞争格局\n"
                "   - 产品或服务的差异化程度\n\n"
                "3. 市场行为分析：\n"
                "   - 龙虎榜数据：大资金流向和主力资金动向\n"
                "   - 大宗交易：机构投资者的交易行为\n"
                "   - 融资融券：市场杠杆使用情况\n"
                "   - 北向资金：外资持仓变化趋势\n\n"
                "4. 风险提示：\n"
                "   - 财务风险\n"
                "   - 经营风险\n"
                "   - 行业风险\n"
                "   - 政策风险\n\n"
                "请基于数据进行深入分析，不要简单罗列数据。对于重要指标的变化，请解释其原因和潜在影响。"
                "在报告末尾，请用 Markdown 表格列出关键指标的同比、环比变化，并给出投资建议。"
            )
            # A 股市场工具
            tools = [
                toolkit.get_akshare_balance_sheet,     # 资产负债表
                toolkit.get_akshare_cashflow,          # 现金流量表
                toolkit.get_akshare_income_stmt,       # 利润表
                toolkit.get_akshare_finance_analysis,  # 财务分析
                toolkit.get_akshare_special_data,      # 特殊市场数据（龙虎榜、大宗交易、融资融券、北向资金等）
            ]
        else:
            system_message = (
                "You are a researcher tasked with analyzing fundamental information over the past week about a company. "
                "Please write a comprehensive report of the company's fundamental information such as financial documents, "
                "company profile, basic company financials, company financial history, insider sentiment and insider "
                "transactions to gain a full view of the company's fundamental information to inform traders. "
                "Make sure to include as much detail as possible. Do not simply state the trends are mixed, provide "
                "detailed and finegrained analysis and insights that may help traders make decisions."
                "Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."
            )
            # 美股市场工具
            if toolkit.config["online_tools"]:
                tools = [toolkit.get_fundamentals_openai]
            else:
                tools = [
                    toolkit.get_finnhub_company_insider_sentiment,
                    toolkit.get_finnhub_company_insider_transactions,
                    toolkit.get_simfin_balance_sheet,
                    toolkit.get_simfin_cashflow,
                    toolkit.get_simfin_income_stmt,
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
                        "For your reference, the current date is {current_date}. We are looking at the company {ticker}",
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
            "fundamentals_report": result.content,
        }

    return fundamentals_analyst_node
