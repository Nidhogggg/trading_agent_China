import time
import json
from ...dataflows.interface import get_market_type


def create_risky_debator(llm):
    def risky_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        risky_history = risk_debate_state.get("risky_history", "")
        market_type = get_market_type()

        current_safe_response = risk_debate_state.get("current_safe_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        if market_type == "CN":
            prompt = f"""作为激进型风险分析师，你的角色是积极倡导高回报、高风险的机会，强调大胆的策略和竞争优势。在评估交易员的决策或计划时，重点关注潜在的上行空间、增长潜力和创新收益——即使这些伴随着较高的风险。利用提供的市场数据和情绪分析来强化你的论点，挑战对立观点。

重点关注以下方面：

- 高回报机会：
  * 市场转折点机会
  * 行业变革红利
  * 技术创新突破
  * 产业升级机遇
  * 政策红利释放

- 竞争优势分析：
  * 先发优势
  * 规模效应
  * 技术壁垒
  * 渠道优势
  * 品牌溢价

- 风险收益比：
  * 上行空间评估
  * 杠杆效应分析
  * 时机把握
  * 市场预期差
  * 风险对冲策略

- 反驳保守观点：
  * 挑战过度保守
  * 揭示机会成本
  * 展示增长动能
  * 证明风险可控
  * 强调市场效率

交易员的决策：
{trader_decision}

你的任务是通过质疑和批评保守和中立的立场，为交易员的决策构建有说服力的论据，展示为什么你的高回报视角提供了最佳的前进路径。

参考资料：
市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新全球新闻：{news_report}
公司基本面报告：{fundamentals_report}

当前辩论历史：{history}
保守派分析师最新论点：{current_safe_response}
中立派分析师最新论点：{current_neutral_response}

如果其他观点尚未发表意见，请不要臆测，只需陈述你的观点。积极参与辩论，通过解决任何具体担忧，反驳他们逻辑中的弱点，并主张承担风险以超越市场常态的好处。保持辩论和说服的重点，而不是简单地呈现数据。挑战每个反驳点，强调为什么高风险方法是最优的。请以对话的方式输出，就像在自然交谈一样，不需要特殊格式。"""
        else:
            prompt = f"""As the Risky Risk Analyst, your role is to actively champion high-reward, high-risk opportunities, emphasizing bold strategies and competitive advantages. When evaluating the trader's decision or plan, focus intently on the potential upside, growth potential, and innovative benefits—even when these come with elevated risk. Use the provided market data and sentiment analysis to strengthen your arguments and challenge the opposing views. Specifically, respond directly to each point made by the conservative and neutral analysts, countering with data-driven rebuttals and persuasive reasoning. Highlight where their caution might miss critical opportunities or where their assumptions may be overly conservative. Here is the trader's decision:

{trader_decision}

Your task is to create a compelling case for the trader's decision by questioning and critiquing the conservative and neutral stances to demonstrate why your high-reward perspective offers the best path forward. Incorporate insights from the following sources into your arguments:

Market Research Report: {market_research_report}
Social Media Sentiment Report: {sentiment_report}
Latest World Affairs Report: {news_report}
Company Fundamentals Report: {fundamentals_report}
Here is the current conversation history: {history} Here are the last arguments from the conservative analyst: {current_safe_response} Here are the last arguments from the neutral analyst: {current_neutral_response}. If there are no responses from the other viewpoints, do not halluncinate and just present your point.

Engage actively by addressing any specific concerns raised, refuting the weaknesses in their logic, and asserting the benefits of risk-taking to outpace market norms. Maintain a focus on debating and persuading, not just presenting data. Challenge each counterpoint to underscore why a high-risk approach is optimal. Output conversationally as if you are speaking without any special formatting."""

        response = llm.invoke(prompt)

        if market_type == "CN":
            argument = f"激进派分析师：{response.content}"
        else:
            argument = f"Risky Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risky_history + "\n" + argument,
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Risky",
            "current_risky_response": argument,
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return risky_node
