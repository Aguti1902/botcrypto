"""NexiTrade - Autonomous Crypto Trading System with AI/ML/RL.

Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger
import uvicorn

from config.settings import settings
from utils.logging import setup_logging
from api import status_router, orders_router, strategies_router, portfolio_router, config_router
from db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for FastAPI app."""
    # Startup
    logger.info("🚀 Starting NexiTrade...")
    setup_logging(log_level=settings.log_level)
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    # TODO: Initialize trading engine based on mode
    logger.info(f"📊 Mode: {settings.environment}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down NexiTrade...")


app = FastAPI(
    title="NexiTrade API",
    description="Autonomous Crypto Trading System with AI/ML/RL",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes (Vercel/Railway)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error": str(exc),
        },
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "type": exc.__class__.__name__},
    )


# Health check endpoints
@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "nexitrade"}


@app.get("/readyz")
async def readiness_check():
    """Readiness check endpoint."""
    # TODO: Check database, exchanges, etc.
    return {"status": "ready", "service": "nexitrade"}


# API routers
app.include_router(status_router, prefix="/api", tags=["Status"])
app.include_router(orders_router, prefix="/api", tags=["Orders"])
app.include_router(strategies_router, prefix="/api", tags=["Strategies"])
app.include_router(portfolio_router, prefix="/api", tags=["Portfolio"])
app.include_router(config_router, prefix="/api", tags=["Config"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "NexiTrade",
        "version": "1.0.0",
        "description": "Autonomous Crypto Trading System with AI/ML/RL",
        "docs": "/docs",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.environment == "development",
    )

