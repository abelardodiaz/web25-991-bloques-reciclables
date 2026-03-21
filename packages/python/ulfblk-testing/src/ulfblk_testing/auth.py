"""Authentication testing utilities: RSA keys, JWT manager, token generation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ulfblk_auth.jwt import JWTManager


def generate_rsa_keys(key_size: int = 2048) -> tuple[str, str]:
    """Generate an RSA key pair for testing.

    Args:
        key_size: RSA key size in bits.

    Returns:
        Tuple of (private_pem, public_pem) as strings.
    """
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=key_size
    )
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


def create_jwt_manager(
    private_pem: str | None = None,
    public_pem: str | None = None,
    access_token_expire_minutes: int = 30,
    refresh_token_expire_days: int = 7,
) -> JWTManager:
    """Create a JWTManager configured for testing.

    If keys are not provided, generates a fresh RSA pair.

    Args:
        private_pem: RSA private key PEM string.
        public_pem: RSA public key PEM string.
        access_token_expire_minutes: Access token TTL.
        refresh_token_expire_days: Refresh token TTL.

    Returns:
        Configured JWTManager instance.
    """
    from ulfblk_auth.jwt import JWTManager

    if private_pem is None or public_pem is None:
        private_pem, public_pem = generate_rsa_keys()

    return JWTManager(
        private_key=private_pem,
        public_key=public_pem,
        access_token_expire_minutes=access_token_expire_minutes,
        refresh_token_expire_days=refresh_token_expire_days,
    )


def create_test_token(
    jwt_manager: JWTManager,
    user_id: str = "test-user-001",
    tenant_id: str = "test-tenant-001",
    roles: list[str] | None = None,
    permissions: list[str] | None = None,
) -> str:
    """Create a JWT access token with test defaults.

    Args:
        jwt_manager: JWTManager instance.
        user_id: User ID claim.
        tenant_id: Tenant ID claim.
        roles: List of role names.
        permissions: List of permission strings.

    Returns:
        Signed JWT access token string.
    """
    return jwt_manager.create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        roles=roles or [],
        permissions=permissions or [],
    )
