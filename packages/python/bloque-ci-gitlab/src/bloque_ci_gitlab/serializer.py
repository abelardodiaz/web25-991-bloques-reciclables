"""YAML serialization for GitLab CI pipelines.

Converts pipeline dicts to YAML strings and writes them to files.
Uses block style and avoids !!python tags for clean output.
"""

from __future__ import annotations

from pathlib import Path

import yaml


class _CleanDumper(yaml.SafeDumper):
    """YAML dumper that produces clean GitLab CI compatible output."""


def _str_representer(dumper: yaml.Dumper, data: str) -> yaml.ScalarNode:
    """Represent strings, using literal block style for multi-line."""
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_CleanDumper.add_representer(str, _str_representer)


def pipeline_to_yaml(pipeline: dict) -> str:
    """Convert a pipeline dict to a YAML string.

    Uses block style, no !!python tags, preserves $VAR references.

    Args:
        pipeline: Pipeline dict from generators.

    Returns:
        YAML string ready to write to a .gitlab-ci.yml file.
    """
    return yaml.dump(
        pipeline,
        Dumper=_CleanDumper,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )


def write_pipeline(pipeline: dict, path: str | Path) -> Path:
    """Write a pipeline dict to a YAML file.

    Creates parent directories if they don't exist.

    Args:
        pipeline: Pipeline dict from generators.
        path: File path for the output .yml file.

    Returns:
        Path to the written file.
    """
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(pipeline_to_yaml(pipeline), encoding="utf-8")
    return out
