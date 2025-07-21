from abc import ABC, abstractmethod
from typing import Any, ContextManager
from .postgres_client import PostgresClient

class AGEClientBase(ABC):
    """Abstract base class for apache age enabeld database clients."""
    def __init__(self):
        self._postgres_client = PostgresClient()

    @abstractmethod
    def managed_connection(self) -> ContextManager[Any]:
        """context-managed connection with auto commit/rollback/close."""
        pass

    @abstractmethod
    def create_connection(self) -> Any:
        """Caller is responsible for commit/rollback/close."""
        pass
