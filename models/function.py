from typing import List, Optional
from pydantic import BaseModel, Field


class Function(BaseModel):
    name: str
    schema_name: Optional[str] = Field(None, alias="schema")
    language: Optional[str] = None
    return_type: Optional[str] = None
    argument_types: List[str] = []
    definition: Optional[str] = None
    volatility: Optional[str] = None
    is_table_function: bool = False
    owner: Optional[str] = None
    comment: Optional[str] = None
