# Publishing py-env-doctor to PyPI

This guide explains how to build and publish releases to TestPyPI and PyPI.

This repo includes GitHub Actions workflows:

- `.github/workflows/ci.yml` runs tests on every push/PR to `main`
- `.github/workflows/publish.yml` publishes on tags starting with `v`

Publishing is intended to be **tag-driven** (recommended), with a manual fallback.

## Prerequisites

- A PyPI account and/or TestPyPI account
- A PyPI API token
- Python 3.9+

Recommended tooling (already in [dev] extras):
- build
- twine

Install dev tools if needed:

```
pip install -e .[dev]
```

## Recommended: GitHub Actions (tag-driven publishing)

### One-time setup

In your GitHub repo settings, add these repository secrets (already set in your screenshot):

- `TEST_PYPI_API_TOKEN`
- `PYPI_API_TOKEN`

### Release rules

The publish workflow triggers on **tags**.

- TestPyPI: tag contains `-rc.`
  - Example: `v0.1.1-rc.1`
- PyPI: tag does **not** contain `-rc.`
  - Example: `v0.1.1`

Important: the workflow validates that the tag version matches `pyproject.toml` `[project].version`.

### Steps (fast)

1) Bump version in BOTH:

- `pyproject.toml` → `[project].version`
- `src/py_env_doctor/__init__.py` → `__version__`

2) Commit and push to `main`.

3) Create and push a tag:

- TestPyPI (recommended first): `vX.Y.Z-rc.N`
- PyPI (stable): `vX.Y.Z`

4) Watch GitHub Actions:

- `Actions` tab → workflow `Publish`

## Manual publishing (fallback)

## 1) Bump version

Edit `src/py_env_doctor/__init__.py` and update `__version__`.
Edit `pyproject.toml` `[project].version` to match.

Commit the change with a tag, e.g. `v0.1.1`.

## 2) Clean previous builds

```
python -m pip install -U build twine
rmdir /s /q dist 2>nul & rmdir /s /q build 2>nul
```

On macOS/Linux:

```
rm -rf dist build
```

## 3) Build

```
python -m build
```

This creates `dist/*.whl` and `dist/*.tar.gz`.

Optional sanity check:

```
python -m twine check dist/*
```

## 4) Upload to TestPyPI (optional, recommended)

Set environment vars for token auth OR use `~/.pypirc`.

Environment variables approach:

- `TWINE_USERNAME=__token__`
- `TWINE_PASSWORD=pypi-AgENdGVzdC5weXBpLm9yZy5...`

Publish to TestPyPI:

```
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

Install from TestPyPI to verify:

```
python -m pip install -U --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple py-env-doctor
py-env-doctor version
py-env-doctor check --format json --project-path .
```

## 5) Upload to PyPI

Ensure `TWINE_USERNAME=__token__` and `TWINE_PASSWORD=<your PyPI token>` are set, or configure `~/.pypirc`.

```
python -m twine upload dist/*
```

## 6) Post-release checks

- Fresh install in a clean venv:

```
py -3 -m venv .venv
.\.venv\Scripts\activate
python -m pip install -U pip
python -m pip install py-env-doctor
py-env-doctor version
py-env-doctor check --project-path .
```

- Verify console script works on Windows/macOS/Linux
- Verify README renders correctly on PyPI

## Notes

- No destructive actions are performed by the tool.
- Keep dependencies minimal for wide compatibility.
- For CI publishing, store `TWINE_PASSWORD` as a secret and use `__token__` username.
