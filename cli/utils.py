import questionary
from typing import List, Optional, Tuple, Dict

from cli.models import AnalystType

ANALYST_ORDER = [
    ("市场分析师", AnalystType.MARKET),
    ("社交媒体分析师", AnalystType.SOCIAL),
    ("新闻分析师", AnalystType.NEWS),
    ("基本面分析师", AnalystType.FUNDAMENTALS),
]


def get_ticker() -> str:
    """Prompt the user to enter a ticker symbol."""
    ticker = questionary.text(
        "请输入要分析的股票代码：",
        validate=lambda x: len(x.strip()) > 0 or "请输入有效的股票代码。",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not ticker:
        console.print("\n[red]未提供股票代码，程序退出...[/red]")
        exit(1)

    return ticker.strip().upper()


def get_analysis_date() -> str:
    """Prompt the user to enter a date in YYYY-MM-DD format."""
    import re
    from datetime import datetime

    def validate_date(date_str: str) -> bool:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    date = questionary.text(
        "请输入分析日期（YYYY-MM-DD格式）：",
        validate=lambda x: validate_date(x.strip())
        or "请输入有效的日期，格式为YYYY-MM-DD。",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not date:
        console.print("\n[red]未提供日期，程序退出...[/red]")
        exit(1)

    return date.strip()


def select_analysts() -> List[AnalystType]:
    """Select analysts using an interactive checkbox."""
    choices = questionary.checkbox(
        "选择您的[分析师团队]：",
        choices=[
            questionary.Choice(display, value=value) for display, value in ANALYST_ORDER
        ],
        instruction="\n- 按空格键选择/取消选择分析师\n- 按'a'键全选/取消全选\n- 选择完成后按回车键",
        validate=lambda x: len(x) > 0 or "您必须至少选择一位分析师。",
        style=questionary.Style(
            [
                ("checkbox-selected", "fg:green"),
                ("selected", "fg:green noinherit"),
                ("highlighted", "noinherit"),
                ("pointer", "noinherit"),
            ]
        ),
    ).ask()

    if not choices:
        console.print("\n[red]未选择任何分析师，程序退出...[/red]")
        exit(1)

    return choices


def select_research_depth() -> int:
    """Select research depth using an interactive selection."""

    # Define research depth options with their corresponding values
    DEPTH_OPTIONS = [
        ("浅层 - 快速研究，较少的辩论和策略讨论轮次", 1),
        ("中等 - 适中的研究深度，适量的辩论和策略讨论", 3),
        ("深入 - 全面研究，深入的辩论和策略讨论", 5),
    ]

    choice = questionary.select(
        "选择您的[研究深度]：",
        choices=[
            questionary.Choice(display, value=value) for display, value in DEPTH_OPTIONS
        ],
        instruction="\n- 使用方向键选择\n- 按回车键确认",
        style=questionary.Style(
            [
                ("selected", "fg:yellow noinherit"),
                ("highlighted", "fg:yellow noinherit"),
                ("pointer", "fg:yellow noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]未选择研究深度，程序退出...[/red]")
        exit(1)

    return choice


def select_shallow_thinking_agent() -> str:
    """Select shallow thinking llm engine using an interactive selection."""

    # Define shallow thinking llm engine options with their corresponding model names
    SHALLOW_AGENT_OPTIONS = [
        ("DeepSeek-V3 - 专业推理模型（紧凑版）", "deepseek-chat"),
        ("DeepSeek-R1 - 完整版高级推理模型", "deepseek-reasoner"),
        ("GPT-4o-mini - 快速高效，适合简单任务", "gpt-4o-mini"),
        ("GPT-4.1-nano - 超轻量级模型，适合基础操作", "gpt-4.1-nano"),
        ("GPT-4.1-mini - 紧凑型模型，性能优良", "gpt-4.1-mini"),
        ("GPT-4o - 标准模型，能力全面", "gpt-4o"),
    ]

    choice = questionary.select(
        "选择您的[快速思维AI引擎]：",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in SHALLOW_AGENT_OPTIONS
        ],
        instruction="\n- 使用方向键选择\n- 按回车键确认",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print(
            "\n[red]未选择快速思维AI引擎，程序退出...[/red]"
        )
        exit(1)

    return choice


def select_deep_thinking_agent() -> str:
    """Select deep thinking llm engine using an interactive selection."""

    # Define deep thinking llm engine options with their corresponding model names
    DEEP_AGENT_OPTIONS = [
        ("DeepSeek-V3 - 专业推理模型（紧凑版）", "deepseek-chat"),
        ("DeepSeek-R1 - 完整版高级推理模型", "deepseek-reasoner"),
        ("GPT-4.1-nano - 超轻量级模型，适合基础操作", "gpt-4.1-nano"),
        ("GPT-4.1-mini - 紧凑型模型，性能优良", "gpt-4.1-mini"),
        ("GPT-4o - 标准模型，能力全面", "gpt-4o"),
        ("o4-mini - 专业推理模型（紧凑版）", "o4-mini"),
        ("o3-mini - 高级推理模型（轻量版）", "o3-mini"),
        ("o3 - 完整版高级推理模型", "o3"),
        ("o1 - 顶级推理和问题解决模型", "o1"),
    ]

    choice = questionary.select(
        "选择您的[深度思维AI引擎]：",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in DEEP_AGENT_OPTIONS
        ],
        instruction="\n- 使用方向键选择\n- 按回车键确认",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]未选择深度思维AI引擎，程序退出...[/red]")
        exit(1)

    return choice
