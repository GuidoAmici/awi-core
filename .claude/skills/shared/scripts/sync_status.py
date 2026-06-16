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
import json
import sys
from pathlib import Path

PRIVATE_DIRS  = {"_data", ".git"}

# .gitmodules is ephemeral — generated per-user on awi-initialize, never mirrored.
# This set is the fallback when .awi-source is not present.
_DEFAULT_PRIVATE_FILES = {".gitmodules"}


def load_awi_source(awi_root: Path) -> dict:
    """
    Load .awi-source from the AWI root if it exists.
    Returns the parsed JSON dict, or an empty dict if the file is missing/invalid.
    """
    source_file = awi_root / ".awi-source"
    if not source_file.exists():
        return {}
    try:
        return json.loads(source_file.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def get_mirror_exclusions(awi_root: Path) -> set:
    """
    Return the set of filenames to exclude from the awi-core mirror.
    Reads 'gitignore_rules.exclude_from_mirror' from .awi-source if present,
    falling back to the hardcoded default set.
    """
    source = load_awi_source(awi_root)
    rules = source.get("gitignore_rules", {})
    exclusions = rules.get("exclude_from_mirror", None)
    if exclusions is not None:
        return set(exclusions)
    return set(_DEFAULT_PRIVATE_FILES)


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def collect_instance_files(awi_root: Path) -> dict:
    """All files in the instance outside _data/ (these are source code).

    Consults .awi-source (via get_mirror_exclusions) to determine which
    filenames are excluded from the awi-core mirror. Falls back to the
    hardcoded default set when .awi-source is absent.
    """
    private_files = get_mirror_exclusions(awi_root)
    files = {}
    for f in sorted(awi_root.rglob("*")):
        rel = str(f.relative_to(awi_root))
        if f.is_file() \
                and not any(p in PRIVATE_DIRS for p in f.relative_to(awi_root).parts) \
                and f.name not in private_files:
            files[rel] = f
    return files


def collect_core_files(core_root: Path) -> dict:
    """All files in awi-core (excluding .git)."""
    files = {}
    for f in sorted(core_root.rglob("*")):
        if f.is_file() and ".git" not in f.parts:
            rel = str(f.relative_to(core_root))
            files[rel] = f
    return files


def find_awi_core_path(awi_root: Path):
    """Discover awi-core by scanning all .gitmodules files for GuidoAmici/awi-core."""
    for gitmodules in sorted(awi_root.rglob(".gitmodules")):
        if ".git" in gitmodules.parts:
            continue
        current_path = None
        for line in gitmodules.read_text().splitlines():
            line = line.strip()
            if line.startswith("path ="):
                current_path = line.split("=", 1)[1].strip()
            elif line.startswith("url =") and "GuidoAmici/awi-core" in line:
                if current_path:
                    return gitmodules.parent / current_path
    return None


def main():
    awi_root = Path(__file__).resolve().parents[4]  # awi/
    core_root = find_awi_core_path(awi_root)

    if not core_root or not core_root.is_dir():
        print("Error: awi-core not found — no submodule with url GuidoAmici/awi-core in .gitmodules")
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
