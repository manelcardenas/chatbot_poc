from langchain_core.runnables import Runnable, RunnableConfig
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
    validate_customer,
)


class SpendingAssistant(Assistant):
    """Spending/billing assistant class."""

    def __init__(self, llm: Runnable, name: str = "spending_assistant") -> None:
        tools = [fetch_spending_events, validate_customer, CompleteOrEscalate]
        runnable = spending_prompt | llm.bind_tools(tools)
        super().__init__(runnable=runnable, name=name, tools=tools)

    def __call__(self, state: State, config: RunnableConfig = None) -> dict:
        """Process the state and manage customer validation."""
        # Call the original method from the parent class
        result = super().__call__(state, config=config)

        # Update state if customer was validated in this interaction
        if "messages" in result and result["messages"].tool_calls:
            last_message = result["messages"]
            for tool_call in last_message.tool_calls:
                # Check for customer validation tool call
                if tool_call.get("name") == "validate_customer":
                    if "output" in tool_call and isinstance(tool_call["output"], dict):
                        output = tool_call["output"]
                        if output.get("valid") and output.get("customer_id"):
                            # Update state with validated customer_id
                            state["customer_id"] = output["customer_id"]

                # Handle fetch_spending_events tool call - inject customer_id if validation has been done
                if tool_call.get("name") == "fetch_spending_events" and state.get("customer_id"):
                    # If args doesn't contain customer_id, add it from state
                    if "args" in tool_call and isinstance(tool_call["args"], dict):
                        if "customer_id" not in tool_call["args"]:
                            tool_call["args"]["customer_id"] = state["customer_id"]

        return result


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
