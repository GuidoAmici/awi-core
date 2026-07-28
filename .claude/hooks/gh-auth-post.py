#!/usr/bin/env python3
"""PostToolUse handler for gh auth switch / gh auth login.

After a successful auth change, detects the new GitHub user, updates
current-user.json, scaffolds a new AWI user if needed, and materialises whatever
that user wants on disk.

Nothing here is a submodule — see ADR 0009. The user's repo is cloned like any
other entry, and re-materialising delegates to /awi-initialize so there is a
single code path for it.
"""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

SHARED = Path(__file__).resolve().parents[1] / "skills" / "shared" / "scripts"
sys.path.insert(0, str(SHARED))
from paths import AWI_ROOT, USERS_DIR, USER_SUBMODULES_FILE

INIT_SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills" / "awi-initialize" / "scripts" / "init_orgs.py"
)


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
    """Put the user's my-awi-user repo on disk, creating it on GitHub if needed."""
    user_dir = AWI_ROOT / f"_data/users/{github_id}"
    user_url = f"https://github.com/{login}/my-awi-user.git"

    exists = subprocess.run(
        ["gh", "repo", "view", f"{login}/my-awi-user"],
        capture_output=True, text=True,
    ).returncode == 0

    if exists:
        user_dir.parent.mkdir(parents=True, exist_ok=True)
        rc = git(["clone", "--branch", "only", user_url, str(user_dir)])
        if rc.returncode != 0:
            print(f"[AWI] Warning: could not clone {login}/my-awi-user — "
                  f"{rc.stderr.strip()}", file=sys.stderr)
            return
    else:
        subprocess.run(
            ["gh", "repo", "create", f"{login}/my-awi-user",
             "--private", "--description", "AWI user workspace"],
            capture_output=True, text=True,
        )
        # A repo created this way is empty, so there is no branch to clone from —
        # build the initial `only` branch locally and push it.
        user_dir.mkdir(parents=True, exist_ok=True)
        git(["init", "-b", "only"], cwd=user_dir)
        git(["remote", "add", "origin", user_url], cwd=user_dir)

    profile = user_dir / "awi-user-profile.md"
    if not profile.exists():
        profile.write_text(
            f"---\nlogin: {login}\ngithub-id: {github_id}\n---\n\n# {login}\n"
        )
    empty_state = user_dir / USER_SUBMODULES_FILE
    if not empty_state.exists():
        empty_state.write_text("{}\n")

    git(["add", "-A"], cwd=user_dir)
    git(["commit", "-m", f"chore({login}): scaffold AWI user"], cwd=user_dir)
    git(["push", "--set-upstream", "origin", "only"], cwd=user_dir)


def reinit_submodules(github_id: str) -> None:
    """Materialise whatever the new user wants on disk.

    Delegates to /awi-initialize rather than reimplementing it, so the clone and
    manifest logic has exactly one home.
    """
    if not (USERS_DIR / github_id / USER_SUBMODULES_FILE).exists():
        return
    rc = subprocess.run(
        [sys.executable, str(INIT_SCRIPT)],
        cwd=AWI_ROOT, capture_output=True, text=True,
    )
    if rc.stdout.strip():
        print(rc.stdout.rstrip())
    if rc.returncode not in (0, 4):
        print(f"[AWI] Warning: initialise reported errors — {rc.stderr.strip()}",
              file=sys.stderr)


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
    reinit_submodules(github_id)
    print(f"[AWI] Workspace configured for @{login}.")


if __name__ == "__main__":
    main()
