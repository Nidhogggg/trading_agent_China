from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from ...dataflows.interface import get_market_type


def create_news_analyst(llm, toolkit):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        market_type = get_market_type()

        if market_type == "CN":
            system_message = (
                "你是一位专业的新闻研究员，负责分析与公司和市场相关的新闻信息。请撰写一份全面的报告，重点关注以下方面：\n"
                "1. 公司新闻：重大事件、管理层变动、业务发展等\n"
                "2. 行业新闻：产业政策、技术突破、竞争格局等\n"
                "3. 市场新闻：宏观经济、监管政策、市场情绪等\n"
                "4. 公告解读：重要公告的详细分析和潜在影响\n\n"
                "请特别关注以下信息来源：\n"
                "- 公司公告和新闻发布\n"
                "- 行业协会和监管机构的政策文件\n"
                "- 主流财经媒体的深度报道\n"
                "- 市场分析师的研究报告\n\n"
                "不要简单地罗列新闻，而是要提供深入的分析和见解，帮助交易者理解新闻背后的影响。"
                "请在报告末尾添加一个 Markdown 表格，总结关键新闻及其潜在影响。"
            )
            # A 股市场工具
            tools = [
                toolkit.get_company_news,  # 公司相关新闻
                toolkit.get_market_news,   # 市场相关新闻
            ]
        else:
            system_message = (
                "You are a news researcher tasked with analyzing recent news and trends over the past week. "
                "Please write a comprehensive report of the current state of the world that is relevant for trading and macroeconomics. "
                "Look at news from EODHD, and finnhub to be comprehensive. Do not simply state the trends are mixed, "
                "provide detailed and finegrained analysis and insights that may help traders make decisions."
                "Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."
            )
            # 美股市场工具
            if toolkit.config["online_tools"]:
                tools = [toolkit.get_global_news_openai, toolkit.get_google_news]
            else:
                tools = [
                    toolkit.get_finnhub_news,
                    toolkit.get_reddit_news,
                    toolkit.get_google_news,
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
            "news_report": result.content,
        }

    return news_analyst_node
