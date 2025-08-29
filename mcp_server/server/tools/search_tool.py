from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun


def search_tool() -> Tool:
    return Tool(
        name="search",
        func=DuckDuckGoSearchRun().run,
        description="Search the web for information related to best foods"
    )
