"""Tests for example pipeline files."""

from pathlib import Path

import yaml
from ulfblk_ci_gitlab.generators import generate_ci_pipeline

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def test_example_files_parse():
    """All example YAML files parse with stages key."""
    for yml_file in EXAMPLES_DIR.glob("*.yml"):
        content = yml_file.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert isinstance(data, dict), f"{yml_file.name} did not parse as dict"
        assert "stages" in data, f"{yml_file.name} missing 'stages'"
        assert isinstance(data["stages"], list), f"{yml_file.name} stages not a list"


def test_ci_example_matches_generated():
    """examples/ci.yml matches the default generate_ci_pipeline() output."""
    ci_example = EXAMPLES_DIR / "ci.yml"
    example_content = yaml.safe_load(ci_example.read_text(encoding="utf-8"))
    generated = generate_ci_pipeline()
    # Compare stages
    assert example_content["stages"] == generated["stages"]
    # Compare job names
    example_jobs = {k for k in example_content if k != "stages"}
    generated_jobs = {k for k in generated if k != "stages"}
    assert example_jobs == generated_jobs
    # Compare python-test script
    assert (
        example_content["python-test"]["script"]
        == generated["python-test"]["script"]
    )
