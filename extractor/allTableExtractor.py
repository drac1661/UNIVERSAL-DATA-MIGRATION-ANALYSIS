"""Universal table extractor using SQLAlchemy for multiple database types."""

from typing import List, Dict, Any, Optional
from sqlalchemy import inspect
from sqlalchemy.engine import Inspector,create_engine
from migrator import load_db_config, connection_manager


class AllTableExtractor:
    """Extract table information from any database supported by SQLAlchemy."""
    
    def __init__(self, config_file: str = "db_config.json"):
        """Initialize the table extractor.
        
        Args:
            config_file: Name of the database config file
        """
        self.config = load_db_config(config_file)
        self.db_type = self.config.get("db_type", "postgres").lower()

        # configure the global connection manager to use this config file
        connection_manager.configure(config_file)
        # reuse engine from connection manager
        self.engine = connection_manager.get_engine()
        self.inspector = inspect(self.engine)
    
    def _create_engine_from_config(self):
        """Create SQLAlchemy engine from existing config using connector modules.
        
        Returns:
            SQLAlchemy Engine object
        """
        if self.db_type in ("postgres", "postgresql"):
            # Use existing PostgresConfig and build_postgres_dsn
            from urllib.parse import quote
            
            user = self.config.get("user", "")
            password = self.config.get("password", "")
            host = self.config.get("host", "127.0.0.1")
            port = self.config.get("port", 5432)
            dbname = self.config.get("dbname", "postgres")
            
            # URL encode credentials to handle special characters
            if user and password:
                url = f"postgresql://{quote(user, safe='')}:{quote(password, safe='')}@{host}:{port}/{quote(dbname, safe='')}"
            else:
                url = f"postgresql://{host}:{port}/{quote(dbname, safe='')}"
            
            return create_engine(url)
        
        elif self.db_type == "mysql":
            # MySQL using existing connector module pattern
            from urllib.parse import quote
            
            user = self.config.get("user", "")
            password = self.config.get("password", "")
            host = self.config.get("host", "localhost")
            port = self.config.get("port", 3306)
            database = self.config.get("database", self.config.get("dbname", ""))
            
            if user and password:
                url = f"mysql+pymysql://{quote(user, safe='')}:{quote(password, safe='')}@{host}:{port}/{quote(database, safe='')}"
            else:
                url = f"mysql+pymysql://{host}:{port}/{quote(database, safe='')}"
            
            return create_engine(url)
        
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def get_all_tables(self) -> List[str]:
        """Get all table names in the database.
        
        Returns:
            List of table names
        """
        return self.inspector.get_table_names()
    
    def get_all_tables_with_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get all tables with their complete information.
        
        Returns tables as a dictionary keyed by schema.table format.
        Automatically filters out system schemas.
        
        Returns:
            Dictionary with 'schema.table' as keys and table info as values
        """
        all_tables = {}
        
        # System schemas to exclude
        system_schemas = {'information_schema', 'pg_catalog', 'pg_toast'}
        
        try:
            # Get schemas
            schemas = self.inspector.get_schema_names()
            
            if not schemas:
                print("Warning: No schemas found. Using 'public' as fallback.")
                schemas = ['public']
            
            for schema in schemas:
                # Skip system schemas
                if schema in system_schemas:
                    continue
                
                try:
                    tables = self.inspector.get_table_names(schema=schema)
                    for table in tables:
                        table_key = f"{schema}.{table}"
                        all_tables[table_key] = {
                            "schema": schema,
                            "table": table,
                            "columns": self.get_table_columns(table, schema),
                            "primary_keys": self.get_table_primary_keys(table, schema),
                            "foreign_keys": self.get_table_foreign_keys(table, schema),
                        }
                except Exception as e:
                    print(f"Warning: Could not inspect schema '{schema}': {e}")
                    continue
        
        except Exception as e:
            print(f"Error getting schemas: {e}")
            print("Falling back to public schema only...")
            try:
                tables = self.inspector.get_table_names(schema='public')
                for table in tables:
                    all_tables[table] = {
                        "schema": "public",
                        "table": table,
                        "columns": self.get_table_columns(table, 'public'),
                        "primary_keys": self.get_table_primary_keys(table, 'public'),
                        "foreign_keys": self.get_table_foreign_keys(table, 'public'),
                    }
            except Exception as fallback_error:
                print(f"Fallback also failed: {fallback_error}")
        
        return all_tables
    
    def get_all_user_schemas(self) -> List[str]:
        """Get all user-defined schemas (excludes system schemas).
        
        Returns:
            List of non-system schema names
        """
        system_schemas = {'information_schema', 'pg_catalog', 'pg_toast'}
        
        try:
            schemas = self.inspector.get_schema_names()
            return [s for s in schemas if s not in system_schemas]
        except Exception as e: 
            print(f"Error getting schemas: {e}")
            return ['public']  # Fallback to public
    
    def get_table_columns(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get column information for a specific table.
        
        Args:
            table_name: Name of the table
            schema: Schema name (optional)
            
        Returns:
            List of dicts with column information
        """
        columns = self.inspector.get_columns(table_name, schema=schema)
        return columns
    
    def get_table_columns_info(self, table_name: str, schema: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Get detailed column information keyed by column name.
        
        Args:
            table_name: Name of the table
            schema: Schema name (optional)
            
        Returns:
            Dictionary with column names as keys and column info as values
        """
        columns = self.get_table_columns(table_name, schema)
        return {col["name"]: col for col in columns}
    
    def get_table_primary_keys(self, table_name: str, schema: Optional[str] = None) -> List[str]:
        """Get primary key columns for a table.
        
        Args:
            table_name: Name of the table
            schema: Schema name (optional)
            
        Returns:
            List of primary key column names
        """
        pk = self.inspector.get_pk_constraint(table_name, schema=schema)
        return pk.get("constrained_columns", [])
    
    def get_table_foreign_keys(self, table_name: str, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get foreign key information for a table.
        
        Args:
            table_name: Name of the table
            schema: Schema name (optional)
            
        Returns:
            List of foreign key constraint dicts
        """
        return self.inspector.get_foreign_keys(table_name, schema=schema)
    
    def get_all_tables_info(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive information for all tables.
        
        Returns:
            Dictionary with table names as keys and their info as values
        """
        tables_info = {}
        
        for table_name in self.get_all_tables():
            tables_info[table_name] = {
                "columns": self.get_table_columns(table_name),
                "primary_keys": self.get_table_primary_keys(table_name),
                "foreign_keys": self.get_table_foreign_keys(table_name),
            }
        
        return tables_info
    
    def close(self):
        """Close the database connection."""
        self.engine.dispose()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Example usage
if __name__ == "__main__":
    # Using context manager
    with AllTableExtractor() as extractor:
        print("All tables:")
        tables = extractor.get_all_tables()
        for table in tables:
            print(f"  - {table}")
        
        print("\nTables with schemas:")
        tables_with_schemas = extractor.get_all_tables_with_schemas()
        for item in tables_with_schemas:
            print(f"  - {item['schema']}.{item['table']}")
        
        if tables:
            first_table = tables[0]
            print(f"\nColumns in '{first_table}':")
            columns = extractor.get_table_columns(first_table)
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
