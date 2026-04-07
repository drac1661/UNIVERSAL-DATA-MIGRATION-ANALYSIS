"""Singleton connection manager for the migrator package.

Provides a central SQLAlchemy engine and helpers to get connections
so other modules can reuse the same engine/connection without
recreating it.

Usage:
    from migrator import connection_manager

    # configure (optional, uses resources/db_config.json by default)
    connection_manager.configure("db_config.json")

    # get SQLAlchemy engine
    engine = connection_manager.get_engine()

    # use context manager
    with connection_manager.connection() as conn:
        result = conn.execute("SELECT 1")

    # get raw DB-API connection (cursor() support)
    raw = connection_manager.get_raw_dbapi_connection()
    cur = raw.cursor()
    cur.execute("SELECT 1")
    raw.close()
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Any, Optional
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, Connection

from .database import load_db_config


class ConnectionManager:
    def __init__(self, config_file: str = "db_config.json", echo: bool = False):
        self.config_file = config_file
        self._engine: Optional[Engine] = None
        self._local = threading.local()
        self.echo = echo
        self._config = None
        # load initial config
        self.configure(config_file)

    def configure(self, config_file: str) -> None:
        """Load (or reload) configuration from a config file under `resources/`.

        Disposes existing engine if it was already created so the new
        configuration will be used when next requesting the engine.
        """
        self.config_file = config_file
        self._config = load_db_config(config_file)
        if self._engine is not None:
            try:
                self._engine.dispose()
            finally:
                self._engine = None

    def _build_url(self) -> str:
        cfg = self._config or {}
        db_type = (cfg.get("db_type") or "postgres").lower()

        if db_type in ("postgres", "postgresql"):
            user = cfg.get("user", "")
            password = cfg.get("password", "")
            host = cfg.get("host", "127.0.0.1")
            port = cfg.get("port", 5432)
            dbname = cfg.get("dbname", "postgres")

            if user:
                return (
                    "postgresql+psycopg2://"
                    f"{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{quote_plus(str(dbname))}"
                )
            else:
                return f"postgresql+psycopg2://{host}:{port}/{quote_plus(str(dbname))}"

        if db_type == "mysql":
            user = cfg.get("user", "")
            password = cfg.get("password", "")
            host = cfg.get("host", "127.0.0.1")
            port = cfg.get("port", 3306)
            database = cfg.get("database", cfg.get("dbname", ""))
            return (
                "mysql+pymysql://"
                f"{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{quote_plus(str(database))}"
            )

        raise ValueError(f"Unsupported database type: {db_type}")

    def get_engine(self) -> Engine:
        if self._engine is None:
            url = self._build_url()
            self._engine = create_engine(url, echo=self.echo, pool_pre_ping=True)
        return self._engine

    @contextmanager
    def connection(self) -> Connection:
        """Context manager yielding a SQLAlchemy Connection object."""
        try:
            eng = self.get_engine()
            with eng.begin() as conn:  # .begin() starts a transaction automatically
                yield conn
        finally:
            conn.close()

    def get_raw_dbapi_connection(self):
        """Return a raw DB-API connection from the engine's pool.

        Caller is responsible for closing it with `.close()`.
        """
        eng = self.get_engine()
        return eng.raw_connection()

    def dispose(self) -> None:
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None


# Module-level singleton
connection_manager = ConnectionManager()


# Convenience wrappers
def get_engine() -> Engine:
    return connection_manager.get_engine()


@contextmanager
def connection() -> Connection:
    """Convenience context manager that yields a SQLAlchemy Connection.

    Wraps the singleton's connection() and adds a clearer error message
    if obtaining the connection fails.
    """
    try:
        with connection_manager.connection() as conn:
            yield conn
    except Exception as e:
        raise RuntimeError(
            "Failed to obtain database connection. Check database availability and migrator configuration."
        ) from e


def get_raw_dbapi_connection():
    return connection_manager.get_raw_dbapi_connection()


def configure(config_file: str) -> None:
    connection_manager.configure(config_file)


def test_connection(timeout: Optional[float] = None) -> bool:
    """Quickly test connectivity by running a lightweight query.

    Args:
        timeout: Optional timeout in seconds (not all DBAPIs honour this).

    Returns:
        True if successful, False otherwise.
    """
    try:
        from sqlalchemy import text
        with connection() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def dispose() -> None:
    connection_manager.dispose()
