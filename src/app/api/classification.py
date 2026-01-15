"""
Message classification API endpoints (Part 1).
"""

from fastapi import APIRouter, HTTPException
import logging

from ..schemas.classification import (
    MessageClassificationRequest,
    MessageClassificationResponse,
    BatchClassificationRequest,
    BatchClassificationResponse,
)
from ..services.classification_service import ClassificationService
from ..utils.config_loader import get_config
from ..utils.file_utils import (
    read_messages_from_file,
    save_classification_results_to_excel,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/classify", response_model=MessageClassificationResponse)
async def classify_message(request: MessageClassificationRequest):
    """
    Classify a single crisis message using few-shot learning.
    
    **Example Request:**
    ```json
    {
        "message": "SOS: 5 people trapped on a roof in Ja-Ela. Water rising fast!",
        "provider_config": {
            "provider": "groq",
            "temperature": 0.0
        }
    }
    ```
    
    **Returns:**
    - Classification result with district, intent, and priority
    - Processing latency and token usage statistics
    """
    try:
        # Get default provider from config
        config = get_config()
        default_provider = config.get("providers", {}).get("default", "groq")
        
        # Initialize service
        service = ClassificationService(provider=default_provider)
        
        # Classify message
        result, latency_ms, tokens_used = service.classify_message(
            message=request.message,
            provider_config=request.provider_config
        )
        
        return MessageClassificationResponse(
            result=result,
            latency_ms=latency_ms,
            tokens_used=tokens_used
        )
    
    except Exception as e:
        logger.error(f"Classification error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )


@router.post("/classify/batch", response_model=BatchClassificationResponse)
async def classify_messages_batch(request: BatchClassificationRequest):
    """
    Classify multiple crisis messages in batch.

    **Automatic File Processing:**
    - Reads messages from `data/Sample Messages.txt` by default (one message per line)
    - Optionally accepts custom file path (absolute or relative to project root)
    - Generates `output/classified_messages.xlsx` (Excel format)

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
        "file_path": "E:\\\\ZuuCrew\\\\AI Engineer Essentials Bootcamp\\\\Mini Project 0 v1\\\\data\\\\Sample Messages.txt",
        "provider_config": {
            "provider": "groq"
        }
    }
    ```

    **Returns:**
    - Paths to generated Excel file
    - Preview of first 5 classification results
    - Aggregate statistics and token usage
    """
    try:
        # Read messages from file (use custom path if provided, otherwise default)
        try:
            file_path = request.file_path if request.file_path else "data/Sample Messages.txt"
            messages = read_messages_from_file(file_path)
            logger.info(f"Read {len(messages)} messages from: {file_path}")
        except FileNotFoundError as e:
            logger.error(f"Input file not found: {e}")
            raise HTTPException(
                status_code=404,
                detail=f"Input file not found: {str(e)}"
            )

        # Get default provider from config
        config = get_config()
        default_provider = config.get("providers", {}).get("default", "groq")

        # Initialize service
        service = ClassificationService(provider=default_provider)

        # Classify batch
        results, total_latency_ms, total_tokens_used = service.classify_batch(
            messages=messages,
            provider_config=request.provider_config
        )

        # Convert results to dictionaries for file output
        results_dicts = [result.model_dump() for result in results]

        # Save and Excel
        excel_path = save_classification_results_to_excel(results_dicts)

        logger.info(f"Saved classification results to {excel_path}")

        # Get preview (first 5 results)
        preview_results = results[:5]

        return BatchClassificationResponse(
            excel_file_path=excel_path,
            preview_results=preview_results,
            total_processed=len(results),
            total_latency_ms=total_latency_ms,
            total_tokens_used=total_tokens_used
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Batch classification error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Batch classification failed: {str(e)}"
        )

