from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from .mongo_collection import MongoDBCollection


class MongoDBDatabase(BaseModel):
    """Represents a MongoDB database with its collections and metadata."""
    dbname: str
    db_type: str = "mongodb"
    version: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    
    # Collections
    collections: List[MongoDBCollection] = []
    
    # Database-level info
    size_in_bytes: Optional[Union[int, float]] = None
    collection_count: Optional[Union[int, float]] = None
    
    # Users and roles
    users: List[Dict[str, Any]] = []
    roles: List[Dict[str, Any]] = []
    
    # Database options
    authentication_enabled: Optional[bool] = None
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    last_scanned: Optional[str] = None
