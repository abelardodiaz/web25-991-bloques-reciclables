# NOTA TEMPORAL: Propuesta bloque ulfblk-api-keys

> **TEMPORAL** - Eliminar este archivo despues de implementar el bloque ulfblk-api-keys.
> Creado por 996 el 2026-03-22 como referencia para 991.

---

## Por que

El patron de autenticacion por API key se repite en multiples proyectos:
- **900** (Interactions Pro) - Python/FastAPI
- **99999** (Project Manager) - Node.js/Express
- **994** (Twitter Publisher API) - proximo proyecto, necesita este bloque

Cada proyecto reimplementa lo mismo. Un bloque reutilizable ahorraria trabajo y estandarizaria el patron.

---

## Patron comun (extraido de 900 y 99999)

| Aspecto | Implementacion |
|---------|---------------|
| Key format | `{prefix}-{project_code}-{48_hex}` (24 bytes os.urandom) |
| Storage | SHA-256 hash only, nunca plain text |
| Cache | In-memory dict, TTL 60 segundos |
| Max keys/proyecto | 5 (configurable) |
| Grace period rotacion | 7 dias (key vieja sigue activa) |
| Audit log | Tabla dedicada con IP + User-Agent + action + details JSONB |
| Request counting | last_used_at + request_count (update async fire-and-forget) |
| Master secret | Requerido para registro y rotacion |
| Extraccion key | Header `X-API-Key` + query param `?api_key=` |

---

## Bloque propuesto: ulfblk-api-keys

### Estructura

```
packages/python/ulfblk-api-keys/
  src/ulfblk_api_keys/
    __init__.py
    middleware.py       # FastAPI Depends() para validar X-API-Key
    service.py          # validate_key(), register_key(), rotate_key(), revoke_key()
    models.py           # SQLAlchemy: api_keys, key_audit_log
    schemas.py          # Pydantic: RegisterRequest, RotateRequest, KeyInfo
    router.py           # FastAPI router: /keys/register, /keys/rotate, /keys/info
    cache.py            # In-memory cache con TTL (sin Redis)
    config.py           # Settings: prefix, max_keys, grace_days, secret_hash_algo
  tests/
    test_middleware.py
    test_service.py
    test_router.py
    test_cache.py
  pyproject.toml
```

### Modelos SQLAlchemy

```python
# api_keys
class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True)
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)  # SHA-256
    project_code: Mapped[str] = mapped_column(String(20), nullable=False)
    project_name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    rate_limit_rpm: Mapped[int] = mapped_column(default=60)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    request_count: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default={})


# key_audit_log
class KeyAuditLog(Base):
    __tablename__ = "key_audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # register, rotate, revoke, failed_attempt
    project_code: Mapped[Optional[str]] = mapped_column(String(20))
    key_id: Mapped[Optional[int]] = mapped_column(ForeignKey("api_keys.id", ondelete="SET NULL"))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6 max
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    details: Mapped[dict] = mapped_column(JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(default=func.now())
```

### Middleware (FastAPI Depends)

```python
from fastapi import Depends, Header, HTTPException, Request

class ApiKeyAuth:
    """FastAPI dependency for API key validation."""

    def __init__(self, required: bool = True):
        self.required = required

    async def __call__(
        self,
        request: Request,
        x_api_key: str | None = Header(None),
    ) -> dict | None:
        raw_key = x_api_key or request.query_params.get("api_key")

        if not raw_key:
            if self.required:
                raise HTTPException(status_code=401, detail="API key required")
            return None

        key_data = await validate_key(raw_key)
        if not key_data:
            raise HTTPException(status_code=401, detail="Invalid API key")

        # Attach to request state for downstream use
        request.state.project_code = key_data["project_code"]
        request.state.project_name = key_data["project_name"]
        request.state.key_id = key_data["key_id"]

        return key_data

# Usage in routes:
# @app.post("/api/tweet")
# async def post_tweet(auth: dict = Depends(ApiKeyAuth())):
#     print(auth["project_code"])  # "994"
```

### Service

```python
class ApiKeyService:
    def __init__(self, db_session, cache, config):
        self.db = db_session
        self.cache = cache  # InMemoryCache(ttl=60)
        self.config = config

    async def validate_key(self, raw_key: str) -> dict | None:
        """Validate key: check format, hash, cache/DB lookup, expiration."""
        # 1. Check prefix format
        # 2. SHA-256 hash
        # 3. Check cache (60s TTL)
        # 4. Query DB if cache miss
        # 5. Check is_active + expires_at
        # 6. Update stats async (fire-and-forget)
        # 7. Return {project_code, project_name, key_id} or None

    async def register_key(self, project_code, project_name, secret) -> str:
        """Register new key. Returns raw key (shown once only)."""
        # 1. Verify master secret
        # 2. Check max keys per project
        # 3. Generate: {prefix}-{project_code}-{48_hex}
        # 4. Store SHA-256 hash
        # 5. Audit log: 'register'
        # 6. Return raw key

    async def rotate_key(self, project_code, old_key, secret) -> str:
        """Rotate key. Old key stays active for grace period."""
        # 1. Verify master secret
        # 2. Validate old key
        # 3. Set old key expires_at = now + grace_days
        # 4. Generate new key
        # 5. Invalidate cache
        # 6. Audit log: 'rotate'
        # 7. Return new raw key

    async def revoke_key(self, key_id) -> bool:
        """Revoke a key immediately."""
        # 1. Set is_active = False
        # 2. Invalidate cache
        # 3. Audit log: 'revoke'
```

### Router

