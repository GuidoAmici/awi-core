#!/usr/bin/env python3
"""
Report sync status between my-awi-instance and awi-core (source code).

Everything outside _data/ in the instance is source code and synced to awi-core.

Status values:
  ok       — identical in both repos
  drift    — exists in both but content differs
  missing  — in instance but absent from awi-core
  extra    — in awi-core but not in instance (stale)
"""

import hashlib
import sys
from pathlib import Path

PRIVATE_DIRS = {"_data", ".git"}


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def collect_instance_files(awi_root: Path) -> dict[str, Path]:
    """All files in the instance outside _data/ (these are source code)."""
    files: dict[str, Path] = {}
    for f in sorted(awi_root.rglob("*")):
        if f.is_file() and not any(p in PRIVATE_DIRS for p in f.relative_to(awi_root).parts):
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
    public_repo_path = awi_root / ".claude" / "config" / "public-repo-path"
    core_root = awi_root / public_repo_path.read_text().strip()

    if not core_root.is_dir():
        print(f"Error: awi-core not found at {core_root}")
        sys.exit(1)

    instance_files = collect_instance_files(awi_root)
    core_files = collect_core_files(core_root)

    ok, drift, missing, extra = [], [], [], []

    for rel, local_path in sorted(instance_files.items()):
        if rel in core_files:
            if md5(local_path) == md5(core_files[rel]):
                ok.append(rel)
            else:
                drift.append(rel)
        else:
            missing.append(rel)

    for rel in sorted(core_files):
        if rel not in instance_files:
            extra.append(rel)

    col_w = 60
    print(f"\n{'FILE':<{col_w}}  STATUS")
    print("-" * (col_w + 10))

    for rel in ok:
        print(f"  {rel:<{col_w}}  ok")
    for rel in drift:
        print(f"  {rel:<{col_w}}  DRIFT")
    for rel in missing:
        print(f"  {rel:<{col_w}}  MISSING from awi-core")
    for rel in extra:
        print(f"  {rel:<{col_w}}  EXTRA in awi-core")

    print()
    print(f"Summary: {len(ok)} ok  |  {len(drift)} drift  |  {len(missing)} missing  |  {len(extra)} extra")
    print()

    if drift or missing or extra:
        sys.exit(2)


if __name__ == "__main__":
    main()
