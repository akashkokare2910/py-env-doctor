from py_env_doctor.core.model import (
    PythonInfo,
    PlatformInfo,
    PipInfo,
    PipBinary,
    ProjectInfo,
)
from py_env_doctor.core import advice


def make_py_info(**overrides):
    base = dict(
        executable="/usr/bin/python3",
        version="3.12.1",
        implementation="CPython",
        environment_type="system",
        is_venv=False,
        is_conda=False,
        is_pyenv=False,
        pep668_externally_managed=True,
        platform=PlatformInfo(system="Linux", release="6.0", distro="Ubuntu 24.04"),
    )
    base.update(overrides)
    return PythonInfo(**base)


def make_proj_info(**overrides):
    base = dict(
        path="/tmp/project",
        pyproject=True,
        project_name="demo-project",
        package_importable=False,
        shadowing=["requests"],
    )
    base.update(overrides)
    return ProjectInfo(**base)


def test_evaluate_issues_and_advice_linux():
    py = make_py_info()
    pip = PipInfo(binaries=[PipBinary(name="pip", path="/usr/bin/pip", python_version="3.11")], mismatches=["pip -> Python 3.11 (current 3.12)"])
    proj = make_proj_info()

    issues = advice.evaluate_issues(py, pip, proj)
    codes = {i.code for i in issues}
    assert "PIP_PYTHON_MISMATCH" in codes
    assert "PEP668_SYSTEM_PYTHON" in codes
    assert "NO_VENV_FOR_PROJECT" in codes
    assert "PROJECT_NOT_IMPORTABLE" in codes
    assert "PATH_SHADOWING_PACKAGE" in codes

    adv = advice.make_advice(py, pip, proj, issues)
    titles = [a.title for a in adv]
    assert any("virtual environment" in t.lower() for t in titles)
    # ensure steps contain venv creation for Linux
    steps = [s for a in adv for s in a.steps]
    assert any("python3 -m venv" in s for s in steps)


def test_windows_store_issue_advice():
    py = make_py_info(platform=PlatformInfo(system="Windows", release="10", distro=None), executable="C:/Users/User/AppData/Local/Microsoft/WindowsApps/python.exe")
    pip = PipInfo()
    proj = make_proj_info(pyproject=False, package_importable=None)

    issues = advice.evaluate_issues(py, pip, proj)
    codes = {i.code for i in issues}
    assert "WINDOWS_STORE_PYTHON" in codes

    adv = advice.make_advice(py, pip, proj, issues)
    steps = [s for a in adv for s in a.steps]
    assert any("py -3 -m venv" in s for s in steps)
