"""
Base storage adapter interface
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from datetime import datetime


class StorageAdapter(ABC):
    """Base class for storage adapters"""
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the storage backend"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the storage backend"""
        pass
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value by key"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Set a value with optional TTL (time to live in seconds)"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a value by key"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists"""
        pass
    
    @abstractmethod
    async def list_keys(self, pattern: str = "*") -> list[str]:
        """List all keys matching a pattern"""
        pass
    
    @abstractmethod
    async def clear_all(self) -> None:
        """Clear all data (use with caution!)"""
        pass

