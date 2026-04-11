# MongoDB Schema and Data Extraction - Implementation Guide

## Overview

I've created a complete MongoDB schema and data extraction system that mirrors the PostgreSQL implementation. The structure follows the same patterns used for PostgreSQL but adapted for MongoDB's document-oriented nature.

## New Files Created

### 1. **Models** (`models/`)
MongoDB-specific data models using Pydantic:

- **`mongo_field.py`** - `MongoDBField` model
  - Represents fields in MongoDB collections
  - Tracks field types, nullability, indexing, nesting
  - Supports both simple and complex (nested/array) fields
  - Includes statistics on field occurrences

- **`mongo_index.py`** - `MongoDBIndex` model
  - Represents MongoDB collection indexes
  - Supports TTL indexes, sparse indexes, partial indexes
  - Tracks unique constraints and collation

- **`mongo_collection.py`** - `MongoDBCollection` model
  - Represents a collection in MongoDB
  - Contains fields, indexes, validation rules
  - Tracks collection statistics (size, document count, etc.)
  - Supports capped collections and validation schemas

- **`mongo_database.py`** - `MongoDBDatabase` model
  - Represents the entire MongoDB database
  - Contains collections, database-level metadata
  - Tracks version, size, users, roles

### 2. **Connectors** (`migrator/connectors/`)

- **`mongodb.py`** - MongoDB connection module
  - `MongoDBConfig` dataclass for connection configuration
  - `build_mongodb_connection_string()` - Creates MongoDB connection strings
  - `connect_mongodb()` & `connect_mongodb_params()` - Connection helpers
  - Supports SSL, replica sets, authentication

### 3. **Extractors** (`extractor/`)

- **`mongo_extractor.py`** - `MongoDBExtractor` class
  - Extracts schema metadata from MongoDB databases
  - Methods:
    - `get_all_collections()` - Lists all collections
    - `get_collection_document_count()` - Gets document count
    - `get_collection_indexes()` - Lists all indexes
    - `get_collection_validation_schema()` - Retrieves validation rules
    - `get_collection_stats()` - Gets collection statistics
    - `sample_documents()` - Samples documents for analysis
    - `infer_collection_schema()` - Intelligently infers schema from samples
    - `get_database_info()` - Gets database-level information

- **`mongo_data_extractor.py`** - `MongoDBDataExtractor` class
  - Extracts actual data from MongoDB collections
  - Methods:
    - `get_collection_data()` - Retrieves documents with filtering/projecting/sorting
    - `export_collection_to_json()` - Exports collection to JSON file
    - `stream_collection_data()` - Streams data in batches (memory efficient)
    - `get_collection_distinct_values()` - Gets unique values for a field
    - `get_collection_field_statistics()` - Analyzes field statistics
  - Handles BSON type serialization to JSON

### 4. **Schema Generator** (`mongo_schema_generator.py`)

Main schema extraction function:
- **`extract_schema_to_models()`** - Extracts complete MongoDB schema
  - Generates `MongoDBDatabase` model from actual MongoDB data
  - Samples documents to infer field types
  - Extracts indexes, validation rules, statistics
  - Outputs to JSON file using Pydantic models

Helper functions:
- **`infer_field_type()`** - Converts Python values to MongoDB type strings
- **`extract_collection_schema()`** - Extracts schema for a single collection
- **`extract_collection_data_to_json()`** - Exports collection data to JSON

### 5. **Main Scripts**

- **`mongo_schema_generator_main.py`** - Command-line entry point
  - Similar to `schema_generator_main.py` but for MongoDB
  - Supports:
    - `--config` - Config file (default: mongo_config.json)
    - `--schema-output` - Output file for schema JSON
    - `--collection` - Extract specific collection
    - `--sample-size` - Documents to sample (default: 100)
    - `--extract-data` - Also extract collection data
    - `--limit` - Limit documents when extracting
    - `--verbose` - Enable debug logging

### 6. **Configuration**

- **`resources/mongo_config.json`** - MongoDB database configuration
  ```json
  {
    "db_type": "mongodb",
    "host": "127.0.0.1",
    "port": 27017,
    "dbname": "test_db",
    "user": null,
    "password": null,
    "auth_source": "admin",
    "ssl": false,
    "replica_set": null
  }
  ```

### 7. **Updated Files**

- **`models/__init__.py`** - Added exports for all MongoDB models
- **`migrator/database.py`** - Added `_get_mongodb_connection()` function, updated `get_connection()` to support MongoDB

## Usage Examples

### 1. Extract MongoDB Schema to JSON

```python
from mongo_schema_generator import extract_schema_to_models

extract_schema_to_models(
    config_file="mongo_config.json",
    output_file="schema/extracted_mongo_schema.json",
    sample_size=100,
    max_collections=None  # None = all collections
)
```

### 2. Extract Collection Data to JSON

```python
from mongo_schema_generator import extract_collection_data_to_json

extract_collection_data_to_json(
    config_file="mongo_config.json",
    collection_name="users",
    output_file="data/users_data.json",
    query={"status": "active"},  # Optional filter
    limit=1000,  # Optional limit
)
```

