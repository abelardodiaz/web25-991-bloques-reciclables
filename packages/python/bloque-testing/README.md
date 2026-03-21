# bloque-testing

Shared testing utilities and pytest fixtures for the Bloques ecosystem.

## Installation

```bash
# Base (HTTP client factories + settings helpers)
uv add --dev bloque-testing

# With JWT auth fixtures
uv add --dev "bloque-testing[auth]"

# With database fixtures
uv add --dev "bloque-testing[db]"

# Everything
uv add --dev "bloque-testing[all]"
```

## Auto-registered Fixtures (pytest plugin)

When installed, these fixtures are automatically available in your tests:

| Fixture | Requires | Scope | Description |
|---------|----------|-------|-------------|
| `test_app` | base | function | Minimal FastAPI app with `/ping` endpoint |
| `test_client` | base | function | AsyncClient bound to `test_app` |
| `rsa_keys` | `[auth]` | session | RSA key pair `(private_pem, public_pem)` |
| `jwt_manager` | `[auth]` | function | `JWTManager` with test RSA keys |
| `test_engine` | `[db]` | function | SQLite in-memory AsyncEngine |
| `test_session_factory` | `[db]` | function | `async_sessionmaker` bound to engine |

## Helper Functions

### HTTP Clients

```python
from bloque_testing import create_test_client, create_authenticated_client

# Basic client
async with create_test_client(app) as client:
    resp = await client.get("/health")

# Authenticated client
token = create_test_token(jwt_manager)
async with create_authenticated_client(app, token) as client:
    resp = await client.get("/protected")
```

### JWT Auth (`[auth]` extra)

```python
from bloque_testing import generate_rsa_keys, create_jwt_manager, create_test_token

# Generate keys + manager
private_pem, public_pem = generate_rsa_keys()
manager = create_jwt_manager(private_pem, public_pem)

# Or auto-generate keys
manager = create_jwt_manager()

# Create test tokens with defaults
token = create_test_token(manager, user_id="u-1", tenant_id="t-1", roles=["admin"])
```

### Database (`[db]` extra)

```python
from bloque_testing import create_test_engine, create_test_session_factory, create_tables

engine = create_test_engine()
session_factory = create_test_session_factory(engine)
await create_tables(engine, Base)

async with session_factory() as session:
    # your test queries
    pass
```

### Settings

```python
from bloque_testing import create_test_settings, override_settings
from bloque_core import BloqueSettings

# Create settings with overrides
settings = create_test_settings(BloqueSettings, debug=True)

# Temporarily patch a settings object
with override_settings("myapp.config.settings", BloqueSettings, debug=True):
    # settings patched here
    pass
```
