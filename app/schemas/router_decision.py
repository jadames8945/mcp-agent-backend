from pydantic import BaseModel


class RouterDecision(BaseModel):
    use_tools: bool = False 