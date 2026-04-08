from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .column import Column
from .foreignkey import ForeignKey
from .index import Index
from .constraint import Constraint


class Table(BaseModel):
    table_name: str
    schema_name: Optional[str] = Field(None, alias="schema")
    owner: Optional[str] = None
    columns: List[Column] = []
    primary_keys: List[str] = []
    foreign_keys: List[ForeignKey] = []
    indexes: List[Index] = []
    constraints: List[Constraint] = []
    unique_constraints: List[Constraint] = []
    table_comment: Optional[str] = None
    row_count: Optional[int] = None
    estimated_rows: Optional[int] = None
    size_in_bytes: Optional[int] = None
    storage_engine: Optional[str] = None
    tablespace: Optional[str] = None
    partition_info: Optional[Dict[str, Any]] = None
    is_temporary: bool = False
    is_partitioned: bool = False
    is_view: bool = False
    is_materialized: bool = False
    created_at: Optional[str] = None
    last_altered: Optional[str] = None
    last_vacuum: Optional[str] = None
