# This file is used to rate limit the API requests

import time
import redis
from fastapi import HTTPException, Request
from .config import settings

r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def rate_limit(key_prefix: str, limit: int = 30, window_sec: int = 60):
    async def dep(request: Request):
        # For production, use user id / api key. For now, IP-based.
        ip = request.client.host if request.client else "unknown"
        key = f"rl:{key_prefix}:{ip}"
        now = int(time.time())

        pipe = r.pipeline()
        pipe.zadd(key, {str(now): now})
        pipe.zremrangebyscore(key, 0, now - window_sec)
        pipe.zcard(key)
        pipe.expire(key, window_sec + 5)
        _, _, count, _ = pipe.execute()

        if int(count) > limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return dep