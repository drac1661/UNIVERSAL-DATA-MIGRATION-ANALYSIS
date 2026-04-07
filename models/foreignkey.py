from typing import List, Optional
from pydantic import BaseModel


class ForeignKey(BaseModel):
    name: Optional[str] = None
    columns: List[str] = []
    referenced_schema: Optional[str] = None
    referenced_table: Optional[str] = None
    referenced_columns: List[str] = []
    on_delete: Optional[str] = None
    on_update: Optional[str] = None
    deferrable: Optional[bool] = None
    initially_deferred: Optional[bool] = None
    match_option: Optional[str] = None
