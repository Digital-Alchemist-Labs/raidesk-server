# RAiDesk Backend Server

AI-powered medical device regulatory assistant backend built with FastAPI, LangChain, and LangGraph.

## Features

### Core Features
- **Device Classification**: Analyzes device concepts to determine medical device status and risk classification
- **Purpose & Mechanism**: Generates detailed technical documentation for intended use and mechanism of action
- **4-Tier Planning**: Creates comprehensive regulatory strategies (Fastest, Normal, Conservative, Innovative)
- **Plan Refinement**: Refines plans based on user feedback and requirements
- **LangGraph Integration**: Stateful agent workflows for complex multi-step processes
- **Ollama Support**: Local LLM inference using Ollama

### New Enterprise Features ✨
- **Session Management**: Track user sessions with persistent storage and automatic expiration
- **Plan Storage & Versioning**: Automatic plan storage with full version history
- **Advanced Error Handling**: Structured error responses with detailed debugging information
- **Rate Limiting**: Protect your API from abuse with configurable rate limits
- **Structured Logging**: JSON logging with request IDs and performance metrics
- **Flexible Storage**: Choose between SQLite (development) or Redis (production)
- **CORS Configuration**: Environment-based CORS for development and production
- **🔥 Streaming Support (SSE)**: Real-time LLM response streaming for better UX

📖 **See [SERVER_FEATURES.md](SERVER_FEATURES.md) for complete documentation**  
📖 **See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for integration guide**  
📖 **See [STREAMING_GUIDE.md](STREAMING_GUIDE.md) for streaming implementation** 🆕

## Architecture

```
raidesk-server/
├── app/
│   ├── agents/              # LangGraph-based agents
│   │   ├── classifier.py       # Device classification
│   │   ├── purpose.py          # Purpose & mechanism
│   │   ├── planner.py          # Plan generation
│   │   └── refiner.py          # Plan refinement
│   ├── routers/             # FastAPI routers
│   │   ├── classify.py         # Classification endpoint
│   │   ├── purpose.py          # Purpose generation endpoint
│   │   ├── standards.py        # Plan generation endpoint
│   │   ├── refine.py           # Plan refinement endpoint
│   │   ├── sessions.py         # Session management ✨
│   │   └── plans.py            # Plan management ✨
│   ├── storage/             # Storage layer ✨
│   │   ├── base.py             # Storage interface
│   │   ├── sqlite_adapter.py   # SQLite implementation
│   │   ├── redis_adapter.py    # Redis implementation
│   │   ├── session_manager.py  # Session management
│   │   └── plan_repository.py  # Plan storage & versioning
│   ├── middleware/          # Middleware components ✨
│   │   ├── error_handler.py    # Global error handling
│   │   ├── logging.py          # Structured logging
│   │   └── rate_limiter.py     # Rate limiting
│   ├── config.py            # Configuration
│   ├── models.py            # Pydantic models
│   ├── prompts.py           # Prompt templates
│   ├── exceptions.py        # Custom exceptions ✨
│   ├── dependencies.py      # Dependency injection ✨
│   └── main.py              # Main FastAPI app
├── requirements.txt
├── env.example              # Environment template ✨
├── README.md
├── SERVER_FEATURES.md       # Complete feature docs ✨
└── MIGRATION_GUIDE.md       # Integration guide ✨
```

## Prerequisites

- Python 3.10+
- Ollama with GPT-OSS model

### Install Ollama and GPT-OSS

```bash
# Install Ollama (if not already installed)
# Visit https://ollama.ai for installation instructions

# Pull GPT-OSS model
ollama pull gpt-oss
```

## Installation

1. **Clone the repository**

```bash
cd /Users/jaylee_83/Documents/_itsjayspace/git_clones/raidesk-server
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment**

```bash
cp env.example .env
# Edit .env file with your settings
```

## Configuration

Edit `.env` file:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gpt-oss

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Storage (SQLite for development, Redis for production)
STORAGE_TYPE=sqlite
DATABASE_PATH=./raidesk.db
# REDIS_URL=redis://localhost:6379

# Session & Plan TTL
SESSION_TTL=86400    # 24 hours
PLAN_TTL=604800      # 7 days

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# LangSmith (Optional - for debugging)
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=your_api_key_here
# LANGCHAIN_PROJECT=raidesk
```

📖 **See [env.example](env.example) for complete configuration options**

## Running the Server

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Run with auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or simply:

