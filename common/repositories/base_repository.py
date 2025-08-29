"""Base repository for database operations."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any

T = TypeVar('T')


class BaseRepository(Generic[T], ABC):
    """Base repository interface for CRUD operations."""
    
    @abstractmethod
    def find_by_id(self, entity_id: Any) -> Optional[T]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def get_all(self, **filters) -> List[T]:
        """Get all entities with optional filters."""
        pass
    
    @abstractmethod
    def delete(self, entity_id: Any) -> bool:
        """Delete entity by ID."""
        pass
    
    @abstractmethod
    def update(self, entity_id: Any, entity: T) -> Optional[T]:
        """Update entity by ID."""
        pass 