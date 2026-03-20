"""Tests for GitLab CI pipeline generators."""

from bloque_ci_gitlab.generators import generate_ci_pipeline, generate_release_pipeline
from bloque_ci_gitlab.models import (
    PipelineConfig,
    PublishConfig,
    PythonJobConfig,
    TypeScriptJobConfig,
)


def test_ci_pipeline_default_has_both_stacks():
    """Default CI pipeline includes python and typescript jobs."""
    pipeline = generate_ci_pipeline()
    assert "python-lint" in pipeline
    assert "python-test" in pipeline
    assert "typescript-lint" in pipeline
    assert "typescript-build" in pipeline


def test_ci_pipeline_python_only():
    """CI pipeline with only Python jobs."""
    config = PipelineConfig(python=PythonJobConfig(), typescript=None)
    pipeline = generate_ci_pipeline(config)
    assert "python-lint" in pipeline
    assert "python-test" in pipeline
    assert "typescript-lint" not in pipeline
    assert "typescript-build" not in pipeline


def test_ci_pipeline_typescript_only():
    """CI pipeline with only TypeScript jobs."""
    config = PipelineConfig(python=None, typescript=TypeScriptJobConfig())
    pipeline = generate_ci_pipeline(config)
    assert "typescript-lint" in pipeline
    assert "typescript-build" in pipeline
    assert "python-lint" not in pipeline
    assert "python-test" not in pipeline


def test_ci_pipeline_python_job_structure():
    """Python jobs have correct image, before_script, and script."""
    pipeline = generate_ci_pipeline()
    job = pipeline["python-test"]
    assert job["image"] == "python:3.12"
    assert "pip install uv" in job["before_script"]
    assert "uv sync --all-packages" in job["before_script"]
    assert "uv run pytest" in job["script"]


def test_ci_pipeline_typescript_job_structure():
    """TypeScript jobs have correct image, before_script, and script."""
    pipeline = generate_ci_pipeline()
    job = pipeline["typescript-lint"]
    assert job["image"] == "node:20"
    assert "npm install -g pnpm" in job["before_script"]
    assert "pnpm install" in job["before_script"]
    assert "pnpm run lint" in job["script"]


def test_ci_pipeline_has_stages():
    """Pipeline has stages key with correct values."""
    pipeline = generate_ci_pipeline()
    assert "stages" in pipeline
    stages = pipeline["stages"]
    assert "lint" in stages
    assert "test" in stages
    assert "build" in stages


def test_ci_pipeline_custom_triggers():
    """Pipeline respects custom trigger config."""
    config = PipelineConfig(triggers=["push"])
    pipeline = generate_ci_pipeline(config)
    # Check that rules reflect the single trigger
    job = pipeline["python-lint"]
    assert len(job["rules"]) == 1
    assert "push" in job["rules"][0]["if"]


def test_release_pipeline_pypi():
    """Release pipeline with PyPI publish has correct structure."""
    pipeline = generate_release_pipeline(
        publish_python=PublishConfig(target="pypi"),
    )
    assert "publish-pypi" in pipeline
    publish_job = pipeline["publish-pypi"]
    assert publish_job["stage"] == "publish"
    assert "$PYPI_TOKEN" in publish_job["variables"]["UV_PUBLISH_TOKEN"]
    assert "python-lint" in publish_job["needs"] or "python-test" in publish_job["needs"]


def test_release_pipeline_npm():
    """Release pipeline with npm publish has correct structure."""
    pipeline = generate_release_pipeline(
        publish_typescript=PublishConfig(target="npm"),
    )
    assert "publish-npm" in pipeline
    publish_job = pipeline["publish-npm"]
    assert publish_job["stage"] == "publish"
    assert "$NPM_TOKEN" in publish_job["variables"]["NODE_AUTH_TOKEN"]
    assert any(
        name.startswith("typescript-") for name in publish_job["needs"]
    )
