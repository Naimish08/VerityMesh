"""
Redis client for pub/sub events, job queues, and caching.
Includes transparent in-memory fallback for local development when Redis is not running.
"""

import asyncio
import json
import logging
from typing import Any, AsyncGenerator

import redis.asyncio as redis

from config import settings

logger = logging.getLogger("veritymesh.redis")


class RedisClient:
    """Async Redis client wrapper with in-memory fallback."""

    def __init__(self):
        self._redis: redis.Redis | None = None
        self._is_in_memory: bool = False
        # In-memory broker fallbacks
        self._memory_queue: asyncio.Queue = asyncio.Queue()
        self._memory_channels: dict[str, list[asyncio.Queue]] = {}
        self._memory_cache: dict[str, Any] = {}

    @property
    def is_connected(self) -> bool:
        return self._redis is not None or self._is_in_memory

    @property
    def is_in_memory(self) -> bool:
        return self._is_in_memory

    async def connect(self):
        """Establish Redis connection, or fall back to in-memory mode."""
        try:
            r = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                retry_on_timeout=True,
                socket_connect_timeout=3.0,
                socket_timeout=None,
            )
            # Test ping with a short timeout
            await asyncio.wait_for(r.ping(), timeout=2.0)
            self._redis = r
            self._is_in_memory = False
            logger.info(f"Connected to Redis at {settings.REDIS_URL}")
        except Exception as e:
            self._redis = None
            self._is_in_memory = True
            logger.warning(
                f"Could not connect to Redis at {settings.REDIS_URL} ({e}). "
                "Falling back to IN-MEMORY queue & event broker for local development. "
                "(To use distributed Redis, start Docker Desktop or redis-server)"
            )

    async def disconnect(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Disconnected from Redis")
        self._is_in_memory = False

    # ── Pub/Sub ─────────────────────────────────────────────

    async def publish_event(self, research_id: str, event_dict: dict):
        """Publish an event to a research-specific channel."""
        channel = f"research:{research_id}:events"
        if self._is_in_memory:
            subscribers = self._memory_channels.get(channel, [])
            for q in subscribers:
                await q.put(event_dict)
            return

        if self._redis:
            await self._redis.publish(channel, json.dumps(event_dict))

    async def subscribe_events(self, research_id: str) -> AsyncGenerator[dict, None]:
        """Subscribe to events for a research run. Yields parsed event dicts."""
        channel = f"research:{research_id}:events"

        if self._is_in_memory:
            q: asyncio.Queue = asyncio.Queue()
            if channel not in self._memory_channels:
                self._memory_channels[channel] = []
            self._memory_channels[channel].append(q)
            try:
                while True:
                    event = await q.get()
                    yield event
                    if event.get("event_type") in ("complete", "error"):
                        break
            finally:
                if channel in self._memory_channels:
                    self._memory_channels[channel] = [
                        sub for sub in self._memory_channels[channel] if sub is not q
                    ]
            return

        if self._redis:
            pubsub = self._redis.pubsub()
            try:
                await pubsub.subscribe(channel)
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        try:
                            yield json.loads(message["data"])
                        except json.JSONDecodeError:
                            logger.warning(f"Malformed event data: {message['data'][:100]}")
            finally:
                await pubsub.unsubscribe(channel)
                await pubsub.close()

    # ── Job Queue ───────────────────────────────────────────

    async def enqueue_research(self, research_id: str, config: dict):
        """Add a research job to the queue."""
        payload = {"research_id": research_id, "config": config}
        if self._is_in_memory:
            await self._memory_queue.put(payload)
            logger.info(f"Enqueued research job in memory: {research_id}")
            return

        if self._redis:
            await self._redis.lpush("research_queue", json.dumps(payload))
            logger.info(f"Enqueued research job in Redis: {research_id}")

    async def dequeue_research(self) -> dict | None:
        """Blocking pop from the research queue. Returns parsed dict or None."""
        if self._is_in_memory:
            try:
                return await asyncio.wait_for(self._memory_queue.get(), timeout=2.0)
            except asyncio.TimeoutError:
                return None

        if self._redis:
            try:
                result = await self._redis.brpop("research_queue", timeout=2)
                if result:
                    _, payload = result
                    return json.loads(payload)
            except (redis.exceptions.TimeoutError, asyncio.TimeoutError):
                return None
            except Exception as e:
                logger.warning(f"Redis dequeue warning: {e}")
                return None
        return None

    # ── Cache ───────────────────────────────────────────────

    async def cache_get(self, key: str) -> Any | None:
        """Get a cached value by key."""
        if self._is_in_memory:
            return self._memory_cache.get(key)

        if self._redis:
            val = await self._redis.get(key)
            if val:
                try:
                    return json.loads(val)
                except json.JSONDecodeError:
                    return val
        return None

    async def cache_set(self, key: str, value: Any, ttl: int = 604800):
        """Set a cached value with TTL (default 7 days)."""
        if self._is_in_memory:
            self._memory_cache[key] = value
            return

        if self._redis:
            await self._redis.setex(key, ttl, json.dumps(value))


# Module-level singleton
redis_client = RedisClient()
