"""Pytest setup: make the skill script packages importable.

The awi-sync scripts use flat imports (`from paths import ...`,
`from sync_status import ...`), so both script dirs must be on sys.path.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for rel in (
    ".claude/skills/shared/scripts",
    ".claude/skills/awi-sync/scripts",
):
    p = ROOT / rel
    if p.is_dir():
        sys.path.insert(0, str(p))
