import json
import os

from colorama import Fore, init
from langchain_core.messages import HumanMessage

from src.core.chatbot import ChatBot
from src.core.graph import ckpnt_to_dict

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

        checkpoint = chatbot.checkpoint_saver.get(chatbot.config)
        id = checkpoint["ts"].split(".")[0]
        id = id.replace(":", "-")  # windows does not allow colons in file names
        chatbot.checkpoint_file = os.path.join("checkpoints", f"{id}.json")
        checkpoint_dict = ckpnt_to_dict(checkpoint)
        checkpoint_data = json.dumps(checkpoint_dict, ensure_ascii=False)

        with open(chatbot.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint_dict, f, ensure_ascii=False)

        bot_reply = chatbot.graph.get_state(config=chatbot.config).values["messages"][-1].content
        print("\n")
        print("-" * 50)
        print(Fore.CYAN + f"Chatbot: {bot_reply}")
        print("-" * 50)
        print("\n")
