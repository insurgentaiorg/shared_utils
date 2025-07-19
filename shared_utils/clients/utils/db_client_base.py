from os import getenv
from abc import ABC, abstractmethod
from typing import Any, ContextManager

class DBClientBase(ABC):
    """Abstract base class for database clients."""
    def __init__(self):
        self.user = getenv("POSTGRES_USER", "postgres")
        self.password = getenv("POSTGRES_PASSWORD", "password")
        self.host = getenv("POSTGRES_HOST", "localhost")
        self.port = getenv("POSTGRES_PORT", "5432")
        self.dbname = getenv("POSTGRES_DB", "kg_db")

        if not self.user:
            raise EnvironmentError("POSTGRES_USER environment variable is not set")
        if not self.password:
            raise EnvironmentError("POSTGRES_PASSWORD environment variable is not set")
        if not self.host:
            raise EnvironmentError("POSTGRES_HOST environment variable is not set")
        if not self.port:
            raise EnvironmentError("POSTGRES_PORT environment variable is not set")
        if not self.dbname:
            raise EnvironmentError("POSTGRES_DB environment variable is not set")

        # psycopg connection parameters
        self.connection_params = {
            "host": self.host,
            "port": self.port,
            "dbname": self.dbname,
            "user": self.user,
            "password": self.password
        }

    @abstractmethod
    def scoped_session(self) -> ContextManager[Any]:
        """Context manager for scoped database operations with auto commit/rollback/close."""

    @abstractmethod
    def get_persistent_session(self) -> Any:
        """Get a persistent session/connection that caller must manage."""
