"""Tests for database testing utilities."""

from sqlalchemy import Column, Integer, String
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool
from ulfblk_testing.db import create_tables, create_test_engine, create_test_session_factory


class _TestBase(DeclarativeBase):
    pass


class _TestModel(_TestBase):
    __tablename__ = "_ulfblk_testing_test"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class TestCreateTestEngine:
    def test_returns_async_engine(self):
        engine = create_test_engine()
        assert isinstance(engine, AsyncEngine)

    def test_sqlite_uses_static_pool(self):
        engine = create_test_engine()
        assert isinstance(engine.pool, StaticPool)

    def test_custom_url(self):
        engine = create_test_engine(database_url="sqlite+aiosqlite:///test.db")
        assert "test.db" in str(engine.url)


class TestCreateTestSessionFactory:
    def test_returns_sessionmaker(self):
        engine = create_test_engine()
        factory = create_test_session_factory(engine)
        assert isinstance(factory, async_sessionmaker)

    def test_expire_on_commit_false(self):
        engine = create_test_engine()
        factory = create_test_session_factory(engine)
        assert factory.kw.get("expire_on_commit") is False

    async def test_produces_async_session(self):
        engine = create_test_engine()
        factory = create_test_session_factory(engine)
        async with factory() as session:
            assert isinstance(session, AsyncSession)


class TestCreateTables:
    async def test_creates_model_tables(self):
        engine = create_test_engine()
        await create_tables(engine, _TestBase)
        async with engine.connect() as conn:
            table_names = await conn.run_sync(
                lambda sync_conn: sa_inspect(sync_conn).get_table_names()
            )
        assert "_ulfblk_testing_test" in table_names
