# RAiDesk Server - Feature Documentation

This document describes all the server-side features implemented in the RAiDesk backend.

## Table of Contents

1. [Session Management](#session-management)
2. [Plan Storage & Versioning](#plan-storage--versioning)
3. [Error Handling](#error-handling)
4. [Rate Limiting](#rate-limiting)
5. [Structured Logging](#structured-logging)
6. [CORS Configuration](#cors-configuration)
7. [Storage Adapters](#storage-adapters)
8. [API Endpoints](#api-endpoints)

---

## Session Management

### Overview
Sessions allow you to track user interactions and maintain state across multiple API calls. Each session has a unique ID and can store arbitrary JSON data.

### Key Features
- Unique session IDs (UUID v4)
- Arbitrary JSON data storage
- Automatic TTL (Time-To-Live) expiration
- CRUD operations via REST API

### Configuration
```env
SESSION_TTL=86400  # 24 hours in seconds
```

### API Endpoints

#### Create Session
```http
POST /api/sessions
Content-Type: application/json

{
  "data": {
    "user_id": "123",
    "device_concept": "Smart insulin pump"
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "user_id": "123",
    "device_concept": "Smart insulin pump"
  },
  "created_at": "2025-11-18T10:00:00Z",
  "updated_at": "2025-11-18T10:00:00Z"
}
```

#### Get Session
```http
GET /api/sessions/{session_id}
```

#### Update Session
```http
PUT /api/sessions/{session_id}
Content-Type: application/json

{
  "data": {
    "risk_class": "III",
    "category": "Insulin delivery"
  }
}
```

#### Delete Session
```http
DELETE /api/sessions/{session_id}
```

#### List Sessions
```http
GET /api/sessions
```

---

## Plan Storage & Versioning

### Overview
All regulatory plans are automatically saved to persistent storage with full version history. This allows you to:
- Retrieve plans without sending full data back to the server
- Track refinements and modifications
- Revert to previous versions
- Associate plans with sessions

### Key Features
- Automatic plan storage on generation
- Version tracking on refinements
- Plan retrieval by ID
- Session association
- Complete version history

### Configuration
```env
PLAN_TTL=604800  # 7 days in seconds (0 = never expire)
```

### API Endpoints

#### Get Plan
```http
GET /api/plans/{plan_id}
GET /api/plans/{plan_id}?version=1  # Get specific version
```

#### Get Plan Record (with version history)
```http
GET /api/plans/{plan_id}/record
```

**Response:**
```json
{
  "id": "plan-123",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "current_version": 3,
  "versions": [
    {
      "version": 1,
      "modifications": "Initial plan generation",
      "created_at": "2025-11-18T10:00:00Z"
    },
    {
      "version": 2,
      "modifications": "Reduced timeline by 6 months",
      "created_at": "2025-11-18T10:30:00Z"
    },
    {
      "version": 3,
      "modifications": "Added FDA pre-submission meeting",
      "created_at": "2025-11-18T11:00:00Z"
    }
  ],
  "created_at": "2025-11-18T10:00:00Z",
  "updated_at": "2025-11-18T11:00:00Z"
}
```

#### List Plans
```http
GET /api/plans
GET /api/plans?session_id={session_id}  # Filter by session
```

#### Delete Plan
```http
DELETE /api/plans/{plan_id}
```

### Plan Generation with Storage

When generating plans, they're automatically saved:

```http
POST /api/standards?session_id={session_id}
```

The `session_id` query parameter is optional and allows you to associate plans with a session.

### Plan Refinement with Storage

When refining plans, the new version is automatically saved:

```http
POST /api/refine
Content-Type: application/json

{
  "planId": "plan-123",
  "modifications": "Reduce timeline by 6 months",
  "context": {
    "budget_constraint": 500000,
    "target_launch": "Q4 2026"
  }
}
```

The original plan is automatically retrieved from storage, refined, and saved as a new version.

---

## Error Handling

### Overview
Comprehensive error handling with structured error responses and proper HTTP status codes.

### Features
- Custom exception classes for different error types
- Consistent error response format
- Detailed validation errors
- Debug mode for development

### Error Response Format
```json
{
  "error": "Plan not found: plan-123",
  "type": "PlanNotFoundException",
  "details": {
    "plan_id": "plan-123"
  },
  "path": "/api/plans/plan-123"
}
```

### Exception Types

| Exception | Status Code | Description |
|-----------|-------------|-------------|
| `SessionNotFoundException` | 404 | Session not found |
| `PlanNotFoundException` | 404 | Plan not found |
| `ValidationException` | 422 | Request validation failed |
| `StorageException` | 500 | Storage operation failed |
| `AIServiceException` | 503 | AI service unavailable |
| `RateLimitExceededException` | 429 | Rate limit exceeded |

---

## Rate Limiting

### Overview
Protects the API from abuse by limiting the number of requests per minute.

### Configuration
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

### Behavior
- Default: 60 requests per minute per IP address
- Returns 429 status code when exceeded
- Includes `Retry-After` header

### Response on Rate Limit
```json
{
  "error": "Rate limit exceeded. Please try again later.",
  "type": "RateLimitExceededException",
  "details": {
    "retry_after": 30
  },
  "path": "/api/classify"
}
```

---

## Structured Logging

### Overview
Comprehensive structured logging for all requests, responses, and errors.

### Features
- Request/response logging with timing
- Unique request IDs (X-Request-ID header)
- Contextual information (IP, method, path)
- JSON format for production
- Human-readable format for development
- Error tracking with full context

### Log Format (Development)
```
[info] request_started method=POST path=/api/classify request_id=123e4567-e89b-12d3-a456-426614174000
[info] request_completed status_code=200 duration_ms=1234.56 request_id=123e4567-e89b-12d3-a456-426614174000
```

### Log Format (Production - JSON)
```json
{
  "event": "request_completed",
  "level": "info",
  "timestamp": "2025-11-18T10:00:00Z",
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "method": "POST",
  "path": "/api/classify",
  "status_code": 200,
  "duration_ms": 1234.56,
  "client_ip": "192.168.1.1"
}
```

---

## CORS Configuration

### Overview
Flexible CORS configuration supporting both development and production origins.

### Configuration
```env
# Development
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Production
CORS_ORIGINS=https://app.yourcompany.com,https://www.yourcompany.com
```

### Features
- Environment-based configuration
- Multiple origins support
- Comma-separated string or list format
- Automatic parsing

---

## Storage Adapters

### Overview
Pluggable storage backends for sessions and plans.

### Supported Backends

#### SQLite (Default)
- **Best for:** Development, small deployments
- **Pros:** No external dependencies, simple setup
- **Cons:** Limited concurrency

**Configuration:**
```env
STORAGE_TYPE=sqlite
DATABASE_PATH=./raidesk.db
```

#### Redis
- **Best for:** Production, high-traffic deployments
- **Pros:** High performance, excellent concurrency
- **Cons:** Requires Redis server

**Configuration:**
```env
STORAGE_TYPE=redis
REDIS_URL=redis://localhost:6379

# With authentication
REDIS_URL=redis://:password@localhost:6379/0
```

### Storage Features
- Automatic TTL (Time-To-Live) support
- Key-value storage with JSON values
- Pattern-based key listing
- Atomic operations
- Automatic cleanup of expired data

---

## API Endpoints

### Complete Endpoint Reference

#### Classification
- `POST /api/classify` - Classify a device concept

#### Purpose & Mechanism
- `POST /api/purpose` - Generate purpose and mechanism

#### Regulatory Plans
- `POST /api/standards` - Generate regulatory plans
  - Query params: `session_id` (optional)

#### Plan Refinement
- `POST /api/refine` - Refine a plan (retrieves from storage)

#### Plan Management
- `GET /api/plans` - List all plans
  - Query params: `session_id` (optional)
- `GET /api/plans/{plan_id}` - Get a specific plan
  - Query params: `version` (optional)
- `GET /api/plans/{plan_id}/record` - Get plan with version history
- `DELETE /api/plans/{plan_id}` - Delete a plan

#### Session Management
- `POST /api/sessions` - Create a session
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{session_id}` - Get a session
- `PUT /api/sessions/{session_id}` - Update a session
- `DELETE /api/sessions/{session_id}` - Delete a session

#### Health & Status
- `GET /` - API information
- `GET /health` - Health check

---

## Frontend Integration

### Typical Workflow

1. **Create a session** (optional but recommended)
```javascript
const session = await fetch('http://localhost:8000/api/sessions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ data: { user_id: '123' } })
}).then(r => r.json());
```

2. **Classify the device**
```javascript
const classification = await fetch('http://localhost:8000/api/classify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ concept: 'Smart insulin pump' })
}).then(r => r.json());
```

3. **Generate plans** (automatically saved to storage)
```javascript
const plans = await fetch(
  `http://localhost:8000/api/standards?session_id=${session.id}`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      classification: classification,
      category: selectedCategory,
      purposeMechanism: purposeData
    })
  }
).then(r => r.json());
```

4. **Refine a plan** (no need to send full plan data!)
```javascript
const refined = await fetch('http://localhost:8000/api/refine', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    planId: plans.plans[0].id,  // Just send the ID!
    modifications: 'Reduce timeline by 6 months',
    context: { budget: 500000 }
  })
}).then(r => r.json());
```

5. **Retrieve plan later**
```javascript
const plan = await fetch(`http://localhost:8000/api/plans/${planId}`)
  .then(r => r.json());
