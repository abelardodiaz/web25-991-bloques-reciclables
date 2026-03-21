"""Tests for workflow validation."""

from ulfblk_ci_github.models import WorkflowConfig
from ulfblk_ci_github.validate import validate_config, validate_workflow_yaml


def test_validate_config_valid():
    """Default config is valid."""
    result = validate_config(WorkflowConfig())
    assert result.valid is True
    assert result.errors == []


def test_validate_config_no_jobs():
    """Config with no jobs is invalid."""
    config = WorkflowConfig(python=None, typescript=None)
    result = validate_config(config)
    assert result.valid is False
    assert any("at least one job" in e for e in result.errors)


def test_validate_workflow_yaml_structure():
    """Valid workflow YAML passes structural validation."""
    from ulfblk_ci_github.generators import generate_ci_workflow
    from ulfblk_ci_github.serializer import workflow_to_yaml

    yaml_str = workflow_to_yaml(generate_ci_workflow())
    result = validate_workflow_yaml(yaml_str)
    assert result.valid is True
    assert result.errors == []
