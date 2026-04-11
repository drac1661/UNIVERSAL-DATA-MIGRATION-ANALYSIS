# MongoDB Implementation - Quick Reference

## 📁 File Structure Created

```
UNIVERSAL-DATA-MIGRATION-ANALYSIS/
├── models/
│   ├── mongo_field.py          ← MongoDB field model
│   ├── mongo_index.py          ← MongoDB index model
│   ├── mongo_collection.py     ← MongoDB collection model
│   ├── mongo_database.py       ← MongoDB database model
│   └── __init__.py             ← Updated with MongoDB exports
│
├── migrator/
│   ├── connectors/
│   │   └── mongodb.py          ← MongoDB connection helper
│   ├── database.py             ← Updated with MongoDB support
│   └── connection.py
│
├── extractor/
│   ├── mongo_extractor.py      ← Schema extractor
│   ├── mongo_data_extractor.py ← Data extractor
│   └── postgres_extractor.py
│
├── resources/
│   ├── mongo_config.json       ← MongoDB config file
│   └── db_config.json
│
├── mongo_schema_generator.py   ← Main schema generator
├── mongo_schema_generator_main.py ← CLI entry point
└── MONGODB_IMPLEMENTATION.md   ← Full documentation
```

## 🚀 Quick Start

### 1. Configure MongoDB Connection
Edit `resources/mongo_config.json`:
```json
{
  "db_type": "mongodb",
  "host": "127.0.0.1",
  "port": 27017,
  "dbname": "your_database",
  "user": null,
  "password": null
}
```

### 2. Extract Schema
```bash
python mongo_schema_generator_main.py \
  --config mongo_config.json \
  --schema-output schema/mongo_schema.json
```

### 3. Extract Data
```bash
python mongo_schema_generator_main.py \
  --collection users \
  --data-output data/users.json
```

## 📊 Available Classes

### Models
- `MongoDBField` - Individual collection field
- `MongoDBIndex` - Collection index
- `MongoDBCollection` - MongoDB collection
- `MongoDBDatabase` - Complete database schema

### Extractors
- `MongoDBExtractor` - Extract schema metadata
- `MongoDBDataExtractor` - Extract collection data

### Connectors
- `MongoDBConfig` - Configuration class
- `connect_mongodb()` - Create connection
- `build_mongodb_connection_string()` - Build connection string

## 🔧 Common Functions

### Schema Generation
```python
extract_schema_to_models(
    config_file="mongo_config.json",
    output_file="schema/mongo_schema.json",
    sample_size=100
)
```

### Data Export
```python
extract_collection_data_to_json(
    config_file="mongo_config.json",
    collection_name="users",
    output_file="data/users.json"
)
```

### Direct Usage
```python
extractor = MongoDBExtractor("mongo_config.json")
collections = extractor.get_all_collections()
schema = extractor.infer_collection_schema("users")
extractor.close()
```

## 📈 Features

✅ **Complete Schema Extraction**
- Collections, fields, indexes
- Validation rules, statistics
- Type inference from samples

✅ **Flexible Data Export**
- Query filtering
- Document limiting
- Memory-efficient streaming
- JSON serialization with BSON handling

✅ **Production Ready**
- Comprehensive error handling
- Logging throughout
- Configuration-driven
- CLI interface available

✅ **Reuses PostgreSQL Patterns**
- Same model structure
- Consistent JSON output
- Same configuration approach
- Compatible with existing code

## 📝 Configuration Options

### mongo_config.json
```json
{
  "db_type": "mongodb",           // Required
  "host": "127.0.0.1",            // Server host
  "port": 27017,                  // Server port
  "dbname": "test_db",            // Database name
  "user": null,                   // Optional username
  "password": null,               // Optional password
  "auth_source": "admin",         // Auth database
  "ssl": false,                   // Use SSL
  "replica_set": null             // Replica set name
}
```

## 🔗 Integration Points

### With Existing PostgreSQL Code
```python
# PostgreSQL
from schema_generator import extract_schema_to_models as pg_extract

# MongoDB
from mongo_schema_generator import extract_schema_to_models as mongo_extract

# Both can be used together
pg_extract(config_file="db_config.json")
mongo_extract(config_file="mongo_config.json")
```

### Database Detection
```python
from migrator import load_db_config

config = load_db_config("mongo_config.json")
db_type = config.get("db_type")  # "mongodb"
```

## 💡 Example Workflows

### Complete Schema + Data Export
```python
from mongo_schema_generator import (
    extract_schema_to_models,
    extract_collection_data_to_json
)

# Get schema
extract_schema_to_models("mongo_config.json", "schema/mongo_schema.json")

# Get all collection data
from extractor.mongo_extractor import MongoDBExtractor
extractor = MongoDBExtractor("mongo_config.json")
for collection in extractor.get_all_collections():
    extract_collection_data_to_json(
        "mongo_config.json",
        collection,
        f"data/{collection}.json"
    )
extractor.close()
```

### Analysis Workflow
```python
from extractor.mongo_extractor import MongoDBExtractor
from extractor.mongo_data_extractor import MongoDBDataExtractor

extractor = MongoDBExtractor("mongo_config.json")
data_extractor = MongoDBDataExtractor(extractor.client, extractor.database)

for collection_name in extractor.get_all_collections():
    schema = extractor.infer_collection_schema(collection_name)
    stats = extractor.get_collection_stats(collection_name)
    docs = data_extractor.get_collection_data(collection_name, limit=10)
    
    print(f"{collection_name}:")
    print(f"  Documents: {stats.get('count', 0)}")
    print(f"  Fields: {len(schema)}")
    print(f"  Sample: {docs[0] if docs else 'No data'}")

extractor.close()
```

## ✨ Special Features

### BSON to JSON Serialization
Automatically converts:
- `ObjectId` → String
- `datetime` → ISO format
- `bytes` → UTF-8 string

### Intelligent Schema Inference
- Samples documents to infer types
- Detects mixed types
- Identifies nested/array fields
- Tracks field frequency

### Memory Efficient
- Stream large collections in batches
- Configurable sample sizes
- Batch processing support

## 📖 Documentation

See `MONGODB_IMPLEMENTATION.md` for:
- Detailed file descriptions
- Complete usage examples
- Output format specifications
- Feature comparisons with PostgreSQL
- Integration guidelines

## 🔗 Related Files

- PostgreSQL equivalent: `schema_generator.py`
- PostgreSQL main: `schema_generator_main.py`
- Models: `models/__init__.py`
- Connection: `migrator/database.py`
