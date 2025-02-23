from functools import wraps
import json
from fastapi import Request
from datetime import datetime
from sqlalchemy import inspect
from inspect import iscoroutinefunction


# Function to get Redis connection (replace with your actual Redis setup)
async def get_redis():
    from app.main import app

    return app.state.redis


def serialize_sqlalchemy(obj):
    """Convert SQLAlchemy model to dict."""
    if hasattr(obj, "__table__"):
        return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
    return obj


class ResponseEncoder(json.JSONEncoder):
    """Handle serialization of various response types:
    - datetime objects
    - lists
    - SQLAlchemy models
    - Pydantic models
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, list):
            return [self.default(item) for item in obj]
        if hasattr(obj, "__table__"):
            return serialize_sqlalchemy(obj)
        if hasattr(obj, "dict"):
            return obj.dict()
        return super().default(obj)


# Cache decorator
def cache_response(expiry: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            redis = await get_redis()
            cache_key = f"{request.url.path}"
            if request.url.query:
                cache_key = f"{cache_key}?{request.url.query}"

            # Check cache
            cached = await redis.get(cache_key)
            if cached:
                return json.loads(cached)

            # Get response
            response = (
                await func(request, *args, **kwargs)
                if iscoroutinefunction(func)
                else func(request, *args, **kwargs)
            )

            # Cache with custom encoder
            await redis.set(
                cache_key, json.dumps(response, cls=ResponseEncoder), expiry
            )

            return response

        return wrapper

    return decorator
