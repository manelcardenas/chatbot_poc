import json
import logging
import os
import sys

from colorama import Fore, init
from langchain_core.messages import AIMessage, HumanMessage

from src.core.chatbot import ChatBot

if __name__ == "__main__":
    init(autoreset=True)

    # Check if the UI flag is present
    if "--ui" in sys.argv:
        logging.info("Starting Streamlit UI...")
        logging.info("If the browser doesn't open automatically, go to http://localhost:8501")
        # Use the simple streamlit command
        os.system("streamlit run src/cli/streamlit_app.py")
    else:
        # Terminal-based chat interface
        chatbot = ChatBot()
        chatbot.build_graph()

        logging.info("\n=== Welcome to the Electricity Chatbot ===\n")
        logging.info("You can ask about your electricity bills or get plan recommendations.")
        logging.info("For billing inquiries, you'll need to identify yourself with your customer ID or email.")
        logging.info("\nChatbot initialized. Type 'exit' to end the chat.")

        while True:
            user_input = input("User: ")
            if user_input.lower() == "exit":
                logging.info("Chatbot session ended.")
                break

            for s in chatbot.graph.stream(
                {"messages": [HumanMessage(content=user_input, name="user")]},
                config=chatbot.config,
            ):
                if "__end__" not in s:
                    logging.info("-" * 50)
                    logging.info(Fore.LIGHTMAGENTA_EX + f"Internal graph message: {s}")

            # Get the checkpoint data
            checkpoint = chatbot.checkpoint_saver.get(chatbot.config)
            timestamp = checkpoint["ts"].split(".")[0]
            timestamp = timestamp.replace(":", "-")  # windows does not allow colons in file names

            # Create a simple, human-readable checkpoint format
            readable_checkpoint = {"thread_id": chatbot.thread_id, "timestamp": timestamp, "conversation": []}

            # Get customer_id if available in state
            state = chatbot.graph.get_state(config=chatbot.config)
            if "customer_id" in state.values:
                readable_checkpoint["customer_id"] = state.values["customer_id"]

            # Extract just the messages in a clean format
            if "messages" in checkpoint["channel_values"]:
                messages = checkpoint["channel_values"]["messages"]
                for msg in messages:
                    # Check the type of message object and handle accordingly
                    if isinstance(msg, HumanMessage):
                        role = "user"
                        content = msg.content
                    elif isinstance(msg, AIMessage):
                        role = "assistant"
                        content = msg.content
                    elif isinstance(msg, dict):
                        # Fallback for dictionary-style messages
                        msg_type = msg.get("type", "")
                        role = "user" if msg_type == "HumanMessage" else "assistant"
                        content = msg.get("content", "")
                    else:
                        # Last resort fallback
                        role = "unknown"
                        content = str(msg)

                    readable_checkpoint["conversation"].append({"role": role, "content": content})

            # Save to file with nice formatting
            chatbot.checkpoint_file = os.path.join("checkpoints", f"{timestamp}.json")
            with open(chatbot.checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(readable_checkpoint, f, ensure_ascii=False, indent=2)

            try:
                bot_reply = chatbot.graph.get_state(config=chatbot.config).values["messages"][-1].content
                logging.info("\n")
                logging.info("-" * 50)
                logging.info(Fore.CYAN + f"Chatbot: {bot_reply}")
                logging.info("-" * 50)
                logging.info("\n")
            except Exception as e:
                logging.error(f"Error getting bot reply: {e}")
                logging.info("Continuing conversation...")
