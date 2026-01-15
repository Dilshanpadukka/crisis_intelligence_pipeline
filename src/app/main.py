"""
Operation Ditwah Crisis Intelligence API

Production-ready FastAPI application for crisis intelligence processing.
Converts the Jupyter notebook pipeline into REST endpoints.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
import logging

from .api import (
    classification_router,
    temperature_router,
    resource_allocation_router,
    token_management_router,
    news_processing_router,
)
from .schemas.common import HealthResponse, ErrorResponse
from .utils.config_loader import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Operation Ditwah Crisis Intelligence API")
    logger.info("Loading configuration...")
    
    # Load configuration
    config = get_config()
    logger.info(f"Default provider: {config.get('providers', {}).get('default', 'groq')}")
    logger.info(f"Enabled providers: {config.get('providers', {}).get('enabled', [])}")
    
    yield
    
    logger.info("Shutting down Operation Ditwah Crisis Intelligence API")


# Create FastAPI app
app = FastAPI(
    title="Operation Ditwah Crisis Intelligence API",
    description="""
    Production-ready API for crisis intelligence processing in post-disaster scenarios.
    
    **Features:**
    - Message classification with few-shot learning
    - Temperature stability analysis for deterministic outputs
    - Resource allocation with CoT & ToT reasoning
    - Token management and spam prevention
    - News feed processing with structured extraction
    
    **Scenario:** Post-Cyclone Ditwah Relief (Sri Lanka)
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            detail={"type": type(exc).__name__, "message": str(exc)}
        ).model_dump()
    )


# Health check endpoint
@app.get("/", response_model=HealthResponse, tags=["Health"])
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns service status and available providers.
    """
    config = get_config()
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        providers_available=config.get("providers", {}).get("enabled", ["groq"])
    )


# Include routers
app.include_router(
    classification_router,
    prefix="/api/v1/classification",
    tags=["Message Classification"]
)

app.include_router(
    temperature_router,
    prefix="/api/v1/temperature",
    tags=["Temperature Analysis"]
)

app.include_router(
    resource_allocation_router,
    prefix="/api/v1/resource-allocation",
    tags=["Resource Allocation"]
)

app.include_router(
    token_management_router,
    prefix="/api/v1/tokens",
    tags=["Token Management"]
)

app.include_router(
    news_processing_router,
    prefix="/api/v1/news",
    tags=["News Processing"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

