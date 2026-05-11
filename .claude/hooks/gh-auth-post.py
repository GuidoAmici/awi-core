#!/usr/bin/env python3
"""PostToolUse handler for gh auth switch / gh auth login.

After a successful auth change, detects the new GitHub user, updates
current-user.json, scaffolds a new AWI user if needed, regenerates
.gitmodules, and reinitialises submodules.
"""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

SHARED = Path(__file__).resolve().parents[1] / "skills" / "shared" / "scripts"
sys.path.insert(0, str(SHARED))
from paths import AWI_ROOT, USERS_DIR, USER_SUBMODULES_FILE
from generate_gitmodules import write_gitmodules


def git(args: list[str], cwd: Path = AWI_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)


def gh_current_user() -> dict | None:
    """Return {id, login} for the currently authenticated gh user, or None."""
    result = subprocess.run(
        ["gh", "api", "user", "--jq", "{id: .id, login: .login}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)


def read_current_user() -> dict | None:
    f = USERS_DIR / "current-user.json"
    return json.loads(f.read_text()) if f.exists() else None


def write_current_user(github_id: str, login: str) -> None:
    record = {
        "user": f"_data/users/{github_id}/",
        "github-id": github_id,
        "login": login,
        "since": date.today().isoformat(),
        "user_repo": f"{login}/my-awi-user",
    }
    (USERS_DIR / "current-user.json").write_text(json.dumps(record, indent=2) + "\n")


def scaffold_user(github_id: str, login: str) -> None:
    """Add the new user's my-awi-user repo as a submodule and create a basic profile."""
    user_path   = f"_data/users/{github_id}"
    user_url    = f"https://github.com/{login}/my-awi-user.git"

    # Check if repo exists on GitHub first
    check = subprocess.run(
        ["gh", "repo", "view", f"{login}/my-awi-user"],
        capture_output=True, text=True,
    )
    if check.returncode != 0:
        # Create the repo
        subprocess.run(
            ["gh", "repo", "create", f"{login}/my-awi-user",
             "--private", "--description", "AWI user workspace"],
            capture_output=True, text=True,
        )

    # Register as submodule
    rc = git(["submodule", "add", "-b", "only", user_url, user_path])
    if rc.returncode != 0:
        print(f"[AWI] Warning: could not add user submodule — {rc.stderr.strip()}",
              file=sys.stderr)
        return

    # Scaffold minimal profile
    user_dir = AWI_ROOT / user_path
    profile  = user_dir / "awi-user-profile.md"
    if not profile.exists():
        profile.write_text(
            f"---\nlogin: {login}\ngithub-id: {github_id}\n---\n\n# {login}\n"
        )
    empty_state = user_dir / USER_SUBMODULES_FILE
    if not empty_state.exists():
        empty_state.write_text("{}\n")

    git(["add", "-A"], cwd=user_dir)
    git(["commit", "-m", f"cos: scaffold AWI user {login}"], cwd=user_dir)
    git(["push", "--set-upstream", "origin", "only"], cwd=user_dir)


def reinit_submodules(github_id: str) -> None:
    """Init active + deinit inactive submodules for the given user."""
    submodules_file = USERS_DIR / github_id / USER_SUBMODULES_FILE
    if not submodules_file.exists():
        return
    raw = json.loads(submodules_file.read_text())

    for name, entry in raw.items():
        path_rel = entry.get("path", "")
        path_abs = AWI_ROOT / path_rel
        if entry.get("active", False):
            git(["submodule", "update", "--init", "--recursive", path_rel])
        elif path_abs.exists() and any(path_abs.iterdir()):
            git(["submodule", "deinit", "-f", path_rel])


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Bash":
        return

    command = data.get("tool_input", {}).get("command", "")
    if "gh auth switch" not in command and "gh auth login" not in command:
        return

    new_user = gh_current_user()
    if not new_user:
        print("[AWI] Could not determine current gh user after auth change.", file=sys.stderr)
        return

    github_id = str(new_user["id"])
    login     = new_user["login"]

    current = read_current_user()
    if current and str(current.get("github-id")) == github_id:
        return  # no change

    print(f"[AWI] Auth changed → @{login} ({github_id}). Reconfiguring…")

    # Scaffold if unknown user
    user_dir = USERS_DIR / github_id
    if not user_dir.exists() or not any(user_dir.iterdir()):
        print(f"[AWI] Unknown AWI user — scaffolding @{login}…")
        scaffold_user(github_id, login)

    write_current_user(github_id, login)

    try:
        write_gitmodules(AWI_ROOT)
        print("[AWI] .gitmodules regenerated.")
    except Exception as e:
        print(f"[AWI] Warning: could not regenerate .gitmodules — {e}", file=sys.stderr)
        return

    reinit_submodules(github_id)
    print(f"[AWI] Workspace configured for @{login}.")


if __name__ == "__main__":
    main()
