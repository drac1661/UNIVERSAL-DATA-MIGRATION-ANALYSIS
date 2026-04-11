# MongoDB Batch Data Processor - Usage Guide

## Overview

The MongoDB Batch Data Processor efficiently reads large MongoDB collections in batches and exports them to JSON files. It's designed to handle collections of any size without loading everything into memory.

## Files

- **`mongo_batch_data_processor.py`** - Main processor class and utilities
- **`mongo_batch_processor_cli.py`** - Command-line interface

## Quick Start

### 1. Export Single Collection

**Using Python:**
```python
from mongo_batch_data_processor import MongoBatchDataProcessor

processor = MongoBatchDataProcessor("mongo_config.json")
stats = processor.export_collection_batched(
    collection_name="users",
    output_file="data/users.json",
    batch_size=1000,
)
processor.close()
```

**Using CLI:**
```bash
python mongo_batch_processor_cli.py export users --output data/users.json --batch-size 1000
```

### 2. Export All Collections

**Using Python:**
```python
from mongo_batch_data_processor import MongoBatchDataProcessor

processor = MongoBatchDataProcessor("mongo_config.json")
all_stats = processor.export_all_collections_batched(
    output_dir="data/all_collections",
    batch_size=1000,
)
processor.close()
```

**Using CLI:**
```bash
python mongo_batch_processor_cli.py export-all --output-dir data/all_collections --batch-size 1000
```

### 3. Export with Filtering

**Using Python:**
```python
processor = MongoBatchDataProcessor("mongo_config.json")
stats = processor.export_collection_with_filtering(
    collection_name="orders",
    output_file="data/active_orders.json",
    query={"status": "active"},
    batch_size=1000,
)
processor.close()
```

**Using CLI:**
```bash
python mongo_batch_processor_cli.py export orders \
  --query '{"status": "active"}' \
  --output data/active_orders.json
```

### 4. Export with Projection (Selected Fields)

**Using Python:**
```python
processor = MongoBatchDataProcessor("mongo_config.json")
stats = processor.export_collection_with_projection(
    collection_name="users",
    output_file="data/user_names_emails.json",
    fields=["name", "email", "created_at"],
    batch_size=1000,
)
processor.close()
```

### 5. Export as JSON Lines (JSONL)

JSON Lines format (one JSON object per line) is better for streaming and large datasets.

**Using Python:**
```python
processor = MongoBatchDataProcessor("mongo_config.json")
stats = processor.export_collection_json_per_line(
    collection_name="events",
    output_file="data/events.jsonl",
    batch_size=5000,
)
processor.close()
```

**Using CLI:**
```bash
python mongo_batch_processor_cli.py export events --format jsonl --output data/events.jsonl
```

## CLI Commands

### Export Command
```bash
python mongo_batch_processor_cli.py export <collection> [options]
```

Options:
- `--output` - Output file path (default: `data/{collection}_data.json`)
- `--query` - MongoDB query filter as JSON string
- `--format` - Output format: `json` or `jsonl` (default: `json`)
- `--batch-size` - Batch size (default: 1000)
- `--config` - Config file (default: `mongo_config.json`)
- `--verbose` - Enable debug logging

Examples:
```bash
# Export users collection
python mongo_batch_processor_cli.py export users

# Export with specific output file
python mongo_batch_processor_cli.py export users --output my_users.json

# Export filtered data
python mongo_batch_processor_cli.py export orders \
  --query '{"total": {"$gt": 100}}' \
  --output high_value_orders.json

# Export as JSONL with larger batch size
python mongo_batch_processor_cli.py export large_collection \
  --format jsonl \
  --batch-size 5000

# Verbose output
python mongo_batch_processor_cli.py export users --verbose
```

### Export All Command
```bash
python mongo_batch_processor_cli.py export-all [options]
```

Options:
- `--output-dir` - Output directory (default: `data/all_collections`)
- `--batch-size` - Batch size (default: 1000)
- `--config` - Config file (default: `mongo_config.json`)
- `--verbose` - Enable debug logging

Examples:
```bash
# Export all collections
python mongo_batch_processor_cli.py export-all

# Export to custom directory
python mongo_batch_processor_cli.py export-all --output-dir exports/

# Larger batches for faster export
python mongo_batch_processor_cli.py export-all --batch-size 5000
```

