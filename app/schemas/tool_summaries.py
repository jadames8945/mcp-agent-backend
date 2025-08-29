from typing import List, Optional, Dict

from pydantic import BaseModel


class Parameter(BaseModel):
    param_name: str
    type: str


class ToolSummary(BaseModel):
    tool_name: Optional[str]
    parameters: List[Parameter]
    description: Optional[str]


class ServerToolsSummary(BaseModel):
    server_name: str
    tools: List[ToolSummary]


class ToolsSummaryByServer(BaseModel):
    servers: Dict[str, List[ToolSummary]]  # server_name -> list of tools