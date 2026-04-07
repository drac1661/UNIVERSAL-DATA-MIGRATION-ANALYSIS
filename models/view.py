from typing import List, Optional
from pydantic import BaseModel


class View(BaseModel):
    name: str
    schema: Optional[str] = None
    definition: Optional[str] = None
    columns: List[str] = []
    is_materialized: bool = False
    owner: Optional[str] = None
    comment: Optional[str] = None
