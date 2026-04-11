from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from .mongo_field import MongoDBField
from .mongo_index import MongoDBIndex


class MongoDBCollection(BaseModel):
    """Represents a MongoDB collection."""
    collection_name: str
    database_name: Optional[str] = None
    owner: Optional[str] = None
    
    fields: List[MongoDBField] = []
    indexes: List[MongoDBIndex] = []
    
    # Collection info
    document_count: Optional[Union[int, float]] = None
    average_document_size: Optional[Union[int, float]] = None
    size_in_bytes: Optional[Union[int, float]] = None
    storage_size_in_bytes: Optional[Union[int, float]] = None
    
    # Validation rules
    validation_schema: Optional[Dict[str, Any]] = None
    validation_action: Optional[str] = None  # "error" or "warn"
    validation_level: Optional[str] = None  # "off", "strict", "moderate"
    
    # Collection options
    capped: bool = False
    capped_size: Optional[Union[int, float]] = None
    capped_max_documents: Optional[Union[int, float]] = None
    
    # Metadata
    collection_comment: Optional[str] = None
    created_at: Optional[str] = None
    last_modified: Optional[str] = None
    
    # Index info
    primary_key_field: str = "_id"
    
    # Statistics
    stats: Optional[Dict[str, Any]] = None
