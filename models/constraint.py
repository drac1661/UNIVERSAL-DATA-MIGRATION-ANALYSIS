from typing import List, Optional
from pydantic import BaseModel


class Constraint(BaseModel):
    name: Optional[str] = None
    constraint_type: Optional[str] = None  # PRIMARY KEY, UNIQUE, CHECK, FOREIGN KEY
    columns: List[str] = []
    definition: Optional[str] = None
    referenced_schema: Optional[str] = None
    referenced_table: Optional[str] = None
    referenced_columns: List[str] = []
    deferrable: Optional[bool] = None
    initially_deferred: Optional[bool] = None
    on_delete: Optional[str] = None
    on_update: Optional[str] = None
