from langchain_core.runnables import Runnable
from langgraph.graph import END
from langgraph.prebuilt import tools_condition

from src.bot.bot_instance import Assistant
from src.core.prompts import primary_prompt, recommendation_prompt, spending_prompt
from src.core.state import State
from src.tools import (
    CompleteOrEscalate,
    ToRecommendationAssistant,
    ToSpendingAssistant,
    fetch_plan_information,
    fetch_spending_events,
    list_supported_plans,
)


class SpendingAssistant(Assistant):
    """Spending/billing assistant class."""

    def __init__(self, llm: Runnable, name: str = "spending_assistant") -> None:
        tools = [fetch_spending_events, CompleteOrEscalate]
        runnable = spending_prompt | llm.bind_tools(tools)
        super().__init__(runnable=runnable, name=name, tools=tools)


class RecommendationAssistant(Assistant):
    """Plan recommendation assistant class."""

    def __init__(self, llm: Runnable, name: str = "recommendation_assistant") -> None:
        tools = [list_supported_plans, fetch_plan_information, CompleteOrEscalate]
        runnable = recommendation_prompt | llm.bind_tools(tools)
        super().__init__(runnable=runnable, name=name, tools=tools)


class PrimaryAssistant(Assistant):
    """Primary assistant class."""

    def __init__(self, llm: Runnable, name: str = "primary_assistant") -> None:
        tools = [ToSpendingAssistant, ToRecommendationAssistant]
        runnable = primary_prompt | llm.bind_tools(tools)
        super().__init__(runnable=runnable, name=name, tools=tools)

    def route_primary_assistant(self, state: State) -> str:
        route = tools_condition(state)
        if route == END:
            return END
        tool_calls = state["messages"][-1].tool_calls
        if tool_calls:
            if tool_calls[0]["name"] == ToSpendingAssistant.__name__:
                return "enter_spending"
            elif tool_calls[0]["name"] == ToRecommendationAssistant.__name__:
                return "enter_recommendation"
            return "primary_assistant_tools"
        raise ValueError("Invalid route")
