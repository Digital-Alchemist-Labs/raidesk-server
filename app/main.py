"""
RAiDesk Backend Server - Main Application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import classify, purpose, standards, refine, sessions, plans, stream
from app.middleware.error_handler import error_handler_middleware
from app.middleware.logging import logging_middleware
from app.middleware.rate_limiter import setup_rate_limiting
from app.dependencies import get_storage_adapter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    
    Handles startup and shutdown events for the application,
    including database connections and cleanup.
    """
    # Startup
    storage = get_storage_adapter()
    await storage.connect()
    print(f"✓ Storage connected: {storage.__class__.__name__}")
    
    yield
    
    # Shutdown
    await storage.disconnect()
    print("✓ Storage disconnected")


# Create FastAPI app
app = FastAPI(
    title="RAiDesk API",
    description="AI-powered medical device regulatory assistant backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup rate limiting
limiter = setup_rate_limiting(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.middleware("http")(logging_middleware)
app.middleware("http")(error_handler_middleware)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "name": "RAiDesk API",
        "version": "1.0.0",
        "status": "operational",
        "ollama_url": settings.ollama_base_url,
        "ollama_model": settings.ollama_model,
        "storage_type": settings.storage_type
    }


@app.get("/health")
async def health():
    """
    Health check endpoint
    
    Returns the health status of the API and its dependencies.
    """
    storage = get_storage_adapter()
    storage_healthy = False
    
    try:
        # Check storage connection
        if hasattr(storage, 'db') and storage.db:
            storage_healthy = True
        elif hasattr(storage, 'client') and storage.client:
            storage_healthy = True
    except Exception:
        pass
    
    return {
        "status": "healthy",
        "storage": "connected" if storage_healthy else "disconnected",
        "storage_type": settings.storage_type
    }


# Include routers
app.include_router(classify.router, prefix="/api", tags=["Classification"])
app.include_router(purpose.router, prefix="/api", tags=["Purpose & Mechanism"])
app.include_router(standards.router, prefix="/api", tags=["Regulatory Plans"])
app.include_router(refine.router, prefix="/api", tags=["Plan Refinement"])
app.include_router(sessions.router, prefix="/api", tags=["Sessions"])
app.include_router(plans.router, prefix="/api", tags=["Plans"])
app.include_router(stream.router, prefix="/api", tags=["Streaming"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )

