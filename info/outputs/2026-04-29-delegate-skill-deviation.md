# Delegate Skill Deviation Analysis
**Date:** 2026-04-29  
**Local:** `my-awi-instance/.claude/skills/delegate/`  
**Upstream:** `bradautomates/second-brain/.claude/skills/delegate/`

---

## File Inventory

| File | Upstream | Local | Delta |
|------|----------|-------|-------|
| `SKILL.md` | ✓ | ✓ | heavily modified |
| `scripts/fork_terminal.py` | ✓ | ✓ | modified |
| `scripts/delegate_run.py` | ✗ | ✓ | **added** |
| `scripts/delegate_monitor.py` | ✗ | ✓ | **added** |
| `scripts/delegate_kill.py` | ✗ | ✓ | **added** |
| `references/fork_summary_user_prompt.md` | ✓ | ✓ | unchanged |

---

## SKILL.md — Detailed Diff

### Upstream approach
Upstream skill delegates by **opening a visible terminal window** via `fork_terminal.py`. The agent runs **interactively** (no `-p` flag). The main user-facing primitive is the forked terminal — the user watches it run.

### Local approach
Local skill replaces the terminal-fork model with a **silent background runner** (`delegate_run.py`). Agents run headless, report via an inbox file (`.claude/tmp/delegates/inbox.md`), and are monitored/killed with dedicated scripts. A `--visible` flag optionally opens a Windows Terminal tab for watching.

### Section-by-section changes

| Section | Upstream | Local | Assessment |
|---------|----------|-------|-----------|
| `description` frontmatter | "fork terminal session to new terminal window" | "background agent, no new terminal" | reflects true behavior change |
| `DEFAULT_BUDGET` | not present | `1.00 USD` | **improvement** — upstream had no spend cap |
| Model table | no budget column | budget per task type | **improvement** — explicit cost control |
| Workflow step 3 | build `claude` CLI command, pass as positional arg | craft prompt only, budget/model separate | neutral (different abstraction) |
| Workflow step 4 | `fork_terminal.py '<full command>'` | `delegate_run.py --prompt ... --model ... --slug ... --budget ...` | architectural change, see below |
| `--visible` flag | not present | added, WSL/Windows Terminal tab | **improvement** — opt-in visibility |
| Fork Summary section | full section (fill-in template, `fork_summary_user_prompt.md`) | **removed** | regression (see below) |
| Monitoring section | not present | added (`delegate_monitor.py`, `delegate_kill.py`) | **improvement** |
| Auto-Reporting section | not present | added (inbox, audible beeps) | **improvement** |
| Logging section | not present | added (`log_command.py`) | **improvement** |
| Cross-repo output path | `outputs/YYYY-MM-DD-<slug>.md` | `info/outputs/YYYY-MM-DD-<slug>.md` | reflects AWI directory layout |

---

## scripts/fork_terminal.py — Diff

### Upstream Windows block
```python
full_command = f'cd /d "{cwd}" && set CLAUDE_DELEGATED=1 && {command}'
subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", full_command], shell=True)
```

### Local Windows block
```python
bat_lines = [
    "@echo off", f'cd /d "{cwd}"', "set CLAUDE_DELEGATED=1",
    "set CLAUDECODE=",  # unset to allow nested claude launch
    command,
]
fd, bat_path = tempfile.mkstemp(suffix=".bat")
# ... writes bat file ...
subprocess.Popen(["cmd", "/c", "start", "", "cmd", "/k", bat_path], shell=False)
```

| Change | Assessment |
|--------|-----------|
| Temp batch file instead of inline command string | **improvement** — avoids quoting hell with complex prompts |
| `shell=True` → `shell=False` | **improvement** — reduces shell injection surface |
| `set CLAUDECODE=` to unset env var | **improvement** — fixes nested claude launch issue |
| Empty title `""` in `start` to avoid arg confusion | **improvement** — correct Windows `start` behavior |
| `CREATE_NO_WINDOW \| CREATE_NEW_PROCESS_GROUP` flags (background path) | **improvement** — prevents blank terminal popup, ensures worker survives parent exit |
| Windows Terminal tab support (`wt --title slug new-tab`) | **improvement** — better UX than raw cmd window |

