# sg-ask-me

AI-powered chatbot application with streaming responses.

## Project Structure

- **Backend**: FastAPI backend with LLM provider abstraction (OpenAI, Gemini support)
  - See [backend/README.md](backend/README.md) for setup instructions
- **Frontend**: Next.js React chat interface
  - See [frontend/README.md](frontend/README.md) for setup instructions

## Quick Start

### Backend

```bash
cd backend
make install  # or: pip install -e .
make dev       # or: uvicorn app.main:app --reload --port 8000
```

Backend runs on http://localhost:8000

### Frontend

**Using Makefile (recommended):**
```bash
cd frontend
make install  # or: npm install
make dev      # or: npm run dev
```

**Or using npm directly:**
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:3000

## Docker Setup

Run everything with Docker Compose:

```bash
# 1. Copy .env.example to .env and fill in your API keys
cp backend/.env.example backend/.env
# Edit backend/.env and set OPENAI_API_KEY or GEMINI_API_KEY

# 2. Start all services (backend, frontend, postgres, redis)
docker compose up --build

# Or run in detached mode
docker compose up -d --build

# View logs (all services)
docker compose logs -f

# View logs for specific service
docker compose logs -f backend
docker compose logs -f frontend

# Stop services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

**Services:**
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000 (with hot reload)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

**Features:**
- ✅ Frontend hot reload enabled (code changes auto-reload in browser)
- ✅ Backend connects to PostgreSQL and Redis automatically
- ✅ All services start in correct order with health checks
- ✅ CORS configured for frontend-backend communication

**Note**: Make sure to set `OPENAI_API_KEY` or `GEMINI_API_KEY` in `backend/.env` before starting.

## Inspecting Data (Redis & PostgreSQL)

**Redis (Rate Limiting Data):**

```bash
# Quick check of all keys
docker compose exec redis redis-cli KEYS "*"

# Check rate limit keys specifically
docker compose exec redis redis-cli KEYS "rl:*"

# View a specific rate limit key's data
docker compose exec redis redis-cli ZRANGE "rl:chat_stream:127.0.0.1" 0 -1 WITHSCORES

# Interactive Redis CLI
docker compose exec redis redis-cli
# Or use helper script:
./scripts/redis-cli.sh
```

**PostgreSQL:**

```bash
# List all databases
docker compose exec postgres psql -U app -c "\l"

# List tables in chatdb
docker compose exec postgres psql -U app -d chatdb -c "\dt"

# Query a table (when you have tables)
docker compose exec postgres psql -U app -d chatdb -c "SELECT * FROM your_table;"

# Interactive PostgreSQL CLI
docker compose exec postgres psql -U app -d chatdb
# Or use helper script:
./scripts/psql.sh
```

**Helper Scripts:**

- `./scripts/check-redis.sh` - Shows all Redis keys and rate limit data
- `./scripts/check-postgres.sh` - Shows database info and tables
- `./scripts/redis-cli.sh` - Interactive Redis CLI
- `./scripts/psql.sh` - Interactive PostgreSQL CLI

## Features

- **Streaming chat responses** via Server-Sent Events (SSE)
- **Multiple LLM providers**: OpenAI (paid) and Google Gemini (free tier)
- **Modern UI**: Next.js with Tailwind CSS, dark mode support
- **Type-safe**: TypeScript throughout
- **Docker support**: Run everything with `docker compose up`
