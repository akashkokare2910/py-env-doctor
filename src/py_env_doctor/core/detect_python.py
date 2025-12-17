from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import List, Optional

from .model import PythonInfo, PlatformInfo, PipInfo, PipBinary
from .detect_pep668 import is_externally_managed


def _read_os_release() -> Optional[str]:
    p = Path("/etc/os-release")
    if p.exists():
        try:
            data = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            return None
        items = {}
        for line in data:
            if "=" in line:
                k, v = line.split("=", 1)
                v = v.strip().strip('"')
                items[k.strip()] = v
        name = items.get("PRETTY_NAME") or items.get("NAME")
        version = items.get("VERSION")
        if name and version:
            return f"{name} {version}"
        return name
    return None


def _env_type(is_venv: bool, is_conda: bool, is_pyenv: bool, pep668: bool) -> str:
    if is_venv:
        return "venv"
    if is_conda:
        return "conda"
    if is_pyenv:
        return "pyenv"
    if pep668:
        return "system"
    return "unknown"


def _is_pyenv_exe() -> bool:
    if os.environ.get("PYENV_ROOT"):
        if os.environ.get("PYENV_SHELL") or ".pyenv" in sys.executable:
            return True
    return ".pyenv" in sys.executable


def _is_windows_store_python() -> bool:
    if platform.system() != "Windows":
        return False
    exe = Path(sys.executable)
    s = str(exe)
    return "WindowsApps" in s or "Microsoft" in s


def gather_python_info() -> PythonInfo:
    is_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    is_conda = bool(os.environ.get("CONDA_DEFAULT_ENV")) or "conda" in sys.prefix.lower()
    is_pyenv = _is_pyenv_exe()
    pep668 = is_externally_managed()
    plat = platform.system()
    rel = platform.release()
    distro = None
    if plat == "Linux":
        distro = _read_os_release()
    env_type = _env_type(is_venv, is_conda, is_pyenv, pep668)
    return PythonInfo(
        executable=sys.executable,
        version=platform.python_version(),
        implementation=platform.python_implementation(),
        environment_type=env_type,
        is_venv=is_venv,
        is_conda=is_conda,
        is_pyenv=is_pyenv,
        pep668_externally_managed=pep668,
        platform=PlatformInfo(system=plat, release=rel, distro=distro),
    )


_PIP_CANDIDATE_NAMES_CACHE: Optional[List[str]] = None


def _pip_candidate_names(pyver: str) -> List[str]:
    global _PIP_CANDIDATE_NAMES_CACHE
    if _PIP_CANDIDATE_NAMES_CACHE is not None:
        return _PIP_CANDIDATE_NAMES_CACHE
    major_minor = ".".join(pyver.split(".")[:2])
    names = [
        "pip",
        "pip3",
        f"pip{major_minor}",
        f"pip{pyver}",
    ]
    _PIP_CANDIDATE_NAMES_CACHE = names
    return names


_PIP_VERSION_RE = re.compile(r"pip\s+(?P<pver>[\w\.]+)\s+from\s+(?P<path>\S+)\s+\(python\s+(?P<pyver>[\d\.]+)\)")


def _pip_info_from_binary(name: str, path: str) -> PipBinary:
    pb = PipBinary(name=name, path=path)
    try:
        proc = subprocess.run([path, "--version"], capture_output=True, text=True, check=False)
        out = (proc.stdout or "") + (proc.stderr or "")
    except Exception:
        out = ""
    m = _PIP_VERSION_RE.search(out)
    if m:
        pb.pip_version = m.group("pver")
        pb.python_version = m.group("pyver")
    return pb


def gather_pip_info(py_info: PythonInfo) -> PipInfo:
    binaries: List[PipBinary] = []
    seen = set()
    for name in _pip_candidate_names(py_info.version):
        p = shutil.which(name)
        if p and p not in seen:
            seen.add(p)
            binaries.append(_pip_info_from_binary(name, p))
    mismatches: List[str] = []
    cur_mm = ".".join(py_info.version.split(".")[:2])
    for b in binaries:
        if b.python_version and b.python_version != cur_mm:
            mismatches.append(f"{b.name} -> Python {b.python_version} (current {cur_mm})")
    return PipInfo(binaries=binaries, mismatches=mismatches)
