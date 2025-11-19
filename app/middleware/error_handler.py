"""
Global error handling middleware
"""
import traceback
from typing import Callable
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.exceptions import RAiDeskException
from app.config import settings


async def error_handler_middleware(request: Request, call_next: Callable):
    """
    Global error handling middleware
    Catches and formats all exceptions consistently
    """
    try:
        return await call_next(request)
    except RAiDeskException as exc:
        # Handle custom RAiDesk exceptions
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "type": exc.__class__.__name__,
                "details": exc.details,
                "path": str(request.url.path)
            }
        )
    except ValidationError as exc:
        # Handle Pydantic validation errors
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation error",
                "type": "ValidationError",
                "details": {"errors": errors},
                "path": str(request.url.path)
            }
        )
    except Exception as exc:
        # Handle unexpected errors
        error_detail = str(exc) if settings.debug else "An unexpected error occurred"
        
        # Log the full traceback in debug mode
        if settings.debug:
            traceback.print_exc()
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": error_detail,
                "type": "InternalServerError",
                "details": {},
                "path": str(request.url.path)
            }
        )

