"""MongoDB schema and data extractor."""

import logging
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.database import Database
from migrator.connectors.mongodb import connect_mongodb, MongoDBConfig, get_database

logger = logging.getLogger(__name__)


class MongoDBExtractor:
    """Extract schema and metadata information from MongoDB."""
    
    def __init__(self, config_file: str = "db_config.json"):
        """Initialize the MongoDB extractor.
        
        Args:
            config_file: Name of the database config file
        """
        logger.info(f"Initializing MongoDBExtractor with config: {config_file}")
        try:
            from migrator import load_db_config
            self.config = load_db_config(config_file)
            self.db_type = self.config.get("db_type", "mongodb").lower()
            logger.debug(f"Database type: {self.db_type}")
            
            # Create connection
            self.client = self._create_connection()
            self.database = self.get_database()
            logger.info("MongoDBExtractor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDBExtractor: {e}", exc_info=True)
            raise
    
    def _create_connection(self) -> MongoClient:
        """Create MongoDB connection from config."""
        try:
            mongodb_config = MongoDBConfig(
                host=self.config.get("host", "127.0.0.1"),
                port=self.config.get("port", 27017),
                dbname=self.config.get("dbname", "test"),
                user=self.config.get("user"),
                password=self.config.get("password"),
                auth_source=self.config.get("auth_source", "admin"),
                ssl=self.config.get("ssl", False),
                replica_set=self.config.get("replica_set"),
            )
            client = connect_mongodb(mongodb_config)
            logger.info(f"Connected to MongoDB at {mongodb_config.host}:{mongodb_config.port}")
            return client
        except Exception as e:
            logger.error(f"Failed to create MongoDB connection: {e}", exc_info=True)
            raise
    
    def get_database(self) -> Database:
        """Get the target MongoDB database."""
        dbname = self.config.get("dbname", "test")
        return get_database(self.client, dbname)
    
    def get_all_collections(self) -> List[str]:
        """Get all collection names in the database.
        
        Returns:
            List of collection names
        """
        try:
            collections = self.database.list_collection_names()
            logger.debug(f"Found {len(collections)} collections")
            return collections
        except Exception as e:
            logger.error(f"Failed to get collection names: {e}", exc_info=True)
            return []
    
    def get_collection_document_count(self, collection_name: str) -> int:
        """Get the number of documents in a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Number of documents
        """
        try:
            collection = self.database[collection_name]
            count = collection.count_documents({})
            logger.debug(f"Collection '{collection_name}' has {count} documents")
            return count
        except Exception as e:
            logger.error(f"Failed to count documents in '{collection_name}': {e}", exc_info=True)
            return 0
    
    def get_collection_indexes(self, collection_name: str) -> List[Dict[str, Any]]:
        """Get all indexes for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            List of index information dictionaries
        """
        try:
            collection = self.database[collection_name]
            indexes = list(collection.list_indexes())
            logger.debug(f"Collection '{collection_name}' has {len(indexes)} indexes")
            return indexes
        except Exception as e:
            logger.error(f"Failed to get indexes for '{collection_name}': {e}", exc_info=True)
            return []
    
    def get_collection_validation_schema(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get the validation schema for a collection if it exists.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Validation schema dict or None
        """
        try:
            collection_info = self.database.command("listCollections", filter={"name": collection_name})
            if collection_info.get("cursor", {}).get("firstBatch"):
                col_data = collection_info["cursor"]["firstBatch"][0]
                return col_data.get("options", {}).get("validator")
            return None
        except Exception as e:
            logger.error(f"Failed to get validation schema for '{collection_name}': {e}", exc_info=True)
            return None
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self.database[collection_name]
            stats = self.database.command("collStats", collection_name)
            logger.debug(f"Retrieved stats for collection '{collection_name}'")
            return stats
        except Exception as e:
            logger.error(f"Failed to get stats for '{collection_name}': {e}", exc_info=True)
            return {}
    
    def sample_documents(self, collection_name: str, sample_size: int = 100) -> List[Dict[str, Any]]:
        """Sample documents from a collection to analyze schema.
        
        Args:
            collection_name: Name of the collection
            sample_size: Number of documents to sample
            
        Returns:
            List of sample documents
        """
        try:
            collection = self.database[collection_name]
            
            # Try to use aggregation pipeline for sampling (efficient)
            try:
                pipeline = [{"$sample": {"size": min(sample_size, 1000)}}]
                samples = list(collection.aggregate(pipeline))
                logger.debug(f"Sampled {len(samples)} documents from '{collection_name}' using aggregation")
                return samples
            except Exception:
                # Fallback to limit if sampling not available
                samples = list(collection.find().limit(sample_size))
                logger.debug(f"Sampled {len(samples)} documents from '{collection_name}' using limit")
                return samples
        except Exception as e:
            logger.error(f"Failed to sample documents from '{collection_name}': {e}", exc_info=True)
            return []
    
    def infer_collection_schema(self, collection_name: str, sample_size: int = 100) -> Dict[str, Any]:
        """Infer the schema of a collection by sampling documents.
        
        Args:
            collection_name: Name of the collection
            sample_size: Number of documents to sample for inference
            
        Returns:
            Dictionary describing the inferred schema
        """
        try:
            samples = self.sample_documents(collection_name, sample_size)
            
            if not samples:
                logger.warning(f"No documents found in collection '{collection_name}'")
                return {}
            
            # Analyze fields across all samples
            field_types = {}
            field_occurrences = {}
            
            for doc in samples:
                for key, value in doc.items():
                    if key not in field_types:
                        field_types[key] = set()
                        field_occurrences[key] = 0
                    
                    field_types[key].add(type(value).__name__)
                    field_occurrences[key] += 1
            
            # Build schema dict
            schema = {}
            total_docs = len(samples)
            
            for field_name in field_types:
                occurrences = field_occurrences[field_name]
                types = sorted(list(field_types[field_name]))
                
                # Determine if field is always present
                always_present = occurrences == total_docs
                
                schema[field_name] = {
                    "types": types,
                    "occurrence": occurrences,
                    "total_sampled": total_docs,
                    "nullable": not always_present,
                    "frequency": occurrences / total_docs,
                }
            
            logger.debug(f"Inferred schema for collection '{collection_name}' from {total_docs} samples")
            return schema
        except Exception as e:
            logger.error(f"Failed to infer schema for '{collection_name}': {e}", exc_info=True)
            return {}
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database-level information.
        
        Returns:
            Dictionary with database information
        """
        try:
            info = {
                "database_name": self.database.name,
                "collections": self.get_all_collections(),
                "collection_count": len(self.get_all_collections()),
            }
            
            # Try to get database stats
            try:
                dbstats = self.database.command("dbStats")
                info["size_in_bytes"] = dbstats.get("dataSize", 0)
                info["storage_size_in_bytes"] = dbstats.get("storageSize", 0)
            except Exception:
                pass
            
            logger.debug(f"Retrieved database info: {info['collection_count']} collections")
            return info
        except Exception as e:
            logger.error(f"Failed to get database info: {e}", exc_info=True)
            return {}
    
    def close(self):
        """Close the MongoDB connection."""
        try:
            if self.client:
                self.client.close()
                logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}", exc_info=True)
    
    def __del__(self):
        """Cleanup on object destruction."""
        self.close()


__all__ = ["MongoDBExtractor"]