### 3. Use the Extractors Directly

```python
from extractor.mongo_extractor import MongoDBExtractor
from extractor.mongo_data_extractor import MongoDBDataExtractor

# Initialize
extractor = MongoDBExtractor("mongo_config.json")
data_extractor = MongoDBDataExtractor(extractor.client, extractor.database)

# Extract schema info
collections = extractor.get_all_collections()
for collection_name in collections:
    schema = extractor.infer_collection_schema(collection_name)
    stats = extractor.get_collection_stats(collection_name)
    print(f"{collection_name}: {stats.get('count', 0)} documents")

# Get collection data
data = data_extractor.get_collection_data(
    "users",
    query={"active": True},
    limit=100
)

# Stream large collections efficiently
for batch in data_extractor.stream_collection_data("large_collection", batch_size=500):
    process_batch(batch)

extractor.close()
```

### 4. Using Command Line

```bash
# Extract schema only
python mongo_schema_generator_main.py \
    --config mongo_config.json \
    --schema-output schema/mongo_schema.json

# Extract schema and all data
python mongo_schema_generator_main.py \
    --config mongo_config.json \
    --schema-output schema/mongo_schema.json \
    --extract-data

# Extract specific collection data
python mongo_schema_generator_main.py \
    --collection users \
    --data-output data/users.json \
    --limit 5000

# Verbose logging
python mongo_schema_generator_main.py \
    --config mongo_config.json \
    --verbose
```

## Output Formats

### Schema JSON Structure

```json
{
  "dbname": "test_db",
  "db_type": "mongodb",
  "version": "5.0.0",
  "host": "127.0.0.1",
  "port": 27017,
  "collections": [
    {
      "collection_name": "users",
      "database_name": "test_db",
      "document_count": 1000,
      "size_in_bytes": 512000,
      "fields": [
        {
          "name": "_id",
          "type": "object",
          "nullable": false,
          "is_primary": true,
          "ordinal_position": 0
        },
        {
          "name": "email",
          "type": "string",
          "nullable": true,
          "unique": true,
          "indexed": true
        }
      ],
      "indexes": [
        {
          "name": "email_1",
          "fields": [["email", 1]],
          "unique": true
        }
      ]
    }
  ]
}
```

### Data JSON Structure

```json
[
  {
    "_id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2021-10-15T10:30:00",
    "status": "active"
  },
  {
    "_id": "507f1f77bcf86cd799439012",
    "name": "Jane Smith",
    "email": "jane@example.com",
    "created_at": "2021-10-16T11:45:00",
    "status": "active"
  }
]
```

## Key Features

### ✅ Reused Code Patterns
- Same model-validation approach using Pydantic
- Similar extractor design pattern
- Consistent JSON output format
- Related configuration management

### ✅ MongoDB-Specific Features
- Automatic BSON to JSON serialization (ObjectId, datetime, etc.)
- Schema inference from document sampling
- Support for nested/array fields
- TTL and sparse index detection
- Validation schema extraction
- Memory-efficient document streaming

### ✅ Comprehensive Schema Analysis
- Field type inference from samples
- Null/missing field detection
- Index and validation rule extraction
- Collection statistics and sizing

### ✅ Flexible Data Extraction
- Query filtering support
- Document projection
- Sorting and limiting
- Batch processing for large collections
- Export to JSON with proper serialization

## Dependencies

Ensure these are installed:
```bash
pip install pymongo pydantic
```

## Integration with PostgreSQL Code

The MongoDB implementation follows the same architecture as PostgreSQL:

| Component | PostgreSQL | MongoDB |
|-----------|-----------|---------|
| Models | `models/table.py`, etc. | `models/mongo_*.py` |
| Connection | `migrator/connectors/postgres.py` | `migrator/connectors/mongodb.py` |
| Schema Extract | `extractor/postgres_extractor.py` | `extractor/mongo_extractor.py` |
| Data Extract | `schema_generator.py` | `mongo_schema_generator.py` |
| Main Script | `schema_generator_main.py` | `mongo_schema_generator_main.py` |
| Config | `resources/db_config.json` | `resources/mongo_config.json` |

Both can coexist - use appropriate config file for each database type.

## Next Steps

1. **Update MongoDB config** - Set your MongoDB connection details in `resources/mongo_config.json`
2. **Install Dependencies** - `pip install pymongo`
3. **Test Connection** - Run extractor to verify MongoDB connectivity
4. **Run Schema Extraction** - `python mongo_schema_generator_main.py --verbose`
5. **Inspect Output** - Check generated JSON in `schema/` and `data/` directories

## Migration Ready

This MongoDB implementation is now ready to be used alongside PostgreSQL for:
- **Schema Comparison** - Compare MongoDB and PostgreSQL schemas
- **Data Migration** - Plan migration from MongoDB to PostgreSQL or vice versa
- **Schema Analysis** - Analyze MongoDB structure in JSON format
- **Data Export** - Export MongoDB data for analysis or migration
