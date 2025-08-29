from pydantic import BaseModel

from app.models.mcp_config import MultiMCPConfig


class ToolSummaryRequest(BaseModel):
    session_id: str
    mcp_config: MultiMCPConfig