### List Command
```bash
python mongo_batch_processor_cli.py list [options]
```

Lists all collections with document counts.

Examples:
```bash
# List all collections
python mongo_batch_processor_cli.py list

# With config file
python mongo_batch_processor_cli.py list --config mongo_config.json
```

### Stats Command
```bash
python mongo_batch_processor_cli.py stats <collection> [options]
```

Shows collection statistics before export.

Examples:
```bash
# Get stats for users collection
python mongo_batch_processor_cli.py stats users

# Get stats with custom batch size info
python mongo_batch_processor_cli.py stats orders --batch-size 5000
```

## Python API Reference

### MongoBatchDataProcessor Class

#### Methods

**`__init__(config_file: str = "mongo_config.json")`**
- Initialize processor with MongoDB config file

**`export_collection_batched(...)`**
```python
export_collection_batched(
    collection_name: str,
    output_file: str,
    batch_size: int = 1000,
    query: Optional[Dict[str, Any]] = None,
    projection: Optional[Dict[str, int]] = None,
    progress_interval: int = 5000,
) -> Dict[str, Any]
```
- Export collection to JSON array format
- Returns export statistics

**`export_all_collections_batched(...)`**
```python
export_all_collections_batched(
    output_dir: str = "data",
    batch_size: int = 1000,
    progress_interval: int = 5000,
) -> List[Dict[str, Any]]
```
- Export all collections to separate JSON files
- Returns list of statistics for each collection

**`export_collection_with_filtering(...)`**
```python
export_collection_with_filtering(
    collection_name: str,
    output_file: str,
    query: Dict[str, Any],
    batch_size: int = 1000,
    progress_interval: int = 5000,
) -> Dict[str, Any]
```
- Export filtered collection data
- Query example: `{"status": "active", "age": {"$gt": 18}}`

**`export_collection_with_projection(...)`**
```python
export_collection_with_projection(
    collection_name: str,
    output_file: str,
    fields: List[str],
    batch_size: int = 1000,
    progress_interval: int = 5000,
) -> Dict[str, Any]
```
- Export only selected fields
- Fields example: `["name", "email", "created_at"]`

**`export_collection_json_per_line(...)`**
```python
export_collection_json_per_line(
    collection_name: str,
    output_file: str,
    batch_size: int = 1000,
    query: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]
```
- Export as JSONL format (one JSON per line)
- Better for streaming and large datasets

**`get_collection_stats_before_export(collection_name: str) -> Dict[str, Any]`**
- Get collection statistics (size, document count, etc.)

**`read_collection_in_batches(...)`**
```python
read_collection_in_batches(
    collection_name: str,
    batch_size: int = 1000,
    query: Optional[Dict[str, Any]] = None,
    projection: Optional[Dict[str, int]] = None,
) -> Iterator[List[Dict[str, Any]]]
```
- Generator yielding batches of documents
- Use for custom processing logic

**`close()`**
- Close MongoDB connection (always call when done)

## Output Example

### JSON Format
```json
[
  {
    "_id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2021-10-15T10:30:00"
  },
  {
    "_id": "507f1f77bcf86cd799439012",
    "name": "Jane Smith",
    "email": "jane@example.com",
    "created_at": "2021-10-16T11:45:00"
  }
]
```

### JSONL Format
```
{"_id": "507f1f77bcf86cd799439011", "name": "John Doe", "email": "john@example.com", "created_at": "2021-10-15T10:30:00"}
{"_id": "507f1f77bcf86cd799439012", "name": "Jane Smith", "email": "jane@example.com", "created_at": "2021-10-16T11:45:00"}
```

## Export Statistics

Each export returns a statistics dictionary:

```python
{
    "collection_name": "users",
    "output_file": "/path/to/output.json",
    "total_documents": 50000,
    "batch_count": 50,
    "batch_size": 1000,
    "elapsed_seconds": 12.34,
    "documents_per_second": 4055.0,
    "file_size_bytes": 2048000,
    "status": "success"
}
```

## Performance Tips

### 1. Optimal Batch Size
- **Small collections (<10k docs)**: 1000-2000
- **Medium collections (10k-1M docs)**: 2000-5000
- **Large collections (>1M docs)**: 5000-10000

```python
# Larger batches = less network overhead, more memory
processor.export_collection_batched(
    "large_collection",
    "output.json",
    batch_size=10000,  # Larger batches for big collections
)
```

