from collections.abc import Callable
from copy import deepcopy
from typing import Literal, TypedDict

from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import BaseCheckpointSaver


def pop_dialog_state(state: dict) -> dict:
    """
    Pop the dialog stack and return to the main assistant.
    This lets the full graph explicitly track the dialog flow and delegate control
    to specific sub-graphs.
    """
    messages = []
    if state["messages"][-1].tool_calls:
        # Note: Doesn't currently handle the edge case where the llm performs parallel tool calls
        messages.append(
            ToolMessage(
                content="Resuming dialog with the primary assistant. Please reflect on the past conversation and assist the user as needed.",
                tool_call_id=state["messages"][-1].tool_calls[0]["id"],
            )
        )
    return {
        "dialog_state": "pop",
        "messages": messages,
    }


def create_entry_node(assistant_name: str, new_dialog_state: str) -> Callable:
    """Utility function to create an entry node for the secondary assistants."""

    def entry_node(state: TypedDict) -> dict:
        tool_call_id = state["messages"][-1].tool_calls[0]["id"]
        return {
            "messages": [
                ToolMessage(
                    content=f"The assistant is now the {assistant_name}. Reflect on the above conversation between the primary assistant and the user."
                    f" The user's intent is unsatisfied. Use the provided tools to assist the user. Remember, you are {assistant_name},"
                    " and the identification, resolution, or any other action is not complete until after you have successfully invoked the appropriate tool."
                    " If the user changes their mind or needs help for other tasks, call the CompleteOrEscalate function to let the primary assistant take control."
                    " Do not mention who you are - just act as the proxy for the assistant.",
                    tool_call_id=tool_call_id,
                )
            ],
            "dialog_state": new_dialog_state,
        }

    return entry_node


def route_to_workflow(
    state: TypedDict,
) -> Literal["primary_assistant", "spending_assistant", "recommendation_assistant"]:
    """If we are in a delegated state, route directly to the appropriate assistant."""
    dialog_state = state.get("dialog_state")
    if not dialog_state:
        return "primary_assistant"
    return dialog_state[-1]


def ckpnt_to_dict(checkpoint: BaseCheckpointSaver) -> dict:
    """Converts a checkpoint to a JSON-compliant dictionary."""
    checkpoint_copy = deepcopy(checkpoint)

    # Extract messages and transform them
    checkpoint_copy["channel_values"]["messages"] = [
        {
            "type": type(m).__name__,
            "content": m.content,
            "name": m.name,
            "id": m.id,
        }
        for m in checkpoint["channel_values"]["messages"]
    ]

    return checkpoint_copy
