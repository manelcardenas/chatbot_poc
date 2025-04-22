import logging
import os
import uuid

import dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.bot import PrimaryAssistant, RecommendationAssistant, SpendingAssistant
from src.core.error_manager import create_tool_node_with_fallback
from src.core.graph import create_entry_node, pop_dialog_state, route_to_workflow
from src.core.state import State
from src.models import ModelFactory, ModelName, ModelProvider

logger = logging.getLogger(__name__)

dotenv.load_dotenv()


class ChatBot:
    def __init__(self) -> None:
        self.llm = ModelFactory().get_model(ModelProvider.OPENAI, ModelName.GPT_4O_MINI)
        self.checkpoint_saver = MemorySaver()
        self.thread_id = self.create_thread_id()
        self.config = {"configurable": {"thread_id": self.thread_id}}

        if not os.path.exists("checkpoints"):
            os.makedirs("checkpoints")

    def create_thread_id(self) -> str:
        """Create a new thread ID for conversation persistence."""
        thread_id = str(uuid.uuid4())
        logger.info(f"Created new thread ID: {thread_id}")
        return thread_id

    def build_graph(self) -> None:
        # ---- Define the various assistants of the chatbot ----
        primary_assistant = PrimaryAssistant(self.llm)
        spending_assistant = SpendingAssistant(self.llm)
        recommendation_assistant = RecommendationAssistant(self.llm)

        # ---- Specify the state of the LangGraph graph. ----
        builder = StateGraph(State)

        # ---- Add the nodes and edges of the LangGraph graph. ----

        # =====================================================================
        # Primary assistant nodes and edges
        # =====================================================================

        # Add the primary assistant node.
        builder.add_node("primary_assistant", primary_assistant)

        # Tools are placed within tool nodes.
        builder.add_node(
            "primary_assistant_tools",
            create_tool_node_with_fallback(primary_assistant.tools),
        )

        # Add conditional edges to enable routing to either i) spending assistant, ii) recommendation assistant, iii) tool node (for tool calling), or iv) END node (directly respond to the user).
        builder.add_conditional_edges(
            "primary_assistant",
            primary_assistant.route_primary_assistant,  # function to determine routing logic
            [
                "enter_spending",
                "enter_recommendation",
                "primary_assistant_tools",
                END,
            ],
        )

        # Add an edge between the tool node and the primary assistant to enable the assistant access the messages of its tools.
        builder.add_edge("primary_assistant_tools", "primary_assistant")

        # =====================================================================
        # Spending assistant nodes and edges
        # =====================================================================

        # Add the 'enter' node (this sets the scope for second level assistants).
        builder.add_node(
            "enter_spending",
            create_entry_node("spending_assistant", "spending_assistant"),
        )
        # Add the spending assistant node.
        builder.add_node("spending_assistant", spending_assistant)
        # Connect the enter node to the spending assistant node.
        builder.add_edge("enter_spending", "spending_assistant")

        # Add node for the tools of the spending assistant.
        builder.add_node(
            "spending_assistant_tools",
            create_tool_node_with_fallback(spending_assistant.tools),
        )

        # Edge from tools to assistant.
        builder.add_edge("spending_assistant_tools", "spending_assistant")

        # The spending assistant can either i) call one of its tools, ii) trigger CompleteOrEscalate and delegate back to the primary assistant, or iii) respond directly to the user.
        builder.add_conditional_edges(
            "spending_assistant",
            spending_assistant.route_non_primary_assistants,
            [
                "spending_assistant_tools",
                "leave_skill",
                END,
            ],
        )

        # =====================================================================
        # Recommendation assistant nodes and edges
        # =====================================================================

        # Similar to spending assistant.
        builder.add_node(
            "enter_recommendation",
            create_entry_node("recommendation_assistant", "recommendation_assistant"),
        )
        builder.add_node("recommendation_assistant", recommendation_assistant)
        builder.add_edge("enter_recommendation", "recommendation_assistant")

        builder.add_node(
            "recommendation_assistant_tools",
            create_tool_node_with_fallback(recommendation_assistant.tools),
        )

        builder.add_edge("recommendation_assistant_tools", "recommendation_assistant")

        builder.add_conditional_edges(
            "recommendation_assistant",
            recommendation_assistant.route_non_primary_assistants,
            [
                "recommendation_assistant_tools",
                "leave_skill",
                END,
            ],
        )

        # ---- From secondary assistant to 'leave_skill' then to primary. ----
        # Update state since we leave a secondary assistant.
        builder.add_node("leave_skill", pop_dialog_state)
        builder.add_edge("leave_skill", "primary_assistant")

        # ---- Allow persistence in specialized assistants. ----
        builder.add_conditional_edges(
            START,
            route_to_workflow,
            ["primary_assistant", "spending_assistant", "recommendation_assistant"],
        )

        # ---- Compile the graph. ----

        self.graph = builder.compile(checkpointer=self.checkpoint_saver)
        # FIXME: This line was blocking the execution
        # self.graph.get_graph().draw_mermaid_png(output_file_path="chatbot_graph.png")
