import time
import json


def create_neutral_debator(llm):
    def neutral_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")

        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_safe_response = risk_debate_state.get("current_safe_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        market_type = state.get("market_type", "EN")  # Default to English market if not specified

        trader_decision = state["trader_investment_plan"]

        if market_type == "CN":
            role_title = "中立风险分析师"
            prompt = f"""作为中立风险分析师,您的角色是提供一个平衡的视角,权衡交易者决策的潜在收益和风险。您优先考虑全面的分析方法,评估上行和下行空间,同时考虑更广泛的市场趋势、潜在的经济变化和投资组合多样化策略。

以下是交易者的决策:
{trader_decision}

您的任务是对激进和保守分析师的观点提出质疑,指出每种观点可能过于乐观或过于谨慎的地方。请使用以下数据源来支持一个温和且可持续的策略,以调整交易者的决策:

市场研究报告: {market_research_report}
社交媒体情绪报告: {sentiment_report}
最新全球事务报告: {news_report}
公司基本面报告: {fundamentals_report}

当前讨论历史: {history}
激进分析师最新回应: {current_risky_response}
保守分析师最新回应: {current_safe_response}

如果其他观点尚未有回应,请不要臆测,只需陈述您的观点。

请积极参与讨论,批判性地分析双方观点,指出激进和保守论点中的弱点,倡导更平衡的方法。质疑他们的每个观点,说明为什么适度的风险策略可能能够在提供增长潜力的同时防范极端波动。专注于辩论而不是简单地呈现数据,旨在表明平衡的观点可以带来最可靠的结果。

请以对话形式输出,就像您在发言一样,不需要任何特殊格式。在分析中要特别关注:
1. A股市场特征和交易规则
2. 中国特色的政策和监管环境
3. 国内外宏观经济形势对A股的影响
4. 结合技术面和基本面的综合分析
5. 市场情绪和交易者心理因素"""
        else:
            role_title = "Neutral Risk Analyst"
            prompt = f"""As the Neutral Risk Analyst, your role is to provide a balanced perspective, weighing both the potential benefits and risks of the trader's decision or plan. You prioritize a well-rounded approach, evaluating the upsides and downsides while factoring in broader market trends, potential economic shifts, and diversification strategies.

Here is the trader's decision:
{trader_decision}

Your task is to challenge both the Risky and Safe Analysts, pointing out where each perspective may be overly optimistic or overly cautious. Use insights from the following data sources to support a moderate, sustainable strategy to adjust the trader's decision:

Market Research Report: {market_research_report}
Social Media Sentiment Report: {sentiment_report}
Latest World Affairs Report: {news_report}
Company Fundamentals Report: {fundamentals_report}
Here is the current conversation history: {history} Here is the last response from the risky analyst: {current_risky_response} Here is the last response from the safe analyst: {current_safe_response}. If there are no responses from the other viewpoints, do not halluncinate and just present your point.

Engage actively by analyzing both sides critically, addressing weaknesses in the risky and conservative arguments to advocate for a more balanced approach. Challenge each of their points to illustrate why a moderate risk strategy might offer the best of both worlds, providing growth potential while safeguarding against extreme volatility. Focus on debating rather than simply presenting data, aiming to show that a balanced view can lead to the most reliable outcomes. Output conversationally as if you are speaking without any special formatting."""

        response = llm.invoke(prompt)

        if market_type == "CN":
            argument = f"中立风险分析师：{response.content}"
        else:
            argument = f"Neutral Risk Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": neutral_history + "\n" + argument,
            "latest_speaker": "Neutral",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": argument,
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return neutral_node
