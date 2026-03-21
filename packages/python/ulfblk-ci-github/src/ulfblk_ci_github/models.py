"""Data models for GitHub Actions workflow configuration.

Frozen dataclasses representing CI and release workflow settings.
Each config maps directly to GitHub Actions workflow structure.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PythonJobConfig:
    """Configuration for a Python CI job.

    Attributes:
        python_version: Python version for setup-uv action.
        run_tests: Whether to run pytest.
        run_lint: Whether to run ruff check.
        run_format_check: Whether to run ruff format --check.
        test_command: Command to run tests.
        lint_command: Command to run linter.
        format_command: Command to check formatting.
    """

    python_version: str = "3.12"
    run_tests: bool = True
    run_lint: bool = True
    run_format_check: bool = False
    test_command: str = "uv run pytest"
    lint_command: str = "uv run ruff check ."
    format_command: str = "uv run ruff format --check ."


@dataclass(frozen=True)
class TypeScriptJobConfig:
    """Configuration for a TypeScript CI job.

    Attributes:
        node_version: Node.js version for setup-node action.
        run_lint: Whether to run lint command.
        run_build: Whether to run build command.
        run_test: Whether to run test command.
        lint_command: Command to run linter.
        build_command: Command to run build.
        test_command: Command to run tests.
    """

    node_version: str = "20"
    run_lint: bool = True
    run_build: bool = True
    run_test: bool = False
    lint_command: str = "pnpm run lint"
    build_command: str = "pnpm run build"
    test_command: str = "pnpm run test"


@dataclass(frozen=True)
class PublishConfig:
    """Configuration for a publish job (PyPI or npm).

    Attributes:
        target: Publish target, either "pypi" or "npm".
        pypi_token_secret: GitHub secret name for PyPI token.
        npm_token_secret: GitHub secret name for npm token.
    """

    target: str  # "pypi" or "npm"
    pypi_token_secret: str = "PYPI_TOKEN"
    npm_token_secret: str = "NPM_TOKEN"


@dataclass(frozen=True)
class WorkflowConfig:
    """Top-level CI workflow configuration.

    Attributes:
        name: Workflow display name in GitHub Actions.
        triggers: List of GitHub event triggers (e.g. "push", "pull_request").
        python: Python job config, or None to skip.
        typescript: TypeScript job config, or None to skip.
    """

    name: str = "CI"
    triggers: list[str] = field(default_factory=lambda: ["push", "pull_request"])
    python: PythonJobConfig | None = field(default_factory=PythonJobConfig)
    typescript: TypeScriptJobConfig | None = field(default_factory=TypeScriptJobConfig)
