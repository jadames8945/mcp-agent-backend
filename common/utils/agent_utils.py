import os
from typing import Any, TypeVar, Optional, Generic, List

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class Utils(Generic[T]):
    VERBOSE = os.getenv("AGENT_VERBOSE", "false").lower() == "true"

    @staticmethod
    def is_null_or_empty(parsed_object: Optional[T]) -> T:
        if not parsed_object:
            raise ValueError("Parsed response is empty.")

        return parsed_object

    @staticmethod
    def parse_response(raw_response: dict[str, Any], parser: PydanticOutputParser) -> Optional[T]:
        try:
            if "output" in raw_response:
                return parser.parse(raw_response["output"])
            elif "result" in raw_response:
                return parser.parse(raw_response["result"])
            elif "response" in raw_response:
                return parser.parse(raw_response["response"])
            else:
                return parser.parse(str(raw_response))
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error parsing response: {e}")
            logger.debug(f"Raw response: {raw_response}")
            return None

    @classmethod
    def run_agent_query(
            cls,
            llm: ChatOpenAI,
            tools: List[Any],
            query: str,
            parser: PydanticOutputParser,
            prompt: ChatPromptTemplate,
            chat_history: str | List[dict],
            available_tools: str | None = None,
            allowed_tool_names: str | None = None,
            previous_result: str | None = None,
    ) -> Optional[T]:

        if not tools:
            formatted_prompt = prompt.format(
                query=query,
                chat_history=chat_history,
                available_tools=available_tools or "",
                previous_result=previous_result or "",
                format_instructions=parser.get_format_instructions()
            )
            
            response = llm.invoke(formatted_prompt)
            return cls.parse_response({"output": response.content}, parser)
        else:
            agent = create_tool_calling_agent(
                llm=llm,
                tools=tools,
                prompt=prompt
            )

            agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=cls.VERBOSE
            )

            agent_query = {"query": query}

            if chat_history:
                # Handle both string and list chat history formats
                if isinstance(chat_history, list):
                    agent_query["chat_history"] = chat_history
                else:
                    # Convert string format to list format for consistency
                    agent_query["chat_history"] = [{"role": "user", "content": chat_history}]

            if available_tools:
                agent_query["available_tools"] = available_tools

            if allowed_tool_names:
                agent_query["allowed_tool_names"] = allowed_tool_names

            if previous_result:
                agent_query["previous_result"] = previous_result

            if cls.VERBOSE:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Agent query input variables: {list(agent_query.keys())}")
                logger.info(f"Prompt template variables: {prompt.input_variables}")

            raw_response: dict[str, Any] = agent_executor.invoke(agent_query)

        return cls.parse_response(
            raw_response=raw_response,
            parser=parser
        )
