"""
Plan storage and versioning for RAiDesk API
"""
import uuid
from typing import Any, Dict, Optional, List
from datetime import datetime

from app.storage.base import StorageAdapter
from app.models import Plan
from app.exceptions import PlanNotFoundException, StorageException


class PlanVersion:
    """Plan version model for tracking refinements"""
    
    def __init__(
        self,
        version: int,
        plan_data: Dict[str, Any],
        modifications: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        self.version = version
        self.plan_data = plan_data
        self.modifications = modifications
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "version": self.version,
            "plan_data": self.plan_data,
            "modifications": self.modifications,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanVersion":
        """Create from dictionary"""
        return cls(
            version=data["version"],
            plan_data=data["plan_data"],
            modifications=data.get("modifications"),
            created_at=datetime.fromisoformat(data["created_at"])
        )


class PlanRecord:
    """Plan record with versioning"""
    
    def __init__(
        self,
        plan_id: str,
        session_id: Optional[str] = None,
        current_version: int = 1,
        versions: Optional[List[PlanVersion]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = plan_id
        self.session_id = session_id
        self.current_version = current_version
        self.versions = versions or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "current_version": self.current_version,
            "versions": [v.to_dict() for v in self.versions],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanRecord":
        """Create from dictionary"""
        return cls(
            plan_id=data["id"],
            session_id=data.get("session_id"),
            current_version=data["current_version"],
            versions=[PlanVersion.from_dict(v) for v in data["versions"]],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
    
    def get_current_plan(self) -> Dict[str, Any]:
        """Get the current version's plan data"""
        if not self.versions:
            raise ValueError("No versions available")
        
        current = next(
            (v for v in self.versions if v.version == self.current_version),
            None
        )
        
        if not current:
            # Fallback to latest version
            current = self.versions[-1]
        
        return current.plan_data
    
    def get_version(self, version: int) -> Optional[PlanVersion]:
        """Get a specific version"""
        return next((v for v in self.versions if v.version == version), None)


class PlanRepository:
    """Repository for storing and managing plans"""
    
    def __init__(self, storage: StorageAdapter, plan_ttl: Optional[int] = None):
        """
        Initialize plan repository
        
        Args:
            storage: Storage adapter to use
            plan_ttl: Plan time-to-live in seconds (None = no expiration)
        """
        self.storage = storage
        self.plan_ttl = plan_ttl
        self._key_prefix = "plan:"
    
    def _make_key(self, plan_id: str) -> str:
        """Create storage key for plan"""
        return f"{self._key_prefix}{plan_id}"
    
    async def save_plan(
        self,
        plan: Plan,
        session_id: Optional[str] = None,
        modifications: Optional[str] = None
    ) -> PlanRecord:
        """
        Save a new plan or create a new version
        
        Args:
            plan: Plan object to save
            session_id: Optional session ID to associate with
            modifications: Optional description of modifications (for versioning)
            
        Returns:
            PlanRecord with version information
        """
        # Check if plan already exists
        plan_id = plan.id
        existing_record = None
        
        try:
            existing_data = await self.storage.get(self._make_key(plan_id))
            if existing_data:
                existing_record = PlanRecord.from_dict(existing_data)
        except Exception:
            pass
        
        # Convert plan to dict
        plan_data = plan.model_dump(by_alias=True)
        
        if existing_record:
            # Add new version
            new_version = existing_record.current_version + 1
            version = PlanVersion(
                version=new_version,
                plan_data=plan_data,
                modifications=modifications
            )
            existing_record.versions.append(version)
            existing_record.current_version = new_version
            existing_record.updated_at = datetime.utcnow()
            record = existing_record
        else:
            # Create new record
            version = PlanVersion(
                version=1,
                plan_data=plan_data,
                modifications=modifications
            )
            record = PlanRecord(
                plan_id=plan_id,
                session_id=session_id,
                current_version=1,
                versions=[version]
            )
        
        # Save to storage
        try:
            await self.storage.set(
                self._make_key(plan_id),
                record.to_dict(),
                ttl=self.plan_ttl
            )
            return record
        except Exception as e:
            raise StorageException(f"Failed to save plan: {str(e)}")
    
    async def get_plan(self, plan_id: str, version: Optional[int] = None) -> Plan:
        """
        Get a plan by ID
        
        Args:
            plan_id: Plan ID
            version: Optional specific version (defaults to current)
            
        Returns:
            Plan object
            
        Raises:
            PlanNotFoundException: If plan doesn't exist
        """
        key = self._make_key(plan_id)
        
        try:
            data = await self.storage.get(key)
            if not data:
                raise PlanNotFoundException(plan_id)
            
            record = PlanRecord.from_dict(data)
            
            if version is not None:
                plan_version = record.get_version(version)
                if not plan_version:
                    raise PlanNotFoundException(f"{plan_id} (version {version})")
                plan_data = plan_version.plan_data
            else:
                plan_data = record.get_current_plan()
            
            return Plan(**plan_data)
        except PlanNotFoundException:
            raise
        except Exception as e:
            raise StorageException(f"Failed to get plan: {str(e)}")
    
    async def get_plan_record(self, plan_id: str) -> PlanRecord:
        """
        Get full plan record with all versions
        
        Args:
            plan_id: Plan ID
            
        Returns:
            PlanRecord object
            
        Raises:
            PlanNotFoundException: If plan doesn't exist
        """
        key = self._make_key(plan_id)
        
        try:
            data = await self.storage.get(key)
            if not data:
                raise PlanNotFoundException(plan_id)
            
            return PlanRecord.from_dict(data)
        except PlanNotFoundException:
            raise
        except Exception as e:
            raise StorageException(f"Failed to get plan record: {str(e)}")
    
    async def delete_plan(self, plan_id: str) -> None:
        """
        Delete a plan
        
        Args:
            plan_id: Plan ID
            
        Raises:
            PlanNotFoundException: If plan doesn't exist
        """
        # Verify plan exists
        await self.get_plan(plan_id)
        
        try:
            await self.storage.delete(self._make_key(plan_id))
        except Exception as e:
            raise StorageException(f"Failed to delete plan: {str(e)}")
    
    async def list_plans(self, session_id: Optional[str] = None) -> List[PlanRecord]:
        """
        List all plans, optionally filtered by session
        
        Args:
            session_id: Optional session ID to filter by
            
        Returns:
            List of plan records
        """
        try:
            keys = await self.storage.list_keys(f"{self._key_prefix}*")
            records = []
            
            for key in keys:
                try:
                    data = await self.storage.get(key)
                    if data:
                        record = PlanRecord.from_dict(data)
                        if session_id is None or record.session_id == session_id:
                            records.append(record)
                except Exception:
                    # Skip invalid records
                    continue
            
            return records
        except Exception as e:
            raise StorageException(f"Failed to list plans: {str(e)}")
    
    async def plan_exists(self, plan_id: str) -> bool:
        """
        Check if a plan exists
        
        Args:
            plan_id: Plan ID
            
        Returns:
            True if plan exists, False otherwise
        """
        try:
            return await self.storage.exists(self._make_key(plan_id))
        except Exception as e:
            raise StorageException(f"Failed to check plan existence: {str(e)}")

