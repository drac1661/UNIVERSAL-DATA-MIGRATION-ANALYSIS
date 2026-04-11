#!/usr/bin/env python
"""CLI for MongoDB batch data processing and JSON export."""

import argparse
import json
import logging
import sys
from pathlib import Path

from mongo_batch_data_processor import MongoBatchDataProcessor, print_export_stats
from logging_config import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Batch export MongoDB collections to JSON"
    )
    
    # Common arguments
    parser.add_argument(
        "--config",
        type=str,
        default="mongo_config.json",
        help="MongoDB config file (default: mongo_config.json)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Batch size for processing (default: 1000)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Export single collection
    export_parser = subparsers.add_parser(
        "export",
        help="Export single collection to JSON"
    )
    export_parser.add_argument(
        "collection",
        help="Collection name to export"
    )
    export_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: data/{collection}_data.json)"
    )
    export_parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="MongoDB query filter as JSON (e.g., '{\"status\": \"active\"}')"
    )
    export_parser.add_argument(
        "--format",
        choices=["json", "jsonl"],
        default="json",
        help="Output format (default: json)",
    )
    
    # Export all collections
    export_all_parser = subparsers.add_parser(
        "export-all",
        help="Export all collections to JSON"
    )
    export_all_parser.add_argument(
        "--output-dir",
        type=str,
        default="data/all_collections",
        help="Output directory (default: data/all_collections)",
    )
    
    # List collections
    list_parser = subparsers.add_parser(
        "list",
        help="List all collections in database"
    )
    
    # Get collection stats
    stats_parser = subparsers.add_parser(
        "stats",
        help="Get collection statistics"
    )
    stats_parser.add_argument(
        "collection",
        help="Collection name"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level)
    
    # Show help if no command
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        processor = MongoBatchDataProcessor(args.config)
        
        if args.command == "export":
            output_file = args.output or f"data/{args.collection}_data.json"
            query = None
            
            if args.query:
                try:
                    query = json.loads(args.query)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON query: {e}")
                    return 1
            
            logger.info(f"Exporting collection '{args.collection}' to {output_file}")
            
            if args.format == "jsonl":
                stats = processor.export_collection_json_per_line(
                    args.collection,
                    output_file,
                    batch_size=args.batch_size,
                    query=query,
                )
            else:
                stats = processor.export_collection_batched(
                    args.collection,
                    output_file,
                    batch_size=args.batch_size,
                    query=query,
                )
            
            print()
            print_export_stats(stats)
        
        elif args.command == "export-all":
            logger.info(f"Exporting all collections to {args.output_dir}")
            print()
            
            all_stats = processor.export_all_collections_batched(
                output_dir=args.output_dir,
                batch_size=args.batch_size,
            )
            
            for stats in all_stats:
                print_export_stats(stats)
                print()
        
        elif args.command == "list":
            collections = processor.extractor.get_all_collections()
            
            print()
            print("Collections in database:")
            print("-" * 50)
            
            for i, collection_name in enumerate(collections, 1):
                doc_count = processor.extractor.get_collection_document_count(collection_name)
                print(f"{i}. {collection_name} ({doc_count:,} documents)")
        
        elif args.command == "stats":
            stats = processor.get_collection_stats_before_export(args.collection)
            
            print()
            print(f"Collection: {stats['collection_name']}")
            print("-" * 50)
            print(f"Documents: {stats['document_count']:,}")
            print(f"Size: {stats['size_bytes'] / (1024*1024):.2f} MB")
            print(f"Storage: {stats['storage_size_bytes'] / (1024*1024):.2f} MB")
            print(f"Avg Doc Size: {stats['avg_doc_size_bytes']:,} bytes")
            
            if stats['document_count'] > 0:
                remaining = stats['size_bytes'] / stats['document_count']
                estimated_batches = (stats['document_count'] / args.batch_size) + 1
                print(f"Estimated batches (at size {args.batch_size}): {estimated_batches:.0f}")
        
        processor.close()
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    sys.exit(main())
