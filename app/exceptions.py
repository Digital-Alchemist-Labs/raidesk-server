"""
Custom exception classes for RAiDesk API
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class RAiDeskException(Exception):
    """Base exception for RAiDesk errors"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class SessionNotFoundException(RAiDeskException):
    """Raised when a session is not found"""
    
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session not found: {session_id}",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"session_id": session_id}
        )


class PlanNotFoundException(RAiDeskException):
    """Raised when a plan is not found"""
    
    def __init__(self, plan_id: str):
        super().__init__(
            message=f"Plan not found: {plan_id}",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"plan_id": plan_id}
        )


class StorageException(RAiDeskException):
    """Raised when storage operations fail"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Storage error: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ValidationException(RAiDeskException):
    """Raised when validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class RateLimitExceededException(RAiDeskException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


class AIServiceException(RAiDeskException):
    """Raised when AI service (Ollama) fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"AI service error: {message}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )

