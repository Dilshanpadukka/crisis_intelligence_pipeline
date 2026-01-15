"""
API routers for Operation Ditwah Crisis Intelligence API.
"""

from .classification import router as classification_router
from .temperature import router as temperature_router
from .resource_allocation import router as resource_allocation_router
from .token_management import router as token_management_router
from .news_processing import router as news_processing_router

__all__ = [
    "classification_router",
    "temperature_router",
    "resource_allocation_router",
    "token_management_router",
    "news_processing_router",
]

