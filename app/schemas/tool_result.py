from pydantic import BaseModel
from typing import Any, Dict

class ToolResult(BaseModel):
    tool_name: str
    input_data:  Dict[str, Any]
    output: str | Dict[str, Any]
    error: str | None = None