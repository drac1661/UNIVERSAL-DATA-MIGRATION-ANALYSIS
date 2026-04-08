from typing import Optional
from pydantic import BaseModel, Field


class Sequence(BaseModel):
    name: str
    schema_name: Optional[str] = Field(None, alias="schema")
    start_value: Optional[int] = None
    increment: Optional[int] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    cache_size: Optional[int] = None
    cycle: Optional[bool] = None
    owned_by: Optional[str] = None
    last_value: Optional[int] = None
