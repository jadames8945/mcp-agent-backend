import os
from typing import Optional, Dict, List, Any
from datetime import datetime
from collections import deque
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import logging

logger = logging.getLogger(__name__)

class VectorStoreConfig:
    def __init__(
        self,
        backend: str = "chroma",
        persist_directory: Optional[str] = None,
        index_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.backend = backend
        self.persist_directory = persist_directory
        self.index_name = index_name
        self.metadata = metadata or {}
        self._vector_store = None
        self.session_memory: Dict[str, Any] = {}
        self._message_buffer: deque = deque(maxlen=10)

    def set_session_memory(self, key: str, value: Any):
        self.session_memory[key] = value

    def get_session_memory(self, key: str) -> Any:
        return self.session_memory.get(key)

    def get_vector_store(self):
        if self._vector_store is None:
            self._embeddings = OpenAIEmbeddings(request_timeout=10, max_retries=2)
            self._vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self._embeddings
            )
        return self._vector_store

    def add_message(
        self,
        content: str,
        role: str = "user",
        extra_metadata: Optional[Dict[str, Any]] = None,
        force_persist: bool = False
    ):
        meta = {**self.metadata, **(extra_metadata or {}), "role": role, "timestamp": datetime.utcnow().isoformat()}
        self._message_buffer.append({
            "content": content,
            "metadata": meta,
            "role": role
        })
        if force_persist or len(self._message_buffer) >= 5:
            self.flush_buffer()

    def flush_buffer(self):
        if not self._message_buffer:
            return
        vector_store = self.get_vector_store()
        contents = [msg["content"] for msg in self._message_buffer]
        metadatas = [msg["metadata"] for msg in self._message_buffer]
        try:
            vector_store.add_texts(contents, metadatas=metadatas)
            if hasattr(vector_store, "persist"):
                vector_store.persist()
            logger.info(f"Persisted {len(self._message_buffer)} messages to vector store (batched)")
            self._message_buffer.clear()
        except Exception as e:
            logger.error(f"Error persisting buffered messages: {e}")
            self._message_buffer.clear()

    def retrieve_similar(
        self,
        search_query: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        vector_store = self.get_vector_store()
        try:
            docs = vector_store.similarity_search(query=search_query, k=k)
            return [
                {"content": doc.page_content, "metadata": doc.metadata}
                for doc in docs
            ]
        except Exception as e:
            logger.error(f"Error retrieving similar documents: {e}")
            return []

    def get_last_n_messages(self, n: int = 10) -> List[Dict[str, str]]:
        buffer = list(self._message_buffer)[-n:]
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in buffer
        ] 