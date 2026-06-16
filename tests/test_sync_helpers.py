"""Unit tests for the pure helpers in sync_submodules.

These cover the label-rendering logic used by /awi-sync and the Mermaid
diagram generation. They test external behaviour only (inputs → outputs),
not implementation details.
"""
from pathlib import Path

import sync_submodules as s


def _result(**overrides):
    base = dict(
        name="repo",
        path="_data/x/repo",
        abs_path=Path("/tmp/repo"),
        parent="AWI",
        parent_abs=Path("/tmp"),
        remote_url="https://github.com/owner/repo.git",
        node_id="repo",
    )
    base.update(overrides)
    return s.SubmoduleResult(**base)


# ── short_repo ────────────────────────────────────────────────────────────────

def test_short_repo_strips_git_suffix():
    assert s.short_repo("https://github.com/GuidoAmici/awi-core.git") == "GuidoAmici/awi-core"


def test_short_repo_without_suffix():
    assert s.short_repo("https://github.com/owner/repo") == "owner/repo"


def test_short_repo_strips_trailing_slash():
    assert s.short_repo("https://github.com/owner/repo/") == "owner/repo"


# ── mermaid_class ─────────────────────────────────────────────────────────────

def test_mermaid_class_not_cloned_is_danger():
    assert s.mermaid_class(_result(cloned=False)) == "danger"


def test_mermaid_class_failed_is_warning():
    assert s.mermaid_class(_result(cloned=True, sync_status="failed")) == "warning"


def test_mermaid_class_healthy_is_safe():
    assert s.mermaid_class(_result(cloned=True, sync_status="ok")) == "safe"


# ── clone_status_label ────────────────────────────────────────────────────────

def test_clone_status_label_not_cloned():
    assert s.clone_status_label(_result(cloned=False)) == "🔴 not cloned"


def test_clone_status_label_failed():
    assert s.clone_status_label(_result(cloned=True, sync_status="failed")) == "🟡 sync failed"


def test_clone_status_label_cloned():
    assert s.clone_status_label(_result(cloned=True, sync_status="ok")) == "🟢 cloned"
