"""Test database connection before running extraction."""

import sys
import json
from pathlib import Path

# Test configuration loading
try:
    config_path = Path(__file__).parent / "resources" / "db_config.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    print(f"✓ Config loaded: {config_path}")
    print(f"  Host: {config['host']}")
    print(f"  Port: {config['port']}")
    print(f"  Database: {config.get('dbname')}")
    print(f"  User: {config.get('user')}")
except Exception as e:
    print(f"✗ Config loading failed: {e}")
    sys.exit(1)

# Test psycopg2 connection
try:
    import psycopg2
    from migrator.connectors import PostgresConfig, connect_postgres
    
    print("\n✓ Imports successful")
    
    pg_config = PostgresConfig(
        host=config["host"],
        port=config.get("port", 5432),
        dbname=config.get("dbname", "postgres"),
        user=config.get("user"),
        password=config.get("password"),
        sslmode=config.get("sslmode", "prefer"),
    )
    
    print("Testing psycopg2 connection...")
    conn = connect_postgres(pg_config)
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    print(f"✓ psycopg2 connection successful!")
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"✗ PostgreSQL not running: {e}")
    print("\nSolutions:")
    print("1. Start PostgreSQL with Docker:")
    print("   cd docker")
    print("   docker-compose up -d")
    print("2. Or start local PostgreSQL service if installed")
    sys.exit(1)
except Exception as e:
    print(f"✗ Connection failed: {e}")
    sys.exit(1)

# Test SQLAlchemy engine
try:
    from sqlalchemy import create_engine
    
    print("\nTesting SQLAlchemy connection...")
    user = config.get("user", "")
    password = config.get("password", "")
    host = config["host"]
    port = config.get("port", 5432)
    dbname = config.get("dbname", "postgres")
    
    url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    engine = create_engine(url)
    
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print(f"✓ SQLAlchemy connection successful!")
    
    engine.dispose()
    
except Exception as e:
    print(f"✗ SQLAlchemy connection failed: {e}")
    sys.exit(1)

print("\n✓ All tests passed! You can now run the extractor.")
