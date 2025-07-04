import time
import json
from ...dataflows.interface import get_market_type


def create_research_manager(llm, memory):
    def research_manager_node(state) -> dict:
        history = state["investment_debate_state"].get("history", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        market_type = get_market_type()

        investment_debate_state = state["investment_debate_state"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        if market_type == "CN":
            prompt = f"""作为投资组合经理和辩论主持人，你的职责是对本轮辩论进行严格评估，并做出明确的决策：支持空方分析师、多方分析师，或者仅在有充分理由的情况下选择持有。

请简明扼要地总结双方的关键观点，重点关注最有说服力的证据或推理。你的建议（买入、卖出或持有）必须清晰明确且可执行。避免仅仅因为双方都有合理观点就默认选择持有；要基于辩论中最有力的论据做出明确的立场。

此外，请为交易员制定详细的投资计划，包括：

你的建议：基于最具说服力的论据做出的明确立场。
理由：解释为什么这些论据支持你的结论。
策略行动：实施建议的具体步骤。

请考虑你在类似情况下的过往错误。利用这些见解来改进你的决策，确保你在不断学习和进步。以自然对话的方式呈现你的分析，不需要特殊格式。

以下是你过去的错误反思：
\"{past_memory_str}\"

以下是辩论内容：
辩论历史：
{history}"""
        else:
            prompt = f"""As the portfolio manager and debate facilitator, your role is to critically evaluate this round of debate and make a definitive decision: align with the bear analyst, the bull analyst, or choose Hold only if it is strongly justified based on the arguments presented.

Summarize the key points from both sides concisely, focusing on the most compelling evidence or reasoning. Your recommendation—Buy, Sell, or Hold—must be clear and actionable. Avoid defaulting to Hold simply because both sides have valid points; commit to a stance grounded in the debate's strongest arguments.

Additionally, develop a detailed investment plan for the trader. This should include:

Your Recommendation: A decisive stance supported by the most convincing arguments.
Rationale: An explanation of why these arguments lead to your conclusion.
Strategic Actions: Concrete steps for implementing the recommendation.
Take into account your past mistakes on similar situations. Use these insights to refine your decision-making and ensure you are learning and improving. Present your analysis conversationally, as if speaking naturally, without special formatting. 

Here are your past reflections on mistakes:
\"{past_memory_str}\"

Here is the debate:
Debate History:
{history}"""

        response = llm.invoke(prompt)

        new_investment_debate_state = {
            "judge_decision": response.content,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": response.content,
            "count": investment_debate_state["count"],
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    return research_manager_node
