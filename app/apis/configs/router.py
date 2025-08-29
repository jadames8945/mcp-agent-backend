import logging
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.models.mcp_config import MultiMCPConfig
from app.services.config_service import ConfigService

router = APIRouter(
    prefix="/configs",
    tags=["configs"],
)

logger = logging.getLogger("configs")

def get_config_service():
    return ConfigService()

class ConfigCreateRequest(BaseModel):
    user_id: str
    name: str
    description: str
    connections: List[dict]

@router.get("/{user_id}", response_model=List[MultiMCPConfig])
async def get_configs(
    user_id: str,
    config_service: ConfigService = Depends(get_config_service)
):
    """Get all configs for a user."""
    try:
        configs = config_service.get_configs_by_user(user_id)
        return configs
    except Exception as e:
        logger.exception("Failed to fetch configs")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/{config_id}", response_model=MultiMCPConfig)
async def get_config(
    user_id: str,
    config_id: str,
    config_service: ConfigService = Depends(get_config_service)
):
    """Get a specific config by user ID and config ID."""
    try:
        config = config_service.get_config_by_user_and_id(user_id, config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Config not found")
        return config
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch config")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=MultiMCPConfig)
async def create_config(
    request: ConfigCreateRequest,
    config_service: ConfigService = Depends(get_config_service)
):
    """Create a new MCP configuration."""
    try:
        config = MultiMCPConfig(
            user_id=request.user_id,
            name=request.name,
            description=request.description,
            connections=request.connections
        )
        created_config = config_service.create_config(config)
        return created_config
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Failed to create config")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{config_id}", response_model=MultiMCPConfig)
async def update_config(
    config_id: str,
    request: ConfigCreateRequest,
    config_service: ConfigService = Depends(get_config_service)
):
    """Update an existing MCP configuration."""
    try:
        config = MultiMCPConfig(
            user_id=request.user_id,
            name=request.name,
            description=request.description,
            connections=request.connections
        )
        updated_config = config_service.update_config(config_id, config)
        if not updated_config:
            raise HTTPException(status_code=404, detail="Config not found")
        return updated_config
    except Exception as e:
        logger.exception("Failed to update config")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{config_id}")
async def delete_config(
    config_id: str,
    config_service: ConfigService = Depends(get_config_service)
):
    """Delete an MCP configuration."""
    try:
        success = config_service.delete_config(config_id)
        if not success:
            raise HTTPException(status_code=404, detail="Config not found")
        return {"message": "Config deleted successfully"}
    except Exception as e:
        logger.exception("Failed to delete config")
        raise HTTPException(status_code=500, detail=str(e)) 