"""MongoDB data extraction utilities."""

import logging
from typing import List, Dict, Any, Iterator, Optional
import json
from pymongo import MongoClient
from pymongo.database import Database
from bson import ObjectId
from datetime import datetime

logger = logging.getLogger(__name__)


class MongoDBDataExtractor:
    """Extract data from MongoDB collections."""
    
    def __init__(self, mongo_client: MongoClient, database: Database):
        """Initialize the data extractor.
        
        Args:
            mongo_client: PyMongo MongoClient instance
            database: PyMongo Database instance
        """
        self.client = mongo_client
        self.database = database
        logger.info(f"MongoDBDataExtractor initialized for database: {database.name}")
    
    @staticmethod
    def _serialize_bson(obj: Any) -> Any:
        """Convert BSON types to JSON-serializable types.
        
        Args:
            obj: Object to serialize
            
        Returns:
            JSON-serializable version of the object
        """
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: MongoDBDataExtractor._serialize_bson(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [MongoDBDataExtractor._serialize_bson(item) for item in obj]
        elif isinstance(obj, bytes):
            return obj.decode('utf-8', errors='replace')
        else:
            return obj
    
    def get_collection_data(
        self, 
        collection_name: str, 
        query: Optional[Dict[str, Any]] = None, 
        projection: Optional[Dict[str, int]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = 0,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """Get documents from a collection.
        
        Args:
            collection_name: Name of the collection
            query: MongoDB query filter
            projection: MongoDB projection
            limit: Maximum number of documents to return
            skip: Number of documents to skip
            sort: List of (field, direction) tuples for sorting
            
        Returns:
            List of documents
        """
        try:
            collection = self.database[collection_name]
            cursor = collection.find(query or {}, projection or {})
            
            if sort:
                cursor = cursor.sort(sort)
            
            if skip:
                cursor = cursor.skip(skip)
            
            if limit:
                cursor = cursor.limit(limit)
            
            documents = list(cursor)
            
            # Serialize BSON types
            serialized = [self._serialize_bson(doc) for doc in documents]
            
            logger.debug(f"Retrieved {len(serialized)} documents from collection '{collection_name}'")
            return serialized
        except Exception as e:
            logger.error(f"Failed to get data from '{collection_name}': {e}", exc_info=True)
            return []
    
    def export_collection_to_json(
        self,
        collection_name: str,
        output_file: str,
        query: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> int:
        """Export a collection to a JSON file.
        
        Args:
            collection_name: Name of the collection
            output_file: Path to output JSON file
            query: Optional MongoDB query filter
            limit: Optional limit on number of documents
            
        Returns:
            Number of documents exported
        """
        try:
            documents = self.get_collection_data(
                collection_name, 
                query=query, 
                limit=limit
            )
            
            with open(output_file, 'w') as f:
                json.dump(documents, f, indent=2, default=str)
            
            logger.info(f"Exported {len(documents)} documents from '{collection_name}' to {output_file}")
            return len(documents)
        except Exception as e:
            logger.error(f"Failed to export collection '{collection_name}' to JSON: {e}", exc_info=True)
            return 0
    
    def stream_collection_data(
        self,
        collection_name: str,
        query: Optional[Dict[str, Any]] = None,
        batch_size: int = 1000,
        projection: Optional[Dict[str, int]] = None,
    ) -> Iterator[List[Dict[str, Any]]]:
        """Stream documents from a collection in batches.
        
        Useful for large collections to avoid loading all documents in memory.
        
        Args:
            collection_name: Name of the collection
            query: MongoDB query filter
            batch_size: Number of documents per batch
            projection: MongoDB projection
            
        Yields:
            Batches of documents
        """
        try:
            collection = self.database[collection_name]
            cursor = collection.find(query or {}, projection or {}).batch_size(batch_size)
            
            batch = []
            for doc in cursor:
                batch.append(self._serialize_bson(doc))
                
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
            
            # Yield remaining documents
            if batch:
                yield batch
            
            logger.debug(f"Streamed data from collection '{collection_name}'")
        except Exception as e:
            logger.error(f"Failed to stream data from '{collection_name}': {e}", exc_info=True)
    
    def get_collection_distinct_values(
        self,
        collection_name: str,
        field_name: str,
        query: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Any]:
        """Get distinct values for a field in a collection.
        
        Args:
            collection_name: Name of the collection
            field_name: Field to get distinct values for
            query: Optional MongoDB query filter
            limit: Optional limit on results
            
        Returns:
            List of distinct values
        """
        try:
            collection = self.database[collection_name]
            distinct_values = collection.distinct(field_name, query or {})
            
            if limit:
                distinct_values = distinct_values[:limit]
            
            # Serialize BSON types
            serialized = [self._serialize_bson(v) for v in distinct_values]
            
            logger.debug(f"Found {len(serialized)} distinct values for field '{field_name}' in '{collection_name}'")
            return serialized
        except Exception as e:
            logger.error(f"Failed to get distinct values: {e}", exc_info=True)
            return []
    
    def get_collection_field_statistics(
        self,
        collection_name: str,
        field_name: str,
    ) -> Dict[str, Any]:
        """Get statistics about a field in a collection.
        
        Args:
            collection_name: Name of the collection
            field_name: Field to analyze
            
        Returns:
            Dictionary with field statistics
        """
        try:
            collection = self.database[collection_name]
            
            # Count documents with the field
            total_count = collection.count_documents({})
            field_count = collection.count_documents({field_name: {"$exists": True}})
            null_count = collection.count_documents({field_name: None})
            
            stats = {
                "field_name": field_name,
                "total_documents": total_count,
                "documents_with_field": field_count,
                "null_count": null_count,
                "presence_percentage": (field_count / total_count * 100) if total_count > 0 else 0,
            }
            
            # Try to get distinct value count
            try:
                distinct_count = len(collection.distinct(field_name, {field_name: {"$exists": True}}))
                stats["distinct_values"] = distinct_count
            except Exception:
                pass
            
            logger.debug(f"Retrieved statistics for field '{field_name}' in '{collection_name}'")
            return stats
        except Exception as e:
            logger.error(f"Failed to get field statistics: {e}", exc_info=True)
            return {}


__all__ = ["MongoDBDataExtractor"]
