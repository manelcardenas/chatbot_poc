import json
import os

from colorama import Fore, init
from langchain_core.messages import AIMessage, HumanMessage

from src.core.chatbot import ChatBot

# TODO: Add UI (Streamlit or Gradio)

if __name__ == "__main__":
    init(autoreset=True)

    chatbot = ChatBot()
    chatbot.build_graph()

    print("Chatbot initialized. Type 'exit' to end the chat.")

    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            print("Chatbot session ended.")
            break

        for s in chatbot.graph.stream(
            {"messages": [HumanMessage(content=user_input, name="user")]},
            config=chatbot.config,
        ):
            if "__end__" not in s:
                print("-" * 50)
                print(Fore.LIGHTMAGENTA_EX + f"Internal graph message: {s}")

        # Get the checkpoint data
        checkpoint = chatbot.checkpoint_saver.get(chatbot.config)
        timestamp = checkpoint["ts"].split(".")[0]
        timestamp = timestamp.replace(":", "-")  # windows does not allow colons in file names

        # Create a simple, human-readable checkpoint format
        readable_checkpoint = {"thread_id": chatbot.thread_id, "timestamp": timestamp, "conversation": []}

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
            print("\n")
            print("-" * 50)
            print(Fore.CYAN + f"Chatbot: {bot_reply}")
            print("-" * 50)
            print("\n")
        except Exception as e:
            print(f"Error getting bot reply: {e}")
            print("Continuing conversation...")
