from fastapi import FastAPI, Depends, HTTPException, status
from redis import asyncio as aioredis
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict
from app.database import get_db
from app.core import app_settings
from app.modules.todo.router import router as todo_router
from app.modules.user.router import router as user_router


app = FastAPI(
    title="FastAPI Base Application",
    description="FastAPI Base Application",
    version="1.0.0",
)


"""
Application module routers
"""

app.include_router(todo_router)
app.include_router(user_router)


"""
Application startup and shutdown events
"""


@app.on_event("startup")
async def startup_event():
    app.state.redis = aioredis.from_url(
        f"redis://{app_settings.redis_host}:{app_settings.redis_port}",
        encoding="utf-8",
        decode_responses=True,
    )


@app.on_event("shutdown")
async def shutdown_event():
    await app.state.redis.close()


"""
Application default routes
"""


@app.get("/")
async def root():
    return {"message": "This is a web application"}


@app.get("/db-test")
async def db_test(db: Session = Depends(get_db)):
    return {"message": "Database connection successful"}


@app.get("/redis-test")
async def redis_test():
    await app.state.redis.incr("hits")
    return {"hits": await app.state.redis.get("hits")}


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check(
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    try:
        # Use text() for raw SQL
        db.execute(text("SELECT 1"))
        # Check Redis
        await app.state.redis.ping()

        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "error": str(e)},
        )
