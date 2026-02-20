# Backend — AI Chat API

A FastAPI backend that streams chat responses from an LLM (default: OpenAI). Built to be **extensible**: you can swap the LLM provider (e.g. OpenAI → Anthropic, local models) via a small configuration change and a factory that returns a common interface.

---

## Why this structure?

| Path | Purpose |
|------|--------|
| **`app/main.py`** | Application entry point. Creates the FastAPI app, wires CORS, logging middleware, and includes API routers. Keeps startup and global middleware in one place. |
| **`app/core/config.py`** | Central configuration from environment (and optional `.env`). Uses Pydantic Settings so all env vars are validated and typed. Single source of truth for `OPENAI_API_KEY`, `REDIS_URL`, `CORS_ORIGINS`, etc. |
| **`app/core/logging.py`** | Structured JSON logging and request-id propagation. Used so production logs work well with aggregators (Datadog, ELK, etc.) and you can trace a request across services via `X-Request-Id`. |
| **`app/core/rate_limit.py`** | Redis-based rate limiting as a FastAPI dependency. Protects endpoints (e.g. chat stream) from abuse by limiting requests per key (e.g. IP or API key) per time window. |
| **`app/core/security.py`** | API key authentication (`X-API-Key`) and a placeholder for future JWT/user auth. Keeps auth logic out of route handlers. |
| **`app/api/routes_chat.py`** | Chat HTTP API: accepts a message (and optional `previous_response_id`), streams SSE events (text deltas + done with response id). Delegates actual LLM calls to the **LLM service layer**. |
| **`app/services/openai_client.py`** | OpenAI-specific client: calls the OpenAI Responses API and yields stream events. Used as one **implementation** of the LLM interface. |
| **`app/services/llm/`** | **LLM abstraction layer** (interface + factory). `base.py` defines the contract (e.g. “stream chat”), `openai_provider.py` implements it for OpenAI, `factory.py` returns the right implementation from config. This is the “C# factory pattern”: routes depend on the interface, not a concrete provider, so you can replace the LLM easily. |
| **`requirements.txt`** / **`pyproject.toml`** | Python dependencies. Use one as the source of truth (e.g. `pip install -e .` from repo root for dev). |
| **`Dockerfile`** | Builds a minimal image to run the FastAPI app with uvicorn. Used by `docker-compose` for the `backend` service. |

---

## Why these libraries? (Python vs C#)

If you’re coming from C#, here’s why each main library is there and what to read.

