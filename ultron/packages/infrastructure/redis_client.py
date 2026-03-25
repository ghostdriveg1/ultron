"""
Ultron v3 — Redis Client (Upstash)
Wraps upstash_redis.Redis with tenacity retry and in-memory fallback cache.
"""

import logging
import sys
from typing import Any, Optional

from tenacity import retry, stop_after_attempt, wait_exponential
from upstash_redis import Redis

logger = logging.getLogger("ultron.redis")


class UltronRedis:
    """
    Redis client wrapping Upstash REST API with:
    - Automatic retries (3 attempts, exponential backoff)
    - In-memory fallback cache when all retries fail
    - Connection health check on init
    """

    def __init__(self, url: str, token: str) -> None:
        self._client = Redis(url=url, token=token)
        self._fallback_cache: dict[str, Any] = {}
        self._healthy = False

        # Verify connection
        try:
            self._client.ping()
            self._healthy = True
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            print(f"[WARN] Redis unavailable — using in-memory fallback", file=sys.stderr)

    @property
    def is_healthy(self) -> bool:
        return self._healthy

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def get(self, key: str) -> Optional[str]:
        """Get a value by key."""
        try:
            result = self._client.get(key)
            self._healthy = True
            return result
        except Exception:
            self._healthy = False
            # Fallback to in-memory cache
            cached = self._fallback_cache.get(key)
            if cached is not None:
                logger.warning(f"Redis get failed — returning cached value for '{key}'")
                return cached
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> None:
        """Set a key-value pair with optional TTL in seconds."""
        try:
            if ex:
                self._client.set(key, value, ex=ex)
            else:
                self._client.set(key, value)
            self._fallback_cache[key] = value
            self._healthy = True
        except Exception:
            self._healthy = False
            self._fallback_cache[key] = value
            logger.warning(f"Redis set failed — cached locally for '{key}'")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def incr(self, key: str) -> int:
        """Atomically increment a key by 1, returning the new value."""
        try:
            result = self._client.incr(key)
            self._healthy = True
            return int(result)
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def hset(self, name: str, mapping: dict) -> None:
        """Set multiple hash fields."""
        try:
            self._client.hset(name, values=mapping)
            self._healthy = True
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Get a single hash field value."""
        try:
            result = self._client.hget(name, key)
            self._healthy = True
            return result
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def zadd(self, name: str, mapping: dict[str, float]) -> None:
        """Add members to a sorted set."""
        try:
            for member, score in mapping.items():
                self._client.zadd(name, {member: score})
            self._healthy = True
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def zrangebyscore(
        self, name: str, min_score: float, max_score: float
    ) -> list[str]:
        """Get sorted set members within score range."""
        try:
            result = self._client.zrangebyscore(name, min_score, max_score)
            self._healthy = True
            return result or []
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def lrange(self, name: str, start: int, end: int) -> list[str]:
        """Get elements from a list."""
        try:
            result = self._client.lrange(name, start, end)
            self._healthy = True
            return result or []
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def zpopmax(self, name: str, count: int = 1) -> list:
        """Remove and return the member with the highest score."""
        try:
            result = self._client.zpopmax(name, count)
            self._healthy = True
            return result or []
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def zcard(self, name: str) -> int:
        """Get the number of members in a sorted set."""
        try:
            result = self._client.zcard(name)
            self._healthy = True
            return result or 0
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def rpush(self, name: str, *values: str) -> None:
        """Append values to a list."""
        try:
            for v in values:
                self._client.rpush(name, v)
            self._healthy = True
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def lpush(self, name: str, *values: str) -> None:
        """Prepend values to a list."""
        try:
            for v in values:
                self._client.lpush(name, v)
            self._healthy = True
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def expire(self, name: str, seconds: int) -> None:
        """Set TTL on a key."""
        try:
            self._client.expire(name, seconds)
            self._healthy = True
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def delete(self, *names: str) -> None:
        """Delete one or more keys."""
        try:
            for name in names:
                self._client.delete(name)
                self._fallback_cache.pop(name, None)
            self._healthy = True
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def ltrim(self, name: str, start: int, end: int) -> None:
        """Trim a list to the specified range."""
        try:
            self._client.ltrim(name, start, end)
            self._healthy = True
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def hincrby(self, name: str, key: str, amount: int) -> int:
        """Increment the integer value of a hash field by the given amount."""
        try:
            result = self._client.hincrby(name, key, amount)
            self._healthy = True
            return int(result)
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def zremrangebyrank(self, name: str, start: int, end: int) -> None:
        """Remove all members in a sorted set within the given indexes."""
        try:
            self._client.zremrangebyrank(name, start, end)
            self._healthy = True
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def zrevrange(self, name: str, start: int, end: int) -> list[str]:
        """Return a range of members in a sorted set, by index, with scores ordered from high to low."""
        try:
            result = self._client.zrevrange(name, start, end)
            self._healthy = True
            return result or []
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def llen(self, name: str) -> int:
        """Get the length of a list."""
        try:
            result = self._client.llen(name)
            self._healthy = True
            return int(result) if result is not None else 0
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def zrange(self, name: str, start: int, end: int) -> list[str]:
        """Return a range of members in a sorted set, by index."""
        try:
            result = self._client.zrange(name, start, end)
            self._healthy = True
            return result or []
        except Exception:
            self._healthy = False
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def eval_lua(
        self, script: str, keys: list[str], args: list[str]
    ) -> Any:
        """Execute a Lua script atomically via Redis EVAL."""
        try:
            result = self._client.eval(script, keys, args)
            self._healthy = True
            return result
        except Exception:
            self._healthy = False
            raise

