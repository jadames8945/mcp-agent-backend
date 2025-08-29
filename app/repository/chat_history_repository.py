import logging
from datetime import datetime
from typing import List, Dict

from app.infrastructure import infra

logger = logging.getLogger(__name__)


class ChatHistoryRepository:
    def __init__(self):
        self.db = infra.mongo_client.get_database_connection()
        self.collection = self.db.chat_histories

    def save_chat_history(self, title: str, chat_history: List[Dict[str, str]],
                          email: str = "john_123@company.com") -> bool:
        try:
            document = {
                "email": email,
                "title": title,
                "chat_history": chat_history,
                "created_at": datetime.utcnow()
            }

            result = self.collection.insert_one(document)
            logger.info(f"Saved chat history with ID: {result.inserted_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save chat history: {e}")
            return False

    def get_chat_history_by_title(self, title: str, email: str = "john_123@company.com"):
        try:
            result: Dict = self.collection.find_one({"email": email, "title": title})
            return result
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            return None

    def get_all_chat_histories(self, email: str = "john_123@company.com") -> List[Dict]:
        try:
            cursor = self.collection.find({"email": email}).sort("created_at", 1)
            chat_histories = []

            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                chat_histories.append(doc)

            return chat_histories
        except Exception as e:
            logger.error(f"Failed to get chat histories: {e}")
            return []

    def delete_chat_history(self, title: str, email: str = "john_123@company.com"):
        try:
            self.collection.delete_one({"email": email, "title": title})

            return {"status": "success"}
        except Exception as e:
            logger.error(f"Failed to delete chat history: {e}")
            return {"status": "error"} 