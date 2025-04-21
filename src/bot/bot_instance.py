from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import END
from langgraph.prebuilt import tools_condition

from src.core.state import State
from src.tools import CompleteOrEscalate


class Assistant:
    """Base assistant class which will be inherited by other assistants."""

    def __init__(self, runnable: Runnable, name: str, tools: list) -> None:
        self.runnable = runnable
        self.name = name
        self.tools = tools

    def __call__(self, state: State, config: RunnableConfig) -> dict:
        while True:
            result = self.runnable.invoke(state)

            if not result.tool_calls and (
                not result.content or isinstance(result.content, list) and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}

    def route_non_primary_assistants(self, state: State) -> str:
        route = tools_condition(state)
        if route == END:
            return END
        tool_calls = state["messages"][-1].tool_calls
        did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
        if did_cancel:
            return "leave_skill"
        return f"{self.name}_tools"
