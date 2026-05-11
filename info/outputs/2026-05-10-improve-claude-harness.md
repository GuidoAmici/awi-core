---
type: output
date: 2026-05-10
affects:
  - .claude/settings.json
  - .claude/hooks/
  - CLAUDE.md
---

# Claude Code Harness Audit — 2026-05-10

## Executive Summary

The AWI Claude Code harness is well-structured: auto-commit hooks, sound notifications, gh-auth guards, and a rich skill library provide a coherent workflow. However, the audit found **1 broken hook**, **several overly broad permissions**, **stale one-off permissions** that should be cleaned up, and **documentation drift** between CLAUDE.md and the actual codebase. The highest-impact fix is the missing `check-delegates.sh` — delegate completion notifications silently fail on every prompt submission.

---

## Findings (prioritised)

### P0 — Broken

#### 1. Missing `check-delegates.sh`

The `UserPromptSubmit` hook runs:
```
bash .claude/hooks/check-delegates.sh || powershell.exe ... check-delegates.ps1
```

**`check-delegates.sh` does not exist.** Only the `.ps1` version is present. On WSL2 the PowerShell fallback works, but:
- Every prompt submission logs a bash error before falling back — unnecessary noise and ~100ms latency per prompt.
- On native Linux (no `powershell.exe`) delegate notifications would silently fail entirely.

**Fix:** Create `check-delegates.sh` — a direct bash port of the 20-line PS1 script.

---

### P1 — Security / Risk

#### 2. Overly broad permissions in `settings.local.json`

| Permission | Risk |
|---|---|
| `Bash(git:*)` | Allows `git push --force`, `git reset --hard`, `git clean -fdx` — all destructive |
| `Bash(python3:*)` | Allows execution of *any* Python script, not just AWI scripts |
| `Bash(find:*)` | Low risk but unnecessary — Glob tool should be used instead |
| `Bash(gh api:*)` | Allows any GitHub API call — delete repos, modify org settings, etc. |
| `Bash(gh auth:*)` | Allows auth switches without confirmation — the pre-hook guards this somewhat but the permission is still very broad |

**Recommendation:** Narrow these to specific subcommands:
```json
"Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)", "Bash(git push:*)",
"Bash(git submodule:*)", "Bash(git checkout:*)", "Bash(git branch:*)",
"Bash(python3 .claude/*)", "Bash(python3 _system/*)",
"Bash(gh issue:*)", "Bash(gh repo view:*)", "Bash(gh api user:*)"
```

#### 3. `skipDangerousModePermissionPrompt: true` in global settings

This bypasses the safety prompt for dangerous operations globally — not just for this project. Combined with the broad `Bash(git:*)` permission, this significantly reduces guardrails.

**Recommendation:** Remove from global settings. If needed, set per-project in `settings.local.json`.

#### 4. `Bash(docker run:*)` and `Bash(docker build:*)` permissions

Docker run with arbitrary arguments can mount the host filesystem, access network, run as root. These should be scoped to specific images or removed if not actively used.

---

### P2 — Performance / Efficiency

#### 5. Double PostToolUse hook on every Bash command

Every Bash command triggers **both**:
1. `auto-commit.sh` — parses JSON, checks for `mv` commands, exits early for most
2. `gh-auth-post.py` — starts Python interpreter, parses JSON, checks for auth commands, exits early for most

That's two process spawns + two JSON parses per Bash call. For a session with 50 Bash commands, that's ~100 unnecessary process invocations.

**Fix:** Narrow the `auto-commit.sh` matcher. The Write/Edit matcher is correct, but the Bash matcher could be split:
```json
{ "matcher": "Write|Edit", "hooks": [{ "command": "bash ... auto-commit.sh" }] },
{ "matcher": "Bash", "hooks": [{ "command": "bash ... auto-commit-bash.sh" }] }
```
Or better: combine both Python hooks into one that handles both auth-check and mv-commit in a single process.

#### 6. Sound hooks spawn PowerShell on every invocation (WSL)