### 2. Use JSONL for Large Datasets
JSONL format is more memory-efficient for streaming:
```python
# Better for very large collections
processor.export_collection_json_per_line(
    "huge_collection",
    "output.jsonl",
    batch_size=10000,
)
```

### 3. Filter Data Before Export
Reduce file size by filtering unnecessary data:
```python
# Export only active users
processor.export_collection_with_filtering(
    "users",
    "active_users.json",
    query={"status": "active"},
)
```

### 4. Project Specific Fields
Further reduce file size by exporting only needed fields:
```python
# Export only name and email
processor.export_collection_with_projection(
    "users",
    "user_contacts.json",
    fields=["name", "email"],
)
```

## Error Handling

```python
from mongo_batch_data_processor import MongoBatchDataProcessor

try:
    processor = MongoBatchDataProcessor("mongo_config.json")
    stats = processor.export_collection_batched(
        "users",
        "output.json",
    )
    
    if stats.get("status") == "error":
        print(f"Export failed: {stats.get('error')}")
    else:
        print(f"✓ Exported {stats['total_documents']} documents")
finally:
    processor.close()
```

## MongoDB Query Examples

### Filter Examples
```bash
# Active users
python mongo_batch_processor_cli.py export users \
  --query '{"status": "active"}'

# Users created after date
python mongo_batch_processor_cli.py export users \
  --query '{"created_at": {"$gt": "2021-01-01"}}'

# Orders with total > 100
python mongo_batch_processor_cli.py export orders \
  --query '{"total": {"$gt": 100}}'

# Users from specific country
python mongo_batch_processor_cli.py export users \
  --query '{"country": {"$in": ["USA", "Canada"]}}'

# Complex query
python mongo_batch_processor_cli.py export orders \
  --query '{"status": "completed", "total": {"$gt": 50}, "items": {"$gt": 2}}'
```

## Real-World Examples

### Example 1: Daily Data Backups
```python
from datetime import datetime
from mongo_batch_data_processor import MongoBatchDataProcessor

def backup_all_collections():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/mongo_{timestamp}"
    
    processor = MongoBatchDataProcessor("mongo_config.json")
    stats = processor.export_all_collections_batched(
        output_dir=backup_dir,
        batch_size=5000,
    )
    processor.close()
    
    print(f"Backup complete: {backup_dir}")

backup_all_collections()
```

### Example 2: Export and Analyze
```python
from mongo_batch_data_processor import MongoBatchDataProcessor
import json

processor = MongoBatchDataProcessor("mongo_config.json")

# Export data
stats = processor.export_collection_batched(
    "orders",
    "orders.json",
)

# Load and analyze
with open("orders.json") as f:
    orders = json.load(f)

# Calculate statistics
total = sum(o.get("total", 0) for o in orders)
average = total / len(orders) if orders else 0

print(f"Total revenue: ${total:,.2f}")
print(f"Average order: ${average:,.2f}")

processor.close()
```

### Example 3: Selective Export by Date Range
```bash
# Export orders from last 30 days
python mongo_batch_processor_cli.py export orders \
  --query '{"created_at": {"$gte": "2024-03-12T00:00:00"}}' \
  --output recent_orders.json
```

## Troubleshooting

### Issue: Memory Usage Too High
**Solution**: Reduce batch size
```bash
python mongo_batch_processor_cli.py export large_collection \
  --batch-size 500  # Smaller batches
```

### Issue: Export Very Slow
**Solution**: Increase batch size and use parallel processing
```bash
python mongo_batch_processor_cli.py export very_large_collection \
  --batch-size 10000  # Larger batches
```

### Issue: Connection Timeout
**Solution**: Check MongoDB config and connection
```bash
python mongo_batch_processor_cli.py list --config mongo_config.json --verbose
```

### Issue: Query Not Working
**Solution**: Verify JSON syntax and MongoDB query operators
```bash
# Test simple query first
python mongo_batch_processor_cli.py export users --query '{"status": "active"}'
```

## See Also

- `mongo_schema_generator.py` - Extract schema definitions
- `mongo_schema_generator_main.py` - Main schema extraction script
- `MONGODB_IMPLEMENTATION.md` - Complete MongoDB implementation guide
- `MONGODB_DOCKER_SETUP.md` - Docker setup instructions
