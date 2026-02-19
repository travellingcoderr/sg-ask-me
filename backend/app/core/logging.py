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

    root = logging.getLogger()
    root.setLevel(log_level)

    # Clear handlers to avoid duplicates under reload
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(JsonFormatter())

    root.addHandler(handler)

    # Make uvicorn logs use root handler/format
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True


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