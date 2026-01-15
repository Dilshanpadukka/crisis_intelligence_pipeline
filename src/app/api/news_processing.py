"""
News processing API endpoints (Part 5).
"""

from fastapi import APIRouter, HTTPException
import logging

from ..schemas.news_processing import (
    NewsProcessingRequest,
    NewsProcessingResponse,
    BatchNewsProcessingRequest,
    BatchNewsProcessingResponse,
    NewsItem,
)
from ..services.news_processing_service import NewsProcessingService
from ..utils.config_loader import get_config
from ..utils.file_utils import (
    read_news_from_file,
    save_crisis_events_to_excel,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/process", response_model=NewsProcessingResponse)
async def process_news_item(request: NewsProcessingRequest):
    """
    Process a single news item into structured crisis event.
    
    **Example Request:**
    ```json
    {
        "news_item": {
            "text": "SOS: 5 people trapped on a roof in Ja-Ela (Gampaha). Water rising fast.",
            "source": "Twitter",
            "timestamp": "2024-01-15T10:30:00Z"
        },
        "provider_config": {
            "provider": "groq"
        }
    }
    ```
    
    **Returns:**
    - Extracted crisis event with structured fields
    - Success status and error message (if failed)
    - Processing metrics
    """
    try:
        config = get_config()
        default_provider = config.get("providers", {}).get("default", "groq")
        
        service = NewsProcessingService(provider=default_provider)
        
        event, success, error, latency_ms, tokens_used = service.extract_crisis_event(
            news_item=request.news_item,
            provider_config=request.provider_config
        )
        
        return NewsProcessingResponse(
            event=event,
            success=success,
            error=error,
            latency_ms=latency_ms,
            tokens_used=tokens_used
        )
    
    except Exception as e:
        logger.error(f"News processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"News processing failed: {str(e)}"
        )


@router.post("/process/batch", response_model=BatchNewsProcessingResponse)
async def process_news_batch(request: BatchNewsProcessingRequest):
    """
    Process multiple news items in batch.

    **Automatic File Processing:**
    - Reads news items from `data/News Feed.txt` by default (one item per line)
    - Optionally accepts custom file path (absolute or relative to project root)
    - Generates `output/flood_report.xlsx` (Excel format with crisis events)

    **Example Request (Default File):**
    ```json
    {
        "provider_config": {
            "provider": "groq"
        }
    }
    ```

    **Example Request (Custom File):**
    ```json
    {
        "file_path": "E:\\\\ZuuCrew\\\\AI Engineer Essentials Bootcamp\\\\Mini Project 0 v1\\\\data\\\\News Feed.txt",
        "provider_config": {
            "provider": "groq"
        }
    }
    ```

    **Returns:**
    - Path to generated Excel file
    - Preview of first 5 successfully extracted crisis events
    - Processing statistics (success rate, failures, etc.)
    - Aggregate token usage
    """
    try:
        # Read news items from file (use custom path if provided, otherwise default)
        try:
            file_path = request.file_path if request.file_path else "data/News Feed.txt"
            news_texts = read_news_from_file(file_path)
            logger.info(f"Read {len(news_texts)} news items from: {file_path}")
        except FileNotFoundError as e:
            logger.error(f"Input file not found: {e}")
            raise HTTPException(
                status_code=404,
                detail=f"Input file not found: {str(e)}"
            )

        # Convert to NewsItem objects
        news_items = [NewsItem(text=text, source="News Feed") for text in news_texts]

        config = get_config()
        default_provider = config.get("providers", {}).get("default", "groq")

        service = NewsProcessingService(provider=default_provider)

        (events, total_processed, successful, failed,
         success_rate, total_latency, total_tokens) = service.process_news_batch(
            news_items=news_items,
            provider_config=request.provider_config
        )

        # Save successfully extracted events to Excel
        if events:
            # Convert events to dictionaries for file output
            events_dicts = [event.model_dump() for event in events]
            excel_path = save_crisis_events_to_excel(events_dicts)
            logger.info(f"Saved {len(events)} crisis events to {excel_path}")
        else:
            # Create empty file if no events extracted
            excel_path = save_crisis_events_to_excel([])
            logger.warning("No crisis events extracted, created empty Excel file")

        # Get preview (first 5 events)
        preview_events = events[:5]

        return BatchNewsProcessingResponse(
            excel_file_path=excel_path,
            preview_events=preview_events,
            total_processed=total_processed,
            successful_extractions=successful,
            failed_extractions=failed,
            success_rate=success_rate,
            total_latency_ms=total_latency,
            total_tokens_used=total_tokens
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Batch news processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Batch news processing failed: {str(e)}"
        )
