# GitHub CLI auth state is the source of truth for AWI user identity

AWI resolves the Current User from `gh auth status` rather than from a manually managed session file. Claude Code PreToolUse/PostToolUse hooks on `gh auth switch`, `gh auth login`, and `gh auth logout` intercept these transitions to enforce commit+push guards and trigger reconfiguration automatically.

This means swapping gh accounts is the user-facing gesture for switching AWI users — no separate `/awi-user switch` command needed during normal operation. If the incoming account has no AWI user record, one is auto-scaffolded inline.

## Considered options

- **Manual `/awi-user` commands only** — explicit but requires the user to remember to run a separate command after every gh auth change; easy to forget, leaving `current-user.json` stale.
- **gh auth hooks** (chosen) — deterministic, zero extra commands, consistent with how developers already think about identity in a gh-centric workflow. Hooks are Python scripts in `.claude/hooks/`, scoped to Claude sessions.

## Consequences

- Protection only applies within Claude sessions. A `gh auth logout` run directly in the terminal bypasses the PreToolUse dirty-state guard.
- `gh auth switch` to an unknown account triggers auto-creation of an AWI user, which requires network access and a writable `_data/users/` path.
