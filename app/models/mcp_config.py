
from typing import Literal, List, Optional, Dict, Any, Union

from pydantic import BaseModel


class StreamableHttpConfig(BaseModel):
    name: str
    description: Optional[str] = None
    connected: bool
    transport: Literal["streamable_http"]
    url: str


class SSEConfig(BaseModel):
    name: str
    description: Optional[str] = None
    connected: bool
    transport: Literal["sse"]
    url: str


class StdioConfig(BaseModel):
    name: str
    description: Optional[str] = None
    connected: bool
    transport: Literal["stdio"]
    command: str
    args: List[str]
    cwd: Optional[str] = None
    env: Optional[Dict[str, Any]] = None


class MultiMCPConfig(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    connections: List[Union[SSEConfig, StdioConfig, StreamableHttpConfig]]
