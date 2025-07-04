from langchain_core.messages import AIMessage
import time
import json
from ...dataflows.interface import get_market_type


def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")
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
            prompt = f"""你是一位多方分析师，负责提出支持投资该股票的论据。你的目标是构建一个基于证据的有力分析，强调增长潜力、竞争优势和积极的市场指标。利用提供的研究和数据来应对担忧，并有效反驳空方论点。

重点关注以下方面：

- 增长潜力：
  * 市场机会分析
  * 收入增长预期
  * 业务扩张空间
  * 新业务布局
  * 产业链延伸

- 竞争优势：
  * 产品技术优势
  * 品牌价值
  * 市场领先地位
  * 成本效益分析
  * 研发创新能力

- 积极指标：
  * 财务健康状况
  * 行业发展趋势
  * 利好消息影响
  * 技术面走强
  * 估值优势分析

- 反驳空方观点：
  * 数据支持论证
  * 澄清市场误解
  * 展示成长韧性
  * 风险应对措施
  * 长期价值论证

分析所需资料：

市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新全球新闻：{news_report}
公司基本面报告：{fundamentals_report}
辩论历史记录：{history}
最新空方论点：{current_response}
类似情况的经验总结：{past_memory_str}

请利用这些信息提出有说服力的多方论据，反驳空方的担忧，展开一场富有洞察力的辩论，展示多方立场的优势。同时，请注意吸取过往的经验教训，避免重复以前的分析失误。"""
        else:
            prompt = f"""You are a Bull Analyst advocating for investing in the stock. Your task is to build a strong, evidence-based case emphasizing growth potential, competitive advantages, and positive market indicators. Leverage the provided research and data to address concerns and counter bearish arguments effectively.

Key points to focus on:
- Growth Potential: Highlight the company's market opportunities, revenue projections, and scalability.
- Competitive Advantages: Emphasize factors like unique products, strong branding, or dominant market positioning.
- Positive Indicators: Use financial health, industry trends, and recent positive news as evidence.
- Bear Counterpoints: Critically analyze the bear argument with specific data and sound reasoning, addressing concerns thoroughly and showing why the bull perspective holds stronger merit.
- Engagement: Present your argument in a conversational style, engaging directly with the bear analyst's points and debating effectively rather than just listing data.

Resources available:
Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bear argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}
Use this information to deliver a compelling bull argument, refute the bear's concerns, and engage in a dynamic debate that demonstrates the strengths of the bull position. You must also address reflections and learn from lessons and mistakes you made in the past.
"""

        response = llm.invoke(prompt)

        if market_type == "CN":
            argument = f"多方分析师：{response.content}"
        else:
            argument = f"Bull Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
