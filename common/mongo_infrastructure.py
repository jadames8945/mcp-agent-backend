import logging
from typing import Optional

from common.configs.mongo_config import MongoConfig

logger = logging.getLogger(__name__)


class MongoInfrastructure:
    def __init__(self):
        self._mongo_config: Optional['MongoConfig'] = None
        self._initialized: bool = False

    def setup(self):
        if self._initialized:
            return

        try:
            self.setup_mongo()
            self._initialized = True
            logger.info("Shared infrastructure (Redis) initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize shared infrastructure: {e}")
            raise

    def setup_mongo(self):
        if self._mongo_config is None:
            try:
                from common.configs.mongo_config import MongoConfig
                self._mongo_config = MongoConfig()
                self._mongo_config.setup()
                logger.info("MongoDB initialized")
            except Exception as e:
                logger.error(f"Failed to initialize MongoDB: {e}")
                raise
        return self._mongo_config

    @property
    def mongo_config(self):
        if self._mongo_config is None:
            self.setup_mongo()
        return self._mongo_config

    def is_initialized(self) -> bool:
        return self._initialized


infra = MongoInfrastructure()
