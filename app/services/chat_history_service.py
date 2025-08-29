import logging
from typing import List, Dict

from app.repository.chat_history_repository import ChatHistoryRepository

logger = logging.getLogger(__name__)


class ChatHistoryService:
    def __init__(self):
        self.repository = ChatHistoryRepository()

    def get_chat_history(self, session_id: str) -> List[Dict[str, str]]:
        logger.info(f"Getting chat history for session: {session_id}")
        
        try:
            # For now, return empty list
            # In a real implementation, you'd use conversation store
            logger.info(f"Retrieved 0 messages for session {session_id}")
            return []
        except Exception as e:
            logger.error(f"Failed to get chat history for session {session_id}: {e}")
            return []

    def generate_title_stream(self, chat_history: List[Dict[str, str]]):
        # For now, return a simple title
        return "Chat History"

    def save_to_mongodb(self, title: str, chat_history: List[Dict[str, str]]) -> bool:
        return self.repository.save_chat_history(title, chat_history)

    def get_chat_history_from_database(self, session_id: str, chat_title: str) -> List[Dict[str, str]]:
        logger.info(f"Loading chat history from database for session {session_id}, title: {chat_title}")
        chat_history_response = self.repository.get_chat_history_by_title(chat_title)
        if chat_history_response is None:
            logger.error(f"Chat history not found for title: {chat_title}")
            raise Exception("Chat history not found")

        chat_history = chat_history_response.chat_history
        logger.info(f"Found {len(chat_history)} messages in database for title: {chat_title}")

        return chat_history

    def get_all_chat_histories(self) -> List[Dict[str, any]]:
        return self.repository.get_all_chat_histories()

    def delete_chat_history(self, title: str, session_id: str = None) -> Dict[str, any]:
        return self.repository.delete_chat_history(title=title) 