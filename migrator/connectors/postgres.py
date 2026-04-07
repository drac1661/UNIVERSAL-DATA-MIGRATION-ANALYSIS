from dataclasses import dataclass
from typing import Optional

import psycopg2
from psycopg2.extensions import connection as Psycopg2Connection


@dataclass(frozen=True)
class PostgresConfig:
    host: str
    port: int = 5432
    dbname: str = "postgres"
    user: Optional[str] = None
    password: Optional[str] = None
    sslmode: str = "prefer"

    def dsn(self) -> str:
        return build_postgres_dsn(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            sslmode=self.sslmode,
        )


def build_postgres_dsn(
    host: str,
    port: int = 5432,
    dbname: str = "postgres",
    user: Optional[str] = None,
    password: Optional[str] = None,
    sslmode: str = "prefer",
) -> str:
    """Build a PostgreSQL DSN for any host."""
    parts = [f"host={host}", f"port={port}", f"dbname={dbname}", f"sslmode={sslmode}"]

    if user:
        parts.append(f"user={user}")
    if password:
        parts.append(f"password={password}")

    return " ".join(parts)


def connect_postgres(config: PostgresConfig) -> Psycopg2Connection:
    """Open a PostgreSQL connection using the given config."""
    dsn = config.dsn()
    return psycopg2.connect(dsn)


def connect_postgres_params(
    host: str,
    port: int = 5432,
    dbname: str = "postgres",
    user: Optional[str] = None,
    password: Optional[str] = None,
    sslmode: str = "prefer",
) -> Psycopg2Connection:
    """Open a PostgreSQL connection from explicit connection parameters."""
    return psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        sslmode=sslmode,
    )


__all__ = ["PostgresConfig", "build_postgres_dsn", "connect_postgres", "connect_postgres_params"]
