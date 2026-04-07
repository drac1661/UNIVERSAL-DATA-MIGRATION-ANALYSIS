from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from .table import Table


class Schema(BaseModel):
    schema_name: str
    owner: Optional[str] = None
    default_tablespace: Optional[str] = None
    comment: Optional[str] = None
    tables: List[Table] = []
    views: List[Dict[str, Any]] = []
    functions: List[Dict[str, Any]] = []
    procedures: List[Dict[str, Any]] = []
    triggers: List[Dict[str, Any]] = []
    acl: List[Dict[str, Any]] = []
    size_in_bytes: Optional[int] = None
    created_at: Optional[str] = None
