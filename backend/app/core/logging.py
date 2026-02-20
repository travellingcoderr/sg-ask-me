import json
import logging
import os
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Context var so all logs in a request include the same request_id
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> str:
    rid = request_id_ctx.get()
    return rid if rid else "-"


class JsonFormatter(logging.Formatter):
    """
    Minimal JSON logger for production log aggregation (Datadog, Azure Log Analytics, ELK, etc.)
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": int(time.time() * 1000),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": get_request_id(),
        }

        # Attach exception info if present
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        # Include extra fields (if caller used logger.info("...", extra={"foo": "bar"}))
        # Filter out standard LogRecord keys
        standard = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process"
        }
        for k, v in record.__dict__.items():
            if k not in standard and k not in payload:
                payload[k] = v

        return json.dumps(payload, ensure_ascii=False)


def setup_logging() -> None:
    """
    Call once at startup.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    app_env = os.getenv("APP_ENV", "local").lower()

    root = logging.getLogger()
    root.setLevel(log_level)

    # Clear handlers to avoid duplicates under reload
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Use simpler format for local dev, JSON for production
    if app_env == "local":
        # Simple readable format for local development
        # Format: timestamp LEVEL logger_name | message
        # Note: uvicorn uses "uvicorn.error" logger for ALL its messages (startup, shutdown, etc.), not just errors
        # The LEVEL field shows the actual severity: INFO=normal, ERROR/WARNING=problems
        class LevelFormatter(logging.Formatter):
            """Formatter that emphasizes log levels for clarity."""
            LEVEL_COLORS = {
                'DEBUG': '\033[36m',    # Cyan
                'INFO': '\033[32m',     # Green
                'WARNING': '\033[33m',  # Yellow
                'ERROR': '\033[31m',    # Red
                'CRITICAL': '\033[35m', # Magenta
            }
            RESET = '\033[0m'
            
            def format(self, record):
                # Add color to level name
                levelname = record.levelname
                if levelname in self.LEVEL_COLORS:
                    colored_level = f"{self.LEVEL_COLORS[levelname]}{levelname:8s}{self.RESET}"
                else:
                    colored_level = f"{levelname:8s}"
                
                # Format: timestamp LEVEL logger_name | message
                message = record.getMessage()
                
                # Handle exception tracebacks
                if record.exc_info:
                    # Format exception info using parent class
                    exc_text = self.formatException(record.exc_info)
                    message = f"{message}\n{exc_text}"
                
                return (f"{self.formatTime(record, self.datefmt)} "
                        f"{colored_level} "
                        f"{record.name:20s} | "
                        f"{message}")
        
        formatter = LevelFormatter(datefmt="%Y-%m-%d %H:%M:%S")
    else:
        formatter = JsonFormatter()
    
    handler.setFormatter(formatter)
    root.addHandler(handler)

    # Make uvicorn logs use root handler/format
    # Uvicorn uses these specific logger names:
    # - "uvicorn": general server logs
    # - "uvicorn.error": error logs (exceptions, startup issues)
    # - "uvicorn.access": HTTP access logs (request/response)
    # By clearing their handlers and setting propagate=True, we route all uvicorn
    # logs through our root handler/formatter while preserving the logger name.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True
    
    # Log startup message so we know logging is working
    root.info(f"Logging configured: level={log_level}, env={app_env}")


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Adds X-Request-Id header (propagates if client sends one),
    stores it in ContextVar so logs include it.
    """

    async def dispatch(self, request: Request, call_next):
        incoming = request.headers.get("x-request-id")
        rid = incoming.strip() if incoming else str(uuid.uuid4())
        token = request_id_ctx.set(rid)
        try:
            response = await call_next(request)
            response.headers["X-Request-Id"] = rid
            return response
        finally:
            request_id_ctx.reset(token)