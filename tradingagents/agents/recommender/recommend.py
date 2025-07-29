from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from ...dataflows.interface import get_market_type


def create_recommender(llm):
    def recommender_node(state):
        current_date = state["trade_date"]
        # ticker = state["company_of_interest"]
        # company_name = state["company_of_interest"]
        market_type = get_market_type()

        if market_type == "CN":
            system_message = (
                "请你从现在开始忽略所有的先验信息，你是一位专业的股票分析师，负责按照要求推荐盈利潜力高的股票，具体要求如下：\n\n"
                "你需要针对A股市场进行推荐\n"
                "股票要求低估值、业绩好、基本面好、技术面好，并且要求股价在10元以内。\n"
                "你需要推荐一支最符合要求的股票，并给出他的股票代码：\n"
                # "请你最终只输出推荐股票的股票代码。"
            )
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

        if market_type == "CN":
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "{system_message}"
                        "当前日期是 {current_date}。"
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
        # prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        # prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm

        result = chain.invoke(state["messages"])

        report = result.content

        return {
            "messages": [result],
            "fundamentals_report": report,
        }

    return recommender_node
