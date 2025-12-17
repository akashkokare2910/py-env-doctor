from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

# Common top-level packages that users often accidentally shadow
_COMMON_PKGS = {
    "requests",
    "numpy",
    "pandas",
    "matplotlib",
    "scipy",
    "typer",
    "click",
    "flask",
    "django",
    "pytest",
    "yaml",
    "pip",
}


def _norm(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    return name.replace("-", "_")


def detect_shadowing(project_path: Path, project_name: Optional[str]) -> List[str]:
    project_path = Path(project_path)
    found: List[str] = []
    try:
        entries = list(project_path.iterdir())
    except Exception:
        entries = []

    names = set()
    for e in entries:
        try:
            if e.is_dir():
                names.add(e.name)
            elif e.is_file():
                if e.suffix == ".py":
                    names.add(e.stem)
                else:
                    # common trap: requirements.txt named like a package? ignore
                    pass
        except Exception:
            continue

    # check common packages
    for pkg in _COMMON_PKGS:
        if pkg in names:
            found.append(pkg)

    # check if project name shadows Python stdlib or third-party usage (basic)
    pn = _norm(project_name)
    if pn and pn in names:
        # shadowing itself by a top-level script/module that conflicts with package
        found.append(pn)

    return sorted(set(found))
