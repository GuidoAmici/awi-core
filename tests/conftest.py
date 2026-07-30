"""Pytest setup: hacer importables los scripts compartidos.

Los scripts usan imports planos (`from paths import ...`, `from manifest import
...`), así que su directorio tiene que estar en sys.path.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / ".claude/skills/shared/scripts"
if SHARED.is_dir():
    sys.path.insert(0, str(SHARED))
