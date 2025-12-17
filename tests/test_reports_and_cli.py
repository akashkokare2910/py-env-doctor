from pathlib import Path
import json

from py_env_doctor.core import detect_python, detect_layout, detect_shadowing, advice
from py_env_doctor.core.model import Report, now_iso
from py_env_doctor.reports import json_report, text_report, markdown_report
from py_env_doctor import cli as cli_mod
from typer.testing import CliRunner


def build_report(tmp_path: Path) -> Report:
    py_info = detect_python.gather_python_info()
    pip_info = detect_python.gather_pip_info(py_info)
    proj_info = detect_layout.inspect_project(tmp_path)
    proj_info.shadowing = detect_shadowing.detect_shadowing(tmp_path, proj_info.project_name)
    issues = advice.evaluate_issues(py_info, pip_info, proj_info)
    adv = advice.make_advice(py_info, pip_info, proj_info, issues)
    return Report(
        type="py_env_doctor_report",
        generated_at=now_iso(),
        python=py_info,
        pip=pip_info,
        project=proj_info,
        issues=issues,
        advice=adv,
    )


def test_report_renderers(tmp_path: Path):
    # create a minimal pyproject
    (tmp_path / "pyproject.toml").write_text("[project]\nname='tmp-proj'\n")
    rep = build_report(tmp_path)

    j = json_report.render(rep)
    data = json.loads(j)
    assert data["type"] == "py_env_doctor_report"
    assert "python" in data and "pip" in data and "project" in data

    t = text_report.render(rep)
    assert "py-env-doctor" in t
    assert "[Python]" in t

    md = markdown_report.render(rep)
    assert md.startswith("# py-env-doctor")
    assert "## Python" in md


def test_cli_check_json(tmp_path: Path):
    # Make a temp project dir
    (tmp_path / "pyproject.toml").write_text("[project]\nname='tmp-proj'\n")
    runner = CliRunner()
    result = runner.invoke(cli_mod.app, ["check", "--project-path", str(tmp_path), "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["type"] == "py_env_doctor_report"
