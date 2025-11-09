"""
Main FastAPI application entry point.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import questions, responses, analytics, crawl
from backend.config.settings import settings
from backend.utils.logger import log


# Initialize FastAPI app
app = FastAPI(
    title="Mulan Marketing Agent API",
    description="API for automated social media marketing with AI agent integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(questions.router, prefix="/api")
app.include_router(responses.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(crawl.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    log.info("Starting Mulan Marketing Agent API")
    log.info(f"Environment: {settings.environment}")
    log.info(f"Auto-post enabled: {settings.auto_post_enabled}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    log.info("Shutting down Mulan Marketing Agent API")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Mulan Marketing Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )

