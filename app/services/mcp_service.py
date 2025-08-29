import asyncio
import logging
from typing import List, Dict, Optional, Any

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import StdioConnection, SSEConnection, MultiServerMCPClient
from langchain_mcp_adapters.sessions import StreamableHttpConnection

from app.models.mcp_config import SSEConfig, StdioConfig, StreamableHttpConfig
from app.schemas.tool_summaries import ToolSummary, Parameter

logger = logging.getLogger(__name__)


class MCPService:
    def __init__(self):
        self._client: Optional[MultiServerMCPClient] = None
        self._connections: Optional[List[SSEConfig | StdioConfig | StreamableHttpConfig]] = None
        self._parsed_connections: Optional[Dict[str, SSEConnection | StdioConnection | StreamableHttpConnection]] = None
        self.session_id: Optional[str] = None

    async def connect(
            self,
            session_id: str,
            connections: List[SSEConfig | StdioConfig | StreamableHttpConfig]
    ) -> 'MCPService':
        """Establish MCP connections and return self for chaining"""
        if self._client and self._connections == connections and self.session_id == session_id:
            return self

        try:
            self._connections = connections
            self._parsed_connections = self._parse_connections(connections)
            self._client = MultiServerMCPClient(self._parsed_connections)
            self.session_id = session_id
            logger.info("MultiServerMCPClient connected successfully")

            return self
        except Exception as e:
            logger.exception("Failed to initialize MultiServerMCPClient")
            raise

    async def get_tools_summary(self) -> Dict[str, List[ToolSummary]]:
        """Retrieve tool summaries from all configured MCP servers"""
        if not self._client:
            raise RuntimeError("Not connected: Call connect() first")

        async def fetch_tools(server_name) -> tuple[str, List[ToolSummary]]:
            try:
                tools = await self._client.get_tools(server_name=server_name)

                tool_summaries = [
                    ToolSummary(
                        tool_name=getattr(tool, "name", None),
                        parameters=[Parameter(
                            param_name=param,
                            type=tool.args_schema.get("properties", {}).get(param, {}).get("type", "unknown")
                        ) for param in tool.args_schema.get("required", [])],
                        description=getattr(tool, "description", None)
                    )
                    for tool in tools
                ]

                return server_name, tool_summaries
            except Exception as e:
                logger.error(f"Failed to get tool summary for {server_name}: {e}")
                return server_name, []

        try:
            fetch_tasks = [fetch_tools(server) for server in self._parsed_connections.keys()]
            results = await asyncio.gather(*fetch_tasks, return_exceptions=True)
            
            # Filter out failed results and only return successful ones
            successful_results = {}
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Task failed with exception: {result}")
                elif isinstance(result, tuple) and len(result) == 2:
                    server_name, tool_summaries = result
                    if tool_summaries:  # Only add servers with tools
                        successful_results[server_name] = tool_summaries
            
            return successful_results
        except Exception as e:
            logger.error(f"Failed to gather tool summaries: {e}")
            return {}

    async def invoke_tool(self, tool_name: str, input_data: dict) -> Dict[str, Any]:
        """Invoke a specific tool by name"""
        if not self._client:
            raise RuntimeError("Not connected to MCP server")

        tools: List[BaseTool] = await self._client.get_tools()

        tool: BaseTool | None = next((t for t in tools if t.name == tool_name), None)

        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")

        logger.info(f"Invoking tool '{tool_name}' with input data: {input_data}")
        return await tool.ainvoke(input_data)

    def _parse_connections(
            self,
            connections: List[SSEConfig | StdioConfig | StreamableHttpConfig]
    ) -> Dict[str, SSEConnection | StdioConnection | StreamableHttpConnection]:
        """Parse connection configs into connection objects"""
        parsed_connections: Dict[str, SSEConnection | StdioConnection | StreamableHttpConnection] = {}

        for config in connections:
            if isinstance(config, SSEConfig):
                parsed_connections[config.name] = SSEConnection(
                    url=config.url,
                    transport="sse"
                )
            elif isinstance(config, StdioConfig):
                parsed_connections[config.name] = StdioConnection(
                    command=config.command,
                    transport="stdio",
                    args=config.args,
                    cwd=config.cwd,
                    env=config.env,
                )
            elif isinstance(config, StreamableHttpConfig):
                parsed_connections[config.name] = StreamableHttpConnection(
                    url=config.url,
                    transport="streamable_http"
                )

        logger.info(f"Parsed connections: {list(parsed_connections.keys())}")
        return parsed_connections

    def is_connected(self) -> bool:
        """Check if service is connected"""
        return self._client is not None

    async def disconnect(self):
        """Clean up connections"""
        if self._client:
            # Add any cleanup logic here if needed
            self._client = None
            self._parsed_connections = None
            self._connections = None
            self.session_id = None
            logger.info("MCP connections cleaned up")
