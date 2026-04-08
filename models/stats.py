from typing import Optional
from pydantic import BaseModel, Field


class TableStats(BaseModel):
    schema_name: Optional[str] = Field(None, alias="schema")
    table: Optional[str] = None
    rows: Optional[int] = None
    total_size_bytes: Optional[int] = None
    index_size_bytes: Optional[int] = None
    toast_size_bytes: Optional[int] = None
    seq_scan: Optional[int] = None
    idx_scan: Optional[int] = None
