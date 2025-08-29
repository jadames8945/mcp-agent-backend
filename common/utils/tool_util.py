from typing import List, Dict, Any

from app.schemas.tool_summaries import ToolSummary, ToolsSummaryByServer
from app.schemas.tool_result import ToolResult


def format_tool(tool: ToolSummary) -> str:
    params = ', '.join(f"{p.param_name}: {p.type}" for p in tool.parameters)
    return (
        f"server_name: {tool.server_name}\n"
        f"tool_name: {tool.tool_name}\n"
        f"description: {tool.description}\n"
        f"parameters: {params}"
    )


def format_tool_by_server_name(tools: ToolsSummaryByServer) -> str:
    formated_tools = []
    for server_name, tool_list in tools.servers.items():
        for tool_summary in tool_list:
            params = ', '.join(f"{p.param_name}: {p.type}" for p in tool_summary.parameters)
            tool_text = (
                f"server_name: {server_name}\n"
                f"tool_name: {tool_summary.tool_name}\n"
                f"description: {tool_summary.description}\n"
                f"parameters: {params}\n"
            )
            formated_tools.append(tool_text)

    return '\n'.join(formated_tools)

def format_tools_text(tools: List[ToolSummary]) -> str:
    """Return a formatted string of all tool descriptions for prompt context."""
    return "\n".join(format_tool(tool) for tool in tools) if tools else "None"


def format_allowed_tool_names(tools: List[ToolSummary], *, sep: str = ", ") -> str:
    """Return a separator-joined string of tool names for prompt constraints."""
    return sep.join(tool.tool_name for tool in tools) if tools else ""


def format_final_summary_result(tool_results: List[ToolResult]) -> Dict[str, Any]:
    """Format tool results into a final summary."""
    lines = []
    for tool_result in tool_results:
        output = tool_result.output
        if not isinstance(output, dict):
            answer = str(output)
        else:
            answer = output.get("result_answer") or output.get("result") or str(output)
        lines.append(f"Tool '{tool_result.tool_name}' executed: {answer}")
    
    return {
        "result_answer": "\n".join(lines),
        "success": True,
        "error_message": None
    }
