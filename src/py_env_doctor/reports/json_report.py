from __future__ import annotations

import json
from ..core.model import Report


def render(report: Report) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=False)
