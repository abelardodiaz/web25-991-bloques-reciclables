"""Tests for YAML serialization."""

import yaml
from bloque_ci_gitlab.generators import generate_ci_pipeline
from bloque_ci_gitlab.serializer import pipeline_to_yaml, write_pipeline


def test_pipeline_to_yaml_valid():
    """Generated YAML parses back to a valid dict."""
    pipeline = generate_ci_pipeline()
    yaml_str = pipeline_to_yaml(pipeline)
    parsed = yaml.safe_load(yaml_str)
    assert "stages" in parsed
    assert "python-lint" in parsed


def test_no_python_tags():
    """YAML output must not contain !!python tags."""
    pipeline = generate_ci_pipeline()
    yaml_str = pipeline_to_yaml(pipeline)
    assert "!!python" not in yaml_str


def test_preserves_var_references():
    """$VAR references survive serialization."""
    from bloque_ci_gitlab.generators import generate_release_pipeline
    from bloque_ci_gitlab.models import PublishConfig

    pipeline = generate_release_pipeline(publish_python=PublishConfig(target="pypi"))
    yaml_str = pipeline_to_yaml(pipeline)
    assert "$PYPI_TOKEN" in yaml_str


def test_write_pipeline(tmp_path):
    """write_pipeline creates a valid YAML file."""
    pipeline = generate_ci_pipeline()
    out = write_pipeline(pipeline, tmp_path / "pipelines" / "ci.yml")
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    parsed = yaml.safe_load(content)
    assert "stages" in parsed
