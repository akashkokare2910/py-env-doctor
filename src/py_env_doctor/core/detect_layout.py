from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Optional

try:  # Python 3.11+
    import tomllib  # type: ignore
except Exception:  # pragma: no cover
    import tomli as tomllib  # type: ignore

from .model import ProjectInfo


def _read_pyproject(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        try:
            with path.open("rb") as f:
                return tomllib.load(f)
        except Exception:
            return None


def _normalize_import_name(dist_name: str) -> str:
    return dist_name.replace("-", "_")


def _is_importable(mod_name: str) -> Optional[bool]:
    if not mod_name:
        return None
    try:
        spec = importlib.util.find_spec(mod_name)
        return spec is not None
    except Exception:
        return False


def inspect_project(project_path: Path) -> ProjectInfo:
    project_path = project_path.resolve()
    pyproject_file = project_path / "pyproject.toml"
    data = _read_pyproject(pyproject_file)
    project_name: Optional[str] = None
    package_importable: Optional[bool] = None

    if data and isinstance(data, dict):
        proj = data.get("project")
        if isinstance(proj, dict):
            name = proj.get("name")
            if isinstance(name, str) and name.strip():
                project_name = name.strip()
                import_name = _normalize_import_name(project_name)
                package_importable = _is_importable(import_name)

    return ProjectInfo(
        path=str(project_path),
        pyproject=pyproject_file.exists(),
        project_name=project_name,
        package_importable=package_importable,
    )
