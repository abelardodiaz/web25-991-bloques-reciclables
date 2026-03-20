"""Tests for example workflow files."""

from pathlib import Path

import yaml
from bloque_ci_github.generators import generate_ci_workflow

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def test_example_files_parse():
    """All example YAML files parse without errors."""
    for yml_file in EXAMPLES_DIR.glob("*.yml"):
        content = yml_file.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert isinstance(data, dict), f"{yml_file.name} did not parse as dict"
        assert "name" in data, f"{yml_file.name} missing 'name'"
        assert "jobs" in data, f"{yml_file.name} missing 'jobs'"


def test_ci_example_matches_generated():
    """examples/ci.yml matches the default generate_ci_workflow() output."""
    ci_example = EXAMPLES_DIR / "ci.yml"
    example_content = yaml.safe_load(ci_example.read_text(encoding="utf-8"))
    generated = generate_ci_workflow()
    # Compare the structure (generated dict should match example)
    assert example_content["name"] == generated["name"]
    assert set(example_content["jobs"].keys()) == set(generated["jobs"].keys())
    # Check python job steps match
    example_py_runs = [
        s.get("run", s.get("uses", ""))
        for s in example_content["jobs"]["python"]["steps"]
    ]
    generated_py_runs = [
        s.get("run", s.get("uses", ""))
        for s in generated["jobs"]["python"]["steps"]
    ]
    assert example_py_runs == generated_py_runs
