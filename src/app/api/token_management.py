"""
Token management API endpoints (Part 4).
"""

from fastapi import APIRouter, HTTPException
import logging

from ..schemas.token_management import (
    TokenCheckRequest,
    TokenCheckResponse,
)
from ..services.token_management_service import TokenManagementService
from ..utils.config_loader import get_config

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/check", response_model=TokenCheckResponse)
async def check_message_tokens(request: TokenCheckRequest):
    """
    Check message token count and apply spam filtering.
    
    **Strategies:**
    - **truncate**: Simple token-based truncation (fast, may lose context)
    - **summarize**: Intelligent LLM-based summarization (slower, preserves key info)
    
    **Example Request:**
    ```json
    {
        "message": "URGENT HELP NEEDED! Please forward this message...",
        "max_tokens": 150,
        "strategy": "truncate",
        "provider_config": {
            "provider": "groq"
        }
    }
    ```
    
    **Returns:**
    - Filter decision (ACCEPTED/BLOCKED/SUMMARIZED)
    - Original and processed token counts
    - Processed message text
    - Tokens saved
    """
    try:
        config = get_config()
        default_provider = config.get("providers", {}).get("default", "groq")
        
        service = TokenManagementService(provider=default_provider)
        
        result, latency_ms = service.check_and_filter_spam(
            message=request.message,
            max_tokens=request.max_tokens,
            strategy=request.strategy,
            provider_config=request.provider_config
        )
        
        return TokenCheckResponse(
            result=result,
            latency_ms=latency_ms
        )
    
    except Exception as e:
        logger.error(f"Token check error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Token check failed: {str(e)}"
        )

