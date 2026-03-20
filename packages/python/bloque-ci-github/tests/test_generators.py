"""Tests for GitHub Actions workflow generators."""

from bloque_ci_github.generators import generate_ci_workflow, generate_release_workflow
from bloque_ci_github.models import (
    PublishConfig,
    PythonJobConfig,
    TypeScriptJobConfig,
    WorkflowConfig,
)


def test_ci_workflow_default_has_both_jobs():
    """Default CI workflow includes python and typescript jobs."""
    wf = generate_ci_workflow()
    assert wf["name"] == "CI"
    assert "python" in wf["jobs"]
    assert "typescript" in wf["jobs"]


def test_ci_workflow_python_only():
    """CI workflow with only Python job."""
    config = WorkflowConfig(python=PythonJobConfig(), typescript=None)
    wf = generate_ci_workflow(config)
    assert "python" in wf["jobs"]
    assert "typescript" not in wf["jobs"]


def test_ci_workflow_typescript_only():
    """CI workflow with only TypeScript job."""
    config = WorkflowConfig(python=None, typescript=TypeScriptJobConfig())
    wf = generate_ci_workflow(config)
    assert "typescript" in wf["jobs"]
    assert "python" not in wf["jobs"]


def test_ci_workflow_python_steps():
    """Python job has correct steps: checkout, setup-uv, sync, pytest, ruff."""
    wf = generate_ci_workflow()
    steps = wf["jobs"]["python"]["steps"]
    runs = [s.get("run", s.get("uses", "")) for s in steps]
    assert "actions/checkout@v4" in runs
    assert "astral-sh/setup-uv@v4" in runs
    assert "uv sync --all-packages" in runs
    assert "uv run pytest" in runs
    assert "uv run ruff check ." in runs


def test_ci_workflow_typescript_steps():
    """TypeScript job has correct steps: checkout, pnpm, node, install, lint, build."""
    wf = generate_ci_workflow()
    steps = wf["jobs"]["typescript"]["steps"]
    runs = [s.get("run", s.get("uses", "")) for s in steps]
    assert "actions/checkout@v4" in runs
    assert "pnpm/action-setup@v4" in runs
    assert "pnpm install" in runs
    assert "pnpm run lint" in runs
    assert "pnpm run build" in runs


def test_ci_workflow_custom_triggers():
    """Workflow respects custom trigger config."""
    config = WorkflowConfig(triggers=["push"])
    wf = generate_ci_workflow(config)
    assert wf["on"] == ["push"]


def test_release_workflow_pypi():
    """Release workflow with PyPI publish has correct structure."""
    wf = generate_release_workflow(
        publish_python=PublishConfig(target="pypi"),
    )
    assert wf["name"] == "Release"
    assert "push" in wf["on"]
    assert "publish-pypi" in wf["jobs"]
    # Check the publish step references the secret
    publish_steps = wf["jobs"]["publish-pypi"]["steps"]
    publish_envs = [s.get("env", {}) for s in publish_steps]
    token_refs = [
        env.get("UV_PUBLISH_TOKEN", "")
        for env in publish_envs
        if "UV_PUBLISH_TOKEN" in env
    ]
    assert any("secrets.PYPI_TOKEN" in ref for ref in token_refs)


def test_release_workflow_npm():
    """Release workflow with npm publish has correct structure."""
    wf = generate_release_workflow(
        publish_typescript=PublishConfig(target="npm"),
    )
    assert "publish-npm" in wf["jobs"]
    publish_steps = wf["jobs"]["publish-npm"]["steps"]
    publish_envs = [s.get("env", {}) for s in publish_steps]
    token_refs = [
        env.get("NODE_AUTH_TOKEN", "")
        for env in publish_envs
        if "NODE_AUTH_TOKEN" in env
    ]
    assert any("secrets.NPM_TOKEN" in ref for ref in token_refs)
