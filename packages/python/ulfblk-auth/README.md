# ulfblk-auth

Authentication and authorization for FastAPI: JWT RS256, RBAC, brute force protection, and credential encryption.

Part of [Bloques Reciclables](https://github.com/abelardodiaz/web25-991-bloques-reciclables) - an open source ecosystem of reusable code blocks.

## Installation

```bash
uv add ulfblk-auth
# or
pip install ulfblk-auth
```

## Features

### JWT Manager (RS256)

Asymmetric JWT tokens with tenant and role support:

```python
from ulfblk_auth.jwt import JWTManager

jwt_manager = JWTManager(
    private_key=PRIVATE_KEY_PEM,
    public_key=PUBLIC_KEY_PEM,
    access_token_expire_minutes=30,
    refresh_token_expire_days=7,
)

# Create tokens
access_token = jwt_manager.create_access_token(
    user_id="user-123",
    tenant_id="acme",
    roles=["admin"],
    permissions=["users:read", "users:write"],
)

refresh_token = jwt_manager.create_refresh_token(
    user_id="user-123",
    tenant_id="acme",
)

# Decode and validate
token_data = jwt_manager.decode_token(access_token)
# token_data.user_id, token_data.tenant_id, token_data.roles, token_data.permissions
```

### RBAC (Role-Based Access Control)

FastAPI dependency injection for permission and role checks:

```python
from ulfblk_auth.rbac import configure, require_permissions, require_roles, get_current_user

# Configure once at startup
configure(jwt_manager)

# Require specific permissions
@app.delete("/users/{user_id}")
async def delete_user(user=Depends(require_permissions("users:delete"))):
    ...

# Require specific roles
@app.get("/admin/stats")
async def admin_stats(user=Depends(require_roles("admin", "manager"))):
    ...

# Get current user (any authenticated user)
@app.get("/me")
async def me(user=Depends(get_current_user)):
    return {"user_id": user.user_id, "tenant": user.tenant_id}
```

### Brute Force Protection

Storage-agnostic login attempt tracking with account lockout:

```python
from ulfblk_auth.brute_force import BruteForceProtection, LoginAttemptState

protection = BruteForceProtection(max_attempts=5, lockout_minutes=30)

# Check if locked
state = LoginAttemptState()  # load from your storage
if protection.is_locked(state):
    raise HTTPException(status_code=429, detail="Account locked")

# Record attempts
state = protection.record_failed_attempt(state, ip_address="1.2.3.4")
# or on success:
state = protection.record_successful_login(state, ip_address="1.2.3.4")
# persist state to your storage
```

### Credential Encryption (Fernet AES-256)

Encrypt sensitive credentials (API keys, tokens) for storage:

```python
from ulfblk_auth.credentials import CredentialEncryptor

# Generate a key (store securely, e.g., in env vars)
key = CredentialEncryptor.generate_key()

encryptor = CredentialEncryptor(key=key)
encrypted = encryptor.encrypt("sk-my-secret-api-key")
decrypted = encryptor.decrypt(encrypted)

# Key rotation
new_key = CredentialEncryptor.generate_key()
re_encrypted = encryptor.rotate_key(encrypted, new_key)
```

## Migrating to External Auth

If your project grows and you need enterprise-grade auth (SOC2, SSO, MFA), you can replace JWTManager with an external provider while keeping RBAC:

```python
# Before: ulfblk-auth JWTManager
from ulfblk_auth.jwt import JWTManager
jwt_manager = JWTManager(private_key=PEM, public_key=PEM)

# After: Auth0 / Clerk / Supabase Auth
# 1. Replace JWTManager with your provider's JWT verification
# 2. Keep using require_permissions() and require_roles() - they only
#    need a TokenData object with user_id, tenant_id, roles, permissions
# 3. Replace configure(jwt_manager) with a custom get_current_user
#    that validates tokens against your provider's JWKS endpoint
```

ulfblk-auth is designed for indie devs and startups who need auth fast. When you outgrow it, the migration path is straightforward because RBAC dependencies are decoupled from token creation.

## Dependencies

- [ulfblk-core](https://github.com/abelardodiaz/web25-991-bloques-reciclables/tree/main/packages/python/ulfblk-core)
- PyJWT (RS256)
- cryptography (Fernet)

## Requirements

- Python 3.11+
- FastAPI 0.115+

## License

[MIT](https://github.com/abelardodiaz/web25-991-bloques-reciclables/blob/main/LICENSE)
