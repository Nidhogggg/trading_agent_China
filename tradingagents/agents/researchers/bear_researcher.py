from langchain_core.messages import AIMessage
import time
import json
from ...dataflows.interface import get_market_type


def create_bear_researcher(llm, memory):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")
        market_type = get_market_type()

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        if market_type == "CN":
            prompt = f"""你是一位空方分析师，负责提出反对投资该股票的论据。你的目标是提出一个论据充分的分析，强调风险、挑战和负面指标。利用提供的研究和数据来突出潜在的下行风险，并有效反驳多方论点。

重点关注以下方面：

- 风险与挑战：
  * 市场饱和度分析
  * 财务稳定性隐患
  * 宏观经济威胁
  * 行业周期风险
  * 政策监管风险

- 竞争劣势：
  * 市场地位弱化
  * 创新能力下降
  * 竞争对手威胁
  * 产品竞争力减弱
  * 成本结构劣势

- 负面指标：
  * 财务数据恶化
  * 市场趋势走弱
  * 不利新闻影响
  * 技术面转弱
  * 估值过高风险

- 反驳多方观点：
  * 用具体数据分析
  * 揭示过度乐观假设
  * 指出逻辑漏洞
  * 提供反面证据
  * 质疑增长预期

分析所需资料：

市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新全球新闻：{news_report}
公司基本面报告：{fundamentals_report}
辩论历史记录：{history}
最新多方论点：{current_response}
类似情况的经验总结：{past_memory_str}

请利用这些信息提出有说服力的空方论据，反驳多方的观点，展开一场富有洞察力的辩论，展示投资该股票的风险和弱点。同时，请注意吸取过往的经验教训，避免重复以前的分析失误。"""
        else:
            prompt = f"""You are a Bear Analyst making the case against investing in the stock. Your goal is to present a well-reasoned argument emphasizing risks, challenges, and negative indicators. Leverage the provided research and data to highlight potential downsides and counter bullish arguments effectively.

Key points to focus on:

- Risks and Challenges: Highlight factors like market saturation, financial instability, or macroeconomic threats that could hinder the stock's performance.
- Competitive Weaknesses: Emphasize vulnerabilities such as weaker market positioning, declining innovation, or threats from competitors.
- Negative Indicators: Use evidence from financial data, market trends, or recent adverse news to support your position.
- Bull Counterpoints: Critically analyze the bull argument with specific data and sound reasoning, exposing weaknesses or over-optimistic assumptions.
- Engagement: Present your argument in a conversational style, directly engaging with the bull analyst's points and debating effectively rather than simply listing facts.

Resources available:

Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bull argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}
Use this information to deliver a compelling bear argument, refute the bull's claims, and engage in a dynamic debate that demonstrates the risks and weaknesses of investing in the stock. You must also address reflections and learn from lessons and mistakes you made in the past.
"""

        response = llm.invoke(prompt)

        if market_type == "CN":
            argument = f"空方分析师：{response.content}"
        else:
            argument = f"Bear Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node
