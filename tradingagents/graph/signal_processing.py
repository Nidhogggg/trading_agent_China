# TradingAgents/graph/signal_processing.py

from langchain_openai import ChatOpenAI
from ..dataflows.interface import get_market_type


class SignalProcessor:
    """Processes trading signals to extract actionable decisions."""

    def __init__(self, quick_thinking_llm: ChatOpenAI):
        """Initialize with an LLM for processing."""
        self.quick_thinking_llm = quick_thinking_llm

    def process_signal(self, full_signal: str) -> str:
        """
        Process a full trading signal to extract the core decision.

        Args:
            full_signal: Complete trading signal text

        Returns:
            Extracted decision (BUY, SELL, or HOLD)
        """
        market_type = get_market_type()
        
        if market_type == "CN":
            system_prompt = (
                "你是一个专门分析A股市场的AI助手，负责分析来自分析师团队的中文市场报告和分析结果。"
                "你的任务是从这些分析中提取出最终的投资决策建议。请只输出以下三种决策之一："
                "买入(BUY)、卖出(SELL)或持有(HOLD)。不要添加任何其他文字或解释。"
            )
        else:
            system_prompt = (
                "You are an efficient assistant designed to analyze paragraphs or financial "
                "reports provided by a group of analysts. Your task is to extract the investment "
                "decision: SELL, BUY, or HOLD. Provide only the extracted decision (SELL, BUY, "
                "or HOLD) as your output, without adding any additional text or information."
            )

        messages = [
            ("system", system_prompt),
            ("human", full_signal),
        ]

        return self.quick_thinking_llm.invoke(messages).content