```python
router = APIRouter(prefix="/keys", tags=["API Keys"])

@router.post("/register")
async def register(body: RegisterRequest):
    """Register new API key. Requires master secret."""
    # Returns: {api_key: "xx-project-hex...", key_id, created_at}

@router.post("/rotate")
async def rotate(body: RotateRequest):
    """Rotate API key. Old key valid for grace period."""
    # Returns: {api_key: "xx-project-hex...", old_key_expires_at}

@router.get("/info")
async def info(auth: dict = Depends(ApiKeyAuth())):
    """Info about keys for authenticated project."""
    # Returns: [{id, is_active, rate_limit_rpm, last_used_at, request_count, created_at, expires_at}]
```

### Config

```python
class ApiKeyConfig(BaseModel):
    prefix: str = "ak"                    # key prefix (900 usa "900", 99999 usa "pm")
    max_keys_per_project: int = 5
    grace_period_days: int = 7
    cache_ttl_seconds: int = 60
    secret_hash_algo: str = "sha256"      # o "argon2id" (900 usa argon2, 99999 usa double-sha256)
    key_bytes: int = 24                   # 24 bytes = 48 hex chars
```

### Uso por otros proyectos

```python
from ulfblk_api_keys import ApiKeyAuth, ApiKeyService, api_keys_router
from ulfblk_api_keys.config import ApiKeyConfig

# Config
config = ApiKeyConfig(prefix="tw", max_keys_per_project=3)

# Mount router
app.include_router(api_keys_router)

# Use as dependency
@app.post("/api/tweet")
async def post_tweet(payload: TweetRequest, auth: dict = Depends(ApiKeyAuth())):
    # auth = {project_code: "073", project_name: "Portfolio Organico", key_id: 1}
    ...
```

### pyproject.toml

```toml
[project]
name = "ulfblk-api-keys"
version = "0.1.0"
description = "API key authentication for FastAPI services"
requires-python = ">=3.11"
dependencies = [
    "ulfblk-core>=0.1.0",
    "ulfblk-db>=0.1.0",
    "fastapi>=0.115.0",
    "pydantic>=2.0",
]

[project.optional-dependencies]
argon2 = ["argon2-cffi>=23.0"]  # opcional, para secret hashing con argon2
dev = ["pytest>=8.0", "pytest-asyncio>=0.24", "httpx>=0.27"]
```

---

## Implementaciones de referencia - Rutas exactas

### 900 (Python/FastAPI) - server003

| Archivo | Ruta |
|---------|------|
| Middleware auth | `/var/www/web25-900-interactions-pro/backend/src/api/middleware/auth.py` |
| Endpoints keys | `/var/www/web25-900-interactions-pro/backend/src/api/endpoints/keys.py` |
| API key service | `/var/www/web25-900-interactions-pro/backend/src/services/api_key_service.py` |
| Audit service | `/var/www/web25-900-interactions-pro/backend/src/services/key_audit_service.py` |
| Rate limiter | `/var/www/web25-900-interactions-pro/backend/src/services/rate_limiter.py` |
| Migration keys | `/var/www/web25-900-interactions-pro/backend/src/database/008_api_keys.sql` |
| Migration mgmt | `/var/www/web25-900-interactions-pro/backend/src/database/009_key_management.sql` |

**Detalles 900:**
- Prefix: `900-`
- Secret: Argon2id hash
- Rate limiting: Redis sliding window, escalating backoff (2min -> 5min -> 15min -> 1h)
- Auth modes: `warn` (default, logs pero permite) y `enforce` (401 sin key)
- Excluded paths: `/`, `/health`, `/docs`, `/redoc`, `/openapi.json`, `/api/v1/keys/register`, `/api/v1/keys/rotate`

### 99999 (Node.js/Express) - server003

| Archivo | Ruta |
|---------|------|
| Middleware api-key | `/home/ubuntu/apps/web26-99999-project-manager/middleware/api-key.js` |
| Middleware auth | `/home/ubuntu/apps/web26-99999-project-manager/middleware/auth.js` |
| Routes keys | `/home/ubuntu/apps/web26-99999-project-manager/routes/api/keys.js` |
| API key service | `/home/ubuntu/apps/web26-99999-project-manager/services/api-key-service.js` |
| Migration v0.7.0 | `/home/ubuntu/apps/web26-99999-project-manager/scripts/migration-v0.7.0-api-keys.sql` |
| Migration v0.8.0 | `/home/ubuntu/apps/web26-99999-project-manager/scripts/migration-v0.8.0-cloudflare.sql` |

**Detalles 99999:**
- Prefix: `pm-`
- Secret: Double SHA-256 + timing-safe comparison
- Permisos granulares: JSONB `cf_permissions` (dns:read, dns:write, cache:purge, allowed_subdomains, allowed_hosts)
- Auth: Falls through a OAuth si no hay API key valida
- CF audit log separado: tabla `manager_cf_audit_log`

---

## Diferencias clave entre 900 y 99999

| Feature | 900 (Python) | 99999 (Node.js) |
|---------|-------------|-----------------|
| Secret hashing | Argon2id | Double SHA-256 timing-safe |
| Rate limiting | Redis sliding window | Env-based manual |
| Permisos extra | No | JSONB cf_permissions |
| Auth fallback | warn/enforce modes | OAuth fallback |
| Audit tables | 1 (key_audit_log) | 2 (key_audit + cf_audit) |

**Recomendacion para el bloque:** Tomar lo mejor de ambos:
- Argon2id de 900 (mas seguro que double-SHA256) como opcion
- SHA-256 como default (mas simple, sin dependency extra)
- Permisos JSONB de 99999 (generico, extensible) como campo opcional
- Cache in-memory de ambos (60s TTL, sin Redis obligatorio)
- Audit log unico (como 900)
