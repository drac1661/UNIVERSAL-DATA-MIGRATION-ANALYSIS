#!/usr/bin/env python
"""Main script to extract MongoDB schema and data."""

import logging
import argparse
import json
from pathlib import Path

from mongo_schema_generator import (
    extract_schema_to_models,
    extract_collection_data_to_json,
    infer_field_type,
)
from extractor.mongo_extractor import MongoDBExtractor
from extractor.mongo_data_extractor import MongoDBDataExtractor

# Configure logging
from logging_config import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Main entry point for MongoDB schema extraction."""
    parser = argparse.ArgumentParser(
        description="Extract MongoDB schema and data"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="mongo_config.json",
        help="Database config file (default: mongo_config.json)",
    )
    parser.add_argument(
        "--schema-output",
        type=str,
        default="schema/extracted_mongo_schema.json",
        help="Output file for schema (default: schema/extracted_mongo_schema.json)",
    )
    parser.add_argument(
        "--data-output",
        type=str,
        default="data/mongo_data.json",
        help="Output file for data (optional)",
    )
    parser.add_argument(
        "--collection",
        type=str,
        help="Specific collection to extract (if not set, extracts all)",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=100,
        help="Number of documents to sample for schema inference (default: 100)",
    )
    parser.add_argument(
        "--max-collections",
        type=int,
        help="Maximum number of collections to process",
    )
    parser.add_argument(
        "--extract-data",
        action="store_true",
        help="Also extract collection data",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of documents when extracting data",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level)

    logger.info("=" * 80)
    logger.info("MongoDB Schema and Data Extractor")
    logger.info("=" * 80)
    logger.info(f"Config file: {args.config}")
    logger.info(f"Schema output: {args.schema_output}")

    try:
        # Extract schema
        logger.info("\nStep 1: Extracting MongoDB schema...")
        extract_schema_to_models(
            config_file=args.config,
            output_file=args.schema_output,
            sample_size=args.sample_size,
            max_collections=args.max_collections,
        )
        logger.info("✓ Schema extraction complete")

        # Optionally extract data
        if args.extract_data or args.collection:
            logger.info("\nStep 2: Extracting MongoDB data...")
            
            try:
                extractor = MongoDBExtractor(args.config)
                data_extractor = MongoDBDataExtractor(
                    extractor.client, 
                    extractor.database
                )
                
                if args.collection:
                    # Extract specific collection
                    output_file = args.data_output or f"data/{args.collection}_data.json"
                    logger.info(f"Extracting collection: {args.collection}")
                    doc_count = extract_collection_data_to_json(
                        config_file=args.config,
                        collection_name=args.collection,
                        output_file=output_file,
                        limit=args.limit,
                    )
                    logger.info(f"✓ Exported {doc_count} documents to {output_file}")
                else:
                    # Extract all collections
                    collections = extractor.get_all_collections()
                    for collection_name in collections:
                        output_file = f"data/mongo_{collection_name}_data.json"
                        try:
                            doc_count = extract_collection_data_to_json(
                                config_file=args.config,
                                collection_name=collection_name,
                                output_file=output_file,
                                limit=args.limit,
                            )
                            logger.info(f"✓ Exported {collection_name}: {doc_count} documents")
                        except Exception as e:
                            logger.error(f"Failed to export {collection_name}: {e}")
                
                extractor.close()
            except Exception as e:
                logger.error(f"Failed to extract data: {e}", exc_info=True)

        logger.info("\n" + "=" * 80)
        logger.info("MongoDB extraction complete!")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Fatal error during extraction: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
