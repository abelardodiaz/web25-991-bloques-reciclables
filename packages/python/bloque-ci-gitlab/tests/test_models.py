"""Tests for pipeline configuration models."""

from bloque_ci_gitlab.models import (
    PipelineConfig,
    PublishConfig,
    PythonJobConfig,
    TypeScriptJobConfig,
)


def test_python_job_defaults():
    """PythonJobConfig has sensible defaults."""
    config = PythonJobConfig()
    assert config.python_version == "3.12"
    assert config.run_tests is True
    assert config.run_lint is True
    assert config.run_format_check is False
    assert "pytest" in config.test_command
    assert "ruff check" in config.lint_command


def test_typescript_job_defaults():
    """TypeScriptJobConfig has sensible defaults."""
    config = TypeScriptJobConfig()
    assert config.node_version == "20"
    assert config.run_lint is True
    assert config.run_build is True
    assert config.run_test is False
    assert "pnpm" in config.lint_command


def test_pipeline_config_defaults():
    """PipelineConfig defaults to both Python and TypeScript jobs."""
    config = PipelineConfig()
    assert config.name == "CI"
    assert config.triggers == ["push", "merge_request"]
    assert config.python is not None
    assert config.typescript is not None


def test_pipeline_config_frozen():
    """PipelineConfig and sub-configs are immutable."""
    config = PipelineConfig()
    try:
        config.name = "Modified"  # type: ignore[misc]
        raised = False
    except AttributeError:
        raised = True
    assert raised, "PipelineConfig should be frozen"

    py = PythonJobConfig()
    try:
        py.python_version = "3.11"  # type: ignore[misc]
        raised = False
    except AttributeError:
        raised = True
    assert raised, "PythonJobConfig should be frozen"


def test_publish_config_variable_names():
    """PublishConfig has correct default CI/CD variable names."""
    pypi = PublishConfig(target="pypi")
    assert pypi.pypi_token_variable == "PYPI_TOKEN"

    npm = PublishConfig(target="npm")
    assert npm.npm_token_variable == "NPM_TOKEN"
