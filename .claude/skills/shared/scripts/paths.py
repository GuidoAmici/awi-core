"""
AWI directory path table — single source of truth.

All directory locations live here. When a dir moves, update this file only.

Two layers:
  *_RELDIR  — relative string, used by init_awi.py to scaffold any target path
  *_DIR     — absolute Path, used by operational scripts on the live AWI instance
"""

from pathlib import Path

# ── AWI root ──────────────────────────────────────────────────────────────────
# Resolves from this file's location: shared/scripts/ → shared/ → skills/ → .claude/ → root
AWI_ROOT = Path(__file__).resolve().parents[4]

# ── Relative dir strings (for scaffolding) ────────────────────────────────────
USERS_RELDIR                  = "_data/users"
USER_PROFILE_INFERENCE_SUBDIR = "agenda/user-profile-inference"  # relative to user root (_data/users/<github-id>/), not AWI root
ORGANIZATIONS_RELDIR   = "_data/organizations"
SUBMODULES_MD_RELPATH  = "_data/submodules.md"

SYSTEM_AWI_RELDIR      = "_system/agentic-workflow-integrator"
SYSTEM_COS_REFS_RELDIR = "_system/chief-of-staff/references"
SYSTEM_GTD_RELDIR      = "_system/getting-things-done"

# ── Absolute paths (for operational scripts) ─────────────────────────────────
USERS_DIR        = AWI_ROOT / USERS_RELDIR
CURRENT_USER     = USERS_DIR / "current-user.md"

ORGANIZATIONS_DIR = AWI_ROOT / ORGANIZATIONS_RELDIR
SUBMODULES_MD    = AWI_ROOT / SUBMODULES_MD_RELPATH

SYSTEM_AWI_DIR      = AWI_ROOT / SYSTEM_AWI_RELDIR
SYSTEM_COS_REFS_DIR = AWI_ROOT / SYSTEM_COS_REFS_RELDIR
SYSTEM_GTD_DIR      = AWI_ROOT / SYSTEM_GTD_RELDIR
