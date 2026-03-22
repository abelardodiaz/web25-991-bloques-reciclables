"""Tests for ApiKeyService: register, validate, rotate, revoke."""

from __future__ import annotations

import pytest


class TestRegister:

    async def test_register_returns_raw_key(self, service, db_session):
        raw_key = await service.register_key(
            db_session, project_code="991", project_name="Bloques",
            secret="test-master-secret-123",
        )
        assert raw_key.startswith("test-991-")
        assert len(raw_key.split("-")) == 3

    async def test_register_invalid_secret_raises(self, service, db_session):
        with pytest.raises(ValueError, match="Invalid master secret"):
            await service.register_key(
                db_session, project_code="991", project_name="Bloques",
                secret="wrong-secret",
            )

    async def test_register_max_keys_exceeded(self, service, db_session):
        for _i in range(3):  # max_keys_per_project=3
            await service.register_key(
                db_session, project_code="991", project_name="Bloques",
                secret="test-master-secret-123",
            )
        with pytest.raises(ValueError, match="Maximum 3 active keys"):
            await service.register_key(
                db_session, project_code="991", project_name="Bloques",
                secret="test-master-secret-123",
            )

    async def test_register_creates_audit_log(self, service, db_session):
        await service.register_key(
            db_session, project_code="991", project_name="Bloques",
            secret="test-master-secret-123",
        )
        from sqlalchemy import select
        from ulfblk_api_keys.models import KeyAuditLog
        result = await db_session.execute(select(KeyAuditLog))
        logs = result.scalars().all()
        assert len(logs) == 1
        assert logs[0].action == "register"
        assert logs[0].project_code == "991"


class TestValidate:

    async def test_validate_valid_key(self, service, db_session):
        raw_key = await service.register_key(
            db_session, project_code="991", project_name="Bloques",
            secret="test-master-secret-123",
        )
        data = await service.validate_key(db_session, raw_key)
        assert data is not None
        assert data["project_code"] == "991"
        assert data["project_name"] == "Bloques"
        assert data["key_id"] >= 1

    async def test_validate_invalid_key_returns_none(self, service, db_session):
        data = await service.validate_key(db_session, "test-991-invalidhex")
        assert data is None

    async def test_validate_wrong_prefix_returns_none(self, service, db_session):
        data = await service.validate_key(db_session, "wrong-991-abcdef")
        assert data is None

    async def test_validate_caches_result(self, service, db_session, cache):
        raw_key = await service.register_key(
            db_session, project_code="991", project_name="Bloques",
            secret="test-master-secret-123",
        )
        # First call: DB lookup
        data1 = await service.validate_key(db_session, raw_key)
        assert data1 is not None
        # Second call: should come from cache
        assert cache.size >= 1
        data2 = await service.validate_key(db_session, raw_key)
        assert data2 == data1

    async def test_validate_increments_request_count(self, service, db_session, cache):
        raw_key = await service.register_key(
            db_session, project_code="991", project_name="Bloques",
            secret="test-master-secret-123",
        )
        # Clear cache to force DB lookup each time
        cache.clear()
        await service.validate_key(db_session, raw_key)
        cache.clear()
        await service.validate_key(db_session, raw_key)

        from sqlalchemy import select
        from ulfblk_api_keys.models import ApiKeyModel
        result = await db_session.execute(select(ApiKeyModel))
        key = result.scalar_one()
        assert key.request_count == 2


class TestRotate:

    async def test_rotate_returns_new_key(self, service, db_session):
        old_key = await service.register_key(
            db_session, project_code="991", project_name="Bloques",
            secret="test-master-secret-123",
        )
        new_key = await service.rotate_key(
            db_session, project_code="991", old_raw_key=old_key,
            secret="test-master-secret-123",
        )
        assert new_key != old_key
        assert new_key.startswith("test-991-")

    async def test_rotate_old_key_gets_expiration(self, service, db_session):
        old_key = await service.register_key(
            db_session, project_code="991", project_name="Bloques",
            secret="test-master-secret-123",
        )
        await service.rotate_key(
            db_session, project_code="991", old_raw_key=old_key,
            secret="test-master-secret-123",
        )
        # Old key should still validate (within grace period)
        data = await service.validate_key(db_session, old_key)
        assert data is not None

    async def test_rotate_invalid_old_key_raises(self, service, db_session):
        with pytest.raises(ValueError, match="Old API key not found"):
            await service.rotate_key(
                db_session, project_code="991", old_raw_key="test-991-fake",
                secret="test-master-secret-123",
            )


class TestRevoke:

    async def test_revoke_deactivates_key(self, service, db_session, cache):
        raw_key = await service.register_key(
            db_session, project_code="991", project_name="Bloques",
            secret="test-master-secret-123",
        )
        # Get key_id
        data = await service.validate_key(db_session, raw_key)
        key_id = data["key_id"]

        # Revoke
        cache.clear()
        result = await service.revoke_key(db_session, key_id)
        assert result is True

        # Should no longer validate
        cache.clear()
        data = await service.validate_key(db_session, raw_key)
        assert data is None

    async def test_revoke_nonexistent_returns_false(self, service, db_session):
        result = await service.revoke_key(db_session, key_id=99999)
        assert result is False
