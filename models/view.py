from typing import List, Optional
from pydantic import BaseModel, Field


class View(BaseModel):
    name: str
    schema_name: Optional[str] = Field(None, alias="schema")
    definition: Optional[str] = None
    columns: List[str] = []
    is_materialized: bool = False
    owner: Optional[str] = None
    comment: Optional[str] = None
