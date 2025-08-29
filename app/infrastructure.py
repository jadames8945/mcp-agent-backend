import logging
from typing import Optional

from pymongo import MongoClient

from app.caches.conversation_store import ConversationStore
from common.mongo_infrastructure import infra as mongo_infra
from common.redis_infrastructure import infra as redis_infra

logger = logging.getLogger(__name__)


class AppInfrastructure:
    def __init__(self):
        self._conversation_store: Optional['ConversationStore'] = None
        self._initialized: bool = False

    def setup(self):
        if self._initialized:
            return

        try:
            self.setup_conversation_store()
            self._initialized = True
            logger.info("App infrastructure initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize app infrastructure: {e}")
            raise

    def setup_conversation_store(self):
        if self._conversation_store is None:
            try:
                from app.caches.conversation_store import ConversationStore
                self._conversation_store = ConversationStore()
                logger.info("Vector store initialized")
            except Exception as e:
                logger.error(f"Failed to initialize vector store: {e}")
                raise
        return self._conversation_store

    @property
    def conversation_store(self):
        if self._conversation_store is None:
            self.setup_conversation_store()
        return self._conversation_store

    @property
    def redis_client(self):
        return redis_infra.redis_client

    @property
    def mongo_client(self) -> MongoClient:
        return mongo_infra.mongo_config

    def is_initialized(self) -> bool:
        return self._initialized


infra = AppInfrastructure()
