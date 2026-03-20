"""Tests for Base and mixins."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, inspect as sa_inspect
from sqlalchemy.orm import DeclarativeBase

from bloque_db import Base, SoftDeleteMixin, TimestampMixin


class TestBase:
    def test_is_declarative_base(self):
        assert issubclass(Base, DeclarativeBase)

    def test_has_registry(self):
        assert hasattr(Base, "registry")


class TestTimestampMixin:
    def test_has_timestamp_columns(self):
        class _TSModel(Base, TimestampMixin):
            __tablename__ = "_test_ts"
            id = Column(Integer, primary_key=True)

        mapper = sa_inspect(_TSModel)
        column_names = [c.key for c in mapper.columns]
        assert "created_at" in column_names
        assert "updated_at" in column_names

    def test_updated_at_has_onupdate(self):
        class _TSModel2(Base, TimestampMixin):
            __tablename__ = "_test_ts2"
            id = Column(Integer, primary_key=True)

        mapper = sa_inspect(_TSModel2)
        updated_col = mapper.columns["updated_at"]
        assert updated_col.onupdate is not None


class TestSoftDeleteMixin:
    def test_deleted_at_default_none(self):
        class _SDModel(Base, SoftDeleteMixin):
            __tablename__ = "_test_sd"
            id = Column(Integer, primary_key=True)

        obj = _SDModel()
        assert obj.deleted_at is None
        assert obj.is_deleted is False

    def test_soft_delete(self):
        class _SDModel2(Base, SoftDeleteMixin):
            __tablename__ = "_test_sd2"
            id = Column(Integer, primary_key=True)

        obj = _SDModel2()
        obj.soft_delete()
        assert obj.is_deleted is True
        assert isinstance(obj.deleted_at, datetime)

    def test_restore(self):
        class _SDModel3(Base, SoftDeleteMixin):
            __tablename__ = "_test_sd3"
            id = Column(Integer, primary_key=True)

        obj = _SDModel3()
        obj.soft_delete()
        obj.restore()
        assert obj.is_deleted is False
        assert obj.deleted_at is None


class TestComposedModel:
    def test_model_with_both_mixins(self):
        class _ComposedModel(Base, TimestampMixin, SoftDeleteMixin):
            __tablename__ = "_test_composed"
            id = Column(Integer, primary_key=True)
            name = Column(String, nullable=False)

        mapper = sa_inspect(_ComposedModel)
        column_names = [c.key for c in mapper.columns]
        assert "created_at" in column_names
        assert "updated_at" in column_names
        assert "deleted_at" in column_names
        assert "name" in column_names

        obj = _ComposedModel()
        obj.soft_delete()
        assert obj.is_deleted is True
