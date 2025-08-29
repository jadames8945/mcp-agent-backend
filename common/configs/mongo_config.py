import logging
import os

from pymongo import MongoClient

logger = logging.getLogger(__name__)


class MongoConfig:
    def __init__(self):
        self.db_connection = None
        username = os.getenv("MONGO_INITDB_ROOT_USERNAME")
        password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

        if not username or not password:
            logger.error("MongoDB username or password not set in environment variables.")
            raise ValueError("MongoDB credentials are missing.")

        self.MONGO_URI = f"mongodb://{username}:{password}@mongo:27017/"

    def setup(self):
        try:
            client = MongoClient(
                self.MONGO_URI,
                maxPoolSize=10,
                minPoolSize=2,
                maxIdleTimeMS=30000,
                waitQueueTimeoutMS=5000,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
            )

            self.db_connection = client["mcp_navigator"]

            logger.info("MongoDB client connected successfully.")

            return None
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_database_connection(self):
        """Get the database connection."""
        if self.db_connection is None:
            raise RuntimeError("Database connection not initialized. Call setup() first.")

        return self.db_connection
