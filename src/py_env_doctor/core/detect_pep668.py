from __future__ import annotations

import os
import sys
import sysconfig
import site
from typing import List


def _candidate_site_dirs() -> List[str]:
    paths: List[str] = []
    # sysconfig paths
    try:
        sc = sysconfig.get_paths()
        for key in ("purelib", "platlib"):
            p = sc.get(key)
            if p:
                paths.append(p)
    except Exception:
        pass
    # site module paths
    try:
        for p in site.getsitepackages():
            paths.append(p)
    except Exception:
        pass
    try:
        up = site.getusersitepackages()
        if up:
            paths.append(up)
    except Exception:
        pass
    # de-duplicate preserving order
    seen = set()
    out: List[str] = []
    for p in paths:
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def is_externally_managed() -> bool:
    """Detect PEP 668 externally-managed environment by scanning for marker files.

    This checks for an 'EXTERNALLY-MANAGED' file in known site/dist-packages
    directories, as used by Debian/Ubuntu/Fedora.
    """
    # Only meaningful for CPython system installs; but harmless elsewhere
    for base in _candidate_site_dirs():
        for candidate in (
            os.path.join(base, "EXTERNALLY-MANAGED"),
            os.path.join(os.path.dirname(base), "EXTERNALLY-MANAGED"),
        ):
            try:
                if os.path.isfile(candidate):
                    return True
            except Exception:
                continue
    return False
