---
name: python-uv-setup
description: Set up and manage Python projects using uv as the dependency manager and pyenv for Python version management. Use when the user wants to initialize a new Python project, add dependencies, configure Python versions, or run Python code in a uv-managed environment.
metadata:
  author: cfachola
  version: "1.0"
compatibility: Requires uv and pyenv. macOS and Linux. Install uv via curl -LsSf https://astral.sh/uv/install.sh | sh
---

# Python Project Setup with UV

## Prerequisites

Verify tooling before starting:

```bash
which uv
which pyenv
```

If `uv` is missing, install it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Ensure the target Python version

Check if the desired version is already available:

```bash
python3.{VERSION} --version
```

If not, install and activate it with pyenv:

```bash
pyenv install 3.{VERSION}
pyenv shell 3.{VERSION}
```

Prefer system or pyenv-installed Python. Do not let uv download its own Python unless explicitly requested.

## Initialize the project

```bash
uv init --python 3.{VERSION}
```

This creates `pyproject.toml`, `.python-version`, `.venv/`, `main.py`, `.gitignore`, `uv.lock`, and `README.md`.

Use `--lib` for a library, `--package` for an installable package, `--bare` for only `pyproject.toml`, or `--app` (default) for an application.

## Add dependencies

```bash
uv add package1 package2
```

This updates `pyproject.toml`, resolves versions, writes `uv.lock`, and installs into `.venv/`.

For dev dependencies use `--dev`. For custom groups use `--group NAME`. For optional extras use `--optional NAME`.

Version constraints follow PEP 508:

```bash
uv add 'requests>=2.28,<3'
```

## Run code

```bash
uv run main.py
uv run python -m module_name
uv run -m pytest
```

`uv run` syncs the environment and activates the venv automatically. No manual activation needed.

## Common operations

- Sync env from lockfile: `uv sync`
- Regenerate lockfile: `uv lock`
- Remove a dependency: `uv remove package`
- Show dependency tree: `uv tree`
- Export to requirements.txt: `uv export > requirements.txt`
- Update all deps: `uv lock --upgrade && uv sync`
- Frozen install in CI: `uv sync --frozen`

## Guidelines

- Commit `uv.lock` to version control for reproducible installs.
- Use `uv run` instead of manually activating the venv.
- Use `uv add` exclusively to manage dependencies; do not hand-edit `pyproject.toml` dependency lists.
- Use pyenv to install specific Python versions rather than uv-managed downloads.
- Separate runtime and dev dependencies using `--dev` and `--group`.
