# 🚨 Crisis Intelligence Pipeline - Operation Ditwah

**Production-ready API for crisis intelligence processing in post-disaster scenarios**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 Overview

The **Crisis Intelligence Pipeline** is a comprehensive AI-powered system designed for post-disaster relief operations. Built for **Operation Ditwah** (post-cyclone relief in Sri Lanka), this API processes crisis messages, analyzes resource allocation, and extracts structured information from news feeds to support emergency response teams.

### 🎯 Key Features

- **🔍 Message Classification** - Distinguish real SOS calls from noise using few-shot learning
- **🌡️ Temperature Analysis** - Ensure deterministic outputs for life-critical decisions
- **🚁 Resource Allocation** - Optimize rescue routes with Chain-of-Thought (CoT) & Tree-of-Thought (ToT) reasoning
- **🛡️ Token Management** - Prevent spam and reduce costs with intelligent filtering
- **📰 News Processing** - Extract structured crisis events from unstructured news feeds

---

## 📁 Project Structure

```
crisis_intelligence_pipeline/
├── data/                           # Input data files
│   ├── Sample Messages.txt         # 99 crisis messages for classification
│   ├── News Feed.txt               # 10 news items for extraction
│   ├── Scenarios.txt               # 3 decision scenarios for temperature testing
│   └── Incidents.txt               # 3 incidents for resource allocation
│
├── output/                         # Generated output files
│   ├── classified_messages.xlsx   # Classification results
│   └── flood_report.xlsx           # Extracted crisis events
│
├── src/app/                        # FastAPI application
│   ├── main.py                     # Application entry point
│   ├── api/                        # API route handlers
│   │   ├── classification.py       # Part 1: Message classification
│   │   ├── temperature.py          # Part 2: Temperature analysis
│   │   ├── resource_allocation.py  # Part 3: Resource allocation
│   │   ├── token_management.py     # Part 4: Token management
│   │   └── news_processing.py      # Part 5: News processing
│   ├── schemas/                    # Pydantic models
│   ├── services/                   # Business logic
│   └── utils/                      # Shared utilities
│
├── config/                         # Configuration files
│   ├── config.yaml                 # Application settings
│   └── models.yaml                 # LLM model configurations
│
├── notebooks/                      # Jupyter notebooks
│   └── operation_ditwah_crisis_pipeline.ipynb
│
├── logs/                           # Application logs
│   └── runs.csv                    # API call logs
│
├── .env                            # Environment variables (API keys)
├── pyproject.toml                  # Python dependencies
├── run_api.py                      # API startup script
├── README.md                       # This file
└── API_DOCUMENTATION.md            # Complete API reference
```

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+** installed
2. **At least one LLM API key** (OpenAI, Google Gemini, or Groq)
3. **Git** (for cloning the repository)

### Installation

#### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd "Mini Project 0 v1"
```

#### Step 2: Install Dependencies

Using **uv** (recommended):

```bash
uv sync
```

Or using **pip**:

```bash
pip install -e .
```

#### Step 3: Configure API Keys

Create a `.env` file in the project root:

```bash
# At least one API key is required
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
GROQ_API_KEY=your-groq-key-here
```

**Get API Keys:**
- **OpenAI**: <https://platform.openai.com/api-keys>
- **Google Gemini**: <https://aistudio.google.com/app/apikey>
- **Groq**: <https://console.groq.com/keys>

#### Step 4: Start the API Server

```bash
python run_api.py
```

Or with auto-reload for development:

```bash
python run_api.py --reload
```

The API will be available at:
- **API Base**: <http://localhost:8000>
- **Interactive Docs**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

---

## 🎓 API Features Explained

### Part 1: Message Classification (Few-Shot Learning)

**Objective:** Distinguish real SOS calls from news noise using few-shot learning.

**How it works:**
- Uses exactly 4 labeled examples covering all categories (Rescue, Supply, Info, Other)
- Classifies messages by district, intent, and priority
- Processes 99 messages in batch mode with Excel output

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/classification/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "SOS: 5 people trapped on roof in Ja-Ela!",
    "provider_config": {"provider": "groq"}
  }'
```

