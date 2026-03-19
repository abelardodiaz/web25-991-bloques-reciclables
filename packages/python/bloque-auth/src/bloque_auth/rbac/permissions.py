"""RBAC permission and role checking as FastAPI dependencies."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..jwt.manager import JWTManager, TokenData

security = HTTPBearer(auto_error=False)

# Module-level JWT manager reference, set via configure()
_jwt_manager: JWTManager | None = None


def configure(jwt_manager: JWTManager) -> None:
    """Configure the RBAC module with a JWTManager instance."""
    global _jwt_manager
    _jwt_manager = jwt_manager


def _get_jwt_manager() -> JWTManager:
    if _jwt_manager is None:
        raise RuntimeError(
            "RBAC not configured. Call bloque_auth.rbac.permissions.configure(jwt_manager) first."
        )
    return _jwt_manager


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(security),
    ],
) -> TokenData:
    """FastAPI dependency to extract and validate the current user from JWT."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    import jwt as pyjwt

    jwt_mgr = _get_jwt_manager()

    try:
        return jwt_mgr.decode_token(credentials.credentials)
    except pyjwt.ExpiredSignatureError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err
    except pyjwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def require_permissions(*required_permissions: str) -> Callable:
    """
    Factory for a FastAPI dependency that requires specific permissions.

    Usage:
        @app.delete("/users/{id}")
        async def delete_user(user=Depends(require_permissions("users:delete"))):
            ...
    """

    async def permission_checker(
        current_user: Annotated[TokenData, Depends(get_current_user)],
    ) -> TokenData:
        if "admin" in current_user.roles:
            return current_user

        user_perms = set(current_user.permissions)
        missing = set(required_permissions) - user_perms

        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(sorted(missing))}",
            )
        return current_user

    return permission_checker


def require_roles(*required_roles: str) -> Callable:
    """
    Factory for a FastAPI dependency that requires specific roles.

    Usage:
        @app.get("/admin/stats")
        async def admin_stats(user=Depends(require_roles("admin", "manager"))):
            ...
    """

    async def role_checker(
        current_user: Annotated[TokenData, Depends(get_current_user)],
    ) -> TokenData:
        user_roles = set(current_user.roles)
        if not user_roles.intersection(required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required roles: {', '.join(required_roles)}",
            )
        return current_user

    return role_checker
