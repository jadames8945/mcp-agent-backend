from pydantic import BaseModel
from typing import Dict, Any, List

class ToolInvocation(BaseModel):
    tool_name: str
    input_data: Dict[str, Any]
    rank: int

class ToolInvocations(BaseModel):
    tools: List[ToolInvocation]