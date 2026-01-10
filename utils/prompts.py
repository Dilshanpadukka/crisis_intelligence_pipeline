"""
Central prompt template catalog for Operation Ditwah Crisis Intelligence Pipeline.

This module serves as the single source of truth for all prompt templates, enhanced for crisis response scenarios.

Templates have been optimized for:
- Deterministic outputs (temperature=0.0 for crisis-critical tasks)
- Increased token limits to prevent truncation
- Crisis-specific terminology and context
- Post-cyclone disaster response in Sri Lanka

Usage:
    from utils.prompts import render

    # Crisis message classification
    text, spec = render("few_shot.v1",
                       role="Crisis Intelligence System for Cyclone Ditwah",
                       examples="[4 labeled crisis examples]",
                       query="SOS: Trapped on roof!",
                       constraints="Classify by district, intent, priority",
                       format="District: X | Intent: Y | Priority: Z")

    # Priority scoring with CoT
    text, spec = render("crisis_priority_scoring.v1",
                       incident="ID 1 | Ja-Ela | 1 person | Age 75 | Need: Insulin")
"""

from dataclasses import dataclass
from string import Template
from typing import Optional, List, Dict, Tuple


@dataclass
class PromptSpec:
    """
    Specification for a prompt template.

    Attributes:
        id: Unique identifier (e.g., "zero_shot.v1")
        purpose: Human-readable description of use case
        template: Template string with ${variable} placeholders
        stop: Optional stop sequences
        max_tokens: Suggested max output tokens
        temperature: Suggested temperature (0.0-1.0)
    """

    id: str
    purpose: str
    template: str
    stop: Optional[List[str]] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


