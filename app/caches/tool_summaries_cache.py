from typing import List, Dict

from app.models.mcp_config import MultiMCPConfig
from app.schemas.tool_summaries import ToolSummary


class ToolSummariesCache:
    def __init__(self):
        self.cache: Dict[str, Dict[str, List[ToolSummary]]] = {}

    def get_tool_summaries(self, session_id: str) -> Dict[str, List[ToolSummary]]:
        """Get tool summaries for a specific session, grouped by server"""
        return self.cache.get(session_id, {})

    def set_tool_summaries(self, session_id: str, tool_summaries: Dict[str, List[ToolSummary]]):
        """Set tool summaries for a specific session, grouped by server"""
        self.cache[session_id] = tool_summaries

    def has_session(self, session_id: str) -> bool:
        """Check if session exists in cache"""
        return session_id in self.cache

    def remove_session(self, session_id: str):
        """Remove a session from cache"""
        if session_id in self.cache:
            del self.cache[session_id]

    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()

    def get_tools_for_server(self, session_id: str, server_name: str) -> List[ToolSummary]:
        """Get tools for a specific server in a session"""
        session_data = self.cache.get(session_id, {})

        return session_data.get(server_name, [])

    def get_all_tools_flat(self, session_id: str) -> List[ToolSummary]:
        """Get all tools as a flat list (for backward compatibility if needed)"""
        session_data = self.cache.get(session_id, {})
        flat_tools = []

        for server_tools in session_data.values():
            flat_tools.extend(server_tools)

        return flat_tools