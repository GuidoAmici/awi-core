#!/usr/bin/env python3
"""
Report sync status between AWI (private) and awi-core (public forkable repo).

For each file covered by the whitelist, shows whether it matches awi-core.
Status values:
  ok       — identical in both repos
  drift    — exists in both but content differs
  missing  — in AWI whitelist but absent from awi-core
  extra    — in awi-core but not covered by the whitelist (shouldn't be synced)
"""

import hashlib
import re
import sys
from pathlib import Path


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def read_kind(path: Path) -> str:
    """Extract `kind:` field from markdown frontmatter, or ''."""
    if path.suffix != ".md":
        return ""
    try:
        text = path.read_text()
        if not text.startswith("---"):
            return ""
        end = text.find("---", 3)
        if end == -1:
            return ""
        frontmatter = text[3:end]
        m = re.search(r"^kind:\s*(\S+)", frontmatter, re.MULTILINE)
        return m.group(1) if m else ""
    except Exception:
        return ""


def parse_whitelist(whitelist_path: Path) -> list[str]:
    entries = []
    for line in whitelist_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            entries.append(line)
    return entries


def is_whitelisted(rel: str, entries: list[str]) -> bool:
    for entry in entries:
        if rel == entry or rel.startswith(entry + "/"):
            return True
    return False


def collect_local_files(awi_root: Path, entries: list[str]) -> dict[str, Path]:
    """Expand whitelist entries to all matching files in AWI."""
    files: dict[str, Path] = {}
    for entry in entries:
        candidate = awi_root / entry
        if candidate.is_file():
            files[entry] = candidate
        elif candidate.is_dir():
            for f in sorted(candidate.rglob("*")):
                if f.is_file():
                    rel = str(f.relative_to(awi_root))
                    files[rel] = f
    return files


def collect_core_files(core_root: Path) -> dict[str, Path]:
    """All files in awi-core (excluding .git)."""
    files: dict[str, Path] = {}
    for f in sorted(core_root.rglob("*")):
        if f.is_file() and ".git" not in f.parts:
            rel = str(f.relative_to(core_root))
            files[rel] = f
    return files


def main():
    awi_root = Path(__file__).resolve().parents[4]  # awi/
    core_root = awi_root / "_data" / "clients" / "rabbitek" / "codebase" / "awi-core"
    whitelist_path = awi_root / ".claude" / "config" / "public-whitelist"

    if not core_root.is_dir():
        print(f"Error: awi-core not found at {core_root}")
        sys.exit(1)

    if not whitelist_path.is_file():
        print(f"Error: whitelist not found at {whitelist_path}")
        sys.exit(1)

    entries = parse_whitelist(whitelist_path)
    local_files = collect_local_files(awi_root, entries)
    core_files = collect_core_files(core_root)

    # Apply kind: context override (excluded even if whitelisted)
    excluded_by_kind: set[str] = set()
    for rel, path in local_files.items():
        if read_kind(path) == "context":
            excluded_by_kind.add(rel)

    # Classify
    ok, drift, missing, extra = [], [], [], []

    for rel, local_path in sorted(local_files.items()):
        if rel in excluded_by_kind:
            continue
        if rel in core_files:
            if md5(local_path) == md5(core_files[rel]):
                ok.append(rel)
            else:
                drift.append(rel)
        else:
            missing.append(rel)

    for rel in sorted(core_files):
        if not is_whitelisted(rel, entries):
            extra.append(rel)

    # Output
    col_w = 60
    print(f"\n{'FILE':<{col_w}}  STATUS")
    print("-" * (col_w + 10))

    for rel in ok:
        print(f"  {rel:<{col_w}}  ok")
    for rel in drift:
        print(f"  {rel:<{col_w}}  DRIFT")
    for rel in missing:
        print(f"  {rel:<{col_w}}  MISSING from core")
    for rel in extra:
        print(f"  {rel:<{col_w}}  EXTRA in core")

    print()
    print(f"Summary: {len(ok)} ok  |  {len(drift)} drift  |  {len(missing)} missing  |  {len(extra)} extra")
    if excluded_by_kind:
        print(f"Skipped (kind: context): {len(excluded_by_kind)} files")
    print()

    if drift or missing or extra:
        sys.exit(2)  # non-zero = drift detected


if __name__ == "__main__":
    main()
