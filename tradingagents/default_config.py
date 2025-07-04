import os

# Get the project root directory (two levels up from this file)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DEFAULT_CONFIG = {
    "project_dir": PROJECT_ROOT,
    "report_dir": PROJECT_ROOT,
    "data_dir": os.path.join(PROJECT_ROOT, "FR1-data"),
    "data_cache_dir": os.path.join(PROJECT_ROOT, "tradingagents/dataflows/data_cache"),
    # Market settings
    "market_type": "CN",  # 'US' or 'CN'
    "market_hours": {
        "US": {
            "open": "09:30",
            "close": "16:00",
            "timezone": "America/New_York"
        },
        "CN": {
            "morning_open": "09:30",
            "morning_close": "11:30",
            "afternoon_open": "13:00",
            "afternoon_close": "15:00",
            "timezone": "Asia/Shanghai"
        }
    },
    # LLM settings
    # "deep_think_llm": "o4-mini",
    # "quick_think_llm": "gpt-4o-mini",
    "deep_think_llm": "deepseek-r1",
    "quick_think_llm": "deepseek-chat",
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": True,
}
