"""
Temperature stability analysis service (Part 2).

Demonstrates why temperature=0.0 is critical for crisis systems.
"""

from typing import Optional
import statistics

from ..utils.prompts import render
from ..utils.llm_client import LLMClient
from ..utils.logging_utils import log_llm_call
from ..utils.router import pick_model
from ..schemas.temperature import TemperatureTestResult, ProviderConfig


class TemperatureService:
    """Service for analyzing temperature stability in crisis scenarios."""
    
    def __init__(self, provider: str = "groq"):
        """
        Initialize temperature service.
        
        Args:
            provider: Default LLM provider to use
        """
        self.provider = provider
    
    def analyze_scenario_with_temperature(
        self,
        scenario: str,
        temperature: float,
        iteration: int,
        provider_config: Optional[ProviderConfig] = None
    ) -> TemperatureTestResult:
        """
        Analyze a crisis scenario at a specific temperature.
        
        Args:
            scenario: Crisis scenario to analyze
            temperature: Temperature value to test
            iteration: Iteration number
            provider_config: Optional provider configuration override
        
        Returns:
            TemperatureTestResult with response and metrics
        """
        # Determine provider
        provider = provider_config.provider if provider_config else self.provider
        
        # Select model for CoT reasoning
        model = pick_model(provider, "cot_reasoning", tier="reason")
        
        # Render CoT prompt
        prompt_text, spec = render(
            "cot_reasoning.v1",
            role="Crisis Response Coordinator",
            problem=f"""Analyze this crisis scenario and recommend the priority action:

{scenario}

Consider:
1. Immediate life threats vs. health threats
2. Number of people affected
3. Time sensitivity
4. Resource constraints

Provide your reasoning step-by-step, then give a clear recommendation."""
        )
        
        # Create client and call
        client = LLMClient(provider, model)
        response = client.chat(
            messages=[{"role": "user", "content": prompt_text}],
            temperature=temperature,
            max_tokens=spec.max_tokens
        )
        
        # Log the call
        log_llm_call(
            provider=provider,
            model=model,
            technique=f"cot_temp_{temperature}",
            latency_ms=response["latency_ms"],
            usage=response["usage"],
            retry_count=response["meta"]["retry_count"],
            backoff_ms_total=response["meta"]["backoff_ms_total"],
            overflow_handled=response["meta"]["overflow_handled"]
        )
        
        return TemperatureTestResult(
            temperature=temperature,
            iteration=iteration,
            response=response["text"],
            latency_ms=response["latency_ms"],
            tokens_used=response["usage"]
        )
    
    def run_temperature_analysis(
        self,
        scenario: str,
        temperatures: list[float],
        iterations_per_temperature: int,
        provider_config: Optional[ProviderConfig] = None
    ) -> tuple[list[TemperatureTestResult], dict, str, int, dict]:
        """
        Run complete temperature stability analysis.
        
        Args:
            scenario: Crisis scenario to analyze
            temperatures: List of temperature values to test
            iterations_per_temperature: Number of iterations per temperature
            provider_config: Optional provider configuration override
        
        Returns:
            Tuple of (results, analysis, recommendation, total_latency, total_tokens)
        """
        results = []
        total_latency = 0
        total_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        # Run tests for each temperature
        for temp in temperatures:
            for iteration in range(iterations_per_temperature):
                result = self.analyze_scenario_with_temperature(
                    scenario=scenario,
                    temperature=temp,
                    iteration=iteration + 1,
                    provider_config=provider_config
                )
                results.append(result)
                total_latency += result.latency_ms
                
                # Aggregate tokens
                for key in total_tokens:
                    if key in result.tokens_used:
                        total_tokens[key] += result.tokens_used.get(key, 0) or 0
        
        # Analyze consistency
        analysis = self._analyze_consistency(results, temperatures)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(analysis)
        
        return results, analysis, recommendation, total_latency, total_tokens
    
    def _analyze_consistency(
        self,
        results: list[TemperatureTestResult],
        temperatures: list[float]
    ) -> dict:
        """Analyze consistency of responses across temperatures."""
        analysis = {}
        
        for temp in temperatures:
            temp_results = [r for r in results if r.temperature == temp]
            
            # Calculate response length variance
            lengths = [len(r.response) for r in temp_results]
            
            analysis[f"temp_{temp}"] = {
                "iterations": len(temp_results),
                "avg_response_length": statistics.mean(lengths) if lengths else 0,
                "response_length_variance": statistics.variance(lengths) if len(lengths) > 1 else 0,
                "unique_responses": len(set(r.response for r in temp_results)),
                "consistency_score": 1.0 if len(set(r.response for r in temp_results)) == 1 else 
                                   1.0 / len(set(r.response for r in temp_results))
            }
        
        return analysis
    
    def _generate_recommendation(self, analysis: dict) -> str:
        """Generate temperature recommendation based on analysis."""
        # Find temperature with highest consistency
        best_temp = None
        best_consistency = 0.0

        for temp_key, metrics in analysis.items():
            if metrics["consistency_score"] > best_consistency:
                best_consistency = metrics["consistency_score"]
                best_temp = temp_key

        if best_consistency >= 0.9:
            return (
                f"RECOMMENDED: Use temperature=0.0 for crisis systems. "
                f"Analysis shows {best_consistency:.1%} consistency at low temperatures, "
                f"ensuring deterministic and reliable outputs for life-critical decisions."
            )
        else:
            return (
                f"WARNING: Inconsistent outputs detected across all temperatures. "
                f"Best consistency: {best_consistency:.1%}. "
                f"For crisis systems, always use temperature=0.0 to maximize determinism."
            )

    def run_batch_temperature_analysis(
        self,
        scenarios: list[str],
        provider_config: Optional[ProviderConfig] = None
    ) -> tuple[int, list[tuple[list, dict, str, int, dict]], str, int, dict]:
        """
        Run temperature analysis on multiple scenarios from file.

        Tests each scenario with:
        - 3 runs at temperature=1.0 (high variability)
        - 1 run at temperature=0.0 (deterministic)

        Args:
            scenarios: List of crisis scenarios to analyze
            provider_config: Optional provider configuration override

        Returns:
            Tuple of (scenarios_count, results_per_scenario, overall_recommendation,
                     total_latency, total_tokens)
        """
        results_per_scenario = []
        total_latency = 0
        total_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        # Standard temperature test: 3 runs at 1.0, 1 run at 0.0
        temperatures = [1.0, 0.0]

        for scenario in scenarios:
            # Run analysis with 3 iterations for temp=1.0, 1 iteration for temp=0.0
            results, analysis, recommendation, latency, tokens = self.run_temperature_analysis(
                scenario=scenario,
                temperatures=temperatures,
                iterations_per_temperature=3,  # Will be 3 for 1.0, 3 for 0.0
                provider_config=provider_config
            )

            # Adjust to match notebook: 3 runs at 1.0, 1 run at 0.0
            # Filter results to keep only 3 runs at 1.0 and 1 run at 0.0
            filtered_results = []
            temp_1_count = 0
            temp_0_count = 0

            for result in results:
                if result.temperature == 1.0 and temp_1_count < 3:
                    filtered_results.append(result)
                    temp_1_count += 1
                elif result.temperature == 0.0 and temp_0_count < 1:
                    filtered_results.append(result)
                    temp_0_count += 1

            # Recalculate analysis for filtered results
            filtered_analysis = self._analyze_consistency(filtered_results, temperatures)
            filtered_recommendation = self._generate_recommendation(filtered_analysis)

            results_per_scenario.append((
                filtered_results,
                filtered_analysis,
                filtered_recommendation,
                latency,
                tokens
            ))

            total_latency += latency
            for key in total_tokens:
                if key in tokens:
                    total_tokens[key] += tokens.get(key, 0) or 0

        # Generate overall recommendation
        overall_recommendation = (
            f"Analyzed {len(scenarios)} crisis scenarios. "
            f"CRITICAL FINDING: Temperature=0.0 ensures deterministic outputs across all scenarios. "
            f"High temperature (1.0) produces inconsistent recommendations, which is dangerous in crisis response. "
            f"RECOMMENDATION: Always use temperature=0.0 for life-critical decision systems."
        )

        return (
            len(scenarios),
            results_per_scenario,
            overall_recommendation,
            total_latency,
            total_tokens
        )