---

## scripts/delegate_run.py — New File

Background runner. Replaces `fork_terminal.py` as the primary delegation mechanism.

**Key features:**
- Launcher/worker split: launcher spawns detached worker process, returns immediately
- Worker runs `claude -p <prompt>` and tracks PID, status, exit code, duration
- Status JSON written to `.claude/tmp/delegates/<slug>/status.json`
- Output log at `.claude/tmp/delegates/<slug>/output.log`
- On completion: appends to `inbox.md`, plays audible beep (Windows PowerShell)
- `--budget` flag maps to `--max-budget-usd` in claude CLI
- `--visible` on Windows: opens Windows Terminal tab instead of silent background
- WSL detection for platform-appropriate behavior

**Assessment: improvement** — the upstream model had no status tracking, no budget enforcement, no programmatic completion notification. Operators had to watch a terminal window.

---

## scripts/delegate_monitor.py — New File

Lists all delegates or inspects one. Features:
- Stuck detection: flags delegates with no log output for 90+ seconds
- Shows PID, model, budget, duration, idle time
- Tails log file
- Shows pending inbox notifications

**Assessment: improvement** — fills a real operational gap.

---

## scripts/delegate_kill.py — New File

Kills delegate by slug. Cross-platform (Windows `taskkill /T` for process tree, Unix SIGTERM to process group). Updates status.json.

**Assessment: improvement** — upstream had no kill mechanism.

---

## Regressions

### Fork Summary feature removed
Upstream SKILL.md has a detailed "Fork Summary User Prompts" section: when the user requests a fork with conversation history, Claude fills out `fork_summary_user_prompt.md` as a template and passes the structured prompt to the new agent. This provides conversation continuity across forked sessions.

Local skill removes this section entirely. The `fork_summary_user_prompt.md` template file still exists in `references/` but is now dead code — SKILL.md no longer references it.

**Severity: medium.** Loss of context-passing on forks. Forked agents start cold. The background model partially compensates (prompts can be crafted with full context), but the structured template mechanism is gone.

### Interactive mode removed
Upstream ran agents with interactive mode (no `-p` flag). Local always uses `-p` (non-interactive). This means agents can't ask clarifying questions mid-task. Acceptable for background work but is a behavioral narrowing.

**Severity: low.** Background agents shouldn't need interactivity; it would block the process.

---

## Unchanged

- `references/fork_summary_user_prompt.md` — file is identical, but now unreferenced by SKILL.md (dead code)
- Variables section (`DEFAULT_MODEL`, `HEAVY_MODEL`, etc.) — same names, same values
- Employees lookup logic — same pattern
- macOS path in `fork_terminal.py` — identical

---

## Overall Assessment

### Deviation score: **HIGH**

The local fork is not a patch on top of upstream — it's a **architectural replacement** of the delegation model. Upstream: visible terminal windows, interactive agents, conversation history passing. Local: silent background agents, status tracking, budget enforcement, inbox-based reporting.

### Verdict breakdown

| Dimension | Upstream | Local | Winner |
|-----------|----------|-------|--------|
| Background execution | ✗ | ✓ | local |
| Budget control | ✗ | ✓ | local |
| Status tracking | ✗ | ✓ | local |
| Kill/monitor tooling | ✗ | ✓ | local |
| Completion notification | ✗ | ✓ | local |
| Windows quoting safety | weak | strong | local |
| Conversation continuity on fork | ✓ | ✗ | upstream |
| Fork summary template | ✓ | dead code | upstream |

**Local is meaningfully better for a headless/background workflow.** The one real regression is loss of the fork summary / conversation continuity mechanism — that template is still on disk but no longer wired. If cross-fork context passing matters, that section should be ported to the background model (embed history in the `--prompt` arg).
