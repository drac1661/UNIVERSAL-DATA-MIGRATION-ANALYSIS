from typing import Optional
from pydantic import BaseModel


class Column(BaseModel):
    name: str
    type: str
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    default: Optional[str] = None
    autoincrement: bool = False
    is_identity: bool = False
    identity_generation: Optional[str] = None
    generated: Optional[str] = None
    computed: bool = False
    generated_expression: Optional[str] = None
    comment: Optional[str] = None
    ordinal_position: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    length: Optional[int] = None
    character_set: Optional[str] = None
    collation: Optional[str] = None
    # Additional metadata
    stats: Optional[dict] = None
