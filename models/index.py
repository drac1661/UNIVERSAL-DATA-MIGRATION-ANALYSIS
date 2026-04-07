from typing import List, Optional
from pydantic import BaseModel


class Index(BaseModel):
    name: str
    columns: List[str] = []
    unique: bool = False
    type: Optional[str] = None
    expression: Optional[str] = None
    method: Optional[str] = None
    predicate: Optional[str] = None
    tablespace: Optional[str] = None
    is_primary: bool = False
    size_in_bytes: Optional[int] = None
