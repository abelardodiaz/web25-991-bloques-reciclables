"""Validation for pipeline configs and generated YAML.

Reuses the ValidationResult pattern from bloque-ci-github.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import yaml

from .models import PipelineConfig


@dataclass
class ValidationResult:
    """Result of pipeline validation.

    Attributes:
        valid: True if no errors found (warnings are acceptable).
        errors: List of critical issues that must be fixed.
        warnings: List of non-critical issues.
    """

    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_config(config: PipelineConfig) -> ValidationResult:
    """Validate a PipelineConfig has at least one job enabled.

    Args:
        config: The pipeline configuration to validate.

    Returns:
        ValidationResult with errors if config is invalid.
    """
    result = ValidationResult()

    if config.python is None and config.typescript is None:
        result.valid = False
        result.errors.append("Pipeline must have at least one job (python or typescript)")

    if not config.name or not config.name.strip():
        result.valid = False
        result.errors.append("Pipeline name must not be empty")

    return result


def validate_pipeline_yaml(yaml_content: str) -> ValidationResult:
    """Validate that a YAML string has valid GitLab CI pipeline structure.

    Checks:
    - YAML parses without errors
    - Has required top-level key: stages (non-empty list)
    - Each job has stage (in the stages list) and script

    Args:
        yaml_content: Raw YAML string to validate.

    Returns:
        ValidationResult with errors for structural issues.
    """
    result = ValidationResult()

    try:
        data = yaml.safe_load(yaml_content)
    except yaml.YAMLError as exc:
        result.valid = False
        result.errors.append(f"Invalid YAML: {exc}")
        return result

    if not isinstance(data, dict):
        result.valid = False
        result.errors.append("Pipeline must be a YAML mapping")
        return result

    # Check stages key
    if "stages" not in data:
        result.valid = False
        result.errors.append("Missing required top-level key: 'stages'")
        return result

    stages = data["stages"]
    if not isinstance(stages, list) or not stages:
        result.valid = False
        result.errors.append("'stages' must be a non-empty list")
        return result

    # Validate each job (all top-level keys except 'stages')
    for key, value in data.items():
        if key == "stages":
            continue
        if not isinstance(value, dict):
            continue
        # This is a job definition
        if "stage" not in value:
            result.valid = False
            result.errors.append(f"Job '{key}' missing 'stage'")
        elif value["stage"] not in stages:
            result.valid = False
            result.errors.append(
                f"Job '{key}' stage '{value['stage']}' not in stages list"
            )
        if "script" not in value:
            result.valid = False
            result.errors.append(f"Job '{key}' missing 'script'")

    return result
