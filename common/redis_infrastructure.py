import logging
from typing import Optional

from redis import Redis as RedisSync

logger = logging.getLogger(__name__)


class RedisInfrastructure:
    def __init__(self):
        self._redis_client: Optional[RedisSync] = None
        self._initialized: bool = False

    def setup(self):
        if self._initialized:
            return

        try:
            self.setup_redis()
            self._initialized = True
            logger.info("Shared infrastructure (Redis) initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize shared infrastructure: {e}")
            raise

    def setup_redis(self) -> RedisSync:
        if self._redis_client is None:
            try:
                from common.services.redis_service import get_sync_redis_client
                self._redis_client = get_sync_redis_client()
                logger.info("Redis client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Redis: {e}")
                raise
        return self._redis_client

    @property
    def redis_client(self) -> RedisSync:
        if self._redis_client is None:
            self.setup_redis()
        return self._redis_client

    def is_initialized(self) -> bool:
        return self._initialized


infra = RedisInfrastructure()