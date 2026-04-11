"""MongoDB schema generator - extracts schema from MongoDB and saves as JSON."""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from models import MongoDBDatabase, MongoDBCollection, MongoDBField, MongoDBIndex
from extractor.mongo_extractor import MongoDBExtractor
from extractor.mongo_data_extractor import MongoDBDataExtractor

logger = logging.getLogger(__name__)


def infer_field_type(value: Any) -> str:
    """Infer MongoDB field type from a Python value.
    
    Args:
        value: Python value to infer type from
        
    Returns:
        MongoDB type string
    """
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "bool"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "double"
    elif isinstance(value, str):
        return "string"
    elif isinstance(value, bytes):
        return "binData"
    elif isinstance(value, list):
        return "array"
    elif isinstance(value, dict):
        return "object"
    elif hasattr(value, 'isoformat'):  # datetime
        return "date"
    else:
        return "mixed"


def extract_collection_schema(
    extractor: MongoDBExtractor,
    collection_name: str,
    sample_size: int = 100
) -> MongoDBCollection:
    """Extract schema information for a MongoDB collection.
    
    Args:
        extractor: MongoDBExtractor instance
        collection_name: Name of the collection
        sample_size: Number of documents to sample for schema inference
        
    Returns:
        MongoDBCollection model instance
    """
    logger.info(f"Extracting schema for collection: {collection_name}")
    
    collection_model = MongoDBCollection(
        collection_name=collection_name,
        database_name=extractor.database.name,
    )
    
    # Get collection stats
    try:
        doc_count = extractor.get_collection_document_count(collection_name)
        collection_model.document_count = doc_count
        
        stats = extractor.get_collection_stats(collection_name)
        if stats:
            collection_model.size_in_bytes = stats.get("size", 0)
            collection_model.storage_size_in_bytes = stats.get("storageSize", 0)
            collection_model.stats = stats
    except Exception as e:
        logger.debug(f"Could not retrieve collection stats: {e}")
    
    # Get validation schema if exists
    try:
        validation = extractor.get_collection_validation_schema(collection_name)
        collection_model.validation_schema = validation
    except Exception as e:
        logger.debug(f"No validation schema found: {e}")
    
    # Get indexes
    try:
        indexes = extractor.get_collection_indexes(collection_name)
        for idx in indexes:
            index_model = MongoDBIndex(
                name=idx.get("name", ""),
                fields=[(k, v) for k, v in idx.get("key", {}).items()],
                unique=idx.get("unique", False),
                sparse=idx.get("sparse", False),
                ttl=idx.get("expireAfterSeconds"),
                partial_filter=idx.get("partialFilterExpression"),
                hidden=idx.get("hidden", False),
                key_pattern=idx.get("key", {}),
            )
            collection_model.indexes.append(index_model)
        logger.debug(f"Found {len(indexes)} indexes")
    except Exception as e:
        logger.debug(f"Could not retrieve indexes: {e}")
    
    # Infer schema from sample documents
    try:
        schema_info = extractor.infer_collection_schema(collection_name, sample_size)
        
        # Create MongoDBField for each inferred field
        ordinal_position = 0
        for field_name, field_info in sorted(schema_info.items()):
            types = field_info.get("types", [])
            
            # Determine primary type
            primary_type = types[0] if types else "mixed"
            
            # Special handling for _id field
            is_primary = field_name == "_id"
            
            field_model = MongoDBField(
                name=field_name,
                type=primary_type,
                nullable=field_info.get("nullable", True),
                occurrence_count=field_info.get("occurrence", 0),
                unique_count=None,  # Could be calculated with aggregation
                null_count=0,  # Would need explicit query
                ordinal_position=ordinal_position,
                is_primary=is_primary,
            )
            
            collection_model.fields.append(field_model)
            ordinal_position += 1
        
        logger.debug(f"Inferred {len(collection_model.fields)} fields")
    except Exception as e:
        logger.warning(f"Could not infer collection schema: {e}")
    
    collection_model.created_at = datetime.now().isoformat()
    logger.debug(f"Schema extraction complete for collection: {collection_name}")
    
    return collection_model


