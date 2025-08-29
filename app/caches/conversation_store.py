from typing import List, Dict, Any

from app.utils.chat_util import chat_history_to_str


class ConversationStore:
    def __init__(self):
        self.cache: Dict[str, List[Dict[str, Any]]] = {}

    def get_session(self, session_id: str) -> 'ConversationSession':
        """Get a session object for easier operations"""
        if session_id not in self.cache:
            self.cache[session_id] = []
        return ConversationSession(session_id, self.cache[session_id])

    def has_session(self, session_id: str) -> bool:
        """Check if session exists in cache"""
        return session_id in self.cache

    def remove_session(self, session_id: str):
        """Remove a session from cache"""
        if session_id in self.cache:
            del self.cache[session_id]

    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()


class ConversationSession:
    def __init__(self, session_id: str, messages: List[Dict[str, Any]]):
        self.session_id = session_id
        self.messages = messages

    def get_all_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in this session"""
        return self.messages

    def add_message(self, message: Dict[str, Any]):
        """Add a message to this session"""
        self.messages.append(message)

    def get_last_n_messages(self, n: int) -> List[Dict[str, Any]]:
        """Get the last n messages from this session"""
        return self.messages[-n:] if self.messages else []

    def get_last_message(self) -> Dict[str, Any]:
        """Get the last message in this session"""
        return self.messages[-1] if self.messages else {}

    def get_last_user_message(self) -> str:
        """Get the last user message content"""
        for message in reversed(self.messages):
            if message.get("role") == "user":
                return message.get("content", "")
        return ""

    def get_count(self) -> int:
        """Get the number of messages in this session"""
        return len(self.messages)

    def get_n_messages_as_string(self, n: int) -> str:
        return chat_history_to_str(self.get_last_n_messages(n))
