from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime, timezone

EnvironmentType = Literal["system", "venv", "conda", "pyenv", "unknown"]
Severity = Literal["info", "warning", "error"]


@dataclass
class PlatformInfo:
    system: str
    release: str
    distro: Optional[str] = None


@dataclass
class PythonInfo:
    executable: str
    version: str
    implementation: str
    environment_type: EnvironmentType
    is_venv: bool
    is_conda: bool
    is_pyenv: bool
    pep668_externally_managed: bool
    platform: PlatformInfo


@dataclass
class PipBinary:
    name: str
    path: str
    pip_version: Optional[str] = None
    python_version: Optional[str] = None
    shebang_python: Optional[str] = None


@dataclass
class PipInfo:
    binaries: List[PipBinary] = field(default_factory=list)
    mismatches: List[str] = field(default_factory=list)


@dataclass
class ProjectInfo:
    path: str
    pyproject: bool
    project_name: Optional[str] = None
    package_importable: Optional[bool] = None
    shadowing: List[str] = field(default_factory=list)


@dataclass
class Issue:
    code: str
    severity: Severity
    details: Optional[str] = None


@dataclass
class AdviceItem:
    title: str
    steps: List[str]


@dataclass
class Report:
    type: str
    generated_at: str
    python: PythonInfo
    pip: PipInfo
    project: ProjectInfo
    issues: List[Issue] = field(default_factory=list)
    advice: List[AdviceItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
