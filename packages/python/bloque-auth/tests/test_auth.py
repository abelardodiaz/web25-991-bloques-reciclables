"""Tests for bloque-auth JWT, RBAC, brute force, and credentials."""

from datetime import UTC, datetime, timedelta

import pytest
from bloque_auth.brute_force import BruteForceProtection
from bloque_auth.brute_force.protection import LoginAttemptState
from bloque_auth.credentials import CredentialEncryptor
from bloque_auth.jwt import JWTManager
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


@pytest.fixture
def rsa_keys():
    """Generate temporary RSA keys for testing."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem


@pytest.fixture
def jwt_manager(rsa_keys):
    private_pem, public_pem = rsa_keys
    return JWTManager(
        private_key=private_pem,
        public_key=public_pem,
        access_token_expire_minutes=30,
        refresh_token_expire_days=7,
    )


class TestJWTManager:
    def test_create_and_decode_access_token(self, jwt_manager):
        token = jwt_manager.create_access_token(
            user_id="user-1",
            tenant_id="tenant-abc",
            roles=["admin"],
            permissions=["users:read", "users:write"],
        )
        data = jwt_manager.decode_token(token)
        assert data.user_id == "user-1"
        assert data.tenant_id == "tenant-abc"
        assert data.roles == ["admin"]
        assert data.permissions == ["users:read", "users:write"]
        assert data.token_type == "access"

    def test_create_and_decode_refresh_token(self, jwt_manager):
        token = jwt_manager.create_refresh_token(
            user_id="user-1",
            tenant_id="tenant-abc",
        )
        data = jwt_manager.decode_token(token)
        assert data.user_id == "user-1"
        assert data.token_type == "refresh"

    def test_expired_token_raises(self, jwt_manager):
        import jwt as pyjwt

        token = jwt_manager.create_access_token(
            user_id="user-1",
            tenant_id="tenant-abc",
            expires_delta=timedelta(seconds=-1),
        )
        with pytest.raises(pyjwt.ExpiredSignatureError):
            jwt_manager.decode_token(token)


class TestBruteForce:
    def test_not_locked_initially(self):
        bf = BruteForceProtection(max_attempts=3, lockout_minutes=15)
        state = LoginAttemptState()
        assert not bf.is_locked(state)

    def test_locks_after_max_attempts(self):
        bf = BruteForceProtection(max_attempts=3, lockout_minutes=15)
        state = LoginAttemptState()
        for _ in range(3):
            state = bf.record_failed_attempt(state)
        assert bf.is_locked(state)

    def test_successful_login_resets(self):
        bf = BruteForceProtection(max_attempts=3, lockout_minutes=15)
        state = LoginAttemptState()
        state = bf.record_failed_attempt(state)
        state = bf.record_failed_attempt(state)
        state = bf.record_successful_login(state, ip_address="127.0.0.1")
        assert state.failed_attempts == 0
        assert state.locked_until is None
        assert state.last_login_ip == "127.0.0.1"

    def test_lock_expires(self):
        bf = BruteForceProtection(max_attempts=2, lockout_minutes=1)
        state = LoginAttemptState(
            failed_attempts=2,
            locked_until=datetime.now(UTC) - timedelta(minutes=2),
        )
        assert not bf.is_locked(state)


class TestCredentialEncryptor:
    def test_encrypt_decrypt_roundtrip(self):
        key = CredentialEncryptor.generate_key()
        enc = CredentialEncryptor(key=key)
        original = "sk-my-secret-api-key-12345"
        encrypted = enc.encrypt(original)
        assert encrypted != original
        assert enc.decrypt(encrypted) == original

    def test_rotate_key(self):
        old_key = CredentialEncryptor.generate_key()
        new_key = CredentialEncryptor.generate_key()
        enc = CredentialEncryptor(key=old_key)
        encrypted = enc.encrypt("secret-value")
        rotated = enc.rotate_key(encrypted, new_key)
        new_enc = CredentialEncryptor(key=new_key)
        assert new_enc.decrypt(rotated) == "secret-value"

    def test_invalid_key_fails(self):
        key = CredentialEncryptor.generate_key()
        enc = CredentialEncryptor(key=key)
        encrypted = enc.encrypt("test")
        wrong_key = CredentialEncryptor.generate_key()
        wrong_enc = CredentialEncryptor(key=wrong_key)
        from cryptography.fernet import InvalidToken
        with pytest.raises(InvalidToken):
            wrong_enc.decrypt(encrypted)