| Library | What it does | Why we use it | C# rough equivalent | Where to learn |
|--------|----------------|---------------|----------------------|----------------|
| **FastAPI** | Web framework: routes, dependency injection, request/response, OpenAPI docs. | Async-first, minimal boilerplate, automatic request/response validation when you use type hints and Pydantic models. | ASP.NET Core (controllers, minimal APIs, DI). | [fastapi.tiangolo.com](https://fastapi.tiangolo.com) — Tutorial and Advanced User Guide. |
| **Pydantic** | Data validation and settings using type hints. You define classes with typed fields; it validates input and env at runtime. | Request bodies (e.g. `ChatIn`) and config (`Settings`) are validated and typed. Invalid data → clear 422 errors. No manual parsing. | Like a mix of **data annotations** + **model validation** (e.g. `DataAnnotations`, FluentValidation) + strongly-typed config (e.g. `IConfiguration` + options pattern). | [docs.pydantic.dev](https://docs.pydantic.dev) — Pydantic V2 docs; “Concepts” and “Settings” sections. |
| **pydantic-settings** | Loads configuration from environment variables (and `.env`) into Pydantic models. | `Settings` in `config.py`: one class, one place for all env vars, with types and defaults. | Similar to **IOptions\<T\>** / **IConfiguration** bound to a typed options class, but driven by env vars. | Same Pydantic docs → “Settings management”. |
| **Uvicorn** | ASGI server: runs the FastAPI app, handles HTTP, WebSockets, and async. | FastAPI is an ASGI app; something must run it. Uvicorn is the standard choice (fast, async, one process or workers). | Like **Kestrel** for ASP.NET Core: the process that listens on a port and runs your app. | [uvicorn.org](https://www.uvicorn.org) — “Deployment” and “Settings”. |
| **Redis** (client) | Python client for Redis. | Used in `rate_limit.py` to count requests per key in a time window (sorted sets). | Like using **StackExchange.Redis** for rate limiting or caching. | [redis-py](https://redis-py.readthedocs.io) — readthedocs. |
| **OpenAI** (official SDK) | Client for OpenAI APIs (chat, responses, embeddings, etc.). | Our default LLM implementation calls the Responses API and streams events. | Like using the **Azure.OpenAI** or **OpenAI** .NET client. | [github.com/openai/openai-python](https://github.com/openai/openai-python) and [platform.openai.com/docs](https://platform.openai.com/docs). |
| **python-dotenv** | Loads a `.env` file into `os.environ` before your app runs. | Optional; Pydantic Settings can also read `.env` when configured with `env_file=".env"`. Keeps local secrets out of the shell. | Like **DotNetEnv** or reading a `.env` file into `IConfiguration` in .NET. | [pypi.org/project/python-dotenv](https://pypi.org/project/python-dotenv). |

**How this fits together:** You define **Pydantic models** for config and request bodies → **FastAPI** uses them for validation and OpenAPI. **Uvicorn** runs the FastAPI app. **Pydantic Settings** fills your config from env/`.env`. The rest (Redis, OpenAI) are just the right tools for rate limiting and calling the LLM.

**Finding good Python references in general:**

- **Official docs** for each library (links above) are the most reliable.
- **PyPI** ([pypi.org](https://pypi.org)): package page often has “Home page” / “Documentation” links.
- **Real Python** ([realpython.com](https://realpython.com)): tutorials on Python and popular libraries.
- **FastAPI’s “Alternatives” and “Comparison”** page explains why FastAPI (and thus Pydantic, Uvicorn) is chosen over Flask/Django for API-only services.

---

## Environment variables and `.env`

- **Local development**: Use a `.env` file in the backend root (or project root). The app loads it via Pydantic Settings (`env_file=".env"`). Copy `.env.example` to `.env` and fill in keys; **do not commit `.env`**.
- **Docker**: Two common approaches:
  1. **`env_file: .env` in docker-compose** — Compose injects variables from the host’s `.env` into the container. No need to copy `.env` into the image; same file works for local runs and for Compose.
  2. **`environment:` in docker-compose** — You can set variables (or use `environment: - OPENAI_API_KEY=${OPENAI_API_KEY}`) so the host’s `.env` is used by Compose when you run `docker compose up`.

So **yes, `.env` is a good approach** even with Docker: keep a `.env` on the host, add `env_file: .env` (and/or `environment:`) in `docker-compose.yml`, and never bake secrets into the image. For production, use a secrets manager or CI/CD env and pass them as env vars or mounted secrets instead of a committed file.

See **`.env.example`** for a template and **Configuration** below for all variables.

---

## Configuration

Copy `.env.example` to `.env` and set:

| Variable | Purpose |
|----------|--------|
| `OPENAI_API_KEY` | Required for the default OpenAI provider. |
| `REDIS_URL` | Used for rate limiting (e.g. `redis://localhost:6379/0`). |
| `DATABASE_URL` | For future DB use (e.g. `postgresql+psycopg://user:pass@host/db`). |
| `CORS_ORIGINS` | Comma-separated origins for CORS (e.g. `http://localhost:3000`). |
| `APP_ENV` | e.g. `local` / `production` for environment-specific behavior. |
| `LLM_PROVIDER` | `openai` (default) or another provider key; the factory uses this to choose the implementation. |
| `API_KEY` | Optional; if set, `X-API-Key` is required by protected routes. |
| `LOG_LEVEL` | Optional; e.g. `DEBUG`, `INFO`. |

---

## Virtual environment (recommended)

Using a virtual environment keeps this project’s dependencies separate from your system Python and any globally installed packages, so you avoid version conflicts and “command not found” for tools like `uvicorn`.

**Create and use a venv from the repo root** (so one venv can serve both backend and any other Python tooling in the repo):

```bash
# From the repository root (sg-ask-me/)
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

cd backend
pip install -e .
```

**Or create a venv inside `backend/`** (backend-only isolation):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -e .
```

After activation, your prompt usually shows `(.venv)`. All `pip` and `python` commands (and `uvicorn`) use the venv; when you’re done, run `deactivate`.

---

## Running locally

```bash
cd backend
cp .env.example .env
# Edit .env and set OPENAI_API_KEY, REDIS_URL, etc.

# Ensure your virtual environment is activated (see above), then:
pip install -e .
uvicorn app.main:app --reload --port 8000
```

If you don’t want to activate the venv, run uvicorn via the venv’s Python:

```bash
cd backend
# If the venv is in repo root (sg-ask-me/.venv):
../.venv/bin/python -m uvicorn app.main:app --reload --port 8000
# If the venv is in backend (backend/.venv):
.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

- Health: `GET http://localhost:8000/health`
- Chat stream: `POST http://localhost:8000/api/chat/stream` with JSON `{"message": "Hello"}` (and optional `previous_response_id`). Example:

  ```bash
  curl -X POST http://localhost:8000/api/chat/stream \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello"}'
  ```

---

## Logs

All application and request logs go to **stdout** in the **terminal where you started uvicorn**. That’s where you see:

- Each request, e.g. `"POST /api/chat/stream HTTP/1.1" 200`
- Errors and stack traces if a request fails
- Any `print()` or `logger` output from your code

**To see more detail:** set `LOG_LEVEL=DEBUG` in `.env` and restart uvicorn.

**If curl seems to hang or you get no response:** keep the uvicorn terminal visible and run curl again; you should see the request line and any error right there. Use `curl -v` to see connection and response headers on the curl side. The stream can take a few seconds before the first chunk (OpenAI latency).

---

## Troubleshooting

### POST /api/chat/stream returns 500 or "Connection refused" (Redis)

The chat stream endpoint uses **Redis** for rate limiting. If Redis is not running, you used to get a 500. The app now **skips rate limiting** when Redis is unavailable, so the API works without Redis for local dev.

- **To use rate limiting**: Start Redis (e.g. `redis-server` or `brew services start redis` on macOS). Set `REDIS_URL` in `.env` if needed (default is `redis://localhost:6379/0`).
- **To test without Redis**: No change needed; the endpoint will work and rate limiting will be skipped.

### Other 500s or curl errors

- **Check server is running**: `GET http://localhost:8000/health` should return 200.
- **Check `.env`**: `OPENAI_API_KEY` must be set for the default OpenAI provider; otherwise the LLM call will fail.
- **Check request format**: `POST /api/chat/stream` expects `Content-Type: application/json` and body `{"message": "Your text"}`.

---

## Swapping the LLM (extensibility)

1. **Implement the interface** in `app/services/llm/base.py` (e.g. a protocol or abstract class with a method like `stream_chat(...)` that yields SSE-relevant events).
2. **Add a new provider** under `app/services/llm/`, e.g. `anthropic_provider.py`, that implements that interface.
3. **Register it in the factory** in `app/services/llm/factory.py` (e.g. `{"openai": OpenAIClient, "anthropic": AnthropicClient}`).
4. **Set `LLM_PROVIDER`** in `.env` or in Docker env to the new key.

The chat route should depend only on “the LLM client” returned by the factory, so no route code changes are needed when you switch providers.

---

## Docker

- **Build and run with Compose** (from repo root):  
  `docker compose up --build`  
  Backend will use env vars from `docker-compose.yml` and, if you add it, `env_file: .env`.
- **Backend only**:  
  `docker build -t sg-ask-me-backend ./backend`  
  Run with env passed in or via `env_file` so `OPENAI_API_KEY`, `REDIS_URL`, etc. are set.

---

## `.env` and Docker

- **Local**: Create `backend/.env` (or a `.env` in the repo root) from `.env.example`. The app loads it via `config.py` (Pydantic Settings `env_file=".env"`). Run from the backend directory so `.env` is found, or set `ENV_FILE` if you use a different path.
- **Docker Compose**: The `backend` service uses `env_file: .env` (path relative to the compose file, so a `.env` in the **repo root** is used). Compose injects those variables into the container; you do **not** need to copy `.env` into the image. This keeps secrets out of the image and lets you use the same `.env` for local and Compose.
- **Production**: Prefer passing env via your orchestrator (e.g. Kubernetes secrets, CI/CD env) or a secrets manager rather than a committed file.

## Project layout (summary)

```
backend/
├── README.md           # This file
├── .env.example        # Template for .env (do not commit .env)
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── app/
    ├── main.py
    ├── core/
    │   ├── config.py
    │   ├── logging.py
    │   ├── rate_limit.py
    │   └── security.py
    ├── api/
    │   └── routes_chat.py
    └── services/
        ├── openai_client.py   # Legacy; prefer llm factory
        └── llm/
            ├── base.py       # Interface / protocol
            ├── openai_provider.py
            └── factory.py
```
