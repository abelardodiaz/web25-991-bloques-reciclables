"""SQLAlchemy declarative base."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models in the Bloques ecosystem.

    Does not include an abstract ``id`` column - each project decides
    its own primary key strategy.

    Example::

        from bloque_db import Base, TimestampMixin

        class User(Base, TimestampMixin):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String, nullable=False)
    """

    pass
