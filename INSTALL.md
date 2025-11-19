# Quick Installation Guide

## Prerequisites

- Python 3.10+
- Ollama with GPT-OSS model
- (Optional) Redis for production

## Step 1: Install Dependencies

```bash
# Navigate to project directory
cd /Users/jaylee_83/Documents/_itsjayspace/git_clones/raidesk-server

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env file (optional - defaults work for development)
nano .env  # or your preferred editor
```

### Minimal Configuration (Development)

The following defaults will work out of the box:

```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Ollama (adjust if your Ollama is running elsewhere)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gpt-oss

# CORS (add your frontend URL if different)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Storage (SQLite - no setup needed)
STORAGE_TYPE=sqlite
DATABASE_PATH=./raidesk.db

# Session & Plan TTL
SESSION_TTL=86400
PLAN_TTL=604800

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

## Step 3: Verify Ollama

Make sure Ollama is running with GPT-OSS model:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not installed, pull GPT-OSS model
ollama pull gpt-oss

# Start Ollama (if needed)
ollama serve
```

## Step 4: Start the Server

```bash
# Option 1: Using Python directly
python -m app.main

# Option 2: Using uvicorn (recommended for development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
✓ Storage connected: SQLiteAdapter
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Step 5: Test the Installation

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "storage": "connected",
  "storage_type": "sqlite"
}
```

### Test 2: Create a Session
```bash
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"data": {"test": true}}'
```

Expected response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {"test": true},
  "created_at": "2025-11-18T10:00:00Z",
  "updated_at": "2025-11-18T10:00:00Z"
}
```

### Test 3: API Documentation
Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Issue: "Storage not connected"

**Solution:**
Check file permissions for database directory:
```bash
mkdir -p $(dirname ./raidesk.db)
chmod 755 $(dirname ./raidesk.db)
```

### Issue: "Ollama connection failed"

**Solution:**
1. Verify Ollama is running: `curl http://localhost:11434/api/tags`
2. Check if GPT-OSS is installed: `ollama list`
3. Update `OLLAMA_BASE_URL` in `.env` if running on different host

### Issue: "CORS error in frontend"

**Solution:**
Add your frontend URL to `CORS_ORIGINS` in `.env`:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:5173
```

### Issue: "Module not found"

**Solution:**
Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: "Rate limit exceeded"

**Solution:**
Adjust rate limit in `.env`:
```env
RATE_LIMIT_PER_MINUTE=120
```

Or disable it temporarily:
```env
RATE_LIMIT_ENABLED=false
```

## Production Setup

For production deployment with Redis:

### 1. Install Redis

```bash
# macOS
brew install redis
redis-server

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:alpine
```

### 2. Update Configuration

```env
# Use Redis for production
STORAGE_TYPE=redis
REDIS_URL=redis://localhost:6379

# Disable debug mode
DEBUG=false

# Add production CORS origins
CORS_ORIGINS=https://app.yourcompany.com

# Adjust rate limits
RATE_LIMIT_PER_MINUTE=30
```

### 3. Run with Production Server

```bash
# Install gunicorn (production WSGI server)
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## Docker Deployment (Optional)

The project includes a Dockerfile:

```bash
# Build image
docker build -t raidesk-server .

# Run container
docker run -d \
  -p 8000:8000 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  --name raidesk-server \
  raidesk-server
```

## Next Steps

1. ✅ Server is running
2. 📖 Read [SERVER_FEATURES.md](SERVER_FEATURES.md) for complete features
3. 🔧 Read [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for frontend integration
4. 🚀 Start building your frontend!

## Useful Commands

```bash
# Check server status
curl http://localhost:8000/health

# List all sessions
curl http://localhost:8000/api/sessions

# List all plans
curl http://localhost:8000/api/plans

# View API documentation
open http://localhost:8000/docs

# Check logs (with structured logging)
tail -f logs/app.log  # If file logging is configured
```

## Getting Help

- Check the health endpoint: `curl http://localhost:8000/health`
- Review server logs for errors
- See [SERVER_FEATURES.md](SERVER_FEATURES.md) for detailed documentation
- See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for frontend integration

## Development Tips

1. **Use SQLite for development** - No extra setup needed
2. **Enable DEBUG mode** - Better error messages
3. **Use --reload flag** - Auto-restart on code changes
4. **Check /docs endpoint** - Interactive API documentation
5. **Monitor logs** - Request IDs help with debugging

Enjoy building with RAiDesk! 🚀

