"""Universal database connection manager supporting multiple database types."""

import json
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Any, Dict, Iterator, Optional

from .connectors import PostgresConfig, connect_postgres

logger = logging.getLogger(__name__)


def load_db_config(config_file: str = "db_config.json") -> Dict[str, Any]:
    """Load database configuration from resources folder.
    
    Args:
        config_file: Name of the config file (default: db_config.json)
        
    Returns:
        Dictionary with database configuration including db_type
    """
    config_path = Path(__file__).parent.parent / "resources" / config_file
    
    logger.debug(f"Loading database config from: {config_path}")
    try:
        with open(config_path, "r") as f:
            config_data = json.load(f)
        logger.info(f"Database config loaded successfully (db_type: {config_data.get('db_type')})")
        return config_data
    except FileNotFoundError as e:
        logger.error(f"Config file not found: {config_path}", exc_info=True)
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file {config_path}: {e}", exc_info=True)
        raise


def get_connection(config_file: str = "db_config.json") -> Any:
    """Get a database connection based on config file.

    Supports:
        - postgresql/postgres
        - mysql
        - mongodb
        - etc.

    Args:
        config_file: Name of the config file
        
    Returns:
        Database connection object
    """
    try:
        config = load_db_config(config_file)
        db_type = config.get("db_type", "postgres").lower()
        logger.debug(f"Getting connection for database type: {db_type}")
        
        if db_type in ("postgres", "postgresql"):
            return _get_postgres_connection(config)
        elif db_type == "mysql":
            return _get_mysql_connection(config)
        elif db_type == "mongodb":
            return _get_mongodb_connection(config)
        else:
            logger.error(f"Unsupported database type: {db_type}")
            raise ValueError(f"Unsupported database type: {db_type}")
    except Exception as e:
        logger.error(f"Failed to get database connection: {e}", exc_info=True)
        raise


def _get_postgres_connection(config: Dict[str, Any]) -> Any:
    """Create PostgreSQL connection from config dict."""
    try:
        logger.debug(f"Creating PostgreSQL connection to {config.get('host')}:{config.get('port')}")
        pg_config = PostgresConfig(
            host=config["host"],
            port=config.get("port", 5432),
            dbname=config.get("dbname", "postgres"),
            user=config.get("user"),
            password=config.get("password"),
            sslmode=config.get("sslmode", "prefer"),
        )
        conn = connect_postgres(pg_config)
        logger.info(f"PostgreSQL connection established to {config.get('host')}:{config.get('port')}/{config.get('dbname')}")
        return conn
    except Exception as e:
        logger.error(f"Failed to create PostgreSQL connection: {e}", exc_info=True)
        raise


def _get_mysql_connection(config: Dict[str, Any]) -> Any:
    """Create MySQL connection from config dict.
    
    Note: Requires mysql-connector-python package
    """
    try:
        import mysql.connector
    except ImportError:
        raise ImportError("MySQL support requires: pip install mysql-connector-python")
    
    return mysql.connector.connect(
        host=config["host"],
        port=config.get("port", 3306),
        database=config.get("database"),
        user=config.get("user"),
        password=config.get("password"),
    )


def _get_mongodb_connection(config: Dict[str, Any]) -> Any:
    """Create MongoDB connection from config dict.
    
    Note: Requires pymongo package
    
    Returns:
        PyMongo MongoClient instance
    """
    try:
        from .connectors.mongodb import MongoDBConfig, connect_mongodb
    except ImportError:
        raise ImportError("MongoDB support requires: pip install pymongo")
    
    try:
        logger.debug(f"Creating MongoDB connection to {config.get('host')}:{config.get('port')}")
        mongodb_config = MongoDBConfig(
            host=config.get("host", "127.0.0.1"),
            port=config.get("port", 27017),
            dbname=config.get("dbname", "test"),
            user=config.get("user"),
            password=config.get("password"),
            auth_source=config.get("auth_source", "admin"),
            ssl=config.get("ssl", False),
            replica_set=config.get("replica_set"),
        )
        client = connect_mongodb(mongodb_config)
        logger.info(f"MongoDB connection established to {config.get('host')}:{config.get('port')}/{config.get('dbname')}")
        return client
    except Exception as e:
        logger.error(f"Failed to create MongoDB connection: {e}", exc_info=True)
        raise


@contextmanager
def get_db_connection(config_file: str = "db_config.json") -> Iterator[Any]:
    """Context manager for database connection.
    
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
    
    Args:
        config_file: Name of the config file
    """
    conn = get_connection(config_file)
    try:
        yield conn
    finally:
        conn.close()


def get_db_connection_direct(config_file: str = "db_config.json") -> Any:
    """Get a direct database connection (caller responsible for closing).
    
    Usage:
        conn = get_db_connection_direct()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
        finally:
            conn.close()
    
    Args:
        config_file: Name of the config file
    """
    return get_connection(config_file)


__all__ = [
    "load_db_config",
    "get_connection",
    "get_db_connection",
    "get_db_connection_direct",
]
