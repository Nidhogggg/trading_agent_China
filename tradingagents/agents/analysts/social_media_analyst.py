from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from ...dataflows.interface import get_market_type


def create_social_media_analyst(llm, toolkit):
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]
        market_type = get_market_type()

        if market_type == "CN":
            system_message = (
                "你是一位社交媒体分析师，负责分析过去一周特定公司的社交媒体讨论和公众情绪。"
                "你将获得一个公司的名称，你的目标是通过分析雪球上的讨论数据，包括热门讨论、用户关注度和情绪变化等，"
                "撰写一份全面的长篇报告，详细说明你的分析、见解以及对交易者和投资者的启示。"
                "请特别关注以下几个方面：\n"
                "1. 讨论热度：帖子数量、评论数量、转发数等\n"
                "2. 讨论质量：高质量分析帖的主要观点\n"
                "3. 情绪倾向：看多/看空比例，情绪变化趋势\n"
                "4. 关注度变化：粉丝增减情况，机构关注度\n"
                "不要简单地说趋势是混合的，请提供详细和细致的分析和见解，以帮助交易者做出决策。"
                "请在报告末尾添加一个 Markdown 表格，以组织和总结报告中的要点，使其易于阅读。"
            )
            # A 股市场工具
            tools = [toolkit.get_xueqiu_stock_info]  # 使用雪球数据接口
        else:
            system_message = (
                "You are a social media and company specific news researcher/analyst tasked with analyzing social media posts, "
                "recent company news, and public sentiment for a specific company over the past week. You will be given a company's "
                "name your objective is to write a comprehensive long report detailing your analysis, insights, and implications "
                "for traders and investors on this company's current state after looking at social media and what people are saying "
                "about that company, analyzing sentiment data of what people feel each day about the company, and looking at recent "
                "company news. Try to look at all sources possible from social media to sentiment to news. Do not simply state the "
                "trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."
                "Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."
            )
            # 美股市场工具
            if toolkit.config["online_tools"]:
                tools = [toolkit.get_stock_news_openai]
            else:
                tools = [
                    toolkit.get_reddit_stock_info,
                    toolkit.get_finnhub_news
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
            "sentiment_report": result.content,
        }

    return social_media_analyst_node
