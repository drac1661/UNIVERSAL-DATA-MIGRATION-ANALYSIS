import pandas as pd
from migrator import connection_manager


class PostgresExtractor:
    """Extract data from PostgreSQL database using the central ConnectionManager."""

    def __init__(self):
        self.conn = None

    def connect(self):
        """Open a raw DB-API connection from the central connection manager."""
        # Returns a DB-API connection (psycopg2 connection for Postgres)
        self.conn = connection_manager.get_raw_dbapi_connection()

    def disconnect(self):
        """Close the raw DB-API connection."""
        if self.conn:
            try:
                self.conn.close()
            finally:
                self.conn = None

    def get_cursor(self):
        """Get a cursor from the raw DB-API connection."""
        if not self.conn:
            raise RuntimeError("Connection not established. Call connect() first.")
        return self.conn.cursor()
    
