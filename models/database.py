from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from .schema import Schema


class Database(BaseModel):
    dbname: str
    db_type: Optional[str] = None
    version: Optional[str] = None
    encoding: Optional[str] = None
    charset: Optional[str] = None
    collation: Optional[str] = None
    owner: Optional[str] = None
    owner_role: Optional[str] = None
    is_template: Optional[bool] = None
    host: Optional[str] = None
    port: Optional[int] = None
    default_tablespace: Optional[str] = None
    schemas: List[Schema] = []
    roles: List[str] = []
    extensions: List[str] = []
    size_in_bytes: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
