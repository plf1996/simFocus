from redis import asyncio as aioredis
from typing import Optional
import json
from app.core.config import settings

# Global Redis client
redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
    return redis_client


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


class CacheService:
    """Service for caching operations"""

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis

    async def get(self, key: str) -> Optional[any]:
        """Get value from cache"""
        value = await self.redis.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    async def set(self, key: str, value: any, ttl: int = None) -> bool:
        """Set value in cache with optional TTL (in seconds)"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return await self.redis.set(key, value, ex=ttl)

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        return await self.redis.delete(key) > 0

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.redis.exists(key) > 0

    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for existing key"""
        return await self.redis.expire(key, ttl)

    async def get_ttl(self, key: str) -> int:
        """Get remaining TTL for key"""
        return await self.redis.ttl(key)


class RateLimitService:
    """Service for rate limiting using Redis"""

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis

    async def is_allowed(
        self,
        key: str,
        limit: int,
        window: int = 60
    ) -> tuple[bool, dict]:
        """
        Check if request is allowed based on rate limit
        key: unique identifier (e.g., user_id, ip)
        limit: max requests
        window: time window in seconds

        Returns: (allowed, info_dict)
        info_dict: {
            'remaining': int,
            'reset': int (unix timestamp)
        }
        """
        current_time = int(__import__('time').time())
        window_start = current_time - window

        # Use Redis sorted set for sliding window
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(current_time): current_time})
        pipe.expire(key, window)
        results = await pipe.execute()

        count = results[1]
        remaining = max(0, limit - count)
        reset = current_time + window

        return count < limit, {
            'limit': limit,
            'remaining': remaining,
            'reset': reset
        }


async def get_cache_service() -> CacheService:
    """Dependency for getting CacheService"""
    redis = await get_redis()
    return CacheService(redis)


async def get_rate_limit_service() -> RateLimitService:
    """Dependency for getting RateLimitService"""
    redis = await get_redis()
    return RateLimitService(redis)
