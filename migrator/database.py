"""Universal database connection manager supporting multiple database types."""

import json
from pathlib import Path
from contextlib import contextmanager
from typing import Any, Dict, Iterator, Optional

from .connectors import PostgresConfig, connect_postgres


def load_db_config(config_file: str = "db_config.json") -> Dict[str, Any]:
    """Load database configuration from resources folder.
    
    Args:
        config_file: Name of the config file (default: db_config.json)
        
    Returns:
        Dictionary with database configuration including db_type
    """
    config_path = Path(__file__).parent.parent / "resources" / config_file
    
    with open(config_path, "r") as f:
        config_data = json.load(f)
    
    return config_data


def get_connection(config_file: str = "db_config.json") -> Any:
    """Get a database connection based on config file.
    
    Supports:
        - postgresql/postgres
        - mysql
        - mongodb (future)
        - etc.
    
    Args:
        config_file: Name of the config file
        
    Returns:
        Database connection object
    """
    config = load_db_config(config_file)
    db_type = config.get("db_type", "postgres").lower()
    
    if db_type in ("postgres", "postgresql"):
        return _get_postgres_connection(config)
    elif db_type == "mysql":
        return _get_mysql_connection(config)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


def _get_postgres_connection(config: Dict[str, Any]) -> Any:
    """Create PostgreSQL connection from config dict."""
    pg_config = PostgresConfig(
        host=config["host"],
        port=config.get("port", 5432),
        dbname=config.get("dbname", "postgres"),
        user=config.get("user"),
        password=config.get("password"),
        sslmode=config.get("sslmode", "prefer"),
    )
    return connect_postgres(pg_config)


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
