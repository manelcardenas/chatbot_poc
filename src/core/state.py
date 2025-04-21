from typing import Annotated, Literal, TypedDict

from langgraph.graph.message import AnyMessage, add_messages


def update_dialog_stack(left: list[str], right: str | None) -> list[str]:
    """Push or pop the state."""
    if right is None:
        # Does nothing
        return left
    if right == "pop":
        # Returns to the previous state
        return left[:-1]
    # Push the new state
    return left + [right]


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_info: str
    dialog_state: Annotated[
        list[Literal["primary", "spending", "recommendation"]],
        update_dialog_stack,
    ]
