"""YAML serialization for GitHub Actions workflows.

Converts workflow dicts to YAML strings and writes them to files.
Uses block style and avoids !!python tags for clean output.
"""

from __future__ import annotations

from pathlib import Path

import yaml


class _CleanDumper(yaml.SafeDumper):
    """YAML dumper that produces clean GitHub Actions compatible output."""


def _str_representer(dumper: yaml.Dumper, data: str) -> yaml.ScalarNode:
    """Represent strings, using literal block style for multi-line."""
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_CleanDumper.add_representer(str, _str_representer)


def workflow_to_yaml(workflow: dict) -> str:
    """Convert a workflow dict to a YAML string.

    Uses block style, no !!python tags, preserves ${{ }} expressions.

    Args:
        workflow: Workflow dict from generators.

    Returns:
        YAML string ready to write to a .yml file.
    """
    return yaml.dump(
        workflow,
        Dumper=_CleanDumper,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )


def write_workflow(workflow: dict, path: str | Path) -> Path:
    """Write a workflow dict to a YAML file.

    Creates parent directories if they don't exist.

    Args:
        workflow: Workflow dict from generators.
        path: File path for the output .yml file.

    Returns:
        Path to the written file.
    """
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(workflow_to_yaml(workflow), encoding="utf-8")
    return out
