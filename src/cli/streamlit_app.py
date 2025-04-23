import json
import os
import sys
from datetime import datetime

# Simple fix to import from parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from src.core.chatbot import ChatBot

# Set page configuration
st.set_page_config(
    page_title="Electricity Chatbot",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom CSS for better UI
st.markdown(
    """
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #e6f2ff;
        border-left: 5px solid #1e88e5;
    }
    .chat-message.bot {
        background-color: #f5f5f5;
        border-left: 5px solid #43a047;
    }
    .chat-message .message-content {
        display: flex;
        margin-top: 0.5rem;
    }
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .chat-message .message {
        flex-grow: 1;
        color: #333333;
        font-weight: 500;
    }
    div.stButton > button {
        width: 100%;
    }
</style>
""",
    unsafe_allow_html=True,
)


def initialize_session_state() -> None:
    """Initialize session state variables if they don't exist"""
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = ChatBot()
        st.session_state.chatbot.build_graph()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []


def display_message(message: str, is_user: bool = False) -> None:
    """Display a single message in the chat UI"""
    if is_user:
        avatar = "👤"
        message_type = "user"
    else:
        avatar = "⚡"
        message_type = "bot"

    with st.container():
        st.markdown(
            f"""
        <div class="chat-message {message_type}">
            <div class="message-content">
                <div class="avatar">{avatar}</div>
                <div class="message">{message}</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def display_conversation_history() -> None:
    """Display the entire conversation history"""
    for message in st.session_state.messages:
        display_message(message["content"], message["role"] == "user")


def process_user_input() -> None:
    """Process the user input and get the chatbot response"""
    user_input = st.session_state.user_input

    if user_input:
        # Add the user message to the conversation
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get chatbot response
        try:
            # Process internal graph stream (we don't display this to the user)
            for s in st.session_state.chatbot.graph.stream(
                {"messages": [HumanMessage(content=user_input, name="user")]},
                config=st.session_state.chatbot.config,
            ):
                if "__end__" not in s:
                    # We could log this for debugging but we don't display it
                    pass

            # Get checkpoint data for saving
            checkpoint = st.session_state.chatbot.checkpoint_saver.get(st.session_state.chatbot.config)
            timestamp = checkpoint["ts"].split(".")[0]
            timestamp = timestamp.replace(":", "-")  # windows does not allow colons in file names

            # Create readable checkpoint format
            readable_checkpoint = {
                "thread_id": st.session_state.chatbot.thread_id,
                "timestamp": timestamp,
                "conversation": [],
            }

            # Get customer_id if available in state
            state = st.session_state.chatbot.graph.get_state(config=st.session_state.chatbot.config)
            if "customer_id" in state.values:
                readable_checkpoint["customer_id"] = state.values["customer_id"]

            # Extract messages in a clean format
            if "messages" in checkpoint["channel_values"]:
                messages = checkpoint["channel_values"]["messages"]
                for msg in messages:
                    if isinstance(msg, HumanMessage):
                        role = "user"
                        content = msg.content
                    elif isinstance(msg, AIMessage):
                        role = "assistant"
                        content = msg.content
                    elif isinstance(msg, dict):
                        msg_type = msg.get("type", "")
                        role = "user" if msg_type == "HumanMessage" else "assistant"
                        content = msg.get("content", "")
                    else:
                        role = "unknown"
                        content = str(msg)

                    readable_checkpoint["conversation"].append({"role": role, "content": content})

            # Save checkpoint to file
            if not os.path.exists("checkpoints"):
                os.makedirs("checkpoints")

            st.session_state.chatbot.checkpoint_file = os.path.join("checkpoints", f"{timestamp}.json")
            with open(st.session_state.chatbot.checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(readable_checkpoint, f, ensure_ascii=False, indent=2)

            # Get the bot's reply
            bot_reply = (
                st.session_state.chatbot.graph.get_state(config=st.session_state.chatbot.config)
                .values["messages"][-1]
                .content
            )

            # Add the bot's reply to the conversation
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        except Exception as e:
            error_message = f"Error getting bot reply: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})

        # Clear the input box
        st.session_state.user_input = ""


def restart_conversation() -> None:
    """Restart the conversation with a new thread ID"""
    st.session_state.chatbot = ChatBot()
    st.session_state.chatbot.build_graph()
    st.session_state.messages = []
    st.session_state.conversation_history = []
    st.rerun()


def download_conversation() -> str | None:
    """Export the current conversation as a JSON file"""
    if len(st.session_state.messages) > 0:
        conversation_data = {
            "thread_id": st.session_state.chatbot.thread_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            "messages": st.session_state.messages,
        }

        json_str = json.dumps(conversation_data, indent=2)

        # Return the JSON as a downloadable file
        return json_str
    return None


def main() -> None:
    # Initialize the session state
    initialize_session_state()

    # Header section
    st.title("⚡ Electricity Chatbot")
    st.markdown("""
    Ask about your electricity bills or get plan recommendations.
    For billing inquiries, you'll need to identify yourself with your customer ID or email.
    """)

    # Sidebar with conversation controls
    with st.sidebar:
        st.subheader("Conversation Controls")

        if st.button("Start New Conversation"):
            restart_conversation()

        # Export conversation button
        if len(st.session_state.messages) > 0:
            conversation_json = download_conversation()
            if conversation_json:
                st.download_button(
                    label="Download Conversation",
                    data=conversation_json,
                    file_name=f"electricity_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                )

        # Display thread ID for reference
        st.divider()
        st.caption(f"Thread ID: {st.session_state.chatbot.thread_id}")

    # Chat interface
    chat_container = st.container()

    # Display chat messages
    with chat_container:
        display_conversation_history()

    # User input section
    st.text_input(
        "Your message:",
        key="user_input",
        on_change=process_user_input,
        placeholder="Type your question here...",
    )


if __name__ == "__main__":
    main()
