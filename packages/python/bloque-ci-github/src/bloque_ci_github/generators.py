"""GitHub Actions workflow generators.

Produces workflow dicts that can be serialized to YAML.
Default output for generate_ci_workflow() matches the existing
.github/workflows/ci.yml in this monorepo.
"""

from __future__ import annotations

from .models import (
    PublishConfig,
    PythonJobConfig,
    TypeScriptJobConfig,
    WorkflowConfig,
)


def _build_python_job(config: PythonJobConfig) -> dict:
    """Build the Python CI job dict."""
    steps: list[dict] = [
        {"uses": "actions/checkout@v4"},
        {"uses": "astral-sh/setup-uv@v4"},
        {"run": "uv sync --all-packages"},
    ]
    if config.run_tests:
        steps.append({"run": config.test_command})
    if config.run_lint:
        steps.append({"run": config.lint_command})
    if config.run_format_check:
        steps.append({"run": config.format_command})
    return {"runs-on": "ubuntu-latest", "steps": steps}


def _build_typescript_job(config: TypeScriptJobConfig) -> dict:
    """Build the TypeScript CI job dict."""
    steps: list[dict] = [
        {"uses": "actions/checkout@v4"},
        {"uses": "pnpm/action-setup@v4"},
        {
            "uses": "actions/setup-node@v4",
            "with": {"node-version": config.node_version, "cache": "pnpm"},
        },
        {"run": "pnpm install"},
    ]
    if config.run_lint:
        steps.append({"run": config.lint_command})
    if config.run_build:
        steps.append({"run": config.build_command})
    if config.run_test:
        steps.append({"run": config.test_command})
    return {"runs-on": "ubuntu-latest", "steps": steps}


def _build_pypi_publish_job(config: PublishConfig) -> dict:
    """Build a PyPI publish job dict."""
    return {
        "runs-on": "ubuntu-latest",
        "needs": "ci",
        "steps": [
            {"uses": "actions/checkout@v4"},
            {"uses": "astral-sh/setup-uv@v4"},
            {"run": "uv sync --all-packages"},
            {"run": "uv build"},
            {
                "name": "Publish to PyPI",
                "run": "uv publish",
                "env": {
                    "UV_PUBLISH_TOKEN": "${{ secrets."
                    + config.pypi_token_secret
                    + " }}",
                },
            },
        ],
    }


def _build_npm_publish_job(config: PublishConfig) -> dict:
    """Build an npm publish job dict."""
    return {
        "runs-on": "ubuntu-latest",
        "needs": "ci",
        "steps": [
            {"uses": "actions/checkout@v4"},
            {"uses": "pnpm/action-setup@v4"},
            {
                "uses": "actions/setup-node@v4",
                "with": {"node-version": "20", "cache": "pnpm"},
            },
            {"run": "pnpm install"},
            {"run": "pnpm run build"},
            {
                "name": "Publish to npm",
                "run": "pnpm publish --no-git-checks",
                "env": {
                    "NODE_AUTH_TOKEN": "${{ secrets."
                    + config.npm_token_secret
                    + " }}",
                },
            },
        ],
    }


def generate_ci_workflow(config: WorkflowConfig | None = None) -> dict:
    """Generate a CI workflow dict.

    With default config, output matches the current .github/workflows/ci.yml.

    Args:
        config: Workflow configuration. Uses defaults if None.

    Returns:
        Dict representing a complete GitHub Actions workflow.
    """
    if config is None:
        config = WorkflowConfig()

    workflow: dict = {
        "name": config.name,
        "on": config.triggers,
        "jobs": {},
    }

    if config.python is not None:
        workflow["jobs"]["python"] = _build_python_job(config.python)

    if config.typescript is not None:
        workflow["jobs"]["typescript"] = _build_typescript_job(config.typescript)

    return workflow


def generate_release_workflow(
    *,
    publish_python: PublishConfig | None = None,
    publish_typescript: PublishConfig | None = None,
    trigger_tag_pattern: str = "v*",
) -> dict:
    """Generate a release workflow dict.

    Creates a workflow triggered by tag pushes that runs CI first,
    then publishes to PyPI and/or npm.

    Args:
        publish_python: PyPI publish config, or None to skip.
        publish_typescript: npm publish config, or None to skip.
        trigger_tag_pattern: Git tag pattern that triggers the release.

    Returns:
        Dict representing a complete GitHub Actions release workflow.
    """
    workflow: dict = {
        "name": "Release",
        "on": {"push": {"tags": [trigger_tag_pattern]}},
        "jobs": {},
    }

    # CI job runs first
    ci_config = WorkflowConfig(
        name="CI",
        triggers=[],
        python=PythonJobConfig() if publish_python else None,
        typescript=TypeScriptJobConfig() if publish_typescript else None,
    )
    ci_jobs: dict = {}
    if ci_config.python is not None:
        ci_jobs["python"] = _build_python_job(ci_config.python)
    if ci_config.typescript is not None:
        ci_jobs["typescript"] = _build_typescript_job(ci_config.typescript)

    # Merge CI jobs under a single "ci" job or keep separate
    if ci_jobs:
        # Use first CI job as the "ci" baseline, combine steps if both
        if len(ci_jobs) == 1:
            workflow["jobs"]["ci"] = next(iter(ci_jobs.values()))
        else:
            # Both Python and TS: create separate ci-python and ci-typescript
            for job_name, job_def in ci_jobs.items():
                workflow["jobs"][f"ci-{job_name}"] = job_def

    if publish_python is not None:
        job = _build_pypi_publish_job(publish_python)
        if len(ci_jobs) > 1:
            job["needs"] = "ci-python"
        workflow["jobs"]["publish-pypi"] = job

    if publish_typescript is not None:
        job = _build_npm_publish_job(publish_typescript)
        if len(ci_jobs) > 1:
            job["needs"] = "ci-typescript"
        workflow["jobs"]["publish-npm"] = job

    return workflow
