from pathlib import Path

from py_env_doctor.core import detect_layout


def test_inspect_project_with_pyproject(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
name = "py-env-doctor"
        """.strip()
    )

    info = detect_layout.inspect_project(tmp_path)
    assert info.pyproject is True
    assert info.project_name == "py-env-doctor"
    # since our src/ is on sys.path in tests, the package should be importable
    assert info.package_importable is True
