"""Validation for workflow configs and generated YAML.

Reuses the ValidationResult pattern from bloque-docker-prod.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import yaml

from .models import WorkflowConfig


@dataclass
class ValidationResult:
    """Result of workflow validation.

    Attributes:
        valid: True if no errors found (warnings are acceptable).
        errors: List of critical issues that must be fixed.
        warnings: List of non-critical issues.
    """

    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_config(config: WorkflowConfig) -> ValidationResult:
    """Validate a WorkflowConfig has at least one job enabled.

    Args:
        config: The workflow configuration to validate.

    Returns:
        ValidationResult with errors if config is invalid.
    """
    result = ValidationResult()

    if config.python is None and config.typescript is None:
        result.valid = False
        result.errors.append("Workflow must have at least one job (python or typescript)")

    if not config.name or not config.name.strip():
        result.valid = False
        result.errors.append("Workflow name must not be empty")

    return result


def validate_workflow_yaml(yaml_content: str) -> ValidationResult:
    """Validate that a YAML string has valid GitHub Actions workflow structure.

    Checks:
    - YAML parses without errors
    - Has required top-level keys: name, on, jobs
    - Each job has runs-on and steps

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
        result.errors.append("Workflow must be a YAML mapping")
        return result

    # Check required top-level keys
    for key in ("name", "on", "jobs"):
        # "on" becomes True when parsed from bare "on:" in some contexts,
        # so we check the original key in the dict
        if key not in data:
            result.valid = False
            result.errors.append(f"Missing required top-level key: '{key}'")

    if "jobs" not in data:
        return result

    jobs = data["jobs"]
    if not isinstance(jobs, dict) or not jobs:
        result.valid = False
        result.errors.append("'jobs' must be a non-empty mapping")
        return result

    # Validate each job
    for job_name, job_def in jobs.items():
        if not isinstance(job_def, dict):
            result.valid = False
            result.errors.append(f"Job '{job_name}' must be a mapping")
            continue
        if "runs-on" not in job_def:
            result.valid = False
            result.errors.append(f"Job '{job_name}' missing 'runs-on'")
        if "steps" not in job_def:
            result.valid = False
            result.errors.append(f"Job '{job_name}' missing 'steps'")

    return result
