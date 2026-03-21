# ulfblk-gateway

API Gateway con rate limiting (Redis/in-memory), reverse proxy via httpx, y circuit breaker para proteger upstreams.

## Instalacion

```bash
uv add ulfblk-gateway
```

## Rate Limiting

```python
from ulfblk_gateway.rate_limiter import (
    InMemoryBackend,
    RateLimiterMiddleware,
    RateLimiterSettings,
)

settings = RateLimiterSettings(
    requests=100,          # max por ventana
    window_seconds=60,
    exclude_paths=["/health"],
)
backend = InMemoryBackend()

app.add_middleware(RateLimiterMiddleware, settings=settings, backend=backend)
```

Con Redis (soft dependency via ulfblk-redis):

```python
from ulfblk_gateway.rate_limiter import RedisBackend, RateLimiterMiddleware, RateLimiterSettings
from ulfblk_redis import RedisManager

redis = RedisManager()
await redis.connect()

backend = RedisBackend(redis)
app.add_middleware(
    RateLimiterMiddleware,
    settings=RateLimiterSettings(requests=100, window_seconds=60),
    backend=backend,
)
```

## Reverse Proxy

```python
from ulfblk_gateway.proxy import ProxyHandler, ProxyMiddleware, ProxyRoute, ProxySettings

settings = ProxySettings(
    routes=[
        ProxyRoute(path_prefix="/api/users", upstream_url="http://user-service:8001"),
        ProxyRoute(path_prefix="/api/orders", upstream_url="http://order-service:8002"),
    ]
)

handler = ProxyHandler(settings)
await handler.start()

app.add_middleware(ProxyMiddleware, handler=handler)
```

## Circuit Breaker

```python
from ulfblk_gateway.circuit_breaker import CircuitBreaker, CircuitBreakerSettings

cb = CircuitBreaker("user-service", CircuitBreakerSettings(
    failure_threshold=5,
    recovery_timeout=30.0,
    success_threshold=2,
))

# Integrado con proxy middleware
app.add_middleware(
    ProxyMiddleware,
    handler=handler,
    circuit_breakers={"http://user-service:8001": cb},
)
```

## Health Check

```python
from ulfblk_gateway.health import gateway_health_check

status = await gateway_health_check(handler)
# {"gateway": True, "upstream:http://user-service:8001": True}
```

## Dependencias

- `ulfblk-core` (obligatorio)
- `httpx>=0.27` (obligatorio)
- `ulfblk-redis` (opcional, para RedisBackend)

## License

MIT
