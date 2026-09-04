from fastapi import APIRouter
from core.redis import redis_client

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("")
async def health_check():
    return {
        "status": "ok",
        "redis": "connected" if (redis_client.is_connected and not redis_client.is_in_memory) else "in_memory_fallback",
    }
