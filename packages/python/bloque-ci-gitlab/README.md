# bloque-ci-gitlab

GitLab CI pipeline generator for Python + TypeScript monorepos.

Generates CI (lint + test) and release/publish (PyPI + npm) pipelines programmatically using dict-to-YAML, making them round-trip testable and IDE-friendly.

## Install

```bash
uv add bloque-ci-gitlab
```

## Quick Start

### Generate a CI pipeline

```python
from bloque_ci_gitlab.generators import generate_ci_pipeline
from bloque_ci_gitlab.serializer import write_pipeline

# Default: matches a standard Python + TypeScript monorepo CI
pipeline = generate_ci_pipeline()
write_pipeline(pipeline, ".gitlab-ci.yml")
```

### Generate a release pipeline

```python
from bloque_ci_gitlab.generators import generate_release_pipeline
from bloque_ci_gitlab.models import PublishConfig
from bloque_ci_gitlab.serializer import write_pipeline

pipeline = generate_release_pipeline(
    publish_python=PublishConfig(target="pypi"),
    publish_typescript=PublishConfig(target="npm"),
)
write_pipeline(pipeline, ".gitlab-ci-release.yml")
```

### Customize jobs

```python
from bloque_ci_gitlab.generators import generate_ci_pipeline
from bloque_ci_gitlab.models import PipelineConfig, PythonJobConfig

config = PipelineConfig(
    name="CI",
    triggers=["push", "merge_request"],
    python=PythonJobConfig(
        run_format_check=True,
        python_version="3.13",
    ),
    typescript=None,  # Skip TypeScript jobs
)
pipeline = generate_ci_pipeline(config)
```

### Validate

```python
from bloque_ci_gitlab.validate import validate_config, validate_pipeline_yaml
from bloque_ci_gitlab.models import PipelineConfig
from bloque_ci_gitlab.serializer import pipeline_to_yaml
from bloque_ci_gitlab.generators import generate_ci_pipeline

# Validate config before generation
result = validate_config(PipelineConfig())
assert result.valid

# Validate generated YAML structure
yaml_str = pipeline_to_yaml(generate_ci_pipeline())
result = validate_pipeline_yaml(yaml_str)
assert result.valid
```

## API

### Models

- `PythonJobConfig` - Python CI job settings (version, test/lint/format commands)
- `TypeScriptJobConfig` - TypeScript CI job settings (node version, lint/build/test)
- `PublishConfig` - Publish target config (PyPI or npm, CI/CD variable names)
- `PipelineConfig` - Top-level pipeline config (name, triggers, jobs)

### Generators

- `generate_ci_pipeline(config?)` - CI pipeline with lint + test + build jobs
- `generate_release_pipeline(publish_python?, publish_typescript?, trigger_tag_pattern?)` - Release pipeline with publish jobs

### Serializer

- `pipeline_to_yaml(pipeline)` - Dict to clean YAML string
- `write_pipeline(pipeline, path)` - Write pipeline to .yml file

### Validation

- `validate_config(config)` - Check config has at least one job
- `validate_pipeline_yaml(yaml_content)` - Check YAML has valid GitLab CI structure (stages, jobs with stage+script)

## GitLab CI vs GitHub Actions

| Concept | GitHub Actions | GitLab CI |
|---------|---------------|-----------|
| Top-level | `name`, `on`, `jobs` | `stages`, jobs at root |
| Job runner | `runs-on: ubuntu-latest` | `image: python:3.12` |
| Steps | `steps: [{uses:...}, {run:...}]` | `before_script` + `script` |
| Triggers | `on: [push, pull_request]` | `rules: [{if: ...}]` |
| Secrets | `${{ secrets.TOKEN }}` | `$TOKEN` (CI/CD variable) |
| Cache | Implicit in actions | Explicit: `cache: {paths:, key:}` |

## Examples

Ready-to-use pipeline files in the `examples/` directory:

- `ci.yml` - Standard CI for Python + TypeScript monorepo
- `release-python.yml` - Tag-triggered release to PyPI
- `release-typescript.yml` - Tag-triggered release to npm
