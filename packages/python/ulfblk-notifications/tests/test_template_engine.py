"""Tests for TemplateEngine."""

import pytest
from ulfblk_notifications.models.settings import TemplateSettings
from ulfblk_notifications.templates.engine import TemplateEngine


def test_register_and_render_format_map():
    engine = TemplateEngine(TemplateSettings(use_jinja2=False))
    engine.register("welcome", subject="Hi {name}", body="Welcome, {name}!")

    subject, body = engine.render("welcome", {"name": "Alice"})
    assert subject == "Hi Alice"
    assert body == "Welcome, Alice!"


def test_render_unregistered_template_raises():
    engine = TemplateEngine(TemplateSettings(use_jinja2=False))

    with pytest.raises(KeyError, match="not_found"):
        engine.render("not_found", {})


def test_render_string_empty():
    engine = TemplateEngine(TemplateSettings(use_jinja2=False))
    assert engine.render_string("", {"x": 1}) == ""


def test_render_string_format_map():
    engine = TemplateEngine(TemplateSettings(use_jinja2=False))
    result = engine.render_string(
        "Hello {user}, you have {count} items.", {"user": "Bob", "count": 3}
    )
    assert result == "Hello Bob, you have 3 items."


def test_tenant_aware_register_and_render():
    engine = TemplateEngine(TemplateSettings(use_jinja2=False, tenant_aware=True))
    engine.register("alert", subject="Alert", body="Alert for {name}", tenant_id="acme")

    subject, body = engine.render("alert", {"name": "Admin"}, tenant_id="acme")
    assert subject == "Alert"
    assert body == "Alert for Admin"


def test_tenant_aware_isolation():
    """Different tenants can have different templates with the same name."""
    engine = TemplateEngine(TemplateSettings(use_jinja2=False, tenant_aware=True))
    engine.register("welcome", subject="A", body="Acme: {name}", tenant_id="acme")
    engine.register("welcome", subject="B", body="Beta: {name}", tenant_id="beta")

    s1, b1 = engine.render("welcome", {"name": "X"}, tenant_id="acme")
    s2, b2 = engine.render("welcome", {"name": "X"}, tenant_id="beta")

    assert s1 == "A"
    assert b1 == "Acme: X"
    assert s2 == "B"
    assert b2 == "Beta: X"


def test_jinja2_fallback_when_not_installed(monkeypatch):
    """When Jinja2 import fails, engine uses str.format_map."""
    original_init = TemplateEngine._init_jinja2

    def fake_init(self):
        self._jinja_available = False
        self._jinja_env = None

    monkeypatch.setattr(TemplateEngine, "_init_jinja2", fake_init)

    engine = TemplateEngine(TemplateSettings(use_jinja2=True))
    assert not engine._jinja_available

    engine.register("test", subject="{greeting}", body="{greeting} world")
    subject, body = engine.render("test", {"greeting": "Hello"})
    assert subject == "Hello"
    assert body == "Hello world"

    monkeypatch.setattr(TemplateEngine, "_init_jinja2", original_init)
