# Purpose: make each tool folder importable from the tests.
# Book: National AI Strategy in Practice, Chapters 2-12 (tests)
# Licence: MIT (see LICENSE)
"""Add the tool folders to sys.path so tests can `import score`, `compute_planner`, etc."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for folder in ("readiness", "portfolio", "planner", "finance", "kpi"):
    sys.path.insert(0, str(ROOT / folder))
