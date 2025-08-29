"""Config repository for database operations."""

import logging
from typing import List, Optional

from bson import ObjectId

from app.infrastructure import infra
from app.models.mcp_config import MultiMCPConfig
from common.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ConfigRepository(BaseRepository[MultiMCPConfig]):
    """Repository for MultiMCPConfig database operations."""

    def __init__(self):
        self.db = infra.mongo_client.get_database_connection()

    def find_by_id(self, entity_id: str) -> Optional[MultiMCPConfig]:
        """Find config by ID."""
        try:
            db = self.db
            object_id = ObjectId(entity_id)
            result = db.multi_mcp_configs.find_one({"_id": object_id})

            if result:
                result["id"] = str(result["_id"])
                result.pop("_id", None)
                return MultiMCPConfig(**result)

            return None
        except Exception as e:
            logger.error(f"Error finding config by ID {entity_id}: {e}")
            return None

    def get_all(self, **filters) -> List[MultiMCPConfig]:
        """Get all configs with optional filters."""
        db = self.db
        query = {}
        if "user_id" in filters:
            query["user_id"] = filters["user_id"]

        docs = list(db.multi_mcp_configs.find(query))

        for doc in docs:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)

        return [MultiMCPConfig(**doc) for doc in docs]

    def delete(self, entity_id: str) -> bool:
        """Delete config by ID."""
        try:
            db = self.db
            object_id = ObjectId(entity_id)
            result = db.multi_mcp_configs.delete_one({"_id": object_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting config by ID {entity_id}: {e}")
            return False

    def update(self, entity_id: str, entity: MultiMCPConfig) -> Optional[MultiMCPConfig]:
        """Update config by ID."""
        try:
            db = self.db
            object_id = ObjectId(entity_id)
            update_data = entity.model_dump(exclude={"id"})
            result = db.multi_mcp_configs.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            return entity if result.modified_count > 0 else None
        except Exception as e:
            logger.error(f"Error updating config by ID {entity_id}: {e}")
            return None

    def create(self, entity: MultiMCPConfig) -> MultiMCPConfig:
        """Create new config."""
        db = self.db
        existing = db.multi_mcp_configs.find_one({
            "user_id": entity.user_id,
            "name": entity.name
        })

        if existing:
            raise ValueError(f"Config already exists for user {entity.user_id} with name {entity.name}")

        entity_data = entity.model_dump(exclude={"id"})
        result = db.multi_mcp_configs.insert_one(entity_data)
        entity.id = str(result.inserted_id)

        return entity

    def find_by_user_and_id(self, user_id: str, config_id: str) -> Optional[MultiMCPConfig]:
        """Find config by user ID and config ID."""
        try:
            db = self.db
            object_id = ObjectId(config_id)
            result = db.multi_mcp_configs.find_one({"user_id": user_id, "_id": object_id})

            if result:
                result["id"] = str(result["_id"])
                result.pop("_id", None)
                return MultiMCPConfig(**result)

            return None
        except Exception as e:
            logger.error(f"Error finding config by user {user_id} and ID {config_id}: {e}")
            return None 