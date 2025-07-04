import time
import json
from ...dataflows.interface import get_market_type


def create_risk_manager(llm, memory):
    def risk_manager_node(state) -> dict:
        company_name = state["company_of_interest"]
        market_type = get_market_type()

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["news_report"]
        sentiment_report = state["sentiment_report"]
        trader_plan = state["investment_plan"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        if market_type == "CN":
            prompt = f"""作为风险管理评审和辩论主持人，你的目标是评估三位风险分析师（激进派、中立派和保守派）之间的辩论，并为交易员确定最佳行动方案。你的决策必须得出明确的建议：买入、卖出或持有。只有在有充分具体论据支持的情况下才选择持有，而不是在所有观点都似乎合理时的默认选择。力求清晰和果断。

决策指南：
1. **总结关键论点**：提取每位分析师最有力的观点，重点关注与当前情况的相关性。
2. **提供理由**：用辩论中的直接引用和反驳论点支持你的建议。
3. **完善交易员计划**：从交易员的原始计划出发，**{trader_plan}**，根据分析师的见解进行调整。
4. **吸取过往教训**：利用 **{past_memory_str}** 中的经验教训来纠正之前的判断失误，确保现在的决策不会做出导致亏损的错误买入/卖出/持有建议。

输出要求：
- 明确且可执行的建议：买入、卖出或持有
- 基于辩论和过往反思的详细推理过程

---

**分析师辩论历史：**  
{history}

---

专注于可执行的见解和持续改进。借鉴过往经验，批判性评估所有观点，确保每个决策都能带来更好的结果。"""
        else:
            prompt = f"""As the Risk Management Judge and Debate Facilitator, your goal is to evaluate the debate between three risk analysts—Risky, Neutral, and Safe/Conservative—and determine the best course of action for the trader. Your decision must result in a clear recommendation: Buy, Sell, or Hold. Choose Hold only if strongly justified by specific arguments, not as a fallback when all sides seem valid. Strive for clarity and decisiveness.

Guidelines for Decision-Making:
1. **Summarize Key Arguments**: Extract the strongest points from each analyst, focusing on relevance to the context.
2. **Provide Rationale**: Support your recommendation with direct quotes and counterarguments from the debate.
3. **Refine the Trader's Plan**: Start with the trader's original plan, **{trader_plan}**, and adjust it based on the analysts' insights.
4. **Learn from Past Mistakes**: Use lessons from **{past_memory_str}** to address prior misjudgments and improve the decision you are making now to make sure you don't make a wrong BUY/SELL/HOLD call that loses money.

Deliverables:
- A clear and actionable recommendation: Buy, Sell, or Hold.
- Detailed reasoning anchored in the debate and past reflections.

---

**Analysts Debate History:**  
{history}

---

Focus on actionable insights and continuous improvement. Build on past lessons, critically evaluate all perspectives, and ensure each decision advances better outcomes."""

        response = llm.invoke(prompt)

        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return risk_manager_node
