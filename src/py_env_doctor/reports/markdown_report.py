from __future__ import annotations

from typing import List

from ..core.model import Report, Issue, AdviceItem


def _h1(text: str) -> str:
    return f"# {text}\n\n"


def _h2(text: str) -> str:
    return f"## {text}\n\n"


def _li(text: str) -> str:
    return f"- {text}\n"


def _code(text: str) -> str:
    return f"`{text}`"


def _block(lines: List[str]) -> str:
    return "".join(lines) + "\n"


def render(report: Report) -> str:
    py = report.python
    pip = report.pip
    proj = report.project

    out: List[str] = []
    out.append(_h1("py-env-doctor: environment check"))

    out.append(_h2("Python"))
    out.append(_li(f"Executable: {py.executable}"))
    out.append(_li(f"Version: {py.version}"))
    plat = f"{py.platform.system} ({py.platform.distro or py.platform.release})"
    out.append(_li(f"Platform: {plat}"))
    out.append(_li(f"Environment: {py.environment_type}"))
    out.append(_li(f"PEP 668: {'EXTERNALLY MANAGED' if py.pep668_externally_managed else 'No'}"))
    out.append("\n")

    out.append(_h2("pip"))
    if not pip.binaries:
        out.append(_li("No pip binaries found on PATH"))
    else:
        for b in pip.binaries:
            ver = b.python_version or "?"
            out.append(_li(f"{_code(b.name)} on PATH: {b.path} -> Python {ver}"))
    if pip.mismatches:
        out.append("\n")
        out.append("Mismatches:\n")
        for m in pip.mismatches:
            out.append(_li(m))
    out.append("\n")

    out.append(_h2("Project"))
    out.append(_li(f"Path: {proj.path}"))
    out.append(_li(f"pyproject.toml: {'found' if proj.pyproject else 'not found'}"))
    if proj.project_name:
        out.append(_li(f"project name: {proj.project_name}"))
    if proj.package_importable is not None:
        out.append(_li(f"package importable: {'yes' if proj.package_importable else 'no'}"))
    if proj.shadowing:
        out.append(_li(f"shadowing: {', '.join(proj.shadowing)}"))
    out.append("\n")

    out.append(_h2("Common issues detected"))
    if not report.issues:
        out.append("None\n\n")
    else:
        for i in report.issues:
            if i.details:
                out.append(_li(f"{i.code} ({i.severity}): {i.details}"))
            else:
                out.append(_li(f"{i.code} ({i.severity})"))
        out.append("\n")

    if report.advice:
        out.append(_h2("Suggested fix"))
        for item in report.advice:
            out.append(f"- **{item.title}**\n\n")
            for step in item.steps:
                out.append(f"    {step}\n")
            out.append("\n")

    return "".join(out)
