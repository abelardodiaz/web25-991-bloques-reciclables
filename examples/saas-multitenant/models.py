"""Application models using ulfblk-db mixins.

This is where the DEVELOPER defines their own models. Bloques provide
Base, TimestampMixin, SoftDeleteMixin - the developer composes them
into application-specific models with their own fields and relationships.
"""

from __future__ import annotations

import hashlib
import json
import secrets

from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from ulfblk_db import Base, SoftDeleteMixin, TimestampMixin


class User(Base, TimestampMixin, SoftDeleteMixin):
    """User model with auth fields and tenant isolation."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    tenant_id = Column(String(100), nullable=False, index=True)
    roles_json = Column(String(1000), nullable=False, default="[]")
    permissions_json = Column(String(2000), nullable=False, default="[]")

    orders: Mapped[list[Order]] = relationship("Order", back_populates="user")

    def set_password(self, password: str) -> None:
        """Hash password with salt using SHA-256."""
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        self.password_hash = f"{salt}:{hashed}"

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        if ":" not in self.password_hash:
            return False
        salt, stored_hash = self.password_hash.split(":", 1)
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() == stored_hash

    def get_roles(self) -> list[str]:
        """Parse roles from JSON string."""
        return json.loads(self.roles_json) if self.roles_json else []

    def get_permissions(self) -> list[str]:
        """Parse permissions from JSON string."""
        return json.loads(self.permissions_json) if self.permissions_json else []


class Order(Base, TimestampMixin):
    """Order model with tenant isolation and user relationship."""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    tenant_id = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="orders")
