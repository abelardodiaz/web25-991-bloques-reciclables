# bloque-ci-github

GitHub Actions workflow generator for Python + TypeScript monorepos.

Generates CI (lint + test) and release/publish (PyPI + npm) workflows programmatically using dict-to-YAML, making them round-trip testable and IDE-friendly.

## Install

```bash
uv add bloque-ci-github
```

## Quick Start

### Generate a CI workflow

```python
from bloque_ci_github.generators import generate_ci_workflow
from bloque_ci_github.serializer import write_workflow

# Default: matches a standard Python + TypeScript monorepo CI
workflow = generate_ci_workflow()
write_workflow(workflow, ".github/workflows/ci.yml")
```

### Generate a release workflow

```python
from bloque_ci_github.generators import generate_release_workflow
from bloque_ci_github.models import PublishConfig
from bloque_ci_github.serializer import write_workflow

workflow = generate_release_workflow(
    publish_python=PublishConfig(target="pypi"),
    publish_typescript=PublishConfig(target="npm"),
)
write_workflow(workflow, ".github/workflows/release.yml")
```

### Customize jobs

```python
from bloque_ci_github.generators import generate_ci_workflow
from bloque_ci_github.models import PythonJobConfig, WorkflowConfig

config = WorkflowConfig(
    name="CI",
    triggers=["push", "pull_request"],
    python=PythonJobConfig(
        run_format_check=True,
        python_version="3.13",
    ),
    typescript=None,  # Skip TypeScript job
)
workflow = generate_ci_workflow(config)
```

### Validate

```python
from bloque_ci_github.validate import validate_config, validate_workflow_yaml
from bloque_ci_github.models import WorkflowConfig
from bloque_ci_github.serializer import workflow_to_yaml
from bloque_ci_github.generators import generate_ci_workflow

# Validate config before generation
result = validate_config(WorkflowConfig())
assert result.valid

# Validate generated YAML structure
yaml_str = workflow_to_yaml(generate_ci_workflow())
result = validate_workflow_yaml(yaml_str)
assert result.valid
```

## API

### Models

- `PythonJobConfig` - Python CI job settings (version, test/lint/format commands)
- `TypeScriptJobConfig` - TypeScript CI job settings (node version, lint/build/test)
- `PublishConfig` - Publish target config (PyPI or npm, secret names)
- `WorkflowConfig` - Top-level workflow config (name, triggers, jobs)

### Generators

- `generate_ci_workflow(config?)` - CI workflow with lint + test jobs
- `generate_release_workflow(publish_python?, publish_typescript?, trigger_tag_pattern?)` - Release workflow with publish jobs

### Serializer

- `workflow_to_yaml(workflow)` - Dict to clean YAML string
- `write_workflow(workflow, path)` - Write workflow to .yml file

### Validation

- `validate_config(config)` - Check config has at least one job
- `validate_workflow_yaml(yaml_content)` - Check YAML has valid GitHub Actions structure

## Examples

Ready-to-use workflow files in the `examples/` directory:

- `ci.yml` - Standard CI for Python + TypeScript monorepo
- `release-python.yml` - Tag-triggered release to PyPI
- `release-typescript.yml` - Tag-triggered release to npm