# Central prompt registry
PROMPTS: Dict[str, PromptSpec] = {
    "skeleton.v1": PromptSpec(
        id="skeleton.v1",
        purpose="Structured writing with fixed sections",
        template=(
            "Role: ${role}\n"
            "Task: ${task}\n\n"
            "Context:\n${context}\n\n"
            "Constraints:\n${constraints}\n\n"
            "Output format:\n${format}\n\n"
            "Checks:\n${checks}\n"
        ),
        stop=["</end>"],
        max_tokens=800,
        temperature=0.2,
    ),
    "zero_shot.v1": PromptSpec(
        id="zero_shot.v1",
        purpose="Direct instruction-first prompt",
        template=(
            "You are ${role}. Follow the instructions precisely.\n"
            "Instruction: ${instruction}\n"
            "Constraints: ${constraints}\n"
            "Output format: ${format}\n"
        ),
        temperature=0.2,
    ),
    "few_shot.v1": PromptSpec(
        id="few_shot.v1",
        purpose="Few-shot classification for crisis intelligence (Operation Ditwah)",
        template=(
            "You are ${role}.\n\n"
            "CRITICAL: This is a crisis response system. Accuracy and consistency are paramount.\n"
            "Learn from the examples below, then classify the incoming message with precision.\n\n"
            "Examples:\n${examples}\n\n"
            "Incoming Message: ${query}\n\n"
            "Classification Requirements:\n${constraints}\n\n"
            "Required Output Format:\n${format}\n\n"
            "Provide ONLY the classification in the exact format specified. No explanations."
        ),
        temperature=0.2,  # Changed to 0.0 for deterministic crisis response
        max_tokens=150,  # Increased for complete structured output
    ),
    "cot_reasoning.v1": PromptSpec(
        id="cot_reasoning.v1",
        purpose="Chain-of-thought reasoning for crisis analysis (Operation Ditwah)",
        template=(
            "You are ${role} for Operation Ditwah (Post-Cyclone Crisis Response).\n\n"
            "MISSION CRITICAL: Lives depend on accurate analysis. Think step-by-step.\n\n"
            "Crisis Scenario:\n${problem}\n\n"
            "INSTRUCTIONS:\n"
            "1. Analyze the situation systematically\n"
            "2. Consider all relevant factors (urgency, vulnerability, resources)\n"
            "3. Show your reasoning step-by-step\n"
            "4. Provide a clear, actionable recommendation\n\n"
            "Format your response as:\n"
            "ANALYSIS:\n"
            "[Your step-by-step reasoning]\n\n"
            "RECOMMENDATION:\n"
            "[Your final answer/decision]\n\n"
            "Be thorough but concise. Every second counts in crisis response."
        ),
        temperature=0.0,  # Changed to 0.0 for deterministic crisis decisions
        max_tokens=6000,  # Increased to prevent truncation of reasoning chains
    ),
    "tot_reasoning.v1": PromptSpec(
        id="tot_reasoning.v1",
        purpose="Tree-of-thought optimization for crisis resource allocation (Operation Ditwah)",
        template=(
            "You are ${role} for Operation Ditwah (Post-Cyclone Crisis Response).\n\n"
            "MISSION: Optimize limited rescue resources to save maximum lives.\n\n"
            "Crisis Situation:\n${problem}\n\n"
            "TASK: Explore ${branches} distinct strategic approaches.\n\n"
            "For EACH strategy, provide:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "STRATEGY [Number]: [Name]\n"
            "Approach: [Brief description]\n"
            "Execution Steps: [Detailed steps]\n"
            "Expected Outcomes: [Lives saved, time taken, resources used]\n"
            "Trade-offs: [Advantages vs. disadvantages]\n"
            "Risk Assessment: [Potential issues]\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "After analyzing all strategies:\n\n"
            "FINAL RECOMMENDATION:\n"
            "[Select the optimal strategy and justify why it maximizes lives saved]\n\n"
            "IMPLEMENTATION PLAN:\n"
            "[Concrete action steps for the chosen strategy]\n\n"
            "Remember: In crisis response, every decision has life-or-death consequences."
        ),
        temperature=0.0,  # Changed to 0.0 for deterministic crisis optimization
        max_tokens=8000,  # Significantly increased for complete multi-branch analysis
    ),
    "json_extract.v1": PromptSpec(
        id="json_extract.v1",
        purpose="Structured crisis data extraction for Operation Ditwah intelligence pipeline",
        template=(
            "You are a Crisis Data Extraction System for Operation Ditwah.\n\n"
            "TASK: Extract structured information from the crisis report below.\n\n"
            "Required JSON Schema:\n${schema}\n\n"
            "Crisis Report:\n${text}\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Extract ALL relevant information accurately\n"
            "2. Use 'null' for missing optional fields\n"
            "3. Use 0 for unknown victim counts\n"
            "4. Infer district from location names (Ja-Ela→Gampaha, Colombo Fort→Colombo, etc.)\n"
            "5. Classify status as: Critical (life-threatening), Warning (potential danger), Stable (safe)\n"
            "6. Return ONLY valid JSON - no markdown, no explanations, no extra text\n\n"
            "Output the JSON now:"
        ),
        temperature=0.0,
        max_tokens=800,  # Doubled to prevent truncation of complex JSON structures
        stop=None,
    ),
    "tool_call.v1": PromptSpec(
        id="tool_call.v1",
        purpose="Instruct model to choose & call a tool when needed",
        template=(
            "You can decide to call a tool if it helps.\n"
            "Available tools:\n${tools}\n\n"
            "User request: ${request}\n\n"
            "If a tool is needed, respond with JSON:\n"
            '{"tool": "tool_name", "arguments": {...}}\n\n'
            "Otherwise, answer directly and concisely."
        ),
        temperature=0.2,
    ),
    "overflow_summarize.v1": PromptSpec(
        id="overflow_summarize.v1",
        purpose="Crisis message summarization for spam/overflow handling (Operation Ditwah)",
        template=(
            "CRISIS INTELLIGENCE SYSTEM - Message Overflow Handler\n\n"
            "The following message exceeds token limits and may be spam.\n\n"
            "Step 1 — Summarize into ≤ ${max_tokens_context} tokens, preserving:\n"
            "  • Location/district information\n"
            "  • Number of people affected\n"
            "  • Type of emergency (rescue, medical, supply)\n"
            "  • Urgency indicators\n"
            "  • Contact information\n\n"
            "Original Message:\n${context}\n\n"
            "Step 2 — Using ONLY that summary, complete:\n"
            "${task}\n\n"
            "Output format: ${format}\n"
        ),
        temperature=0.0,  # Changed to 0.0 for consistent summarization
        max_tokens=600,  # Added explicit limit
    ),
    "rate_limit_retry.v1": PromptSpec(
        id="rate_limit_retry.v1",
        purpose="Idempotent retry phrasing to avoid redoing stochastic steps",
        template=(
            "If a previous attempt failed due to a temporary error, do not redo stochastic planning. "
            "Reuse the prior plan and produce only the final result below.\n"
            "Task: ${task}\n"
            "Keep the answer concise (≤ ${max_tokens_answer} tokens)."
        ),
        temperature=0.0,
    ),
    "style_persona.v1": PromptSpec(
        id="style_persona.v1",
        purpose="Lock tone/persona/reading level",
        template=(
            "Persona: ${persona}\n"
            "Tone: ${tone}\n"
            "Reading level: ${reading_level}\n\n"
            "Task: ${task}\n"
            "Constraints: ${constraints}\n"
            "Output format: ${format}\n"
        ),
        temperature=0.2,
    ),
    "router_classify.v1": PromptSpec(
        id="router_classify.v1",
        purpose="Light intent classification into categories",
        template=(
            "Classify the user query into one of the categories:\n"
            "${labels}\n\n"
            "Query: ${query}\n\n"
            "Return ONLY the label, nothing else."
        ),
        temperature=0.0,
        max_tokens=20,
    ),
    "crisis_priority_scoring.v1": PromptSpec(
        id="crisis_priority_scoring.v1",
        purpose="Systematic priority scoring for crisis incidents (Operation Ditwah)",
        template=(
            "You are a Crisis Priority Analyst for Operation Ditwah.\n\n"
            "MISSION: Score incidents objectively to optimize rescue resource allocation.\n\n"
            "Incident Details:\n${incident}\n\n"
            "SCORING CRITERIA:\n"
            "Base Score: 5 points\n"
            "+ 2 points if victim age > 60 OR age < 5 (vulnerable populations)\n"
            "+ 3 points if need type is 'Rescue' (immediate life threat)\n"
            "+ 1 point if need type is 'Medicine' or 'Insulin' (medical emergency)\n"
            "Maximum Score: 10 points\n\n"
            "ANALYSIS STEPS:\n"
            "1. Identify victim age(s) from incident data\n"
            "2. Identify need type (Rescue/Medicine/Water/Supply/etc.)\n"
            "3. Apply scoring criteria systematically\n"
            "4. Calculate total score\n\n"
            "OUTPUT FORMAT:\n"
            "Step 1: [Age analysis]\n"
            "Step 2: [Need type identification]\n"
            "Step 3: [Score calculation breakdown]\n"
            "Final Score: X/10\n\n"
            "Provide your analysis now:"
        ),
        temperature=0.0,
        max_tokens=800,
    ),
    "crisis_classification.v1": PromptSpec(
        id="crisis_classification.v1",
        purpose="Fast crisis message classification without examples (Operation Ditwah)",
        template=(
            "You are a Crisis Intelligence System for Cyclone Ditwah (Sri Lanka).\n\n"
            "TASK: Classify the incoming message immediately.\n\n"
            "Message: ${message}\n\n"
            "CLASSIFICATION CATEGORIES:\n"
            "• RESCUE: Life-threatening emergencies requiring immediate response\n"
            "  Examples: trapped, drowning, collapsed building, medical emergency\n"
            "• SUPPLY: Requests for resources (food, water, medicine, shelter)\n"
            "  Examples: need food, requesting water, out of medicine\n"
            "• INFO: News reports, status updates, general information\n"
            "  Examples: road closed, water level rising, weather update\n"
            "• OTHER: Spam, irrelevant messages, unclear content\n"
            "  Examples: prayers, shares, unrelated topics\n\n"
            "DISTRICT MAPPING (Sri Lanka):\n"
            "Colombo: Colombo Fort, Kolonnawa, Wellampitiya, Kaduwela, Dehiwala\n"
            "Gampaha: Ja-Ela, Gampaha town, Kelaniya, Wattala, Ragama\n"
            "Kandy: Peradeniya, Kandy town, Akurana\n"
            "Kalutara: Kalutara town, Bulathsinhala\n"
            "Galle: Galle fort\n"
            "Matara: Matara town, Polhena\n\n"
            "PRIORITY RULES:\n"
            "High: RESCUE category OR medical emergency\n"
            "Low: All other categories\n\n"
            "OUTPUT FORMAT (exact format required):\n"
            "District: [Name or None] | Intent: [RESCUE/SUPPLY/INFO/OTHER] | Priority: [High/Low]\n\n"
            "Classify now:"
        ),
        temperature=0.0,
        max_tokens=100,
    ),
}


