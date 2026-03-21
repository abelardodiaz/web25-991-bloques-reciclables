"""Role-based access control for FastAPI."""

from .permissions import configure, get_current_user, require_permissions, require_roles

__all__ = ["configure", "get_current_user", "require_permissions", "require_roles"]
