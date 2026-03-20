"""Production environment validation.

Detects placeholder passwords (CHANGE_ME), missing required env vars,
and invalid configuration values. Not present in bloque-docker-dev
because dev environments use known-safe defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

REQUIRED_ENV_VARS: list[str] = ["DATABASE_URL", "REDIS_URL", "APP_WORKERS"]

SENSITIVE_DEFAULTS: list[str] = ["CHANGE_ME", "bloques_dev"]

SSL_ENV_VARS: list[str] = ["SSL_CERTIFICATE", "SSL_CERTIFICATE_KEY"]


@dataclass
class ValidationResult:
    """Result of environment validation.

    Attributes:
        valid: True if no errors found (warnings are acceptable).
        errors: List of critical issues that must be fixed.
        warnings: List of non-critical issues (e.g. placeholder passwords).
    """

    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_env() -> ValidationResult:
    """Check required environment variables and detect placeholder passwords.

    Validates:
    - Required env vars are set (DATABASE_URL, REDIS_URL, APP_WORKERS)
    - No placeholder passwords (CHANGE_ME, bloques_dev) in connection URLs
    - APP_WORKERS is a positive integer

    Returns:
        ValidationResult with errors and warnings.
    """
    result = ValidationResult()

    # Check required vars exist
    for var in REQUIRED_ENV_VARS:
        value = os.environ.get(var)
        if not value:
            result.valid = False
            result.errors.append(f"Required environment variable {var} is not set")

    # Check for placeholder passwords in URLs
    for var in ("DATABASE_URL", "REDIS_URL"):
        value = os.environ.get(var, "")
        for placeholder in SENSITIVE_DEFAULTS:
            if placeholder in value:
                result.warnings.append(
                    f"{var} contains placeholder password '{placeholder}' "
                    f"- change before deploying to production"
                )

    # Validate APP_WORKERS is a positive integer
    workers = os.environ.get("APP_WORKERS", "")
    if workers:
        try:
            workers_int = int(workers)
            if workers_int < 1:
                result.valid = False
                result.errors.append(
                    f"APP_WORKERS must be a positive integer, got {workers_int}"
                )
        except ValueError:
            result.valid = False
            result.errors.append(
                f"APP_WORKERS must be a valid integer, got '{workers}'"
            )

    return result


def validate_prod_config() -> ValidationResult:
    """Higher-level validation: env + SSL configuration.

    Calls validate_env() and additionally checks SSL vars
    if port 443 is configured (via SSL_CERTIFICATE env var presence).

    Returns:
        ValidationResult with combined errors and warnings.
    """
    result = validate_env()

    # Check SSL config if any SSL var is partially set
    ssl_vars_set = {var: os.environ.get(var) for var in SSL_ENV_VARS}
    any_ssl = any(ssl_vars_set.values())
    all_ssl = all(ssl_vars_set.values())

    if any_ssl and not all_ssl:
        missing = [var for var, val in ssl_vars_set.items() if not val]
        result.valid = False
        result.errors.append(
            f"Partial SSL configuration: missing {', '.join(missing)}"
        )

    return result
