import pandas as pd 
from sqlalchemy import create_engine, inspect
from migrator import get_db_connection, get_db_connection_direct


class PostgresExtractor:
    """Extract data from PostgreSQL database."""
    
    def __init__(self):
        """Initialize the PostgreSQL extractor."""
        self.conn = None
    
    def connect(self):
        """Open a direct connection (caller responsible for closing)."""
        self.conn = get_db_connection_direct()
    
    def disconnect(self):
        """Close the direct connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def get_cursor(self):
        """Get a cursor from the connection."""
        if not self.conn:
            raise RuntimeError("Connection not established. Call connect() first.")
        return self.conn.cursor()
    