**Output Format:**
```
District: Gampaha | Intent: Rescue | Priority: High
```

**Batch Processing:**
- Reads from `data/Sample Messages.txt` (or custom file path)
- Generates `output/classified_messages.xlsx`
- Supports custom file paths (absolute or relative)

---

### Part 2: Temperature Analysis (Deterministic Outputs)

**Objective:** Demonstrate why temperature=0.0 is critical for crisis decision-making.

**How it works:**
- Tests 3 scenarios with different temperature values
- Compares 3 runs at temp=1.0 vs 1 run at temp=0.0
- Shows consistency differences for life-critical decisions

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/temperature/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "5 people trapped on roof vs diabetic patient needs insulin. Which to prioritize?",
    "temperatures": [0.0, 1.0],
    "iterations_per_temperature": 3,
    "provider_config": {"provider": "groq"}
  }'
```

**Key Insight:** Temperature=0.0 produces consistent, deterministic outputs essential for emergency response.

---

### Part 3: Resource Allocation (CoT & ToT Reasoning)

**Objective:** Optimize rescue routes using advanced reasoning techniques.

**How it works:**
- **Chain-of-Thought (CoT)**: Scores incidents with explicit reasoning
  - Base score: 5
  - +2 for elderly/children
  - +3 for rescue operations
  - +1 for medical needs
- **Tree-of-Thought (ToT)**: Explores 3 route optimization strategies
  1. Highest priority first (greedy)
  2. Closest location first (minimize travel)
  3. Furthest location first (logistics)

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/resource-allocation/process-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "starting_location": "Ragama",
    "provider_config": {"provider": "groq"}
  }'
```

**Batch Processing:**
- Reads from `data/Incidents.txt`
- Scores all incidents with CoT reasoning
- Optimizes route with ToT reasoning
- Returns optimal route with estimated time

---

### Part 4: Token Management (Spam Prevention)

**Objective:** Prevent spam and reduce costs with intelligent token filtering.

**How it works:**
- Counts tokens in messages
- Applies filtering strategies when over limit:
  - **Truncate**: Fast, simple token-based truncation
  - **Summarize**: Intelligent LLM-based summarization

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/tokens/check" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "URGENT HELP NEEDED! Please forward...",
    "max_tokens": 150,
    "strategy": "truncate",
    "provider_config": {"provider": "groq"}
  }'
```

**Strategies:**
- **ACCEPTED**: Message within token limit
- **BLOCKED/TRUNCATED**: Message truncated to fit limit
- **SUMMARIZED**: Message intelligently summarized

---

### Part 5: News Processing (Structured Extraction)

**Objective:** Extract structured crisis events from unstructured news feeds.

**How it works:**
- Parses news text into structured fields
- Extracts: district, flood level, victim count, main need, status
- Validates against predefined schema
- Handles extraction failures gracefully

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/news/process" \
  -H "Content-Type: application/json" \
  -d '{
    "news_item": {
      "text": "SOS: 5 people trapped on roof in Ja-Ela (Gampaha). Water rising fast.",
      "source": "Twitter",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    "provider_config": {"provider": "groq"}
  }'
```

**Batch Processing:**
- Reads from `data/News Feed.txt` (or custom file path)
- Generates `output/flood_report.xlsx`
- Includes success/failure statistics

---

## 🔧 Configuration

### Provider Selection

The API supports three LLM providers:

| Provider | Best For | Speed | Cost |
|----------|----------|-------|------|
| **Groq** | Fast inference, development | ⚡⚡⚡ | 💰 Free tier |
| **OpenAI** | Production, reliability | ⚡⚡ | 💰💰 Pay-per-use |
| **Google Gemini** | Multimodal, large context | ⚡⚡ | 💰 Free tier |

**Default Provider:** Groq (configured in `config/config.yaml`)

