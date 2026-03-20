"""Tests for YAML serialization."""

import yaml
from bloque_ci_github.generators import generate_ci_workflow
from bloque_ci_github.serializer import workflow_to_yaml, write_workflow


def test_workflow_to_yaml_valid():
    """Generated YAML parses back to a valid dict."""
    wf = generate_ci_workflow()
    yaml_str = workflow_to_yaml(wf)
    parsed = yaml.safe_load(yaml_str)
    assert parsed["name"] == "CI"
    assert "jobs" in parsed


def test_no_python_tags():
    """YAML output must not contain !!python tags."""
    wf = generate_ci_workflow()
    yaml_str = workflow_to_yaml(wf)
    assert "!!python" not in yaml_str


def test_preserves_secrets_expression():
    """${{ secrets.X }} expressions survive serialization."""
    from bloque_ci_github.generators import generate_release_workflow
    from bloque_ci_github.models import PublishConfig

    wf = generate_release_workflow(publish_python=PublishConfig(target="pypi"))
    yaml_str = workflow_to_yaml(wf)
    assert "${{ secrets.PYPI_TOKEN }}" in yaml_str


def test_write_workflow(tmp_path):
    """write_workflow creates a valid YAML file."""
    wf = generate_ci_workflow()
    out = write_workflow(wf, tmp_path / "workflows" / "ci.yml")
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    parsed = yaml.safe_load(content)
    assert parsed["name"] == "CI"
