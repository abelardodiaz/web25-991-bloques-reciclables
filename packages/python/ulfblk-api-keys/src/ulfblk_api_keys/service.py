"""Core API key service: validate, register, rotate, revoke."""

from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .cache import InMemoryCache
from .config import ApiKeyConfig
from .models import ApiKeyModel, KeyAuditLog


def _hash_key(raw_key: str) -> str:
    """SHA-256 hash of a raw API key."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


def _hash_secret(secret: str) -> str:
    """SHA-256 hash for master secret comparison."""
    return hashlib.sha256(secret.encode()).hexdigest()


def _generate_raw_key(prefix: str, project_code: str, key_bytes: int = 24) -> str:
    """Generate a new raw API key: {prefix}-{project_code}-{hex}."""
    random_hex = os.urandom(key_bytes).hex()
    return f"{prefix}-{project_code}-{random_hex}"


class ApiKeyService:
    """Manages API key lifecycle: validate, register, rotate, revoke.

    Args:
        config: API key configuration.
        cache: In-memory cache instance (shared across requests).

    Example::

        config = ApiKeyConfig(prefix="ak", master_secret="my-secret")
        cache = InMemoryCache(default_ttl=60)
        service = ApiKeyService(config=config, cache=cache)

        async with session_factory() as db:
            raw_key = await service.register_key(
                db, project_code="991", project_name="Bloques", secret="my-secret"
            )
            key_data = await service.validate_key(db, raw_key)
    """

    def __init__(self, config: ApiKeyConfig, cache: InMemoryCache | None = None) -> None:
        self.config = config
        self.cache = cache or InMemoryCache(default_ttl=config.cache_ttl_seconds)
        self._secret_hash = _hash_secret(config.master_secret) if config.master_secret else ""

    def _verify_secret(self, secret: str) -> bool:
        """Verify master secret using constant-time comparison."""
        if not self._secret_hash:
            return False
        return _hash_secret(secret) == self._secret_hash

    async def validate_key(self, db: AsyncSession, raw_key: str) -> dict | None:
        """Validate an API key. Returns key data dict or None.

        Checks: format, cache, DB lookup, is_active, expiration.
        Updates request_count and last_used_at asynchronously.
        """
        # Check prefix format
        parts = raw_key.split("-", 2)
        if len(parts) != 3 or parts[0] != self.config.prefix:
            return None

        key_hash = _hash_key(raw_key)

        # Check cache
        cached = self.cache.get(key_hash)
        if cached is not None:
            return cached

        # Query DB
        result = await db.execute(
            select(ApiKeyModel).where(ApiKeyModel.key_hash == key_hash)
        )
        key_record = result.scalar_one_or_none()
        if key_record is None:
            return None

        # Check active
        if not key_record.is_active:
            return None

        # Check expiration
        now = datetime.now(UTC)
        if key_record.expires_at and key_record.expires_at.replace(tzinfo=UTC) < now:
            return None

        key_data = {
            "key_id": key_record.id,
            "project_code": key_record.project_code,
            "project_name": key_record.project_name,
            "permissions": key_record.permissions,
        }

        # Cache the result
        self.cache.set(key_hash, key_data)

        # Update stats (fire-and-forget style, within same session)
        key_record.last_used_at = now
        key_record.request_count += 1
        await db.commit()

        return key_data

    async def register_key(
        self,
        db: AsyncSession,
        project_code: str,
        project_name: str,
        secret: str,
        permissions: dict | None = None,
    ) -> str:
        """Register a new API key. Returns the raw key (shown once only).

        Raises ValueError if secret is invalid or max keys exceeded.
        """
        if not self._verify_secret(secret):
            raise ValueError("Invalid master secret.")

        # Check max keys per project
        result = await db.execute(
            select(ApiKeyModel).where(
                ApiKeyModel.project_code == project_code,
                ApiKeyModel.is_active.is_(True),
            )
        )
        active_keys = result.scalars().all()
        if len(active_keys) >= self.config.max_keys_per_project:
            raise ValueError(
                f"Maximum {self.config.max_keys_per_project} active keys per project."
            )

        # Generate key
        raw_key = _generate_raw_key(
            self.config.prefix, project_code, self.config.key_bytes,
        )
        key_hash = _hash_key(raw_key)

        # Store
        key_record = ApiKeyModel(
            key_hash=key_hash,
            project_code=project_code,
            project_name=project_name,
            is_active=True,
            permissions=permissions,
        )
        db.add(key_record)

        # Audit
        db.add(KeyAuditLog(
            action="register",
            project_code=project_code,
            details={"project_name": project_name},
        ))

        await db.commit()
        await db.refresh(key_record)

        return raw_key

    async def rotate_key(
        self, db: AsyncSession, project_code: str, old_raw_key: str, secret: str,
    ) -> str:
        """Rotate a key. Old key stays active for grace period.

        Returns the new raw key. Raises ValueError if secret or old key is invalid.
        """
        if not self._verify_secret(secret):
            raise ValueError("Invalid master secret.")

        # Validate old key exists
        old_hash = _hash_key(old_raw_key)
        result = await db.execute(
            select(ApiKeyModel).where(
                ApiKeyModel.key_hash == old_hash,
                ApiKeyModel.project_code == project_code,
                ApiKeyModel.is_active.is_(True),
            )
        )
        old_record = result.scalar_one_or_none()
        if old_record is None:
            raise ValueError("Old API key not found or inactive.")

        # Set old key to expire after grace period
        old_record.expires_at = datetime.now(UTC) + timedelta(
            days=self.config.grace_period_days
        )

        # Generate new key
        raw_key = _generate_raw_key(
            self.config.prefix, project_code, self.config.key_bytes,
        )
        key_hash = _hash_key(raw_key)

        new_record = ApiKeyModel(
            key_hash=key_hash,
            project_code=project_code,
            project_name=old_record.project_name,
            is_active=True,
            permissions=old_record.permissions,
        )
        db.add(new_record)

        # Invalidate cache for old key
        self.cache.invalidate(old_hash)

        # Audit
        db.add(KeyAuditLog(
            action="rotate",
            project_code=project_code,
            key_id=old_record.id,
            details={"old_expires_at": str(old_record.expires_at)},
        ))

        await db.commit()
        return raw_key

    async def revoke_key(self, db: AsyncSession, key_id: int) -> bool:
        """Revoke a key immediately. Returns True if found and revoked."""
        result = await db.execute(
            select(ApiKeyModel).where(ApiKeyModel.id == key_id)
        )
        key_record = result.scalar_one_or_none()
        if key_record is None:
            return False

        key_record.is_active = False

        # Invalidate cache
        self.cache.invalidate(key_record.key_hash)

        # Audit
        db.add(KeyAuditLog(
            action="revoke",
            project_code=key_record.project_code,
            key_id=key_id,
        ))

        await db.commit()
        return True

    async def get_project_keys(
        self, db: AsyncSession, project_code: str,
    ) -> list[dict]:
        """List all keys for a project."""
        result = await db.execute(
            select(ApiKeyModel).where(ApiKeyModel.project_code == project_code)
        )
        keys = result.scalars().all()
        return [
            {
                "id": k.id,
                "project_code": k.project_code,
                "project_name": k.project_name,
                "is_active": k.is_active,
                "request_count": k.request_count,
                "last_used_at": k.last_used_at,
                "created_at": k.created_at,
                "expires_at": k.expires_at,
            }
            for k in keys
        ]
