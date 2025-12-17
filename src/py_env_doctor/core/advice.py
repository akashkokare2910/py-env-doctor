from __future__ import annotations

from typing import List

from .model import PythonInfo, PipInfo, ProjectInfo, Issue, AdviceItem


def _is_windows_store(executable: str) -> bool:
    return "WindowsApps" in executable or "Microsoft" in executable


def evaluate_issues(py: PythonInfo, pip: PipInfo, proj: ProjectInfo) -> List[Issue]:
    issues: List[Issue] = []
    if pip.mismatches:
        issues.append(
            Issue(
                code="PIP_PYTHON_MISMATCH",
                severity="error",
                details="; ".join(pip.mismatches),
            )
        )

    if py.pep668_externally_managed and py.environment_type == "system":
        issues.append(Issue(code="PEP668_SYSTEM_PYTHON", severity="warning"))

    if proj.pyproject and not (py.is_venv or py.is_conda):
        issues.append(Issue(code="NO_VENV_FOR_PROJECT", severity="warning"))

    if proj.project_name and proj.package_importable is False:
        issues.append(Issue(code="PROJECT_NOT_IMPORTABLE", severity="error"))

    if proj.shadowing:
        issues.append(
            Issue(
                code="PATH_SHADOWING_PACKAGE",
                severity="warning",
                details=", ".join(sorted(set(proj.shadowing))),
            )
        )

    if py.platform.system == "Windows" and _is_windows_store(py.executable):
        issues.append(Issue(code="WINDOWS_STORE_PYTHON", severity="warning"))

    return issues


def _venv_steps(system: str) -> List[str]:
    if system == "Windows":
        return [
            "py -3 -m venv .venv",
            ".\\.venv\\Scripts\\activate",
            "python -m pip install --upgrade pip",
        ]
    return [
        "python3 -m venv .venv",
        "source .venv/bin/activate",
        "python -m pip install --upgrade pip",
    ]


def _install_project_steps(system: str, editable: bool = True) -> List[str]:
    if editable:
        return [
            "python -m pip install -e .",
        ]
    return ["python -m pip install ."]


def _pip_mismatch_steps() -> List[str]:
    return [
        "Always prefer: python -m pip <cmd>",
        "Check: python -m pip --version",
    ]


def _pep668_steps(system: str) -> List[str]:
    return _venv_steps(system) + [
        "Install packages inside the virtual environment only.",
    ]


def _shadowing_steps() -> List[str]:
    return [
        "Rename or remove local files/folders that shadow installed packages (e.g., requests.py).",
        "Avoid naming project modules after popular packages.",
    ]


def _win_store_steps() -> List[str]:
    return [
        "Use the Python Launcher: py -3 -m venv .venv",
        "Alternatively, install Python from python.org or use pyenv-win.",
    ]


def make_advice(py: PythonInfo, pip: PipInfo, proj: ProjectInfo, issues: List[Issue]) -> List[AdviceItem]:
    system = py.platform.system
    items: List[AdviceItem] = []

    codes = {i.code for i in issues}

    if "PIP_PYTHON_MISMATCH" in codes:
        items.append(
            AdviceItem(title="Use python -m pip consistently", steps=_pip_mismatch_steps())
        )

    if "PEP668_SYSTEM_PYTHON" in codes:
        items.append(
            AdviceItem(title="Create and use a virtual environment", steps=_pep668_steps(system))
        )

    if "NO_VENV_FOR_PROJECT" in codes:
        steps = _venv_steps(system)
        items.append(AdviceItem(title="Set up a project-specific virtual environment", steps=steps))

    if "PROJECT_NOT_IMPORTABLE" in codes:
        items.append(
            AdviceItem(title="Install your project into the active environment", steps=_install_project_steps(system))
        )

    if "PATH_SHADOWING_PACKAGE" in codes:
        items.append(AdviceItem(title="Resolve module shadowing in project directory", steps=_shadowing_steps()))

    if "WINDOWS_STORE_PYTHON" in codes:
        items.append(AdviceItem(title="Avoid Microsoft Store Python for development", steps=_win_store_steps()))

    return items
