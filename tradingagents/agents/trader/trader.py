import functools
import time
import json


def create_trader(llm, memory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        market_type = state.get("market_type", "EN")  # Default to English market if not specified

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        if market_type == "CN":
            system_content = f"""您是一位专业的交易员，负责分析市场数据并做出投资决策。基于您的分析，请提供明确的买入、卖出或持有建议。在分析时请特别关注A股市场特征（如涨跌停限制、交易规则等）、中国特色的政策和监管环境、国内外宏观经济形势对A股的影响、技术面和基本面分析、市场情绪和交易者心理因素、行业政策和产业周期、相关概念板块联动性等。请从过往类似交易情况中吸取经验教训：{past_memory_str}请在回复的最后以"最终交易建议：**买入/持有/卖出**"的格式确认您的建议。"""

            context = {
                "role": "user",
                "content": f"基于分析师团队的综合分析，这里有一份针对{company_name}的投资计划。该计划整合了当前技术面趋势、宏观经济指标和社交媒体情绪等多方面信息。请以此为基础评估您的下一步交易决策。\n\n建议的投资计划：{investment_plan}\n\n请利用这些见解做出明智的战略决策。",
            }
        else:
            system_content = f"""You are a trading agent analyzing market data to make investment decisions. Based on your analysis, provide a specific recommendation to buy, sell, or hold. End with a firm decision and always conclude your response with 'FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**' to confirm your recommendation. Do not forget to utilize lessons from past decisions to learn from your mistakes. Here is some reflections from similar situatiosn you traded in and the lessons learned: {past_memory_str}"""

            context = {
                "role": "user",
                "content": f"Based on a comprehensive analysis by a team of analysts, here is an investment plan tailored for {company_name}. This plan incorporates insights from current technical market trends, macroeconomic indicators, and social media sentiment. Use this plan as a foundation for evaluating your next trading decision.\n\nProposed Investment Plan: {investment_plan}\n\nLeverage these insights to make an informed and strategic decision.",
            }

        messages = [
            {
                "role": "system",
                "content": system_content,
            },
            context,
        ]

        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
