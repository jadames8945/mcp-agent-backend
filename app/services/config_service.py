from typing import List, Optional

from app.models.mcp_config import MultiMCPConfig
from app.repositories.config_repository import ConfigRepository


class ConfigService:
    """Service for managing MCP configurations."""

    def __init__(self):
        self.config_repository = ConfigRepository()

    def create_config(self, config: MultiMCPConfig) -> MultiMCPConfig:
        """Create a new configuration."""
        return self.config_repository.create(config)

    def get_config_by_user_and_id(self, user_id: str, config_id: str) -> Optional[MultiMCPConfig]:
        """Get a configuration by user ID and config ID."""
        return self.config_repository.find_by_user_and_id(user_id, config_id)

    def get_configs_by_user(self, user_id: str) -> List[MultiMCPConfig]:
        """Get all configurations for a user."""
        return self.config_repository.get_all(user_id=user_id)

    def update_config(self, config_id: str, config: MultiMCPConfig) -> Optional[MultiMCPConfig]:
        """Update a configuration."""
        return self.config_repository.update(config_id, config)

    def delete_config(self, config_id: str) -> bool:
        """Delete a configuration."""
        return self.config_repository.delete(config_id) 