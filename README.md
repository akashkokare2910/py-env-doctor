# py-env-doctor

Diagnose Python environment issues and provide actionable fixes in plain language.

- Pinpoints pip/python mismatches
- Detects venv/conda/pyenv/system Python and PEP 668 (externally-managed)
- Surfaces path/module shadowing and project importability issues
- Generates text/JSON/Markdown reports for humans and CI

Why this tool? Python 3.12+ and distro packaging changes made setup pitfalls far more common. `py-env-doctor` explains what is wrong and how to fix it safely, with OS-aware guidance.

## Installation

- From PyPI:

```
pip install py-env-doctor
```

- From source (editable for development):

```
pip install -e .[dev]
```

Requires Python 3.9+.

## Quickstart

- Human-friendly report:

```
py-env-doctor check --project-path .
```

- JSON for CI or tooling:

```
py-env-doctor check --format json > env_report.json
```

- Markdown report to file:

```
py-env-doctor check --format md --out env_report.md
```

## Commands

- `py-env-doctor check` — run diagnostics and print a report
- `py-env-doctor version` — print tool version

### Options (check)

- `--project-path PATH` directory to analyze (default `.`)
- `--format text|json|md` output format (default `text`)
- `--out PATH` write output to a file
- `--level basic|full` reserved for future expansion
- `--diagnostics-only` omit recommendations and only emit facts

## Example output (text)

```
py-env-doctor: environment check

[Python]
- Executable: /usr/bin/python3.12
- Version: 3.12.3
- Platform: Linux (Ubuntu 24.04)
- Environment: system
- PEP 668: EXTERNALLY MANAGED

[pip]
- `pip` on PATH: /usr/bin/pip -> Python 3.12

[Project]
- Path: /home/user/myapp
- pyproject.toml: found
- project name: myapp
- package importable: no

[Common issues detected]
1) PEP668_SYSTEM_PYTHON (warning)
2) PROJECT_NOT_IMPORTABLE (error)

[Suggested fix]
- Create and use a virtual environment

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip

- Install your project into the active environment

    python -m pip install -e .
```

## JSON schema (simplified)

```json
{
  "type": "py_env_doctor_report",
  "generated_at": "RFC3339 timestamp",
  "python": {
    "executable": "str",
    "version": "str",
    "implementation": "CPython|PyPy|...",
    "environment_type": "system|venv|conda|pyenv|unknown",
    "is_venv": true,
    "is_conda": false,
    "is_pyenv": false,
    "pep668_externally_managed": true,
    "platform": {"system": "Windows|Linux|Darwin", "release": "str", "distro": "str|null"}
  },
  "pip": {
    "binaries": [{"name": "pip", "path": "str", "pip_version": "str|null", "python_version": "str|null"}],
    "mismatches": ["str"]
  },
  "project": {
    "path": "str",
    "pyproject": true,
    "project_name": "str|null",
    "package_importable": true,
    "shadowing": ["str"]
  },
  "issues": [{"code": "str", "severity": "info|warning|error", "details": "str|null"}],
  "advice": [{"title": "str", "steps": ["str"]}]
}
```

### Issue codes

- `PIP_PYTHON_MISMATCH`
- `PEP668_SYSTEM_PYTHON`
- `NO_VENV_FOR_PROJECT`
- `PROJECT_NOT_IMPORTABLE`
- `PATH_SHADOWING_PACKAGE`
- `WINDOWS_STORE_PYTHON`

## Architecture

```
src/py_env_doctor/
  cli.py                  # Typer CLI entrypoint
  core/
    model.py              # dataclasses for report schema
    detect_python.py      # python/pip mapping, env type, OS
    detect_pep668.py      # PEP 668 detection
    detect_shadowing.py   # cwd shadowing checks
    detect_layout.py      # pyproject + importability
    advice.py             # rules: issues -> recommendations
  reports/
    text_report.py        # human-readable export
    json_report.py        # machine-readable export
    markdown_report.py    # markdown export
```

Core modules gather facts. `advice.py` maps facts to actionable steps per OS. CLI orchestrates and prints reports.

## Development

- Create venv and install dev deps:

```
py -3 -m venv .venv
.\\.venv\\Scripts\\activate
python -m pip install -U pip
python -m pip install -e .[dev]
```

- Run tests:

```
pytest -q
```

- Linting/formatting: bring your own tooling; the codebase has no heavy runtime deps.

## Releasing to PyPI

See PYPI.md for full instructions. TL;DR:

```
python -m build
python -m twine upload dist/*
```

## License

MIT
