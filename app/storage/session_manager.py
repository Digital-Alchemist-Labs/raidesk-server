"""
Session management for RAiDesk API
"""
import uuid
from typing import Any, Dict, Optional, List
from datetime import datetime

from app.storage.base import StorageAdapter
from app.exceptions import SessionNotFoundException, StorageException


class Session:
    """Session model"""
    
    def __init__(
        self,
        session_id: str,
        data: Dict[str, Any],
        created_at: datetime,
        updated_at: datetime
    ):
        self.id = session_id
        self.data = data
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "id": self.id,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create session from dictionary"""
        return cls(
            session_id=data["id"],
            data=data["data"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )


class SessionManager:
    """Manage user sessions"""
    
    def __init__(self, storage: StorageAdapter, session_ttl: int = 86400):
        """
        Initialize session manager
        
        Args:
            storage: Storage adapter to use
            session_ttl: Session time-to-live in seconds (default: 24 hours)
        """
        self.storage = storage
        self.session_ttl = session_ttl
        self._key_prefix = "session:"
    
    def _make_key(self, session_id: str) -> str:
        """Create storage key for session"""
        return f"{self._key_prefix}{session_id}"
    
    async def create_session(self, initial_data: Optional[Dict[str, Any]] = None) -> Session:
        """
        Create a new session
        
        Args:
            initial_data: Optional initial session data
            
        Returns:
            Created session
        """
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        session = Session(
            session_id=session_id,
            data=initial_data or {},
            created_at=now,
            updated_at=now
        )
        
        try:
            await self.storage.set(
                self._make_key(session_id),
                session.to_dict(),
                ttl=self.session_ttl
            )
            return session
        except Exception as e:
            raise StorageException(f"Failed to create session: {str(e)}")
    
    async def get_session(self, session_id: str) -> Session:
        """
        Get a session by ID
        
        Args:
            session_id: Session ID
            
        Returns:
            Session object
            
        Raises:
            SessionNotFoundException: If session doesn't exist
        """
        key = self._make_key(session_id)
        
        try:
            data = await self.storage.get(key)
            if not data:
                raise SessionNotFoundException(session_id)
            
            return Session.from_dict(data)
        except SessionNotFoundException:
            raise
        except Exception as e:
            raise StorageException(f"Failed to get session: {str(e)}")
    
    async def update_session(self, session_id: str, data: Dict[str, Any]) -> Session:
        """
        Update session data
        
        Args:
            session_id: Session ID
            data: New data to merge into session
            
        Returns:
            Updated session
            
        Raises:
            SessionNotFoundException: If session doesn't exist
        """
        # Get existing session
        session = await self.get_session(session_id)
        
        # Merge data
        session.data.update(data)
        session.updated_at = datetime.utcnow()
        
        # Save updated session
        try:
            await self.storage.set(
                self._make_key(session_id),
                session.to_dict(),
                ttl=self.session_ttl
            )
            return session
        except Exception as e:
            raise StorageException(f"Failed to update session: {str(e)}")
    
    async def delete_session(self, session_id: str) -> None:
        """
        Delete a session
        
        Args:
            session_id: Session ID
            
        Raises:
            SessionNotFoundException: If session doesn't exist
        """
        # Verify session exists
        await self.get_session(session_id)
        
        try:
            await self.storage.delete(self._make_key(session_id))
        except Exception as e:
            raise StorageException(f"Failed to delete session: {str(e)}")
    
    async def list_sessions(self) -> List[Session]:
        """
        List all active sessions
        
        Returns:
            List of sessions
        """
        try:
            keys = await self.storage.list_keys(f"{self._key_prefix}*")
            sessions = []
            
            for key in keys:
                try:
                    data = await self.storage.get(key)
                    if data:
                        sessions.append(Session.from_dict(data))
                except Exception:
                    # Skip invalid sessions
                    continue
            
            return sessions
        except Exception as e:
            raise StorageException(f"Failed to list sessions: {str(e)}")
    
    async def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists
        
        Args:
            session_id: Session ID
            
        Returns:
            True if session exists, False otherwise
        """
        try:
            return await self.storage.exists(self._make_key(session_id))
        except Exception as e:
            raise StorageException(f"Failed to check session existence: {str(e)}")

