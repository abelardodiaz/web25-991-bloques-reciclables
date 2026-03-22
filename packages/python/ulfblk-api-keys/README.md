# ulfblk-api-keys

API key authentication for FastAPI services.

## Install

```bash
uv add ulfblk-api-keys
```

## Quick Start

```python
from ulfblk_api_keys import ApiKeyConfig, ApiKeyService, InMemoryCache, create_api_keys_router

config = ApiKeyConfig(prefix="ak", master_secret="your-secret")
cache = InMemoryCache(default_ttl=60)
service = ApiKeyService(config=config, cache=cache)

router = create_api_keys_router(service, db_dependency)
app.include_router(router)
```
