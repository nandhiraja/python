import redis.asyncio as redis


class RedisService:

    def __init__(self):
        self.client = redis.Redis(
            host="localhost",
            port=6379,
            decode_responses=True
        )

    async def get(self, key: str):
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int):
        await self.client.set(key, value, ex=ttl)

    async def ttl(self, key: str):
        return await self.client.ttl(key)


redis_service = RedisService()