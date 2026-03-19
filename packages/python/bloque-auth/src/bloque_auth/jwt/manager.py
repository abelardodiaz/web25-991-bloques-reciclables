"""JWT RS256 token manager with tenant and role support."""

from datetime import UTC, datetime, timedelta

import jwt
from pydantic import BaseModel


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str  # user_id
    tenant: str  # tenant_id or slug
    exp: datetime
    iat: datetime
    type: str  # "access" or "refresh"
    roles: list[str] = []
    permissions: list[str] = []


class TokenData(BaseModel):
    """Decoded token data for application use."""

    user_id: str
    tenant_id: str
    roles: list[str]
    permissions: list[str]
    token_type: str


class JWTManager:
    """
    JWT token manager using RS256 (asymmetric keys).

    Args:
        private_key: RSA private key in PEM format (for signing)
        public_key: RSA public key in PEM format (for verification)
        algorithm: JWT algorithm (default RS256)
        access_token_expire_minutes: Access token TTL
        refresh_token_expire_days: Refresh token TTL
    """

    def __init__(
        self,
        private_key: str | None = None,
        public_key: str | None = None,
        algorithm: str = "RS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        self.private_key = private_key
        self.public_key = public_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(
        self,
        user_id: str,
        tenant_id: str,
        roles: list[str] | None = None,
        permissions: list[str] | None = None,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create an access token."""
        if not self.private_key:
            raise ValueError("Private key required for signing tokens")

        if expires_delta is None:
            expires_delta = timedelta(minutes=self.access_token_expire_minutes)

        now = datetime.now(UTC)
        payload = TokenPayload(
            sub=user_id,
            tenant=tenant_id,
            exp=now + expires_delta,
            iat=now,
            type="access",
            roles=roles or [],
            permissions=permissions or [],
        )

        return jwt.encode(
            payload.model_dump(),
            self.private_key,
            algorithm=self.algorithm,
        )

    def create_refresh_token(
        self,
        user_id: str,
        tenant_id: str,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a refresh token."""
        if not self.private_key:
            raise ValueError("Private key required for signing tokens")

        if expires_delta is None:
            expires_delta = timedelta(days=self.refresh_token_expire_days)

        now = datetime.now(UTC)
        payload = TokenPayload(
            sub=user_id,
            tenant=tenant_id,
            exp=now + expires_delta,
            iat=now,
            type="refresh",
        )

        return jwt.encode(
            payload.model_dump(),
            self.private_key,
            algorithm=self.algorithm,
        )

    def decode_token(self, token: str) -> TokenData:
        """
        Decode and validate a JWT token.

        Raises:
            jwt.ExpiredSignatureError: Token expired
            jwt.InvalidTokenError: Token invalid
        """
        key = self.public_key or self.private_key
        if not key:
            raise ValueError("Public or private key required for decoding tokens")

        payload = jwt.decode(token, key, algorithms=[self.algorithm])

        return TokenData(
            user_id=payload["sub"],
            tenant_id=payload["tenant"],
            roles=payload.get("roles", []),
            permissions=payload.get("permissions", []),
            token_type=payload["type"],
        )
