"""
Redis storage adapter for high-performance caching
"""
import json
from typing import Any, Optional, Dict

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from app.storage.base import StorageAdapter
from app.exceptions import StorageException


class RedisAdapter(StorageAdapter):
    """Redis-based storage adapter"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        if not REDIS_AVAILABLE:
            raise StorageException("Redis is not installed. Install with: pip install redis")
        
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None
    
    async def connect(self) -> None:
        """Connect to Redis"""
        try:
            self.client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.client.ping()
        except Exception as e:
            raise StorageException(f"Failed to connect to Redis: {str(e)}")
    
    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            self.client = None
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value by key"""
        if not self.client:
            raise StorageException("Redis not connected")
        
        value = await self.client.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Set a value with optional TTL"""
        if not self.client:
            raise StorageException("Redis not connected")
        
        value_json = json.dumps(value)
        
        if ttl:
            await self.client.setex(key, ttl, value_json)
        else:
            await self.client.set(key, value_json)
    
    async def delete(self, key: str) -> None:
        """Delete a value by key"""
        if not self.client:
            raise StorageException("Redis not connected")
        
        await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists"""
        if not self.client:
            raise StorageException("Redis not connected")
        
        return await self.client.exists(key) > 0
    
    async def list_keys(self, pattern: str = "*") -> list[str]:
        """List all keys matching a pattern"""
        if not self.client:
            raise StorageException("Redis not connected")
        
        keys = []
        async for key in self.client.scan_iter(match=pattern):
            keys.append(key)
        return keys
    
    async def clear_all(self) -> None:
        """Clear all data"""
        if not self.client:
            raise StorageException("Redis not connected")
        
        await self.client.flushdb()

