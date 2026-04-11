from typing import Optional, List, Dict, Any, Union, Tuple
from pydantic import BaseModel, field_validator


class MongoDBIndex(BaseModel):
    """Represents an index in a MongoDB collection."""
    name: str
    fields: List[Tuple[str, int]]  # List of (field_name, order) tuples, e.g., [("email", 1), ("created_at", -1)]
    unique: bool = False
    sparse: bool = False
    ttl: Optional[Union[int, float]] = None  # TTL in seconds for TTL indexes
    partial_filter: Optional[Dict[str, Any]] = None  # Partial index filter expression
    collation: Optional[Dict[str, Any]] = None
    hidden: bool = False
    description: Optional[str] = None
    key_pattern: Optional[Dict[str, int]] = None  # Raw MongoDB format: {"field": 1, "field2": -1}
    
    @field_validator('ttl', mode='before')
    @classmethod
    def convert_ttl(cls, v):
        """Convert float TTL to int."""
        if isinstance(v, float) and v.is_integer():
            return int(v)
        return v
