"""GitLab CI pipeline generators.

Produces pipeline dicts that can be serialized to YAML.
Default output for generate_ci_pipeline() produces a standard
.gitlab-ci.yml for a Python + TypeScript monorepo.
"""

from __future__ import annotations

from .models import (
    PipelineConfig,
    PublishConfig,
    PythonJobConfig,
    TypeScriptJobConfig,
)


def _trigger_to_rule(trigger: str) -> dict:
    """Convert a trigger name to a GitLab CI rule dict.

    Args:
        trigger: Trigger name ("push", "merge_request", "tag").

    Returns:
        GitLab CI rule dict.
    """
    if trigger == "push":
        return {"if": '$CI_PIPELINE_SOURCE == "push"'}
    if trigger == "merge_request":
        return {"if": '$CI_PIPELINE_SOURCE == "merge_request_event"'}
    if trigger == "tag":
        return {"if": "$CI_COMMIT_TAG"}
    return {"if": f'$CI_PIPELINE_SOURCE == "{trigger}"'}


def _build_python_jobs(
    config: PythonJobConfig, rules: list[dict]
) -> dict[str, dict]:
    """Build Python CI job dicts.

    Returns:
        Dict mapping job names to job definitions.
    """
    image = f"python:{config.python_version}"
    before_script = [
        "pip install uv",
        "uv sync --all-packages",
    ]
    cache = {
        "paths": [".venv/"],
        "key": "python",
    }

    jobs: dict[str, dict] = {}

    if config.run_lint or config.run_format_check:
        lint_script: list[str] = []
        if config.run_lint:
            lint_script.append(config.lint_command)
        if config.run_format_check:
            lint_script.append(config.format_command)
        jobs["python-lint"] = {
            "stage": "lint",
            "image": image,
            "before_script": before_script,
            "script": lint_script,
            "cache": cache,
            "rules": rules,
        }

    if config.run_tests:
        jobs["python-test"] = {
            "stage": "test",
            "image": image,
            "before_script": before_script,
            "script": [config.test_command],
            "cache": cache,
            "rules": rules,
        }

    return jobs


def _build_typescript_jobs(
    config: TypeScriptJobConfig, rules: list[dict]
) -> dict[str, dict]:
    """Build TypeScript CI job dicts.

    Returns:
        Dict mapping job names to job definitions.
    """
    image = f"node:{config.node_version}"
    before_script = [
        "npm install -g pnpm",
        "pnpm install",
    ]
    cache = {
        "paths": ["node_modules/", ".pnpm-store/"],
        "key": "typescript",
    }

    jobs: dict[str, dict] = {}

    if config.run_lint:
        jobs["typescript-lint"] = {
            "stage": "lint",
            "image": image,
            "before_script": before_script,
            "script": [config.lint_command],
            "cache": cache,
            "rules": rules,
        }

    if config.run_build:
        jobs["typescript-build"] = {
            "stage": "build",
            "image": image,
            "before_script": before_script,
            "script": [config.build_command],
            "cache": cache,
            "rules": rules,
        }

    if config.run_test:
        jobs["typescript-test"] = {
            "stage": "test",
            "image": image,
            "before_script": before_script,
            "script": [config.test_command],
            "cache": cache,
            "rules": rules,
        }

    return jobs


def _build_pypi_publish_job(
    config: PublishConfig, needs: list[str]
) -> dict:
    """Build a PyPI publish job dict."""
    return {
        "stage": "publish",
        "image": "python:3.12",
        "before_script": [
            "pip install uv",
            "uv sync --all-packages",
        ],
        "script": [
            "uv build",
            "uv publish",
        ],
        "variables": {
            "UV_PUBLISH_TOKEN": f"${config.pypi_token_variable}",
        },
        "needs": needs,
        "rules": [{"if": "$CI_COMMIT_TAG"}],
    }


def _build_npm_publish_job(
    config: PublishConfig, needs: list[str]
) -> dict:
    """Build an npm publish job dict."""
    return {
        "stage": "publish",
        "image": "node:20",
        "before_script": [
            "npm install -g pnpm",
            "pnpm install",
        ],
        "script": [
            "pnpm run build",
            "pnpm publish --no-git-checks",
        ],
        "variables": {
            "NODE_AUTH_TOKEN": f"${config.npm_token_variable}",
        },
        "needs": needs,
        "rules": [{"if": "$CI_COMMIT_TAG"}],
    }


def _collect_stages(jobs: dict[str, dict]) -> list[str]:
    """Collect unique stages in order from jobs."""
    stage_order = ["lint", "test", "build", "publish"]
    used = {job["stage"] for job in jobs.values() if "stage" in job}
    return [s for s in stage_order if s in used]


def generate_ci_pipeline(config: PipelineConfig | None = None) -> dict:
    """Generate a CI pipeline dict.

    With default config, output produces a standard .gitlab-ci.yml
    for a Python + TypeScript monorepo.

    Args:
        config: Pipeline configuration. Uses defaults if None.

    Returns:
        Dict representing a complete GitLab CI pipeline.
    """
    if config is None:
        config = PipelineConfig()

    rules = [_trigger_to_rule(t) for t in config.triggers]

    jobs: dict[str, dict] = {}

    if config.python is not None:
        jobs.update(_build_python_jobs(config.python, rules))

    if config.typescript is not None:
        jobs.update(_build_typescript_jobs(config.typescript, rules))

    pipeline: dict = {"stages": _collect_stages(jobs)}
    pipeline.update(jobs)

    return pipeline


def generate_release_pipeline(
    *,
    publish_python: PublishConfig | None = None,
    publish_typescript: PublishConfig | None = None,
    trigger_tag_pattern: str = "v*",
) -> dict:
    """Generate a release pipeline dict.

    Creates a pipeline triggered by tag pushes that runs CI first,
    then publishes to PyPI and/or npm.

    Args:
        publish_python: PyPI publish config, or None to skip.
        publish_typescript: npm publish config, or None to skip.
        trigger_tag_pattern: Git tag pattern that triggers the release.

    Returns:
        Dict representing a complete GitLab CI release pipeline.
    """
    tag_rules = [{"if": "$CI_COMMIT_TAG"}]

    jobs: dict[str, dict] = {}

    # CI jobs run first
    if publish_python is not None:
        py_config = PythonJobConfig()
        py_jobs = _build_python_jobs(py_config, tag_rules)
        jobs.update(py_jobs)

    if publish_typescript is not None:
        ts_config = TypeScriptJobConfig()
        ts_jobs = _build_typescript_jobs(ts_config, tag_rules)
        jobs.update(ts_jobs)

    # Publish jobs
    if publish_python is not None:
        py_needs = [name for name in jobs if name.startswith("python-")]
        jobs["publish-pypi"] = _build_pypi_publish_job(publish_python, py_needs)

    if publish_typescript is not None:
        ts_needs = [
            name for name in jobs
            if name.startswith("typescript-") and name != "publish-npm"
        ]
        jobs["publish-npm"] = _build_npm_publish_job(publish_typescript, ts_needs)

    pipeline: dict = {"stages": _collect_stages(jobs)}
    pipeline.update(jobs)

    return pipeline
