"""Tests for pipeline validation."""

from ulfblk_ci_gitlab.models import PipelineConfig
from ulfblk_ci_gitlab.validate import validate_config, validate_pipeline_yaml


def test_validate_config_valid():
    """Default config is valid."""
    result = validate_config(PipelineConfig())
    assert result.valid is True
    assert result.errors == []


def test_validate_config_no_jobs():
    """Config with no jobs is invalid."""
    config = PipelineConfig(python=None, typescript=None)
    result = validate_config(config)
    assert result.valid is False
    assert any("at least one job" in e for e in result.errors)


def test_validate_pipeline_yaml_structure():
    """Valid pipeline YAML passes structural validation."""
    from ulfblk_ci_gitlab.generators import generate_ci_pipeline
    from ulfblk_ci_gitlab.serializer import pipeline_to_yaml

    yaml_str = pipeline_to_yaml(generate_ci_pipeline())
    result = validate_pipeline_yaml(yaml_str)
    assert result.valid is True
    assert result.errors == []
