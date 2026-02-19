# This version gives you a clean API Key auth (great for internal/prototype → production path) 
# and an optional JWT scaffold you can enable later
import os
import secrets
from typing import Optional

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

# ---------
# API KEY AUTH (no extra dependencies)
# ---------

API_KEY_HEADER_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)

def get_api_key_required(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Protect endpoints using a shared API key.
    - Set API_KEY in env for backend.
    - Next.js sends X-API-Key header.
    """
    expected = os.getenv("API_KEY")
    if not expected:
        # In production you SHOULD require this; for local dev you may allow it.
        # Flip this behavior once you're ready.
        return "dev-mode-no-api-key-set"

    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    # constant-time compare to prevent timing attacks
    if not secrets.compare_digest(api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid API key")

    return api_key


# ---------
# OPTIONAL: USER AUTH PLACEHOLDER
# (Enable later if you add JWT deps)
# ---------

def get_current_user_placeholder():
    """
    Replace with real user auth:
    - JWT verification
    - user lookup
    """
    raise HTTPException(status_code=501, detail="User auth not implemented yet")