### Custom File Paths (New Feature!)

Both batch endpoints now support custom file paths:

```json
{
  "file_path": "E:\\path\\to\\custom\\messages.txt",
  "provider_config": {"provider": "groq"}
}
```

Supports:
- ✅ Absolute paths
- ✅ Relative paths (from project root)
- ✅ Backward compatible (defaults to standard paths)

---

## 📊 Output Files

All batch operations generate Excel files with detailed results:

### Classification Output (`output/classified_messages.xlsx`)

| Message | District | Intent | Priority | Raw Output |
|---------|----------|--------|----------|------------|
| SOS: Trapped on roof! | Gampaha | Rescue | High | District: Gampaha \| Intent: Rescue \| Priority: High |

### News Processing Output (`output/flood_report.xlsx`)

| District | Flood Level (m) | Victim Count | Main Need | Status |
|----------|-----------------|--------------|-----------|--------|
| Gampaha | 2.5 | 5 | Rescue | Critical |

---

## 🧪 Testing

### Interactive API Documentation

Visit <http://localhost:8000/docs> for interactive Swagger UI where you can:
- Test all endpoints directly in the browser
- View request/response schemas
- See example payloads
- Execute API calls with authentication

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "providers_available": ["groq", "openai", "google"]
}
```

### Complete cURL Examples

See [API_CURL_COMMANDS.md](API_CURL_COMMANDS.md) for comprehensive cURL examples for all endpoints.

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. API Key Not Found

**Error:** `No LLM API keys configured!`

**Solution:** Create `.env` file with at least one API key:

```bash
GROQ_API_KEY=your-key-here
```

#### 2. File Not Found

**Error:** `Input file not found: data/Sample Messages.txt`

**Solution:** Ensure input files exist in the `data/` directory or provide custom file path:

```json
{
  "file_path": "path/to/your/file.txt"
}
```

#### 3. Port Already in Use

**Error:** `Address already in use`

**Solution:** Use a different port:

```bash
python run_api.py --port 8080
```

#### 4. Module Import Errors

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:** Reinstall dependencies:

```bash
pip install -e .
```

---

## 📚 Documentation

### Complete Documentation

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference with all endpoints
- **[API_CURL_COMMANDS.md](API_CURL_COMMANDS.md)** - Ready-to-use cURL commands

### Additional Resources

- **OpenAI API**: <https://platform.openai.com/docs>
- **Google Gemini**: <https://ai.google.dev/docs>
- **Groq**: <https://console.groq.com/docs>
- **FastAPI**: <https://fastapi.tiangolo.com/>
- **Pydantic**: <https://docs.pydantic.dev/>

---

## 🎓 Learning Outcomes

This project demonstrates:

1. **Few-Shot Learning** - Effective classification with minimal examples
2. **Temperature Control** - Importance of deterministic outputs in crisis systems
3. **Advanced Reasoning** - Chain-of-Thought (CoT) and Tree-of-Thought (ToT) techniques
4. **Token Management** - Cost optimization and spam prevention
5. **Structured Extraction** - Converting unstructured text to structured data
6. **API Design** - Production-ready REST API with FastAPI
7. **Error Handling** - Robust error handling and validation
8. **Batch Processing** - Efficient processing of multiple items
9. **File I/O** - Reading inputs and generating Excel outputs
10. **Configuration Management** - Flexible provider and parameter configuration

---

## 🙏 Acknowledgments

- **Operation Ditwah** - Post-cyclone relief scenario (Sri Lanka)
- **FastAPI** - Modern web framework for building APIs
- **Pydantic** - Data validation using Python type annotations
- **OpenAI, Google, Groq** - LLM providers

---

## 📞 Support

For questions or issues:

1. Check the [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. Review [Troubleshooting](#-troubleshooting) section
3. Check API logs in `logs/runs.csv`
4. Test with interactive docs at <http://localhost:8000/docs>

---

**Built with ❤️ for crisis response and disaster relief operations**

