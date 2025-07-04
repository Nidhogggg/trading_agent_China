from langchain_core.messages import AIMessage
import time
import json
from ...dataflows.interface import get_market_type


def create_safe_debator(llm):
    def safe_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        safe_history = risk_debate_state.get("safe_history", "")
        market_type = get_market_type()

        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        if market_type == "CN":
            prompt = f"""作为保守型风险分析师，你的首要目标是保护资产、降低波动性并确保稳定可靠的增长。你优先考虑稳定性、安全性和风险控制，仔细评估潜在损失、经济下行和市场波动。在评估交易员的决策或计划时，重点审查高风险要素，指出决策可能使公司承担过度风险的地方，以及更谨慎的替代方案如何能确保长期收益。

重点关注以下方面：

- 风险防控：
  * 系统性风险评估
  * 流动性风险管理
  * 信用风险控制
  * 操作风险防范
  * 合规风险把控

- 稳健策略：
  * 资产配置优化
  * 止损策略设计
  * 对冲工具运用
  * 分散投资布局
  * 现金流管理

- 下行保护：
  * 极端情况分析
  * 压力测试评估
  * 风险预警机制
  * 应急预案准备
  * 止损位设置

- 反驳激进观点：
  * 揭示风险盲点
  * 强调长期稳定
  * 质疑乐观预期
  * 突出保本重要
  * 论证谨慎价值

交易员的决策：
{trader_decision}

你的任务是积极反驳激进派和中立派分析师的论点，指出他们的观点可能忽视了潜在威胁或未能优先考虑可持续性。直接回应他们的观点，利用以下数据源为交易员决策的低风险调整方案构建有说服力的论据：

参考资料：
市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新全球新闻：{news_report}
公司基本面报告：{fundamentals_report}

当前辩论历史：{history}
激进派分析师最新论点：{current_risky_response}
中立派分析师最新论点：{current_neutral_response}

如果其他观点尚未发表意见，请不要臆测，只需陈述你的观点。通过质疑他们的乐观态度并强调他们可能忽视的潜在下行风险来参与辩论。针对他们的每个论点进行回应，展示为什么保守立场最终是保护公司资产的最安全路径。专注于辩论和批评他们的论点，以证明低风险策略相对于他们的方法的优势。请以对话的方式输出，就像在自然交谈一样，不需要特殊格式。"""
        else:
            prompt = f"""As the Safe/Conservative Risk Analyst, your primary objective is to protect assets, minimize volatility, and ensure steady, reliable growth. You prioritize stability, security, and risk mitigation, carefully assessing potential losses, economic downturns, and market volatility. When evaluating the trader's decision or plan, critically examine high-risk elements, pointing out where the decision may expose the firm to undue risk and where more cautious alternatives could secure long-term gains. Here is the trader's decision:

{trader_decision}

Your task is to actively counter the arguments of the Risky and Neutral Analysts, highlighting where their views may overlook potential threats or fail to prioritize sustainability. Respond directly to their points, drawing from the following data sources to build a convincing case for a low-risk approach adjustment to the trader's decision:

Market Research Report: {market_research_report}
Social Media Sentiment Report: {sentiment_report}
Latest World Affairs Report: {news_report}
Company Fundamentals Report: {fundamentals_report}
Here is the current conversation history: {history} Here is the last response from the risky analyst: {current_risky_response} Here is the last response from the neutral analyst: {current_neutral_response}. If there are no responses from the other viewpoints, do not halluncinate and just present your point.

Engage by questioning their optimism and emphasizing the potential downsides they may have overlooked. Address each of their counterpoints to showcase why a conservative stance is ultimately the safest path for the firm's assets. Focus on debating and critiquing their arguments to demonstrate the strength of a low-risk strategy over their approaches. Output conversationally as if you are speaking without any special formatting."""

        response = llm.invoke(prompt)

        if market_type == "CN":
            argument = f"保守派分析师：{response.content}"
        else:
            argument = f"Safe Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": safe_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Safe",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": argument,
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return safe_node
