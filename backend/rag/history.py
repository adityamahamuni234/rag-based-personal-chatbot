from pathlib import Path
from langchain_community.chat_message_histories import FileChatMessageHistory

CHAT_FILE = Path("backend/db/chat_history.json")

CHAT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


def get_chat_history():

    return FileChatMessageHistory(
        str(CHAT_FILE)
    )