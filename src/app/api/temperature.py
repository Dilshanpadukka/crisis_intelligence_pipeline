"""
Temperature stability analysis API endpoints (Part 2).
"""

from fastapi import APIRouter, HTTPException
import logging

from ..schemas.temperature import (
    TemperatureAnalysisRequest,
    TemperatureAnalysisResponse,
    BatchTemperatureAnalysisRequest,
    BatchTemperatureAnalysisResponse,
)
from ..services.temperature_service import TemperatureService
from ..utils.config_loader import get_config
from ..utils.file_utils import read_scenarios_from_file

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=TemperatureAnalysisResponse)
async def analyze_temperature_stability(request: TemperatureAnalysisRequest):
    """
    Analyze temperature stability for crisis decision-making.
    
    Demonstrates why temperature=0.0 is critical for deterministic outputs
    in life-critical systems.
    
    **Example Request:**
    ```json
    {
        "scenario": "SCENARIO: 5 people trapped on roof (immediate danger) vs. diabetic patient needs insulin (medical emergency). Which to prioritize?",
        "temperatures": [0.0, 1.0],
        "iterations_per_temperature": 3,
        "provider_config": {
            "provider": "groq"
        }
    }
    ```
    
    **Returns:**
    - Test results for each temperature/iteration combination
    - Statistical analysis of consistency
    - Recommendation for crisis systems
    """
    try:
        # Get default provider from config
        config = get_config()
        default_provider = config.get("providers", {}).get("default", "groq")
        
        # Initialize service
        service = TemperatureService(provider=default_provider)
        
        # Run analysis
        results, analysis, recommendation, total_latency, total_tokens = service.run_temperature_analysis(
            scenario=request.scenario,
            temperatures=request.temperatures,
            iterations_per_temperature=request.iterations_per_temperature,
            provider_config=request.provider_config
        )
        
        return TemperatureAnalysisResponse(
            results=results,
            analysis=analysis,
            recommendation=recommendation,
            total_latency_ms=total_latency,
            total_tokens_used=total_tokens
        )
    
    except Exception as e:
        logger.error(f"Temperature analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Temperature analysis failed: {str(e)}"
        )


@router.post("/analyze-batch", response_model=BatchTemperatureAnalysisResponse)
async def analyze_temperature_stability_batch(request: BatchTemperatureAnalysisRequest):
    """
    Analyze temperature stability for all scenarios from file.

    **Automatic File Processing:**
    - Reads scenarios from `data/Scenarios.txt`
    - Tests each scenario with 3 runs at temp=1.0 vs 1 run at temp=0.0
    - Demonstrates why temperature=0.0 is critical for crisis systems

    **Example Request:**
    ```json
    {
        "provider_config": {
            "provider": "groq"
        }
    }
    ```

    **Returns:**
    - Analysis results for each scenario
    - Overall recommendation for crisis systems
    - Demonstrates determinism vs variability
    """
    try:
        # Read scenarios from file
        try:
            scenarios = read_scenarios_from_file()
            logger.info(f"Read {len(scenarios)} scenarios from file")
        except FileNotFoundError as e:
            logger.error(f"Scenarios file not found: {e}")
            raise HTTPException(
                status_code=404,
                detail=f"Scenarios file not found: {str(e)}"
            )

        # Get default provider from config
        config = get_config()
        default_provider = config.get("providers", {}).get("default", "groq")

        # Initialize service
        service = TemperatureService(provider=default_provider)

        # Run batch analysis
        (scenarios_count, results_per_scenario, overall_recommendation,
         total_latency, total_tokens) = service.run_batch_temperature_analysis(
            scenarios=scenarios,
            provider_config=request.provider_config
        )

        # Convert results to response format
        response_results = []
        for results, analysis, recommendation, latency, tokens in results_per_scenario:
            response_results.append(
                TemperatureAnalysisResponse(
                    results=results,
                    analysis=analysis,
                    recommendation=recommendation,
                    total_latency_ms=latency,
                    total_tokens_used=tokens
                )
            )

        return BatchTemperatureAnalysisResponse(
            scenarios_analyzed=scenarios_count,
            results_per_scenario=response_results,
            overall_recommendation=overall_recommendation,
            total_latency_ms=total_latency,
            total_tokens_used=total_tokens
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Batch temperature analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Batch temperature analysis failed: {str(e)}"
        )

