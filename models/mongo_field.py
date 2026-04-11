from typing import Optional, List, Any, Dict, Union
from pydantic import BaseModel, field_validator


class MongoDBField(BaseModel):
    """Represents a field in a MongoDB collection."""
    name: str
    type: str  # e.g., "string", "int", "object", "array", "date", "bool", "null", "mixed"
    nullable: bool = True
    required: bool = False
    unique: bool = False
    indexed: bool = False
    is_primary: bool = False  # For _id field
    description: Optional[str] = None
    ordinal_position: Optional[Union[int, float]] = None
    
    # Nested/Array details
    is_array: bool = False
    is_nested: bool = False
    nested_fields: List['MongoDBField'] = []
    
    # Statistics
    unique_count: Optional[Union[int, float]] = None
    null_count: Optional[Union[int, float]] = None
    occurrence_count: Optional[Union[int, float]] = None
    stats: Optional[Dict[str, Any]] = None
    
    @field_validator('ordinal_position', 'unique_count', 'null_count', 'occurrence_count', mode='before')
    @classmethod
    def convert_numbers(cls, v):
        """Convert float to int for numeric fields."""
        if isinstance(v, float) and v.is_integer():
            return int(v)
        return v


MongoDBField.model_rebuild()


MongoDBField.model_rebuild()
