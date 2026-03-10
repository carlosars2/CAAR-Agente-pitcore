"""Redis-backed conversation memory with TTL."""

import json
from datetime import datetime

import redis.asyncio as aioredis

from src.config.settings import settings


class RedisMemory:
    """Stores conversation history in Redis with automatic expiration."""

    def __init__(self):
        self._redis: aioredis.Redis | None = None
        self._ttl_seconds = settings.conversation_ttl_hours * 3600

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
        return self._redis

    def _key(self, conversation_id: str) -> str:
        return f"pitcore:conv:{conversation_id}"

    def _lead_key(self, conversation_id: str) -> str:
        return f"pitcore:lead:{conversation_id}"

    async def get_history(self, conversation_id: str) -> list[dict]:
        """Retrieve conversation history."""
        r = await self._get_redis()
        raw = await r.get(self._key(conversation_id))
        if raw is None:
            return []
        return json.loads(raw)

    async def append_message(
        self, conversation_id: str, role: str, content: str
    ) -> None:
        """Append a message and refresh TTL."""
        r = await self._get_redis()
        key = self._key(conversation_id)
        history = await self.get_history(conversation_id)
        history.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        await r.set(key, json.dumps(history, ensure_ascii=False), ex=self._ttl_seconds)

    async def save_lead(self, conversation_id: str, lead_data: dict) -> None:
        """Save lead information linked to a conversation."""
        r = await self._get_redis()
        key = self._lead_key(conversation_id)
        existing = await r.get(key)
        merged = json.loads(existing) if existing else {}
        merged.update(lead_data)
        merged["updated_at"] = datetime.utcnow().isoformat()
        await r.set(key, json.dumps(merged, ensure_ascii=False), ex=self._ttl_seconds)

    async def get_lead(self, conversation_id: str) -> dict | None:
        """Retrieve lead data for a conversation."""
        r = await self._get_redis()
        raw = await r.get(self._lead_key(conversation_id))
        if raw is None:
            return None
        return json.loads(raw)

    async def clear(self, conversation_id: str) -> None:
        """Delete conversation and lead data."""
        r = await self._get_redis()
        await r.delete(self._key(conversation_id), self._lead_key(conversation_id))

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None


memory = RedisMemory()
