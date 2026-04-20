---
name: delegate-task
description: Delegate a task to a background agent. Use when the user says 'delegate', 'run in background', or 'delegate to <name>'.
---

# Purpose

Delegate tasks to background agents that run silently — no new terminal window.
Agents report back automatically via the UserPromptSubmit hook when they complete.

## Variables

DEFAULT_MODEL: opus
HEAVY_MODEL: opus
BASE_MODEL: sonnet
FAST_MODEL: haiku

DEFAULT_BUDGET: 1.00   (USD — prevents runaway spending)
HEAVY_BUDGET: 2.00
FAST_BUDGET: 0.20

## Employees

If user specifies "delegate to <name>", read `.claude/reference/employees.json` to get the repo path.

## Instructions

### Model & Budget Selection

| Task type        | Model  | Budget |
|-----------------|--------|--------|
| Research, analysis | sonnet | 1.00 |
| Complex coding   | opus   | 2.00 |
| Quick lookup     | haiku  | 0.20 |
| Frontend (Gemini)| —      | —     |

If 'fast' is requested → FAST_MODEL + FAST_BUDGET.
If 'heavy' is requested → HEAVY_MODEL + HEAVY_BUDGET.

### Cross-Repo Context (CRITICAL)

When delegating to a different repo (employee), the agent runs in THEIR directory.

1. Run `pwd` to get SOURCE_REPO (absolute path)
2. Use absolute paths in the prompt for all source repo references
3. Include: "First check .claude/skills/ for relevant skills."
4. Specify output: "Save to {SOURCE_REPO}/info/outputs/YYYY-MM-DD-<slug>.md"

### File Handling

- Instruct agent to update existing vault files directly — never create duplicates
- Deliverables → source repo's `info/outputs/YYYY-MM-DD-<slug>.<ext>`
- Link outputs from task file under `## Outputs` using `[[slug]]` format

### Source Task Callback

When related to an existing task/project:
1. Identify the source file (e.g., `info/tasks/my-task.md`)
2. Include in prompt: "When complete, update {absolute_path} with status and output link."

## Workflow

1. Understand the task and choose model + budget.
2. Craft a clear, complete prompt (include all context the agent needs — it can't ask you).
3. Build the slug: short kebab-case name (e.g., `research-competitor-pricing`).
4. Run the delegate:

**Same repo (silent background):**
```
python .claude/skills/delegate/scripts/delegate_run.py \
  --prompt "<PROMPT>" \
  --model <MODEL> \
  --slug <SLUG> \
  --budget <BUDGET>
```

**Same repo (visible tab in Windows Terminal — user can TAB to it):**
```
python .claude/skills/delegate/scripts/delegate_run.py \
  --prompt "<PROMPT>" \
  --model <MODEL> \
  --slug <SLUG> \
  --budget <BUDGET> \
  --visible
```

**Different repo (employee):**
```
python .claude/skills/delegate/scripts/delegate_run.py \
  --prompt "<PROMPT>" \
  --model <MODEL> \
  --slug <SLUG> \
  --budget <BUDGET> \
  --repo "<EMPLOYEE_REPO_PATH>"
```

5. Report the slug back to the user so they can track it.

Add `--visible` if the user says "let me watch it", "open in tab", or "visible". Omit for all other cases (silent is default).

## Monitoring & Control

**List all delegates:**
```
python .claude/skills/delegate/scripts/delegate_monitor.py
```

**Inspect a specific delegate (tail logs + stuck detection):**
```
python .claude/skills/delegate/scripts/delegate_monitor.py <slug>
python .claude/skills/delegate/scripts/delegate_monitor.py <slug> --tail 100
```

**Kill a stuck/runaway delegate:**
```
python .claude/skills/delegate/scripts/delegate_kill.py <slug>
```

**Restart a delegate** (kill then re-run with same or adjusted prompt).

## Auto-Reporting

When a delegate finishes, it:
1. Plays a completion sound (ascending beep = success, descending = failure)
2. Writes to `.claude/tmp/delegates/inbox.md`
3. The inbox is surfaced automatically at the top of your next message to me

You don't need to ask — completed delegates appear automatically.

## Examples

User: "delegate research on X"
→ model: sonnet, budget: 0.50
→ `delegate_run.py --prompt "Research X thoroughly..." --model sonnet --slug research-x --budget 0.50`

User: "delegate to gemini-website: update the homepage hero"
→ Read employees.json for gemini-website path
→ `delegate_run.py --prompt "..." --model sonnet --slug update-homepage-hero --repo "<path>"`

User: "check my delegates"
→ `delegate_monitor.py`

User: "kill the research-x delegate, it's stuck"
→ `delegate_kill.py research-x`

---

## Logging

At the end of this skill — regardless of outcome — log the invocation:

```bash
python3 .claude/skills/shared/scripts/log_command.py delegate <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
