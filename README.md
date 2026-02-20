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

## Features

- **Streaming chat responses** via Server-Sent Events (SSE)
- **Multiple LLM providers**: OpenAI (paid) and Google Gemini (free tier)
- **Modern UI**: Next.js with Tailwind CSS, dark mode support
- **Type-safe**: TypeScript throughout
