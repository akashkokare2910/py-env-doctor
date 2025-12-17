from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .core.model import Report, now_iso
from . import __version__
from .core import detect_python, detect_layout, detect_pep668, detect_shadowing, advice
from .reports import json_report, text_report, markdown_report

app = typer.Typer(add_completion=False, help="Diagnose Python environment issues and provide actionable fixes.")


def _build_report(project_path: Path, level: str, diagnostics_only: bool) -> Report:
    py_info = detect_python.gather_python_info()
    pip_info = detect_python.gather_pip_info(py_info)

    proj_info = detect_layout.inspect_project(project_path)
    shadow = detect_shadowing.detect_shadowing(project_path, proj_info.project_name)
    proj_info.shadowing = shadow

    issues = advice.evaluate_issues(py_info, pip_info, proj_info)
    adv = [] if diagnostics_only else advice.make_advice(py_info, pip_info, proj_info, issues)

    return Report(
        type="py_env_doctor_report",
        generated_at=now_iso(),
        python=py_info,
        pip=pip_info,
        project=proj_info,
        issues=issues,
        advice=adv,
    )


@app.command()
def check(
    project_path: Path = typer.Option(Path("."), "--project-path", help="Path to the project (defaults to current directory)."),
    output_format: str = typer.Option(
        "text",
        "--format",
        "--output",
        "--fmt",
        case_sensitive=False,
        help="Output format: text|json|md",
    ),
    out: Optional[Path] = typer.Option(None, "--out", help="Write report to the given file instead of stdout."),
    level: str = typer.Option("basic", "--level", case_sensitive=False, help="Analysis level: basic|full"),
    diagnostics_only: bool = typer.Option(False, "--diagnostics-only", help="Emit raw diagnostics without advice."),
    no_network: bool = typer.Option(True, "--no-network/--network", help="Avoid network calls (reserved for future use)."),
):
    """Run environment diagnostics and print a report."""
    # level and no_network are placeholders for future behavior, included for CLI stability
    report = _build_report(project_path, level, diagnostics_only)

    fmt = output_format.lower()
    if fmt == "json":
        output = json_report.render(report)
    elif fmt in ("md", "markdown"):
        output = markdown_report.render(report)
    else:
        output = text_report.render(report)

    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output, encoding="utf-8")
    else:
        typer.echo(output)


@app.command()
def version():
    """Show py-env-doctor version."""
    typer.echo(__version__)


def main():  # console_scripts entry point
    app()


if __name__ == "__main__":
    main()
