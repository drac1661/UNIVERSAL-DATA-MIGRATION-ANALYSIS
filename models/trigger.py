from typing import List, Optional
from pydantic import BaseModel, Field


class Trigger(BaseModel):
    name: str
    schema_name: Optional[str] = Field(None, alias="schema")
    event_manipulation: List[str] = []  # INSERT, UPDATE, DELETE, TRUNCATE
    event_timing: Optional[str] = None  # BEFORE, AFTER, INSTEAD OF
    action_orientation: Optional[str] = None  # ROW, STATEMENT
    action_statement: Optional[str] = None
    action_condition: Optional[str] = None
    enabled: Optional[bool] = True
    when: Optional[str] = None
