"""Tests that ulfblk-db mixins compose correctly into real models with relationships."""

from sqlalchemy import inspect as sa_inspect, select

from .conftest import Order, User


class TestModelComposition:
    def test_user_has_all_mixin_columns(self):
        """User has columns from Base + TimestampMixin + SoftDeleteMixin."""
        mapper = sa_inspect(User)
        cols = {c.key for c in mapper.columns}
        assert "id" in cols
        assert "email" in cols
        assert "tenant_id" in cols
        assert "created_at" in cols
        assert "updated_at" in cols
        assert "deleted_at" in cols

    def test_order_has_timestamp_but_not_soft_delete(self):
        """Order has TimestampMixin but not SoftDeleteMixin."""
        mapper = sa_inspect(Order)
        cols = {c.key for c in mapper.columns}
        assert "created_at" in cols
        assert "updated_at" in cols
        assert "deleted_at" not in cols

    async def test_insert_user_sets_timestamps(self, db_session):
        """Inserting a User auto-sets created_at via server_default."""
        user = User(email="test@test.com", name="Test", tenant_id="test")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        assert user.created_at is not None
        assert user.updated_at is not None

    async def test_user_order_relationship(self, db_session):
        """FK relationship between User and Order works with bloque mixins."""
        user = User(email="rel@test.com", name="Rel User", tenant_id="test")
        db_session.add(user)
        await db_session.flush()

        order = Order(
            product="Test Product", amount=99.0, tenant_id="test", user_id=user.id
        )
        db_session.add(order)
        await db_session.commit()

        # Navigate relationship
        result = await db_session.execute(
            select(User).where(User.id == user.id)
        )
        loaded_user = result.scalar_one()
        await db_session.refresh(loaded_user, ["orders"])
        assert len(loaded_user.orders) == 1
        assert loaded_user.orders[0].product == "Test Product"

    async def test_soft_delete_preserves_relationships(self, db_session):
        """Soft-deleting a user does not cascade-delete orders."""
        user = User(email="soft@test.com", name="Soft User", tenant_id="test")
        db_session.add(user)
        await db_session.flush()

        order = Order(
            product="Preserved", amount=50.0, tenant_id="test", user_id=user.id
        )
        db_session.add(order)
        await db_session.commit()

        user.soft_delete()
        await db_session.commit()

        assert user.is_deleted is True

        # Order still exists
        result = await db_session.execute(
            select(Order).where(Order.user_id == user.id)
        )
        assert result.scalar_one().product == "Preserved"
