import secrets

from langchain_community.chat_message_histories.file import FileChatMessageHistory

from law_rag.config import Settings

def generate_hex() -> str:
    """New token generation"""
    return secrets.token_hex(16)

def get_session_history_with_local_file(session_id) -> FileChatMessageHistory:
    fpath = Settings.web.path_to_history + f"{session_id}.txt"
    return FileChatMessageHistory(file_path = fpath, encoding = "utf-8", ensure_ascii = False)
