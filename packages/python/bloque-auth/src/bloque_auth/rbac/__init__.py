"""Role-based access control for FastAPI."""

from .permissions import require_permissions, require_roles

__all__ = ["require_permissions", "require_roles"]
