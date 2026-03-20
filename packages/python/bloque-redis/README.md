# bloque-redis

Redis async utilities: cache, streams with consumer groups, and health checks.

## Features

- **RedisManager** - Connection lifecycle, async context manager, tenant-aware key prefixing
- **RedisCache** - Key-value cache with TTL, JSON serialization, `@cached` decorator
- **StreamProducer / StreamConsumer** - Redis Streams with consumer groups, auto-claim pending messages
- **Health check** - Compatible with `bloque-core` `HealthResponse.checks`

## Installation

```bash
uv add bloque-redis
```

## Quick Start

### Cache

```python
from bloque_redis.client import RedisManager, RedisSettings
from bloque_redis.cache import RedisCache, cached

settings = RedisSettings(url="redis://localhost:6379/0", key_prefix="myapp")

async with RedisManager(settings) as manager:
    cache = RedisCache(manager, default_ttl=300)

    await cache.set("user:1", {"name": "Alice"})
    user = await cache.get("user:1")  # {"name": "Alice"}

    # Decorator
    @cached(cache, ttl=60)
    async def get_user(user_id: str) -> dict:
        return await db.fetch_user(user_id)
```

### Streams

```python
from bloque_redis.client import RedisManager
from bloque_redis.streams import StreamProducer, StreamConsumer

async with RedisManager() as manager:
    producer = StreamProducer(manager, stream="events")
    await producer.publish({"action": "signup", "user": "alice"})

    consumer = StreamConsumer(
        manager, stream="events", group="workers", consumer_name="w1"
    )
    await consumer.ensure_group()

    async for msg in consumer.listen():
        print(msg.data)
        await consumer.ack(msg.message_id)
```

### Multitenant

```python
# Automatic tenant prefixing (soft dependency on bloque-multitenant)
settings = RedisSettings(key_prefix="app", tenant_aware=True)
manager = RedisManager(settings)

# With bloque_multitenant context active (tenant_id="t1"):
# manager.make_key("session:abc") -> "app:t1:session:abc"

# Or explicit:
# manager.make_key("session:abc", tenant_id="t1") -> "app:t1:session:abc"
```

### Health Check

```python
from bloque_redis.health import redis_health_check

checks = await redis_health_check(manager)
# {"redis": True}
```

## Dependencies

- `bloque-core` - Logging, health response schemas
- `redis[hiredis]>=5.0` - Async Redis client

## Development

```bash
uv sync --all-packages --all-extras
uv run pytest packages/python/bloque-redis -v
```
