"""
Session management endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from app.storage.session_manager import SessionManager, Session
from app.exceptions import SessionNotFoundException, StorageException
from app.dependencies import get_session_manager


router = APIRouter()


# Request/Response Models
class CreateSessionRequest(BaseModel):
    """Request to create a new session"""
    data: Optional[Dict[str, Any]] = None


class UpdateSessionRequest(BaseModel):
    """Request to update session data"""
    data: Dict[str, Any]


class SessionResponse(BaseModel):
    """Session response model"""
    id: str
    data: Dict[str, Any]
    created_at: str
    updated_at: str


class SessionListResponse(BaseModel):
    """List of sessions response"""
    sessions: List[SessionResponse]
    count: int


# Endpoints
@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(
    request: CreateSessionRequest,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Create a new session
    
    Sessions are used to track user interactions and store temporary data.
    Each session has a unique ID and can store arbitrary JSON data.
    """
    try:
        session = await session_manager.create_session(initial_data=request.data)
        return SessionResponse(
            id=session.id,
            data=session.data,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat()
        )
    except StorageException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Get a session by ID
    
    Retrieves the current state of a session including all stored data.
    """
    try:
        session = await session_manager.get_session(session_id)
        return SessionResponse(
            id=session.id,
            data=session.data,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat()
        )
    except SessionNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except StorageException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Update session data
    
    Merges the provided data with existing session data.
    Existing keys will be overwritten, new keys will be added.
    """
    try:
        session = await session_manager.update_session(session_id, request.data)
        return SessionResponse(
            id=session.id,
            data=session.data,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat()
        )
    except SessionNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except StorageException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Delete a session
    
    Permanently removes a session and all associated data.
    """
    try:
        await session_manager.delete_session(session_id)
    except SessionNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except StorageException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    List all active sessions
    
    Returns a list of all sessions currently stored in the system.
    """
    try:
        sessions = await session_manager.list_sessions()
        return SessionListResponse(
            sessions=[
                SessionResponse(
                    id=s.id,
                    data=s.data,
                    created_at=s.created_at.isoformat(),
                    updated_at=s.updated_at.isoformat()
                )
                for s in sessions
            ],
            count=len(sessions)
        )
    except StorageException as e:
        raise HTTPException(status_code=500, detail=str(e))

