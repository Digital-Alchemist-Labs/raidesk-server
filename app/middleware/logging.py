"""
Structured logging middleware
"""
import time
import logging
import structlog
from typing import Callable
from fastapi import Request, Response
from uuid import uuid4

from app.config import settings


# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if settings.debug else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()


async def logging_middleware(request: Request, call_next: Callable):
    """
    Structured logging middleware
    
    Logs all requests and responses with timing information
    """
    # Generate request ID
    request_id = str(uuid4())
    
    # Start timer
    start_time = time.time()
    
    # Add request context to logs
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else None,
    )
    
    # Log request
    logger.info(
        "request_started",
        query_params=dict(request.query_params),
        headers={k: v for k, v in request.headers.items() if k.lower() not in ["authorization", "cookie"]},
    )
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            "request_completed",
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        # Calculate duration
        duration = time.time() - start_time
        
        # Log error
        logger.error(
            "request_failed",
            error=str(e),
            error_type=type(e).__name__,
            duration_ms=round(duration * 1000, 2),
        )
        
        # Re-raise to let error handler middleware handle it
        raise


def get_logger():
    """Get the configured logger instance"""
    return logger

