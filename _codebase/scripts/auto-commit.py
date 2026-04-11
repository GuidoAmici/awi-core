#!/usr/bin/env python3
"""Auto-commit vault changes after file write/edit operations.

Works as a hook for Claude Code (PostToolUse) and Gemini CLI (AfterTool).
Also usable standalone: python auto-commit.py <file_path>

Reads tool event JSON from stdin to extract the file path,
then commits the file if it's in a vault content directory.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Vault content directories that trigger auto-commit
# Top-level vault folders
VALID_FOLDERS = {"tasks", "projects", "daily", "weekly", "outputs", "info"}

TYPE_MAP = {
    "tasks": "task",
    "projects": "project",
    "daily": "daily plan",
    "weekly": "weekly summary",
    "outputs": "output",
    # info/ subfolders
    "context": "context",
    "people": "person",
    "ideas": "idea",
    "products": "product",
    "planning": "planning",
    "wiki": "wiki",
}


def get_vault_root() -> Path:
    """Derive vault root from script location (apps/scripts/ is two levels below vault root)."""
    return Path(__file__).resolve().parent.parent.parent


def extract_file_path_from_stdin() -> str | None:
    """Extract file path from hook JSON on stdin (Claude Code or Gemini CLI)."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return None
        data = json.loads(raw)

        # Claude Code: {"tool_input": {"file_path": "..."}} or {"tool_input": {"filePath": "..."}}
        tool_input = data.get("tool_input", {})
        path = tool_input.get("file_path") or tool_input.get("filePath")
        if path:
            return path

        # Gemini CLI: may nest under tool_input with different key names
        # Try common variations
        for key in ("path", "file", "filename", "target_file"):
            path = tool_input.get(key)
            if path:
                return path

        return None
    except (json.JSONDecodeError, AttributeError, TypeError):
        return None


def extract_file_path() -> str | None:
    """Get file path from CLI args or stdin."""
    # CLI arg takes priority (for standalone / Codex usage)
    if len(sys.argv) > 1:
        return sys.argv[1]

    # Otherwise try stdin (hook mode)
    if not sys.stdin.isatty():
        return extract_file_path_from_stdin()

    return None


def run_git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


def main() -> None:
    file_path_str = extract_file_path()
    if not file_path_str:
        sys.exit(0)

    file_path = Path(file_path_str).resolve()
    vault_root = get_vault_root()

    # Check file is inside vault
    try:
        rel = file_path.relative_to(vault_root)
    except ValueError:
        sys.exit(0)

    rel_posix = rel.as_posix()

    # Check file is in a valid vault folder
    folder = rel.parts[0] if rel.parts else ""
    if folder not in VALID_FOLDERS:
        sys.exit(0)

    # For info/ subfolders, use the subfolder name for type mapping
    if folder == "info" and len(rel.parts) > 1:
        subfolder = rel.parts[1]
        file_type = TYPE_MAP.get(subfolder, subfolder)
    else:
        file_type = TYPE_MAP.get(folder, folder)
    filename = file_path.stem

    # Check if file has changes
    has_diff = False

    result = run_git("diff", "--quiet", str(file_path), cwd=vault_root)
    if result.returncode != 0:
        has_diff = True

    result = run_git("diff", "--cached", "--quiet", str(file_path), cwd=vault_root)
    if result.returncode != 0:
        has_diff = True

    if has_diff:
        run_git("add", str(file_path), cwd=vault_root)
        run_git("commit", "-m", f"cos: update {file_type} - {filename}", cwd=vault_root)
    else:
        # Check if file is untracked
        result = run_git("ls-files", "--error-unmatch", str(file_path), cwd=vault_root)
        if result.returncode != 0:
            run_git("add", str(file_path), cwd=vault_root)
            run_git("commit", "-m", f"cos: new {file_type} - {filename}", cwd=vault_root)


if __name__ == "__main__":
    main()
