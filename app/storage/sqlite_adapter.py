"""
SQLite storage adapter for persistent storage
"""
import json
import aiosqlite
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from pathlib import Path

from app.storage.base import StorageAdapter
from app.exceptions import StorageException


class SQLiteAdapter(StorageAdapter):
    """SQLite-based storage adapter"""
    
    def __init__(self, database_path: str = "./raidesk.db"):
        self.database_path = database_path
        self.db: Optional[aiosqlite.Connection] = None
    
    async def connect(self) -> None:
        """Connect to SQLite database"""
        try:
            # Ensure directory exists
            db_path = Path(self.database_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.db = await aiosqlite.connect(self.database_path)
            await self._initialize_schema()
        except Exception as e:
            raise StorageException(f"Failed to connect to SQLite: {str(e)}")
    
    async def disconnect(self) -> None:
        """Disconnect from SQLite database"""
        if self.db:
            await self.db.close()
            self.db = None
    
    async def _initialize_schema(self) -> None:
        """Initialize database schema"""
        if not self.db:
            raise StorageException("Database not connected")
        
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS storage (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index on expires_at for efficient cleanup
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_expires_at 
            ON storage(expires_at)
        """)
        
        await self.db.commit()
    
    async def _cleanup_expired(self) -> None:
        """Remove expired entries"""
        if not self.db:
            return
        
        await self.db.execute("""
            DELETE FROM storage 
            WHERE expires_at IS NOT NULL AND expires_at < ?
        """, (datetime.utcnow(),))
        await self.db.commit()
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value by key"""
        if not self.db:
            raise StorageException("Database not connected")
        
        await self._cleanup_expired()
        
        cursor = await self.db.execute("""
            SELECT value FROM storage 
            WHERE key = ? AND (expires_at IS NULL OR expires_at > ?)
        """, (key, datetime.utcnow()))
        
        row = await cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None
    
    async def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Set a value with optional TTL"""
        if not self.db:
            raise StorageException("Database not connected")
        
        expires_at = None
        if ttl:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        value_json = json.dumps(value)
        
        await self.db.execute("""
            INSERT INTO storage (key, value, expires_at, updated_at) 
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET 
                value = excluded.value,
                expires_at = excluded.expires_at,
                updated_at = excluded.updated_at
        """, (key, value_json, expires_at, datetime.utcnow()))
        
        await self.db.commit()
    
    async def delete(self, key: str) -> None:
        """Delete a value by key"""
        if not self.db:
            raise StorageException("Database not connected")
        
        await self.db.execute("DELETE FROM storage WHERE key = ?", (key,))
        await self.db.commit()
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists"""
        if not self.db:
            raise StorageException("Database not connected")
        
        await self._cleanup_expired()
        
        cursor = await self.db.execute("""
            SELECT 1 FROM storage 
            WHERE key = ? AND (expires_at IS NULL OR expires_at > ?)
        """, (key, datetime.utcnow()))
        
        row = await cursor.fetchone()
        return row is not None
    
    async def list_keys(self, pattern: str = "*") -> list[str]:
        """List all keys matching a pattern"""
        if not self.db:
            raise StorageException("Database not connected")
        
        await self._cleanup_expired()
        
        # Convert glob pattern to SQL LIKE pattern
        sql_pattern = pattern.replace("*", "%").replace("?", "_")
        
        cursor = await self.db.execute("""
            SELECT key FROM storage 
            WHERE key LIKE ? AND (expires_at IS NULL OR expires_at > ?)
        """, (sql_pattern, datetime.utcnow()))
        
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
    
    async def clear_all(self) -> None:
        """Clear all data"""
        if not self.db:
            raise StorageException("Database not connected")
        
        await self.db.execute("DELETE FROM storage")
        await self.db.commit()

