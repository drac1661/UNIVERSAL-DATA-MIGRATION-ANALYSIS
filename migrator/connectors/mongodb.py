from dataclasses import dataclass
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database


@dataclass(frozen=True)
class MongoDBConfig:
    host: str
    port: int = 27017
    dbname: str = "test"
    user: Optional[str] = None
    password: Optional[str] = None
    auth_source: str = "admin"
    ssl: bool = False
    replica_set: Optional[str] = None

    def connection_string(self) -> str:
        return build_mongodb_connection_string(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            auth_source=self.auth_source,
            ssl=self.ssl,
            replica_set=self.replica_set,
        )


def build_mongodb_connection_string(
    host: str,
    port: int = 27017,
    user: Optional[str] = None,
    password: Optional[str] = None,
    auth_source: str = "admin",
    ssl: bool = False,
    replica_set: Optional[str] = None,
) -> str:
    """Build a MongoDB connection string.
    
    Args:
        host: MongoDB host
        port: MongoDB port
        user: Username (optional)
        password: Password (optional)
        auth_source: Database to authenticate against
        ssl: Whether to use SSL
        replica_set: Replica set name (optional)
    
    Returns:
        MongoDB connection string
    """
    if user and password:
        from urllib.parse import quote_plus
        user_pass = f"{quote_plus(user)}:{quote_plus(password)}@"
    else:
        user_pass = ""
    
    schema = "mongodb+srv" if "," in host or replica_set else "mongodb"
    connection_str = f"{schema}://{user_pass}{host}:{port}"
    
    params = []
    if user and password:
        params.append(f"authSource={auth_source}")
    if ssl:
        params.append("ssl=true")
    if replica_set:
        params.append(f"replicaSet={replica_set}")
    
    if params:
        connection_str += "?" + "&".join(params)
    
    return connection_str


def connect_mongodb(config: MongoDBConfig) -> MongoClient:
    """Open a MongoDB connection using the given config."""
    connection_string = config.connection_string()
    return MongoClient(connection_string)


def connect_mongodb_params(
    host: str,
    port: int = 27017,
    dbname: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    auth_source: str = "admin",
    ssl: bool = False,
    replica_set: Optional[str] = None,
) -> MongoClient:
    """Open a MongoDB connection from explicit connection parameters."""
    connection_string = build_mongodb_connection_string(
        host=host,
        port=port,
        user=user,
        password=password,
        auth_source=auth_source,
        ssl=ssl,
        replica_set=replica_set,
    )
    return MongoClient(connection_string)


def get_database(client: MongoClient, dbname: str) -> Database:
    """Get a MongoDB database from a client."""
    return client[dbname]


__all__ = [
    "MongoDBConfig",
    "build_mongodb_connection_string",
    "connect_mongodb",
    "connect_mongodb_params",
    "get_database",
]
