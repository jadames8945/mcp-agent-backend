from typing import List, Dict, Any

from app.schemas.tool_result import ToolResult

MAX_HISTORY = 100


def convert_contexts_to_base_messages(retrieved_contexts, default_role="user"):
    return [{"role": default_role, "content": ctx} for ctx in retrieved_contexts]


def chat_history_to_str(chat_history):
    return "\n".join(f"{msg['role']}: {msg['content']}" for msg in chat_history)


def docs_to_chat_history(relevant_docs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    return [
        {"role": doc.get("metadata", {}).get("role", "user"), "content": doc.get("content", "")}
        for doc in relevant_docs
    ]


def format_final_summary_result(tool_results: List[ToolResult]) -> str:
    result_str = [
        (
            f"tool_name:{tool_result.tool_name} \n"
            f"input_data:{tool_result.input_data} \n"
            f"output:{tool_result.output} \n"
        )
        for tool_result in tool_results
    ]

    return ",".join(result_str)


def trim_vector_store(vector_store: List[Dict[str, str]]):
    if len(vector_store) > MAX_HISTORY:
        del vector_store[:-MAX_HISTORY]
