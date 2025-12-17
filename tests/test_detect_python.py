from pathlib import Path

from py_env_doctor.core import detect_python
from py_env_doctor.core.model import PythonInfo, PipInfo


def test_gather_python_info_basic():
    info = detect_python.gather_python_info()
    assert isinstance(info, PythonInfo)
    assert info.executable
    assert info.version
    assert info.platform.system in {"Linux", "Windows", "Darwin"}
    assert info.environment_type in {"system", "venv", "conda", "pyenv", "unknown"}


def test_gather_pip_info_basic():
    py_info = detect_python.gather_python_info()
    pip_info = detect_python.gather_pip_info(py_info)
    assert isinstance(pip_info, PipInfo)
    assert isinstance(pip_info.binaries, list)
    # if any binaries are present, ensure they have at least a name and path
    for b in pip_info.binaries:
        assert b.name
        assert b.path