```

---

## Production Deployment

### Checklist

- [ ] Set `DEBUG=false`
- [ ] Configure production `CORS_ORIGINS`
- [ ] Use Redis for storage (`STORAGE_TYPE=redis`)
- [ ] Configure appropriate rate limits
- [ ] Set up proper TTL values
- [ ] Configure external logging service (optional)
- [ ] Add authentication (if needed)
- [ ] Set up monitoring and alerts
- [ ] Use environment-specific secrets management
- [ ] Configure reverse proxy (nginx, etc.)
- [ ] Set up SSL/TLS certificates

### Environment Variables for Production

```env
DEBUG=false
STORAGE_TYPE=redis
REDIS_URL=redis://:password@your-redis-server:6379/0
CORS_ORIGINS=https://app.yourcompany.com,https://www.yourcompany.com
RATE_LIMIT_PER_MINUTE=30
SESSION_TTL=43200  # 12 hours
PLAN_TTL=2592000   # 30 days
```

---

## Troubleshooting

### Common Issues

#### Storage Connection Failed
- **SQLite:** Check database file permissions
- **Redis:** Verify Redis is running: `redis-cli ping`

#### Rate Limit Too Restrictive
Adjust in `.env`:
```env
RATE_LIMIT_PER_MINUTE=120
```

#### CORS Errors
Add your frontend domain to `CORS_ORIGINS`:
```env
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
```

#### Plans Not Saving
Check storage connection in health endpoint:
```bash
curl http://localhost:8000/health
```

---

## Development

### Running the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Run the server
python -m app.main
# or
uvicorn app.main:app --reload
```

### Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Create a session
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"data": {"test": true}}'

# List sessions
curl http://localhost:8000/api/sessions
```

---

## Future Enhancements

### Planned Features
- [ ] Streaming support (SSE/WebSocket)
- [ ] Authentication (API keys, JWT, OAuth2)
- [ ] Metrics and monitoring dashboard
- [ ] Export plans to PDF/Word
- [ ] Bulk operations
- [ ] Search and filtering
- [ ] Webhooks for events
- [ ] Multi-tenancy support