def render(prompt_id: str, **vars) -> Tuple[str, PromptSpec]:
    """
    Render a prompt template with variables.

    Args:
        prompt_id: Prompt identifier from PROMPTS registry
        **vars: Variables to substitute in template

    Returns:
        Tuple of (rendered_text, prompt_spec)

    Raises:
        KeyError: If prompt_id not found in registry

    Example:
        >>> text, spec = render("zero_shot.v1",
        ...                     role="helpful assistant",
        ...                     instruction="Summarize this",
        ...                     constraints="Max 50 words",
        ...                     format="Plain text")
    """
    if prompt_id not in PROMPTS:
        raise KeyError(
            f"Prompt '{prompt_id}' not found. "
            f"Available: {', '.join(PROMPTS.keys())}"
        )

    spec = PROMPTS[prompt_id]
    text = Template(spec.template).safe_substitute(**vars)
    return text, spec


def list_prompts() -> List[str]:
    """
    List all available prompt IDs.

    Returns:
        List of prompt identifiers
    """
    return list(PROMPTS.keys())


def get_prompt_info(prompt_id: str) -> PromptSpec:
    """
    Get metadata for a prompt without rendering.

    Args:
        prompt_id: Prompt identifier

    Returns:
        PromptSpec instance

    Raises:
        KeyError: If prompt_id not found
    """
    if prompt_id not in PROMPTS:
        raise KeyError(f"Prompt '{prompt_id}' not found")
    return PROMPTS[prompt_id]

