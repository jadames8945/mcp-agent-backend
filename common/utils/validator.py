from typing import Union
from pydantic import BaseModel

def validate_query_not_empty(input_data: Union[str | BaseModel]) -> None:
    """Raise exception if input_date is empty"""

    if isinstance(input_data, BaseModel):
        input_data = str(input_data)

    if not input_data:
        raise Exception("Query is empty. Please enter a valid query.")