```bash
python app/main.py
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check

```
GET /         # API information
GET /health   # Health status with storage check
```

### Device Classification

```
POST /api/classify
```

**Request:**
```json
{
  "concept": "CT 영상에서 폐결절을 자동으로 검출하는 AI 소프트웨어",
  "context": "추가 컨텍스트 (선택사항)"
}
```

**Response:**
```json
{
  "classification": {
    "isMedicalDevice": true,
    "reasoning": "판단 근거",
    "confidence": 0.92,
    "category": "영상의학 진단보조 소프트웨어",
    "riskClass": "II"
  },
  "suggestedCategories": [...]
}
```

### Purpose & Mechanism

```
POST /api/purpose
```

**Request:**
```json
{
  "concept": "폐결절 검출 AI",
  "category": "영상의학 진단보조 소프트웨어"
}
```

**Response:**
```json
{
  "intendedUse": "사용 목적",
  "mechanismOfAction": "작용 원리",
  "targetPopulation": "대상 환자군",
  "clinicalBenefit": "임상적 이점",
  "contraindications": ["금기사항"]
}
```

### Generate Plans

```
POST /api/standards
```

**Request:**
```json
{
  "classification": {...},
  "category": {...},
  "purposeMechanism": {...}
}
```

**Response:**
```json
{
  "plans": [
    {
      "id": "plan-fastest",
      "tier": "fastest",
      "title": "최단 경로",
      "description": "...",
      "totalDuration": "6개월",
      "estimatedCost": "1억 ~ 1.5억원",
      "riskLevel": "high",
      "commonStandards": {...},
      "performanceEvaluation": {...},
      "pros": [...],
      "cons": [...],
      "recommendations": [...]
    },
    ...
  ]
}
```

### Refine Plan

```
POST /api/refine
```

**Request:**
```json
{
  "planId": "plan-fastest",
  "modifications": "비용을 더 낮추고 싶습니다",
  "context": {
    "budget": 100000000
  }
}
```

> **Note:** Plans are now automatically retrieved from storage. No need to send `original_plan` in context!

### Session Management ✨

```
POST   /api/sessions              # Create session
GET    /api/sessions              # List sessions
GET    /api/sessions/{id}         # Get session
PUT    /api/sessions/{id}         # Update session
DELETE /api/sessions/{id}         # Delete session
```

### Plan Management ✨

```
GET    /api/plans                 # List all plans
GET    /api/plans/{id}            # Get plan
GET    /api/plans/{id}?version=1  # Get specific version
GET    /api/plans/{id}/record     # Get version history
DELETE /api/plans/{id}            # Delete plan
```

### Streaming Endpoints 🔥

Real-time streaming for better user experience:

```
POST   /api/stream/classify       # Stream classification results
POST   /api/stream/purpose        # Stream purpose generation
POST   /api/stream/standards      # Stream plan generation
POST   /api/stream/refine         # Stream plan refinement
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/api/stream/classify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ concept: '스마트 인슐린 펌프' })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  console.log('Stream:', chunk);
}
```

📖 **See [STREAMING_GUIDE.md](STREAMING_GUIDE.md) for complete examples and React hooks**

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Technologies

- **[FastAPI](https://fastapi.tiangolo.com/)**: Modern, fast web framework
- **[LangChain](https://docs.langchain.com/oss/python/langchain/overview)**: LLM application framework
- **[LangGraph](https://docs.langchain.com/oss/python/langgraph/overview)**: State machine for agent workflows
- **[Ollama](https://ollama.ai)**: Local LLM inference
- **[Pydantic](https://docs.pydantic.dev/)**: Data validation

## LangGraph Agent Architecture

Each endpoint uses a LangGraph agent for stateful processing:

1. **Classifier Agent**: Multi-step classification with reasoning
2. **Purpose Agent**: Generates comprehensive technical documentation
3. **Planner Agent**: Creates 4 parallel regulatory strategies
4. **Refiner Agent**: Iteratively improves plans based on feedback

### Example Agent Flow

```python
from langgraph.graph import StateGraph, START, END

workflow = StateGraph(State)
workflow.add_node("classify", classify_node)
workflow.add_edge(START, "classify")
workflow.add_edge("classify", END)
agent = workflow.compile()

result = await agent.ainvoke({"concept": "..."})
```

## Development

### Project Structure

```python
app/
├── agents/          # LangGraph agents
├── routers/         # FastAPI endpoints
├── config.py        # Settings
├── models.py        # Pydantic schemas
├── prompts.py       # LLM prompts
└── main.py          # App entry point
```

### Adding a New Agent

1. Create agent file in `app/agents/`
2. Define state using `TypedDict`
3. Create nodes and edges
4. Compile workflow with `StateGraph`
5. Export agent function

### Adding a New Endpoint

1. Create router in `app/routers/`
2. Define request/response models in `app/models.py`
3. Import agent function
4. Add router to `app/main.py`

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama (if not running)
ollama serve
```

### Model Not Found

```bash
# List available models
ollama list

# Pull GPT-OSS if missing
ollama pull gpt-oss
```

### CORS Issues

Update `CORS_ORIGINS` in `.env` to include your frontend URL:

```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

## License

See LICENSE file for details.

## References

- [LangChain Documentation](https://docs.langchain.com/oss/python/langchain/overview)
- [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph/overview)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ollama Documentation](https://github.com/ollama/ollama)

## Support

For issues and questions, please open an issue on GitHub.