`permission-sound.sh` and `victory-sound.sh` try Linux audio tools first (which typically aren't available in WSL2), then fall through to PowerShell. PowerShell startup is ~500ms.

**Fix:** Cache the audio method on first run (write to `/tmp/.awi-audio-method`) and skip the probing on subsequent calls. Or use `wslpath` + a WSL-native player.

---

### P3 — Documentation Drift

#### 7. CLAUDE.md references `_data/entities/` — actual path is `_data/organizations/`

```
PostToolUse hook auto-commits after Write/Edit operations on `_data/entities/` and `_system/`
```

The auto-commit hook has no path filter — it commits changes to *any* file. And the actual structure uses `_data/organizations/`, not `_data/entities/`. This misleads the model about both the scope and the path.

**Fix:** Update CLAUDE.md to:
```
PostToolUse hook auto-commits after Write/Edit operations — do NOT commit manually unless asked.
```

#### 8. `wrap-session` SKILL.md references `current-user.md` but actual file is `current-user.json`

Step 2 of wrap-session says:
```
1. Read `_data/users/current-user.md`
```

The actual file is `current-user.json` (confirmed in paths.py and gh-auth-post.py). This causes the skill to fail on first attempt until the model self-corrects.

**Fix:** Update wrap-session SKILL.md Step 2 to reference `current-user.json`.

#### 9. INSTRUCTIONS.md structure table is outdated

The structure section shows `_data/entities/<name>/` but the codebase uses `_data/organizations/<name>/`. The path constants in `paths.py` use `ORGANIZATIONS_RELDIR = "_data/organizations"`.

**Fix:** Update the structure table in INSTRUCTIONS.md to match reality.

---

### P4 — Gaps / Missing Features

#### 10. No session-start hook to check for stale delegates

Delegates report via `inbox.md` on `UserPromptSubmit`, but if a delegate finished between sessions, the notification only appears on the first prompt of the next session. There's no proactive "you have N completed delegates" on session start.

**Recommendation:** Add a `SessionStart` or `PreToolUse` (first-call) hook that checks `.claude/tmp/delegates/` for completed results and surfaces them immediately.

#### 11. No `.claude/config/` directory

`sync-public.sh` references `.claude/config/public-repo-path` and `.claude/config/public-whitelist`, but the config directory doesn't exist. The script exits silently — correct behavior — but this feature is effectively dead code until configured.

**Recommendation:** Either document the public sync feature in CLAUDE.md or remove the dead code path from `auto-commit.sh` (line 101).

#### 12. Stale one-off permissions in `settings.local.json`

Several permissions are clearly from one-time operations:
- `Bash(cp "/mnt/d/Descargas/afin-srl-design-system/...` (3 entries)
- `Bash(mkdir -p _data/organizations/afin/codebase/...`
- `Bash(gunzip -c "/home/unixadmin/.claude/projects/...`
- `Bash(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)`
- `Bash(tar -t)`
- `Bash(fuser -k 3000/tcp 3001/tcp)`

These add noise and make the permission list harder to audit.

**Fix:** Remove all one-off permissions. They were auto-added during sessions and serve no ongoing purpose.

#### 13. No pre-push confirmation hook

The `Bash(git:*)` permission allows `git push` without any confirmation. Given that AWI manages multiple submodules with different remotes, an accidental push to the wrong remote or branch could be disruptive.

**Recommendation:** Add a `PreToolUse` hook for `Bash` that detects `git push` commands and requires explicit `--force` flag to be absent (or blocks force-push entirely).

---

### P5 — Minor / Cosmetic

#### 14. `auto-commit.sh` path check uses `_system/agentic-workflow-integrator/skills/`

Line 78 checks for skill files to regenerate the workflow diagram, but the path uses a different structure (`_system/agentic-workflow-integrator/skills/`) from the `.claude/skills/` directory where skills actually live. If skills have been migrated entirely to `.claude/skills/`, this code path may be dead.

#### 15. Redundant `Bash(grep:*)` permission in project settings

CLAUDE.md instructs using relative paths and the Grep tool. The bash grep permission encourages using the wrong tool.

**Fix:** Remove `Bash(grep:*)` from project `settings.json`.

---

## Recommendations — Quick Wins

| # | Action | Effort | Impact |
|---|---|---|---|
| 1 | Create `check-delegates.sh` (bash port of PS1) | 10 min | Fixes broken delegate notifications |
| 2 | Clean stale one-off permissions from `settings.local.json` | 5 min | Reduces audit noise |
| 3 | Fix `current-user.md` → `current-user.json` in wrap-session | 2 min | Prevents skill failure |
| 4 | Fix `_data/entities/` → `_data/organizations/` in CLAUDE.md | 2 min | Corrects model mental map |
| 5 | Narrow `Bash(git:*)` to specific subcommands | 10 min | Reduces blast radius |
| 6 | Remove `Bash(grep:*)` from project settings | 1 min | Encourages correct tool use |

## Recommendations — Medium Effort

| # | Action | Effort | Impact |
|---|---|---|---|
| 7 | Merge `gh-auth-post.py` and `auto-commit.sh` Bash hooks into single dispatcher | 30 min | Halves PostToolUse overhead |
| 8 | Narrow `Bash(python3:*)` to `Bash(python3 .claude/*)` | 5 min | Limits script execution scope |
| 9 | Cache audio method in sound hooks | 15 min | Saves ~500ms per sound event |
| 10 | Add force-push guard to PreToolUse | 20 min | Prevents destructive pushes |
