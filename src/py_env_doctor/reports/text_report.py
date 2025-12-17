from __future__ import annotations

from typing import List

from ..core.model import Report, Issue, AdviceItem


def _section(title: str) -> str:
    return f"{title}\n"


def _kv(key: str, value: str | None) -> str:
    v = value if value is not None else ""
    return f"- {key}: {v}\n"


def _issues(issues: List[Issue]) -> str:
    if not issues:
        return "[Common issues detected]\nNone\n\n"
    lines = ["[Common issues detected]\n"]
    for idx, i in enumerate(issues, start=1):
        if i.details:
            lines.append(f"{idx}) {i.code} ({i.severity}): {i.details}\n")
        else:
            lines.append(f"{idx}) {i.code} ({i.severity})\n")
    lines.append("\n")
    return "".join(lines)


def _advice(items: List[AdviceItem]) -> str:
    if not items:
        return ""
    out: List[str] = ["[Suggested fix]\n"]
    for item in items:
        out.append(f"- {item.title}\n\n")
        for step in item.steps:
            out.append(f"    {step}\n")
        out.append("\n")
    return "".join(out)


def render(report: Report) -> str:
    py = report.python
    pip = report.pip
    proj = report.project

    parts: List[str] = []
    parts.append("py-env-doctor: environment check\n\n")

    parts.append("[Python]\n")
    parts.append(_kv("Executable", py.executable))
    parts.append(_kv("Version", py.version))
    parts.append(_kv("Platform", f"{py.platform.system} ({py.platform.distro or py.platform.release})"))
    parts.append(_kv("Environment", py.environment_type))
    parts.append(_kv("PEP 668", "EXTERNALLY MANAGED" if py.pep668_externally_managed else "No"))
    parts.append("\n")

    parts.append("[pip]\n")
    if not pip.binaries:
        parts.append("- No pip binaries found on PATH\n\n")
    else:
        for b in pip.binaries:
            ver = b.python_version or "?"
            parts.append(f"- `{b.name}` on PATH: {b.path} -> Python {ver}\n")
        parts.append("\n")
    if pip.mismatches:
        parts.append("Mismatches:\n")
        for m in pip.mismatches:
            parts.append(f"- {m}\n")
        parts.append("\n")

    parts.append("[Project]\n")
    parts.append(_kv("Path", proj.path))
    parts.append(_kv("pyproject.toml", "found" if proj.pyproject else "not found"))
    if proj.project_name:
        parts.append(_kv("project name", proj.project_name))
    if proj.package_importable is not None:
        parts.append(_kv("package importable", "yes" if proj.package_importable else "no"))
    if proj.shadowing:
        parts.append(_kv("shadowing", ", ".join(proj.shadowing)))
    parts.append("\n")

    parts.append(_issues(report.issues))
    parts.append(_advice(report.advice))

    return "".join(parts)
