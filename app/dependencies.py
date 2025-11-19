"""
Dependency injection for FastAPI endpoints
"""
from functools import lru_cache
from typing import Optional

from app.config import settings
from app.storage.base import StorageAdapter
from app.storage.sqlite_adapter import SQLiteAdapter
from app.storage.redis_adapter import RedisAdapter
from app.storage.session_manager import SessionManager
from app.storage.plan_repository import PlanRepository


# Global storage adapter instance
_storage_adapter: Optional[StorageAdapter] = None


def get_storage_adapter() -> StorageAdapter:
    """
    Get the configured storage adapter
    
    Returns SQLite or Redis adapter based on configuration.
    This is cached to ensure we use the same adapter instance.
    """
    global _storage_adapter
    
    if _storage_adapter is None:
        # Determine which storage backend to use
        storage_type = getattr(settings, 'storage_type', 'sqlite').lower()
        
        if storage_type == 'redis':
            redis_url = getattr(settings, 'redis_url', 'redis://localhost:6379')
            _storage_adapter = RedisAdapter(redis_url)
        else:
            # Default to SQLite
            database_path = getattr(settings, 'database_path', './raidesk.db')
            _storage_adapter = SQLiteAdapter(database_path)
    
    return _storage_adapter


@lru_cache()
def get_session_manager() -> SessionManager:
    """
    Get the session manager instance
    
    This is cached to ensure we use the same manager instance.
    """
    storage = get_storage_adapter()
    session_ttl = getattr(settings, 'session_ttl', 86400)  # 24 hours default
    return SessionManager(storage, session_ttl=session_ttl)


@lru_cache()
def get_plan_repository() -> PlanRepository:
    """
    Get the plan repository instance
    
    This is cached to ensure we use the same repository instance.
    """
    storage = get_storage_adapter()
    plan_ttl = getattr(settings, 'plan_ttl', None)  # No expiration by default
    return PlanRepository(storage, plan_ttl=plan_ttl)