def extract_schema_to_models(
    config_file: str = "db_config.json", 
    output_file: str = "schema/extracted_mongo_schema.json",
    sample_size: int = 100,
    max_collections: Optional[int] = None,
) -> None:
    """Extract MongoDB schema and save as JSON using Pydantic models.
    
    Args:
        config_file: Database config file name
        output_file: Output JSON file path
        sample_size: Number of documents to sample for schema inference
        max_collections: Maximum number of collections to process (None = all)
    """
    logger.info(f"Starting MongoDB schema extraction from {config_file} to {output_file}")
    
    try:
        extractor = MongoDBExtractor(config_file)
    except Exception as e:
        logger.error(f"Failed to initialize extractor: {e}", exc_info=True)
        raise
    
    try:
        # Create database model
        cfg = extractor.config or {}
        db_model = MongoDBDatabase(
            dbname=cfg.get("dbname") or "test",
            db_type="mongodb",
            host=cfg.get("host"),
            port=cfg.get("port"),
        )
        logger.debug(f"Created MongoDBDatabase model for {db_model.dbname}")
        
        # Get database info
        try:
            db_info = extractor.get_database_info()
            db_model.collection_count = db_info.get("collection_count", 0)
            db_model.size_in_bytes = db_info.get("size_in_bytes")
        except Exception as e:
            logger.debug(f"Could not retrieve database info: {e}")
        
        # Get MongoDB version
        try:
            server_info = extractor.database.client.server_info()
            db_model.version = server_info.get("version")
        except Exception as e:
            logger.debug(f"Could not retrieve MongoDB version: {e}")
        
        # Extract collection schemas
        collection_names = extractor.get_all_collections()
        if max_collections:
            collection_names = collection_names[:max_collections]
        
        logger.info(f"Processing {len(collection_names)} collection(s)")
        
        for collection_name in collection_names:
            try:
                collection_model = extract_collection_schema(
                    extractor,
                    collection_name,
                    sample_size=sample_size
                )
                db_model.collections.append(collection_model)
            except Exception as e:
                logger.error(f"Failed to extract schema for collection '{collection_name}': {e}")
                continue
        
        # Ensure output folder exists and save JSON
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving schema to {output_file}")
        db_model_dict = db_model.model_dump(exclude_none=False)
        
        with open(out_path, "w") as f:
            json.dump(db_model_dict, f, indent=2, default=str)
        
        logger.info(f"Schema extraction complete. Processed {len(db_model.collections)} collections")
        logger.info(f"Output saved to {out_path.absolute()}")
    
    except Exception as e:
        logger.error(f"Schema extraction failed: {e}", exc_info=True)
        raise
    finally:
        try:
            extractor.close()
        except Exception as e:
            logger.error(f"Error closing extractor: {e}")


def extract_collection_data_to_json(
    config_file: str = "db_config.json",
    collection_name: str = None,
    output_file: str = None,
    query: Dict[str, Any] = None,
    limit: int = None,
) -> int:
    """Extract data from a MongoDB collection and save as JSON.
    
    Args:
        config_file: Database config file name
        collection_name: Name of collection to extract
        output_file: Output JSON file path
        query: Optional MongoDB query filter
        limit: Optional document limit
        
    Returns:
        Number of documents extracted
    """
    if not collection_name or not output_file:
        raise ValueError("collection_name and output_file are required")
    
    logger.info(f"Extracting data from collection '{collection_name}'")
    
    try:
        extractor = MongoDBExtractor(config_file)
        data_extractor = MongoDBDataExtractor(extractor.client, extractor.database)
        
        doc_count = data_extractor.export_collection_to_json(
            collection_name,
            output_file,
            query=query,
            limit=limit,
        )
        
        logger.info(f"Successfully exported {doc_count} documents to {output_file}")
        return doc_count
    
    except Exception as e:
        logger.error(f"Failed to extract collection data: {e}", exc_info=True)
        raise
    finally:
        try:
            extractor.close()
        except Exception:
            pass


__all__ = [
    "extract_collection_schema",
    "extract_schema_to_models",
    "extract_collection_data_to_json",
    "infer_field_type",
]
