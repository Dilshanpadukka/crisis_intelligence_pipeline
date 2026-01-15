# 📘 API Documentation - Crisis Intelligence Pipeline

**Complete API Reference for Operation Ditwah Crisis Intelligence System**

Version: 1.0.0  
Base URL: `http://localhost:8000`  
Interactive Docs: `http://localhost:8000/docs`

---

## 📑 Table of Contents

1. [Overview](#overview)
2. [Authentication & Configuration](#authentication--configuration)
3. [Common Schemas](#common-schemas)
4. [Health Check](#health-check)
5. [Part 1: Message Classification](#part-1-message-classification)
6. [Part 2: Temperature Analysis](#part-2-temperature-analysis)
7. [Part 3: Resource Allocation](#part-3-resource-allocation)
8. [Part 4: Token Management](#part-4-token-management)
9. [Part 5: News Processing](#part-5-news-processing)
10. [Error Handling](#error-handling)
11. [Rate Limiting & Performance](#rate-limiting--performance)
12. [Integration Examples](#integration-examples)

---

## Overview

The Crisis Intelligence Pipeline API provides five core capabilities for post-disaster relief operations:

| Feature | Endpoint Prefix | Purpose |
|---------|----------------|---------|
| **Message Classification** | `/api/v1/classification` | Classify crisis messages by district, intent, and priority |
| **Temperature Analysis** | `/api/v1/temperature` | Analyze model consistency across temperature values |
| **Resource Allocation** | `/api/v1/resource-allocation` | Optimize rescue routes with CoT & ToT reasoning |
| **Token Management** | `/api/v1/tokens` | Prevent spam and manage token costs |
| **News Processing** | `/api/v1/news` | Extract structured crisis events from news feeds |

### Key Features

- ✅ **RESTful API** - Standard HTTP methods and status codes
- ✅ **JSON Payloads** - All requests and responses use JSON
- ✅ **Batch Processing** - Process multiple items efficiently
- ✅ **Custom File Paths** - Support for absolute and relative file paths
- ✅ **Multiple Providers** - OpenAI, Google Gemini, and Groq support
- ✅ **Excel Outputs** - Structured results in Excel format
- ✅ **Interactive Docs** - Swagger UI and ReDoc available

---

## Authentication & Configuration

### API Keys

The API requires at least one LLM provider API key configured in the `.env` file:

```bash
# At least one is required
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
GROQ_API_KEY=your-groq-key-here
```

### Provider Configuration

All endpoints accept an optional `provider_config` object:

```json
{
  "provider_config": {
    "provider": "groq",           // "openai" | "google" | "groq"
    "temperature": 0.0,            // 0.0-2.0 (optional)
    "max_tokens": 500              // positive integer (optional)
  }
}
```

**Default Provider:** Groq (configured in `config/config.yaml`)

### Provider Comparison

| Provider | Speed | Cost | Best For |
|----------|-------|------|----------|
| **Groq** | ⚡⚡⚡ Very Fast | 💰 Free tier | Development, fast inference |
| **OpenAI** | ⚡⚡ Fast | 💰💰 Pay-per-use | Production, reliability |
| **Google Gemini** | ⚡⚡ Fast | 💰 Free tier | Large context, multimodal |

---

## Common Schemas

### ProviderConfig

```json
{
  "provider": "groq",              // Required: "openai" | "google" | "groq"
  "temperature": 0.0,              // Optional: 0.0-2.0
  "max_tokens": 500                // Optional: positive integer
}
```

### TokenUsage

```json
{
  "prompt_tokens": 150,            // Tokens in the prompt
  "completion_tokens": 20,         // Tokens in the response
  "total_tokens": 170              // Total tokens used
}
```

### ErrorResponse

```json
{
  "detail": "Error message here"   // Human-readable error description
}
```

---

## Health Check

### GET /health

Check API health status and available providers.

**Request:**

```bash
curl -X GET "http://localhost:8000/health"
```

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "providers_available": ["groq", "openai", "google"]
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Service status ("healthy" or "unhealthy") |
| `version` | string | API version |
| `providers_available` | array | List of configured LLM providers |

---

## Part 1: Message Classification

Classify crisis messages using few-shot learning to distinguish real SOS calls from noise.

### POST /api/v1/classification/classify

Classify a single crisis message.

**Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/classification/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "SOS: 5 people trapped on roof in Ja-Ela (Gampaha). Water rising fast!",
    "provider_config": {
      "provider": "groq",
      "temperature": 0.0
    }
  }'
```

**Request Schema:**

```json
{
  "message": "string (required, 1-10000 chars)",
  "provider_config": {
    "provider": "groq",
    "temperature": 0.0
  }
}
```

**Response:** `200 OK`

```json
{
  "result": {
    "message": "SOS: 5 people trapped on roof in Ja-Ela (Gampaha). Water rising fast!",
    "district": "Gampaha",
    "intent": "Rescue",
    "priority": "High",
    "raw_output": "District: Gampaha | Intent: Rescue | Priority: High",
    "confidence": null
  },
  "latency_ms": 1234,
  "tokens_used": {
    "prompt_tokens": 150,
    "completion_tokens": 20,
    "total_tokens": 170
  }
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `result.message` | string | Original message text |
| `result.district` | string | Identified district or "None" |
| `result.intent` | string | "Rescue" \| "Supply" \| "Info" \| "Other" |
| `result.priority` | string | "High" \| "Low" |
| `result.raw_output` | string | Raw LLM classification output |
| `result.confidence` | float \| null | Classification confidence (0.0-1.0) |
| `latency_ms` | integer | Processing time in milliseconds |
| `tokens_used` | object | Token usage statistics |

**Classification Categories:**

| Intent | Description | Example |
|--------|-------------|---------|
| **Rescue** | Life-threatening emergencies | "SOS: Trapped on roof!" |
| **Supply** | Resource requests | "Need dry rations for camp" |
| **Info** | Updates and information | "Road cleared near Peradeniya" |
| **Other** | Spam and irrelevant content | "Please forward this message" |

---

### POST /api/v1/classification/classify/batch

Classify multiple crisis messages in batch from a file.

**Features:**
- ✅ Reads from `data/Sample Messages.txt` by default
- ✅ Supports custom file paths (absolute or relative)
- ✅ Generates Excel output: `output/classified_messages.xlsx`
- ✅ Returns preview of first 5 results
- ✅ Includes aggregate statistics

**Request (Default File):**

```bash
curl -X POST "http://localhost:8000/api/v1/classification/classify/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_config": {
      "provider": "groq"
    }
  }'
```

**Request (Custom File Path - Absolute):**

```bash
curl -X POST "http://localhost:8000/api/v1/classification/classify/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "E:\\\\path\\\\to\\\\custom\\\\messages.txt",
    "provider_config": {
      "provider": "groq"
    }
  }'
```

**Request (Custom File Path - Relative):**

```bash
curl -X POST "http://localhost:8000/api/v1/classification/classify/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "data/custom_messages.txt",
    "provider_config": {
      "provider": "groq"
    }
  }'
```

**Request Schema:**

```json
{
  "file_path": "string (optional)",
  "provider_config": {
    "provider": "groq",
    "temperature": 0.0
  }
}
```

**Response:** `200 OK`

```json
{
  "excel_file_path": "E:\\...\\output\\classified_messages.xlsx",
  "preview_results": [
    {
      "message": "SOS: Trapped on roof!",
      "district": "Gampaha",
      "intent": "Rescue",
      "priority": "High",
      "raw_output": "District: Gampaha | Intent: Rescue | Priority: High",
      "confidence": null
    }
  ],
  "total_processed": 99,
  "total_latency_ms": 45000,
  "total_tokens_used": {
    "prompt_tokens": 14850,
    "completion_tokens": 1980,
    "total_tokens": 16830
  }
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `excel_file_path` | string | Path to generated Excel file |
| `preview_results` | array | First 5 classification results |
| `total_processed` | integer | Total number of messages processed |
| `total_latency_ms` | integer | Total processing time in milliseconds |
| `total_tokens_used` | object | Aggregate token usage |

**Input File Format:**

```text
SOS: 5 people trapped on roof in Ja-Ela!
Need dry rations for camp in Gampaha.
Road cleared near Peradeniya.
```

- One message per line
- UTF-8 encoding
- Empty lines are skipped

**Output Excel Columns:**

| Column | Description |
|--------|-------------|
| Message | Original message text |
| District | Identified district |
| Intent | Message intent category |
| Priority | Priority level |
| Raw Output | Raw LLM classification |

---

## Part 2: Temperature Analysis

Analyze model consistency across different temperature values to demonstrate the importance of deterministic outputs in crisis systems.

### POST /api/v1/temperature/analyze

Analyze temperature stability for a single scenario.

**Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/temperature/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "SCENARIO: 5 people trapped on roof (immediate danger) vs. diabetic patient needs insulin (medical emergency). Which to prioritize?",
    "temperatures": [0.0, 1.0],
    "iterations_per_temperature": 3,
    "provider_config": {
      "provider": "groq"
    }
  }'
```

**Request Schema:**

```json
{
  "scenario": "string (required)",
  "temperatures": [0.0, 1.0],
  "iterations_per_temperature": 3,
  "provider_config": {
    "provider": "groq"
  }
}
```

**Response:** `200 OK`

```json
{
  "scenario": "SCENARIO: 5 people trapped on roof...",
  "results": [
    {
      "temperature": 0.0,
      "responses": [
        "Prioritize the 5 people trapped on roof (immediate danger)",
        "Prioritize the 5 people trapped on roof (immediate danger)",
        "Prioritize the 5 people trapped on roof (immediate danger)"
      ],
      "consistency": "100.0%",
      "unique_responses": 1
    },
    {
      "temperature": 1.0,
      "responses": [
        "Prioritize the 5 people trapped on roof",
        "Prioritize the diabetic patient",
        "Both are critical, but prioritize roof rescue"
      ],
      "consistency": "33.3%",
      "unique_responses": 3
    }
  ],
  "recommendation": "Use temperature=0.0 for deterministic crisis decisions",
  "total_latency_ms": 3500,
  "total_tokens_used": {
    "prompt_tokens": 600,
    "completion_tokens": 180,
    "total_tokens": 780
  }
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `scenario` | string | Original scenario text |
| `results` | array | Results for each temperature value |
| `results[].temperature` | float | Temperature value tested |
| `results[].responses` | array | All responses at this temperature |
| `results[].consistency` | string | Percentage of identical responses |
| `results[].unique_responses` | integer | Number of unique responses |
| `recommendation` | string | Recommended temperature setting |
| `total_latency_ms` | integer | Total processing time |
| `total_tokens_used` | object | Aggregate token usage |

**Key Insight:**

Temperature=0.0 produces **100% consistent** outputs, essential for life-critical decisions where determinism is required.

---

### POST /api/v1/temperature/analyze-batch

Analyze temperature stability for all scenarios from a file.

**Features:**
- ✅ Reads from `data/Scenarios.txt` by default
- ✅ Tests each scenario with 3 runs at temp=1.0 vs 1 run at temp=0.0
- ✅ Demonstrates consistency differences

**Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/temperature/analyze-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_config": {
      "provider": "groq"
    }
  }'
```

**Request Schema:**

```json
{
  "provider_config": {
    "provider": "groq"
  }
}
```

**Response:** `200 OK`

```json
{
  "results": [
    {
      "scenario": "SCENARIO: 5 people trapped on roof...",
      "temp_0_response": "Prioritize the 5 people trapped on roof",
      "temp_1_responses": [
        "Prioritize the 5 people trapped on roof",
        "Prioritize the diabetic patient",
        "Both are critical"
      ],
      "consistency_at_temp_1": "33.3%",
      "recommendation": "Use temperature=0.0"
    }
  ],
  "total_scenarios": 3,
  "total_latency_ms": 10500,
  "total_tokens_used": {
    "prompt_tokens": 1800,
    "completion_tokens": 540,
    "total_tokens": 2340
  }
}
```

**Input File Format:**

```text
SCENARIO: 5 people trapped on roof vs. diabetic patient needs insulin. Which to prioritize?
SCENARIO: Rescue 3 elderly people vs. deliver food to 50 people. Which first?
SCENARIO: Clear blocked road vs. rescue 2 people from flooded house. Which to prioritize?
```

---

## Part 3: Resource Allocation

Optimize rescue routes using Chain-of-Thought (CoT) and Tree-of-Thought (ToT) reasoning.

### POST /api/v1/resource-allocation/score

Score a single incident using Chain-of-Thought reasoning.

**Scoring Logic:**
- Base score: 5
- +2 for elderly/children
- +3 for rescue operations
- +1 for medical needs

**Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/resource-allocation/score" \
  -H "Content-Type: application/json" \
  -d '{
    "incident": {
      "location": "Ja-Ela",
      "description": "5 elderly people trapped on roof",
      "people_affected": 5,
      "need_type": "Rescue"
    },
    "provider_config": {
      "provider": "groq"
    }
  }'
```

**Request Schema:**

```json
{
  "incident": {
    "location": "string (required)",
    "description": "string (required)",
    "people_affected": 5,
    "need_type": "Rescue"
  },
  "provider_config": {
    "provider": "groq"
  }
}
```

**Response:** `200 OK`

```json
{
  "incident": {
    "location": "Ja-Ela",
    "description": "5 elderly people trapped on roof",
    "people_affected": 5,
    "need_type": "Rescue"
  },
  "score": 10,
  "reasoning": "Base:5 + Elderly:2 + Rescue:3 = 10",
  "latency_ms": 1200,
  "tokens_used": {
    "prompt_tokens": 200,
    "completion_tokens": 50,
    "total_tokens": 250
  }
}
```

---

### POST /api/v1/resource-allocation/optimize-route

Optimize rescue route using Tree-of-Thought reasoning.

**Strategies Explored:**
1. **Highest priority first** (greedy approach)
2. **Closest location first** (minimize travel time)
3. **Furthest location first** (logistics optimization)

**Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/resource-allocation/optimize-route" \
  -H "Content-Type: application/json" \
  -d '{
    "scored_incidents": [
      {
        "incident": {
          "location": "Ja-Ela",
          "description": "5 people trapped on roof",
          "people_affected": 5,
          "need_type": "Rescue"
        },
        "score": 10,
        "reasoning": "Base:5 + Rescue:3 + Elderly:2 = 10"
      }
    ],
    "starting_location": "Ragama",
    "travel_times": {
      "Ragama->Ja-Ela": 10,
      "Ja-Ela->Gampaha": 40,
      "Ragama->Gampaha": 30
    },
    "provider_config": {
      "provider": "groq"
    }
  }'
```

**Response:** `200 OK`

```json
{
  "optimal_route": ["Ja-Ela", "Gampaha"],
  "strategy_used": "Highest priority first",
  "reasoning": "Prioritize highest-scoring incidents to save most lives",
  "estimated_total_time": 50,
  "total_priority_score": 18,
  "latency_ms": 2000,
  "tokens_used": {
    "prompt_tokens": 400,
    "completion_tokens": 100,
    "total_tokens": 500
  }
}
```

---

### POST /api/v1/resource-allocation/process-batch

Process all incidents from file with CoT scoring and ToT route optimization.

**Features:**
- ✅ Reads from `data/Incidents.txt`
- ✅ Scores each incident with CoT reasoning
- ✅ Optimizes route with ToT reasoning
- ✅ Default starting location: Ragama

**Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/resource-allocation/process-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "starting_location": "Ragama",
    "provider_config": {
      "provider": "groq"
    }
  }'
```

**Request Schema:**

```json
{
  "starting_location": "Ragama",
  "travel_times": {
    "Ragama->Ja-Ela": 10,
    "Ja-Ela->Gampaha": 40,
    "Ragama->Gampaha": 30
  },
  "provider_config": {
    "provider": "groq"
  }
}
```

**Response:** `200 OK`

```json
{
  "scored_incidents": [
    {
      "incident": {
        "location": "Ja-Ela",
        "description": "5 elderly people trapped on roof",
        "people_affected": 5,
        "need_type": "Rescue"
      },
      "score": 10,
      "reasoning": "Base:5 + Elderly:2 + Rescue:3 = 10"
    }
  ],
  "optimal_route": ["Ja-Ela", "Gampaha"],
  "strategy_used": "Highest priority first",
  "route_reasoning": "Prioritize highest-scoring incidents",
  "estimated_total_time": 50,
  "total_priority_score": 18,
  "total_latency_ms": 5000,
  "total_tokens_used": {
    "prompt_tokens": 800,
    "completion_tokens": 200,
    "total_tokens": 1000
  }
}
```

**Input File Format:**

```text
Location: Ja-Ela | Description: 5 elderly people trapped on roof | People: 5 | Need: Rescue
Location: Gampaha | Description: Diabetic patient needs insulin | People: 1 | Need: Medical
Location: Colombo | Description: Food supplies needed for 50 people | People: 50 | Need: Supply
```

---

## Part 4: Token Management

Prevent spam and reduce costs with intelligent token filtering.

### POST /api/v1/tokens/check

Check message token count and apply spam filtering.

**Strategies:**
- **truncate**: Fast token-based truncation (may lose context)
- **summarize**: Intelligent LLM-based summarization (preserves key info)

**Request (Truncate Strategy):**

```bash
curl -X POST "http://localhost:8000/api/v1/tokens/check" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "URGENT HELP NEEDED! Please forward this message to everyone you know. We need immediate assistance in Colombo district. This is a very long message that exceeds the token limit and needs to be truncated to prevent spam and reduce costs.",
    "max_tokens": 50,
    "strategy": "truncate",
    "provider_config": {
      "provider": "groq"
    }
  }'
```

**Request (Summarize Strategy):**

```bash
curl -X POST "http://localhost:8000/api/v1/tokens/check" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "URGENT HELP NEEDED! Please forward this message to everyone you know. We need immediate assistance in Colombo district. This is a very long message that exceeds the token limit.",
    "max_tokens": 50,
    "strategy": "summarize",
    "provider_config": {
      "provider": "groq"
    }
  }'
```

**Request Schema:**

```json
{
  "message": "string (required, 1-100000 chars)",
  "max_tokens": 150,
  "strategy": "truncate",
  "provider_config": {
    "provider": "groq"
  }
}
```

**Response (Accepted):** `200 OK`

```json
{
  "result": {
    "status": "ACCEPTED",
    "original_token_count": 45,
    "processed_token_count": 45,
    "processed_message": "URGENT HELP NEEDED! We need assistance in Colombo.",
    "action": "None",
    "tokens_saved": 0
  },
  "latency_ms": 50
}
```

**Response (Truncated):** `200 OK`

```json
{
  "result": {
    "status": "BLOCKED/TRUNCATED",
    "original_token_count": 120,
    "processed_token_count": 50,
    "processed_message": "URGENT HELP NEEDED! Please forward this message to everyone... [TRUNCATED]",
    "action": "Truncated",
    "tokens_saved": 70
  },
  "latency_ms": 100
}
```

**Response (Summarized):** `200 OK`

```json
{
  "result": {
    "status": "SUMMARIZED",
    "original_token_count": 120,
    "processed_token_count": 35,
    "processed_message": "Urgent assistance needed in Colombo district for immediate help.",
    "action": "Intelligently Summarized",
    "tokens_saved": 85
  },
  "latency_ms": 1500
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `result.status` | string | "ACCEPTED" \| "BLOCKED/TRUNCATED" \| "SUMMARIZED" |
| `result.original_token_count` | integer | Original message token count |
| `result.processed_token_count` | integer | Processed message token count |
| `result.processed_message` | string | Processed message text |
| `result.action` | string | Action taken |
| `result.tokens_saved` | integer | Number of tokens saved |
| `latency_ms` | integer | Processing time in milliseconds |

**Filter Decisions:**

| Status | When | Action |
|--------|------|--------|
| **ACCEPTED** | Token count ≤ max_tokens | No modification |
| **BLOCKED/TRUNCATED** | Token count > max_tokens, strategy="truncate" | Truncate to max_tokens |
| **SUMMARIZED** | Token count > max_tokens, strategy="summarize" | LLM summarization |

---

## Part 5: News Processing

Extract structured crisis events from unstructured news feeds.

### POST /api/v1/news/process

Process a single news item into structured crisis event.

**Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/news/process" \
  -H "Content-Type: application/json" \
  -d '{
    "news_item": {
      "text": "SOS: 5 people trapped on a roof in Ja-Ela (Gampaha). Water rising fast. Flood level at 2.5 meters.",
      "source": "Twitter",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    "provider_config": {
      "provider": "groq"
    }
  }'
```

**Request Schema:**

```json
{
  "news_item": {
    "text": "string (required)",
    "source": "string (optional)",
    "timestamp": "string (optional, ISO 8601)"
  },
  "provider_config": {
    "provider": "groq"
  }
}
```

**Response (Success):** `200 OK`

```json
{
  "event": {
    "district": "Gampaha",
    "flood_level_meters": 2.5,
    "victim_count": 5,
    "main_need": "Rescue",
    "status": "Critical"
  },
  "success": true,
  "error": null,
  "latency_ms": 1500,
  "tokens_used": {
    "prompt_tokens": 250,
    "completion_tokens": 80,
    "total_tokens": 330
  }
}
```

**Response (Failure):** `200 OK`

```json
{
  "event": null,
  "success": false,
  "error": "Failed to extract structured data from news text",
  "latency_ms": 1200,
  "tokens_used": {
    "prompt_tokens": 250,
    "completion_tokens": 50,
    "total_tokens": 300
  }
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `event` | object \| null | Extracted crisis event (null if failed) |
| `event.district` | string | "Colombo" \| "Gampaha" \| "Kandy" \| etc. |
| `event.flood_level_meters` | float \| null | Flood level in meters |
| `event.victim_count` | integer | Number of people affected |
| `event.main_need` | string | Primary need or emergency type |
| `event.status` | string | "Critical" \| "Warning" \| "Stable" |
| `success` | boolean | Whether extraction succeeded |
| `error` | string \| null | Error message if failed |
| `latency_ms` | integer | Processing time |
| `tokens_used` | object | Token usage statistics |

---

### POST /api/v1/news/process/batch

Process multiple news items in batch from a file.

**Features:**
- ✅ Reads from `data/News Feed.txt` by default
- ✅ Supports custom file paths (absolute or relative)
- ✅ Generates Excel output: `output/flood_report.xlsx`
- ✅ Returns preview of first 5 successful extractions
- ✅ Includes success/failure statistics

**Request (Default File):**

```bash
curl -X POST "http://localhost:8000/api/v1/news/process/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_config": {
      "provider": "groq"
    }
  }'
```

**Request (Custom File Path):**

```bash
curl -X POST "http://localhost:8000/api/v1/news/process/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "E:\\\\path\\\\to\\\\custom\\\\news.txt",
    "provider_config": {
      "provider": "groq"
    }
  }'
```

**Request Schema:**

```json
{
  "file_path": "string (optional)",
  "provider_config": {
    "provider": "groq"
  }
}
```

**Response:** `200 OK`

```json
{
  "excel_file_path": "E:\\...\\output\\flood_report.xlsx",
  "preview_events": [
    {
      "district": "Gampaha",
      "flood_level_meters": 2.5,
      "victim_count": 5,
      "main_need": "Rescue",
      "status": "Critical"
    }
  ],
  "total_processed": 10,
  "successful_extractions": 8,
  "failed_extractions": 2,
  "success_rate": "80.0%",
  "total_latency_ms": 15000,
  "total_tokens_used": {
    "prompt_tokens": 2500,
    "completion_tokens": 800,
    "total_tokens": 3300
  }
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `excel_file_path` | string | Path to generated Excel file |
| `preview_events` | array | First 5 successful extractions |
| `total_processed` | integer | Total news items processed |
| `successful_extractions` | integer | Number of successful extractions |
| `failed_extractions` | integer | Number of failed extractions |
| `success_rate` | string | Success rate percentage |
| `total_latency_ms` | integer | Total processing time |
| `total_tokens_used` | object | Aggregate token usage |

**Input File Format:**

```text
SOS: 5 people trapped on roof in Ja-Ela (Gampaha). Water rising fast. Flood level at 2.5m.
BREAKING: Kelani River (Colombo) at 9.5 meters. Critical flood warning issued.
Update: Kandy road cleared near Peradeniya. No victims reported.
```

**Output Excel Columns:**

| Column | Description |
|--------|-------------|
| District | District where event occurred |
| Flood Level (m) | Flood level in meters |
| Victim Count | Number of people affected |
| Main Need | Primary need or emergency type |
| Status | Event status (Critical/Warning/Stable) |

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| **200** | OK | Request successful |
| **400** | Bad Request | Invalid request payload |
| **404** | Not Found | File not found (batch endpoints) |
| **422** | Unprocessable Entity | Validation error |
| **500** | Internal Server Error | Processing error |

### Error Response Format

All errors return a JSON response with a `detail` field:

```json
{
  "detail": "Human-readable error message"
}
```

### Common Errors

#### 1. File Not Found (404)

**Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/classification/classify/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "data/nonexistent.txt",
    "provider_config": {"provider": "groq"}
  }'
```

**Response:** `404 Not Found`

```json
{
  "detail": "Input file not found: E:\\...\\data\\nonexistent.txt"
}
```

#### 2. Validation Error (422)

**Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/classification/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "",
    "provider_config": {"provider": "groq"}
  }'
```

**Response:** `422 Unprocessable Entity`

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "message"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

#### 3. Processing Error (500)

**Response:** `500 Internal Server Error`

```json
{
  "detail": "Classification failed: API key not configured"
}
```

---

## Rate Limiting & Performance

### Performance Characteristics

| Endpoint | Avg Latency | Throughput |
|----------|-------------|------------|
| Single classification | ~1-2s | ~30-60 req/min |
| Batch classification (99 items) | ~45-60s | ~1-2 batches/min |
| Temperature analysis | ~3-5s | ~12-20 req/min |
| Resource allocation | ~5-10s | ~6-12 req/min |
| Token check | ~0.05-1.5s | ~40-1200 req/min |
| News processing | ~1.5-3s | ~20-40 req/min |

### Optimization Tips

1. **Use Groq for Development** - Fastest inference times
2. **Batch Processing** - More efficient than individual requests
3. **Temperature=0.0** - Faster and more consistent
4. **Truncate vs Summarize** - Truncate is 10-30x faster
5. **Parallel Requests** - API supports concurrent requests

### Rate Limits

Rate limits depend on your LLM provider:

| Provider | Free Tier Limit | Paid Tier Limit |
|----------|----------------|-----------------|
| **Groq** | 30 req/min | Higher limits available |
| **OpenAI** | Varies by tier | Varies by tier |
| **Google Gemini** | 60 req/min | Higher limits available |

---

## Integration Examples

### Python Integration

```python
import requests

# Configuration
BASE_URL = "http://localhost:8000"
PROVIDER = "groq"

# Single message classification
def classify_message(message: str):
    response = requests.post(
        f"{BASE_URL}/api/v1/classification/classify",
        json={
            "message": message,
            "provider_config": {"provider": PROVIDER}
        }
    )
    return response.json()

# Batch classification
def classify_batch(file_path: str = None):
    payload = {"provider_config": {"provider": PROVIDER}}
    if file_path:
        payload["file_path"] = file_path

    response = requests.post(
        f"{BASE_URL}/api/v1/classification/classify/batch",
        json=payload
    )
    return response.json()

# Usage
result = classify_message("SOS: Trapped on roof in Ja-Ela!")
print(f"District: {result['result']['district']}")
print(f"Intent: {result['result']['intent']}")
print(f"Priority: {result['result']['priority']}")

# Batch processing
batch_result = classify_batch()
print(f"Processed {batch_result['total_processed']} messages")
print(f"Excel file: {batch_result['excel_file_path']}")
```

### JavaScript Integration

```javascript
const BASE_URL = "http://localhost:8000";
const PROVIDER = "groq";

// Single message classification
async function classifyMessage(message) {
  const response = await fetch(`${BASE_URL}/api/v1/classification/classify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: message,
      provider_config: { provider: PROVIDER }
    })
  });
  return await response.json();
}

// Batch classification
async function classifyBatch(filePath = null) {
  const payload = { provider_config: { provider: PROVIDER } };
  if (filePath) {
    payload.file_path = filePath;
  }

  const response = await fetch(`${BASE_URL}/api/v1/classification/classify/batch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return await response.json();
}

// Usage
classifyMessage("SOS: Trapped on roof in Ja-Ela!")
  .then(result => {
    console.log(`District: ${result.result.district}`);
    console.log(`Intent: ${result.result.intent}`);
    console.log(`Priority: ${result.result.priority}`);
  });

classifyBatch()
  .then(result => {
    console.log(`Processed ${result.total_processed} messages`);
    console.log(`Excel file: ${result.excel_file_path}`);
  });
```

### cURL Integration (Bash Script)

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"
PROVIDER="groq"

# Single message classification
classify_message() {
  local message="$1"
  curl -X POST "$BASE_URL/api/v1/classification/classify" \
    -H "Content-Type: application/json" \
    -d "{
      \"message\": \"$message\",
      \"provider_config\": {\"provider\": \"$PROVIDER\"}
    }"
}

# Batch classification
classify_batch() {
  local file_path="$1"
  local payload="{\"provider_config\": {\"provider\": \"$PROVIDER\"}"

  if [ -n "$file_path" ]; then
    payload="${payload}, \"file_path\": \"$file_path\""
  fi
  payload="${payload}}"

  curl -X POST "$BASE_URL/api/v1/classification/classify/batch" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# Usage
classify_message "SOS: Trapped on roof in Ja-Ela!"
classify_batch
classify_batch "data/custom_messages.txt"
```

---

## Interactive Testing

### Swagger UI

Visit <http://localhost:8000/docs> for interactive API documentation where you can:

1. **Browse all endpoints** - Complete API catalog
2. **View schemas** - Request/response models
3. **Try it out** - Execute requests directly in browser
4. **See examples** - Pre-filled example payloads
5. **Download OpenAPI spec** - For code generation

### ReDoc

Visit <http://localhost:8000/redoc> for alternative documentation with:

1. **Clean layout** - Easy-to-read format
2. **Code samples** - Multiple languages
3. **Search functionality** - Find endpoints quickly
4. **Downloadable spec** - OpenAPI 3.0 specification

---

## Best Practices

### 1. Use Appropriate Temperature

| Use Case | Recommended Temperature |
|----------|------------------------|
| Classification | 0.0 (deterministic) |
| Extraction | 0.0 (consistent) |
| Scoring | 0.0-0.3 (mostly deterministic) |
| Route optimization | 0.3-0.5 (some creativity) |
| Summarization | 0.5-0.7 (balanced) |

### 2. Handle Errors Gracefully

```python
try:
    result = classify_message("SOS: Help!")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("File not found")
    elif e.response.status_code == 500:
        print("Processing error")
    else:
        print(f"Error: {e}")
```

### 3. Use Batch Processing

For multiple items, always use batch endpoints:
- ✅ More efficient
- ✅ Single Excel output
- ✅ Aggregate statistics
- ✅ Better error handling

### 4. Validate File Paths

Before calling batch endpoints, verify files exist:

```python
from pathlib import Path

file_path = "data/Sample Messages.txt"
if not Path(file_path).exists():
    print(f"File not found: {file_path}")
else:
    result = classify_batch(file_path)
```

### 5. Monitor Token Usage

Track token usage to optimize costs:

```python
result = classify_message("SOS: Help!")
tokens = result['tokens_used']['total_tokens']
print(f"Tokens used: {tokens}")
```

---

## Appendix

### File Path Support

Both classification and news processing batch endpoints support custom file paths:

**Absolute Path (Windows):**

```json
{
  "file_path": "E:\\\\ZuuCrew\\\\data\\\\messages.txt"
}
```

**Absolute Path (Linux/Mac):**

```json
{
  "file_path": "/home/user/data/messages.txt"
}
```

**Relative Path:**

```json
{
  "file_path": "data/custom_messages.txt"
}
```

**Default (No file_path):**

```json
{
  "provider_config": {"provider": "groq"}
}
```

### Supported Districts

| District | Region |
|----------|--------|
| Colombo | Western Province |
| Gampaha | Western Province |
| Kandy | Central Province |
| Kalutara | Western Province |
| Galle | Southern Province |
| Matara | Southern Province |
| Ratnapura | Sabaragamuwa Province |
| Other | Unspecified |

### Intent Categories

| Intent | Priority | Example |
|--------|----------|---------|
| **Rescue** | High | "SOS: Trapped on roof!" |
| **Supply** | Low | "Need dry rations" |
| **Info** | Low | "Road cleared" |
| **Other** | Low | "Please forward" |

---

## Support & Resources

### Documentation

- **README.md** - Project overview and quick start
- **API_CURL_COMMANDS.md** - Complete cURL command reference
- **Interactive Docs** - <http://localhost:8000/docs>

### API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/v1/classification/classify` | POST | Single message classification |
| `/api/v1/classification/classify/batch` | POST | Batch message classification |
| `/api/v1/temperature/analyze` | POST | Single temperature analysis |
| `/api/v1/temperature/analyze-batch` | POST | Batch temperature analysis |
| `/api/v1/resource-allocation/score` | POST | Score single incident |
| `/api/v1/resource-allocation/optimize-route` | POST | Optimize rescue route |
| `/api/v1/resource-allocation/process-batch` | POST | Batch resource allocation |
| `/api/v1/tokens/check` | POST | Token check and spam filter |
| `/api/v1/news/process` | POST | Process single news item |
| `/api/v1/news/process/batch` | POST | Batch news processing |

### External Resources

- **OpenAI API**: <https://platform.openai.com/docs>
- **Google Gemini**: <https://ai.google.dev/docs>
- **Groq**: <https://console.groq.com/docs>
- **FastAPI**: <https://fastapi.tiangolo.com/>
- **Pydantic**: <https://docs.pydantic.dev/>

---

**Last Updated:** 2026-01-15
**API Version:** 1.0.0
**Built with ❤️ for crisis response and disaster relief operations**



