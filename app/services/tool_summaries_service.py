import asyncio
from typing import List, Dict, Set

from app.caches.tool_summaries_cache import ToolSummariesCache
from app.models.mcp_config import MultiMCPConfig
from app.schemas.tool_summaries import ToolSummary, ToolsSummaryByServer
from app.services.mcp_service import MCPService


class ToolSummariesService:
    def __init__(self):
        self.tool_summaries_cache = ToolSummariesCache()
        self._session_services: Dict[str, MCPService] = {}

    async def fetch_tool_summaries(
            self,
            session_id: str,
            mcp_config: MultiMCPConfig
    ) -> ToolsSummaryByServer:
        if self.tool_summaries_cache.has_session(session_id):
            cached_tools = self.tool_summaries_cache.get_tool_summaries(session_id)

            if self._is_cache_valid(cached_tools, mcp_config):
                return ToolsSummaryByServer(servers=cached_tools)

            self.tool_summaries_cache.remove_session(session_id)

        mcp_service: MCPService = await self._get_session_service(
            session_id=session_id,
            mcp_config=mcp_config
        )

        tool_summaries: Dict[str, List[ToolSummary]] = await mcp_service.get_tools_summary()

        self.tool_summaries_cache.set_tool_summaries(
            session_id=session_id,
            tool_summaries=tool_summaries
        )

        return ToolsSummaryByServer(servers=tool_summaries)

    async def fetch_missing_tool_summaries(
            self,
            session_id: str,
            mcp_config: MultiMCPConfig
    ) -> ToolsSummaryByServer:
        if not self.tool_summaries_cache.has_session(session_id):
            return await self.fetch_tool_summaries(session_id, mcp_config)

        cached_tools = self.tool_summaries_cache.get_tool_summaries(session_id)
        _, missing_servers = self._is_cache_valid(cached_tools, mcp_config)

        if not missing_servers:
            return ToolsSummaryByServer(servers=cached_tools)

        missing_config = MultiMCPConfig(
            connections=[
                conn for conn in mcp_config.connections
                if conn.name in missing_servers
            ]
        )

        mcp_service = await self._get_session_service(session_id, missing_config)
        missing_tools = await mcp_service.get_tools_summary()

        merged_tools = {**cached_tools, **missing_tools}
        self.tool_summaries_cache.set_tool_summaries(session_id, merged_tools)

        return ToolsSummaryByServer(servers=merged_tools)

    async def get_mcp_service(self, session_id: str) -> MCPService:
        if session_id not in self._session_services:
            raise RuntimeError(f"MCP service not connected for session {session_id}")

        service = self._session_services[session_id]
        if not service.is_connected():
            raise RuntimeError(f"MCP service disconnected for session {session_id}")

        return service

    async def _get_session_service(
            self,
            session_id: str,
            mcp_config: MultiMCPConfig
    ) -> MCPService:
        if session_id not in self._session_services:
            self._session_services[session_id] = MCPService()

        service = self._session_services[session_id]

        await service.connect(session_id, mcp_config.connections)

        return service

    def _is_cache_valid(
            self,
            cached_tools: Dict[str, List[ToolSummary]],
            mcp_config: MultiMCPConfig
    ) -> tuple[bool, Set[str]]:
        cached_servers = set(cached_tools.keys())
        config_servers = set(conn.name for conn in mcp_config.connections)
        missing = config_servers.difference(cached_servers)
        return len(missing) == 0, missing

    def cleanup_invalid_cache(self, mcp_config: MultiMCPConfig):
        for session_id in list(self.tool_summaries_cache.cache.keys()):
            cached_tools = self.tool_summaries_cache.get_tool_summaries(session_id)
            if not self._is_cache_valid(cached_tools, mcp_config)[0]:
                self.tool_summaries_cache.remove_session(session_id)

    def cleanup_session(self, session_id: str):
        if session_id in self._session_services:
            service = self._session_services[session_id]
            asyncio.create_task(service.disconnect())
            del self._session_services[session_id]