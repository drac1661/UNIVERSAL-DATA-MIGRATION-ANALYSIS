"""MongoDB batch data reader and JSON converter.

Efficiently reads MongoDB collections in batches and exports to JSON files.
Ideal for large collections that don't fit in memory.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Iterator, List
from datetime import datetime

from extractor.mongo_extractor import MongoDBExtractor
from extractor.mongo_data_extractor import MongoDBDataExtractor

logger = logging.getLogger(__name__)


class MongoBatchDataProcessor:
    """Process MongoDB collections in batches and export to JSON."""
    
    def __init__(self, config_file: str = "mongo_config.json"):
        """Initialize the batch processor.
        
        Args:
            config_file: Path to MongoDB config file
        """
        logger.info(f"Initializing MongoBatchDataProcessor with config: {config_file}")
        self.extractor = MongoDBExtractor(config_file)
        self.data_extractor = MongoDBDataExtractor(
            self.extractor.client,
            self.extractor.database
        )
        self.config_file = config_file
    
    def read_collection_in_batches(
        self,
        collection_name: str,
        batch_size: int = 1000,
        query: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, int]] = None,
    ) -> Iterator[List[Dict[str, Any]]]:
        """Read collection data in batches.
        
        Args:
            collection_name: Name of the collection
            batch_size: Number of documents per batch
            query: Optional MongoDB query filter
            projection: Optional MongoDB projection
            
        Yields:
            List of documents in each batch
        """
        logger.info(f"Reading collection '{collection_name}' in batches of {batch_size}")
        yield from self.data_extractor.stream_collection_data(
            collection_name,
            query=query,
            batch_size=batch_size,
            projection=projection,
        )
    
    def export_collection_batched(
        self,
        collection_name: str,
        output_file: str,
        batch_size: int = 1000,
        query: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, int]] = None,
        progress_interval: int = 5000,
    ) -> Dict[str, Any]:
        """Export collection to JSON file, processing in batches.
        
        Args:
            collection_name: Name of the collection
            output_file: Path to output JSON file
            batch_size: Number of documents per batch
            query: Optional MongoDB query filter
            projection: Optional MongoDB projection
            progress_interval: Log progress every N documents
            
        Returns:
            Dictionary with export statistics
        """
        logger.info(f"Export started for collection '{collection_name}' to {output_file}")
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        total_documents = 0
        batch_count = 0
        start_time = datetime.now()
        
        try:
            with open(output_path, 'w') as f:
                f.write('[\n')
                first_doc = True
                
                for batch in self.read_collection_in_batches(
                    collection_name,
                    batch_size=batch_size,
                    query=query,
                    projection=projection,
                ):
                    batch_count += 1
                    
                    for doc in batch:
                        if not first_doc:
                            f.write(',\n')
                        json.dump(doc, f, default=str)
                        first_doc = False
                        total_documents += 1
                        
                        # Log progress
                        if total_documents % progress_interval == 0:
                            logger.info(f"Progress: {total_documents} documents exported")
                
                f.write('\n]')
            
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = total_documents / elapsed if elapsed > 0 else 0
            
            stats = {
                "collection_name": collection_name,
                "output_file": str(output_path.absolute()),
                "total_documents": total_documents,
                "batch_count": batch_count,
                "batch_size": batch_size,
                "elapsed_seconds": elapsed,
                "documents_per_second": rate,
                "file_size_bytes": output_path.stat().st_size,
                "status": "success",
            }
            
            logger.info(f"Export completed: {total_documents} documents in {elapsed:.2f}s ({rate:.1f} docs/s)")
            return stats
        
        except Exception as e:
            logger.error(f"Export failed: {e}", exc_info=True)
            return {
                "collection_name": collection_name,
                "output_file": str(output_path.absolute()),
                "total_documents": total_documents,
                "status": "error",
                "error": str(e),
            }
    
    def export_all_collections_batched(
        self,
        output_dir: str = "data",
        batch_size: int = 1000,
        progress_interval: int = 5000,
    ) -> List[Dict[str, Any]]:
        """Export all collections to separate JSON files using batches.
        
        Args:
            output_dir: Directory to store output files
            batch_size: Number of documents per batch
            progress_interval: Log progress every N documents
            
        Returns:
            List of export statistics for each collection
        """
        logger.info(f"Exporting all collections to '{output_dir}'")
        
        collections = self.extractor.get_all_collections()
        logger.info(f"Found {len(collections)} collections to export")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        all_stats = []
        
        for collection_name in collections:
            output_file = output_path / f"{collection_name}_data.json"
            
            try:
                logger.info(f"Exporting collection: {collection_name}")
                stats = self.export_collection_batched(
                    collection_name,
                    str(output_file),
                    batch_size=batch_size,
                    progress_interval=progress_interval,
                )
                all_stats.append(stats)
            except Exception as e:
                logger.error(f"Failed to export collection '{collection_name}': {e}")
                all_stats.append({
                    "collection_name": collection_name,
                    "status": "error",
                    "error": str(e),
                })
        
        return all_stats
    
    def export_collection_with_filtering(
        self,
        collection_name: str,
        output_file: str,
        query: Dict[str, Any],
        batch_size: int = 1000,
        progress_interval: int = 5000,
    ) -> Dict[str, Any]:
        """Export filtered collection data to JSON.
        
        Args:
            collection_name: Name of the collection
            output_file: Path to output JSON file
            query: MongoDB query filter (e.g., {"status": "active"})
            batch_size: Number of documents per batch
            progress_interval: Log progress every N documents
            
        Returns:
            Export statistics
        """
        logger.info(f"Exporting filtered data from '{collection_name}' with query: {query}")
        
        return self.export_collection_batched(
            collection_name,
            output_file,
            batch_size=batch_size,
            query=query,
            progress_interval=progress_interval,
        )
    
    def export_collection_with_projection(
        self,
        collection_name: str,
        output_file: str,
        fields: List[str],
        batch_size: int = 1000,
        progress_interval: int = 5000,
    ) -> Dict[str, Any]:
        """Export collection with only selected fields.
        
        Args:
            collection_name: Name of the collection
            output_file: Path to output JSON file
            fields: List of field names to include
            batch_size: Number of documents per batch
            progress_interval: Log progress every N documents
            
        Returns:
            Export statistics
        """
        # Create MongoDB projection dict
        projection = {field: 1 for field in fields}
        
        logger.info(f"Exporting '{collection_name}' with projection: {fields}")
        
        return self.export_collection_batched(
            collection_name,
            output_file,
            batch_size=batch_size,
            projection=projection,
            progress_interval=progress_interval,
        )
    
    def export_collection_json_per_line(
        self,
        collection_name: str,
        output_file: str,
        batch_size: int = 1000,
        query: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Export collection as JSON Lines (one JSON object per line).
        
        Useful for streaming processing and large datasets.
        
        Args:
            collection_name: Name of the collection
            output_file: Path to output JSONL file
            batch_size: Number of documents per batch
            query: Optional MongoDB query filter
            
        Returns:
            Export statistics
        """
        logger.info(f"Exporting collection '{collection_name}' as JSONL to {output_file}")
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        total_documents = 0
        batch_count = 0
        start_time = datetime.now()
        
        try:
            with open(output_path, 'w') as f:
                for batch in self.read_collection_in_batches(
                    collection_name,
                    batch_size=batch_size,
                    query=query,
                ):
                    batch_count += 1
                    
                    for doc in batch:
                        f.write(json.dumps(doc, default=str) + '\n')
                        total_documents += 1
            
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = total_documents / elapsed if elapsed > 0 else 0
            
            stats = {
                "collection_name": collection_name,
                "output_file": str(output_path.absolute()),
                "total_documents": total_documents,
                "batch_count": batch_count,
                "batch_size": batch_size,
                "elapsed_seconds": elapsed,
                "documents_per_second": rate,
                "file_size_bytes": output_path.stat().st_size,
                "format": "jsonl",
                "status": "success",
            }
            
            logger.info(f"JSONL export completed: {total_documents} documents in {elapsed:.2f}s ({rate:.1f} docs/s)")
            return stats
        
        except Exception as e:
            logger.error(f"JSONL export failed: {e}", exc_info=True)
            return {
                "collection_name": collection_name,
                "output_file": str(output_path.absolute()),
                "status": "error",
                "error": str(e),
            }
    
    def get_collection_stats_before_export(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics before exporting.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection statistics
        """
        doc_count = self.extractor.get_collection_document_count(collection_name)
        stats = self.extractor.get_collection_stats(collection_name)
        
        return {
            "collection_name": collection_name,
            "document_count": doc_count,
            "size_bytes": stats.get("size", 0),
            "storage_size_bytes": stats.get("storageSize", 0),
            "avg_doc_size_bytes": stats.get("avgObjSize", 0),
        }
    
    def close(self):
        """Close MongoDB connection."""
        try:
            self.extractor.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")


def print_export_stats(stats: Dict[str, Any]) -> None:
    """Print export statistics in a formatted way.
    
    Args:
        stats: Statistics dictionary from export operations
    """
    if stats.get("status") == "error":
        print(f"❌ Error: {stats.get('error')}")
        return
    
    print(f"✓ Export Summary:")
    print(f"  Collection: {stats.get('collection_name')}")
    print(f"  Documents: {stats.get('total_documents'):,}")
    print(f"  Batches: {stats.get('batch_count')}")
    print(f"  Time: {stats.get('elapsed_seconds', 0):.2f}s")
    print(f"  Rate: {stats.get('documents_per_second', 0):.1f} docs/s")
    print(f"  File: {stats.get('output_file')}")
    if stats.get('file_size_bytes'):
        size_mb = stats['file_size_bytes'] / (1024 * 1024)
        print(f"  Size: {size_mb:.2f} MB")


if __name__ == "__main__":
    # Example usage
    from logging_config import setup_logging
    
    setup_logging(level=logging.INFO)
    
    processor = MongoBatchDataProcessor("mongo_config.json")
    
    # Example 1: Export single collection
    print("\n" + "="*60)
    print("Example 1: Export single collection")
    print("="*60)
    stats = processor.export_collection_batched(
        collection_name="users",
        output_file="data/users_batched.json",
        batch_size=500,
    )
    print_export_stats(stats)
    
    # Example 2: Export all collections
    print("\n" + "="*60)
    print("Example 2: Export all collections")
    print("="*60)
    all_stats = processor.export_all_collections_batched(
        output_dir="data/all_collections",
        batch_size=1000,
    )
    for stat in all_stats:
        print_export_stats(stat)
    
    # Example 3: Export with filtering
    print("\n" + "="*60)
    print("Example 3: Export filtered data")
    print("="*60)
    stats = processor.export_collection_with_filtering(
        collection_name="users",
        output_file="data/active_users.json",
        query={"status": "active"},
        batch_size=500,
    )
    print_export_stats(stats)
    
    # Example 4: Export as JSONL
    print("\n" + "="*60)
    print("Example 4: Export as JSON Lines")
    print("="*60)
    stats = processor.export_collection_json_per_line(
        collection_name="users",
        output_file="data/users.jsonl",
        batch_size=500,
    )
    print_export_stats(stats)
    
    processor.close()
