"""
Resource allocation API endpoints (Part 3).
"""

from fastapi import APIRouter, HTTPException
import logging

from ..schemas.resource_allocation import (
    PriorityScoreRequest,
    PriorityScoreResponse,
    RouteOptimizationRequest,
    RouteOptimizationResponse,
    BatchResourceAllocationRequest,
    BatchResourceAllocationResponse,
    IncidentData,
)
from ..services.resource_allocation_service import ResourceAllocationService
from ..utils.config_loader import get_config
from ..utils.file_utils import read_incidents_from_file

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/priority-score", response_model=PriorityScoreResponse)
async def score_incident_priority(request: PriorityScoreRequest):
    """
    Score incident priority using Chain-of-Thought reasoning.
    
    **Scoring Logic:**
    - Base Score: 5
    - +2 if Age > 60 or < 5 (vulnerable populations)
    - +3 if Need == "Rescue" (life-threatening)
    - +1 if Need == "Medicine/Insulin" (medical emergency)
    - Result: Score 0-10
    
    **Example Request:**
    ```json
    {
        "incidents": [
            {
                "location": "Ja-Ela",
                "description": "5 people trapped on roof",
                "people_affected": 5,
                "need_type": "Rescue",
                "age_info": "Including 2 children under 5"
            }
        ],
        "provider_config": {
            "provider": "groq"
        }
    }
    ```
    """
    try:
        config = get_config()
        default_provider = config.get("providers", {}).get("default", "groq")
        
        service = ResourceAllocationService(provider=default_provider)
        
        scored_incidents, total_latency, total_tokens = service.score_incidents_batch(
            incidents=request.incidents,
            provider_config=request.provider_config
        )
        
        return PriorityScoreResponse(
            scored_incidents=scored_incidents,
            total_latency_ms=total_latency,
            total_tokens_used=total_tokens
        )
    
    except Exception as e:
        logger.error(f"Priority scoring error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Priority scoring failed: {str(e)}"
        )


@router.post("/optimize-route", response_model=RouteOptimizationResponse)
async def optimize_rescue_route(request: RouteOptimizationRequest):
    """
    Optimize rescue route using Tree-of-Thought reasoning.
    
    Explores 3 strategies:
    1. Highest priority first (greedy)
    2. Closest location first (minimize travel)
    3. Furthest location first (logistics)
    
    **Example Request:**
    ```json
    {
        "scored_incidents": [
            {
                "incident": {
                    "location": "Ja-Ela",
                    "description": "Trapped on roof",
                    "people_affected": 5,
                    "need_type": "Rescue"
                },
                "score": 10,
                "reasoning": "High priority rescue"
            }
        ],
        "starting_location": "Ragama",
        "provider_config": {
            "provider": "groq"
        }
    }
    ```
    """
    try:
        config = get_config()
        default_provider = config.get("providers", {}).get("default", "groq")
        
        service = ResourceAllocationService(provider=default_provider)
        
        (optimal_route, strategy, reasoning, est_time, 
         total_score, latency, tokens) = service.optimize_route_with_tot(
            scored_incidents=request.scored_incidents,
            starting_location=request.starting_location,
            travel_times=request.travel_times,
            provider_config=request.provider_config
        )
        
        return RouteOptimizationResponse(
            optimal_route=optimal_route,
            strategy_used=strategy,
            reasoning=reasoning,
            estimated_total_time=est_time,
            total_priority_score=total_score,
            latency_ms=latency,
            tokens_used=tokens
        )
    
    except Exception as e:
        logger.error(f"Route optimization error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Route optimization failed: {str(e)}"
        )


@router.post("/process-batch", response_model=BatchResourceAllocationResponse)
async def process_incidents_batch(request: BatchResourceAllocationRequest):
    """
    Process all incidents from file with CoT scoring and ToT route optimization.

    **Automatic File Processing:**
    - Reads incidents from `data/Incidents.txt`
    - Scores each incident using CoT reasoning (Base:5, +2 age, +3 rescue, +1 medicine)
    - Optimizes rescue route using ToT reasoning (3 strategies)
    - Default starting location: Ragama
    - Travel times: Ragama→Ja-Ela (10m), Ja-Ela→Gampaha (40m), Ragama→Gampaha (30m)

    **Example Request:**
    ```json
    {
        "starting_location": "Ragama",
        "provider_config": {
            "provider": "groq"
        }
    }
    ```

    **Returns:**
    - All scored incidents
    - Optimal rescue route
    - ToT strategy and reasoning
    - Total priority score
    """
    try:
        # Read incidents from file
        try:
            incident_texts = read_incidents_from_file()
            logger.info(f"Read {len(incident_texts)} incidents from file")
        except FileNotFoundError as e:
            logger.error(f"Incidents file not found: {e}")
            raise HTTPException(
                status_code=404,
                detail=f"Incidents file not found: {str(e)}"
            )

        # Parse incident texts into IncidentData objects
        # Format: "Location: X | Description: Y | People: Z | Need: W | Age: A"
        incidents = []
        for text in incident_texts:
            # Simple parsing - extract key information
            parts = {}
            for part in text.split("|"):
                if ":" in part:
                    key, value = part.split(":", 1)
                    parts[key.strip().lower()] = value.strip()

            # Create IncidentData
            incident = IncidentData(
                location=parts.get("location", "Unknown"),
                description=text,  # Use full text as description
                people_affected=int(parts.get("people", 0)) if parts.get("people", "").isdigit() else None,
                need_type=parts.get("need"),
                age_info=parts.get("age")
            )
            incidents.append(incident)

        # Get default provider from config
        config = get_config()
        default_provider = config.get("providers", {}).get("default", "groq")

        # Initialize service
        service = ResourceAllocationService(provider=default_provider)

        # Score all incidents
        scored_incidents, scoring_latency, scoring_tokens = service.score_incidents_batch(
            incidents=incidents,
            provider_config=request.provider_config
        )

        # Optimize route
        (optimal_route, strategy, reasoning, est_time,
         total_score, route_latency, route_tokens) = service.optimize_route_with_tot(
            scored_incidents=scored_incidents,
            starting_location=request.starting_location,
            travel_times=None,  # Use default travel times
            provider_config=request.provider_config
        )

        # Aggregate metrics
        total_latency = scoring_latency + route_latency
        total_tokens = {
            "prompt_tokens": scoring_tokens.get("prompt_tokens", 0) + route_tokens.get("prompt_tokens", 0),
            "completion_tokens": scoring_tokens.get("completion_tokens", 0) + route_tokens.get("completion_tokens", 0),
            "total_tokens": scoring_tokens.get("total_tokens", 0) + route_tokens.get("total_tokens", 0)
        }

        return BatchResourceAllocationResponse(
            scored_incidents=scored_incidents,
            optimal_route=optimal_route,
            strategy_used=strategy,
            reasoning=reasoning,
            total_priority_score=total_score,
            total_latency_ms=total_latency,
            total_tokens_used=total_tokens
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Batch resource allocation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Batch resource allocation failed: {str(e)}"
        )

