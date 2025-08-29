from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper


def wiki_tool(top_k: int = 1, char_limit: int = 100) -> WikipediaQueryRun:
    return WikipediaQueryRun(
        api_wrapper=WikipediaAPIWrapper(
            top_k_results=top_k,
            doc_content_chars_max=char_limit
        )
    )
