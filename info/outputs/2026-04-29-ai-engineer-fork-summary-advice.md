# AI Engineer Analysis: Fork Summary Re-Integration

**Date:** 2026-04-29 (updated — supersedes prior version)  
**Author:** AI Engineer Agent  
**Scope:** `delegate` skill — fork_summary_user_prompt.md regression analysis

---

## Files Reviewed

| File | Lines | State |
|---|---|---|
| `.claude/skills/delegate/references/fork_summary_user_prompt.md` | 26 | Dead code — never read by any script |
| `.claude/skills/delegate/scripts/delegate_run.py` | 232 | Correct — passes `--prompt` string via `claude -p` |
| `.claude/skills/delegate/SKILL.md` | 157 | Says "include all context" but gives no structure |

---

## The Regression

`delegate_run.py` passes context via one channel:

```python
base_cmd = [claude_bin, "-p", prompt, "--model", model, "--dangerously-skip-permissions"]
```

`fork_summary_user_prompt.md` is never read, written, or referenced by any code. Delegated agents start cold with only what Claude embeds in `--prompt`. The template is dead code.

---

## Should Fork Summary Be Re-Integrated? No — With a Caveat

**Not as a file-based mechanism.** Yes as an inline prompt discipline enforced by SKILL.md.

### The Cold-Start Problem Is Real

Delegated agents run non-interactively (`claude -p`). They cannot ask follow-ups. When a user has a multi-turn conversation then says "delegate this," the agent has no context about:
- What was already tried and rejected
- File paths already identified in the conversation
- Constraints the user stated
- Why the task exists at all

The upstream (bradautomates/second-brain) was right to address this. The file-based mechanism was the wrong tool.

### Why Not the File-Based Pattern

**Race condition:** Two simultaneous delegates overwrite each other's `fork_summary_user_prompt.md`. The file path is fixed; there's no slug-scoped version.

**Stale state:** The file persists between sessions. An unfilled `<fill_in_conversation_summary_here>` placeholder could poison a future delegate.

**Contradictory semantics:** The prior analysis in this file said "use the template" but also "no file-based injection." Writing to the file and reading it back IS file-based injection — just with the complexity hidden in Claude's prompt construction step instead of `delegate_run.py`.

**Unnecessary coupling:** If Claude fills the file then passes its contents as `--prompt`, the file serves no purpose. The content is already in memory. Write it directly to the prompt string.

**2025/2026 context windows:** Models have 200K+ token windows. A 3K-token context summary is noise. There's no compression or transport benefit to the file intermediary.

### The Correct Pattern: Inline Context Block

Claude distills relevant conversation context directly into the `--prompt` string using a structured template. No file I/O. No runner changes. No coupling.

This is already partially implied by SKILL.md line 66 — *"include all context the agent needs"* — but without structure or enforcement, it's consistently skipped.

---

## Exact Changes Required

### Change 1: SKILL.md — Add Context Distillation Section

Insert before the `## Workflow` heading (after line 64 of current SKILL.md):

```markdown
### Context Distillation (Required)

Delegated agents are non-interactive — they cannot ask follow-up questions.
Before writing the prompt, extract from the current conversation:

| Field | What to capture |
|---|---|
| **Goal** | User's actual objective — not the task title, the *why* |
| **Constraints** | Rejected approaches, locked decisions, hard limits |
| **Known paths** | Files, repos, directories already identified in conversation |
| **Source task** | Absolute path if this relates to an existing task file |

**Every delegate prompt must open with a `## Context` block:**

\```
## Context
Goal: <user's actual objective>
Constraints: <rejected approaches, locked decisions, hard limits>
Known paths: <relevant files, dirs, repos — absolute paths>
Source task: <absolute path, or "n/a">

## Task
<specific instruction>

## Output
Save to: {SOURCE_REPO}/info/outputs/YYYY-MM-DD-<slug>.md
When complete: update {source_task_path} under ## Outputs
\```

**What to include in context:**
- Files read and their key findings (reference paths, not raw content)
- Decisions already made with rationale
- User preferences stated in conversation ("terse output", "no tests", etc.)
- Constraints established: budget, scope, deadline, excluded approaches

**What to omit:**
- Raw code dumps → reference file paths instead
- Tool call JSON → summarize outcomes, not tool mechanics
- Turns unrelated to the delegated task

Omit the `## Context` block ONLY for fully self-contained tasks with zero
dependency on prior conversation (e.g., "run the tests and report failures").
```

### Change 2: SKILL.md — Update Step 2 in Workflow

**Current (line 66):**
```
2. Craft a clear, complete prompt (include all context the agent needs — it can't ask you).
```

**Replace with:**
```
2. Craft the prompt following the Context Distillation instructions above.
   Use a shell heredoc when the prompt is multi-line (it always will be):
```

And add example showing heredoc usage in the Workflow section's bash examples:

```bash
# Correct pattern — context block + task inline in prompt
python .claude/skills/delegate/scripts/delegate_run.py \
  --prompt "## Context
Goal: Audit all Python files for SQL injection vectors
Constraints: Read-only — do not modify code
Known paths: /home/unixadmin/GitHub/GuidoAmici/my-awi-instance
Source task: n/a

## Task
Search all .py files for string-formatted SQL queries (f-strings, % format, .format()).
Report each finding: file, line number, query pattern, severity.

## Output
Save to: /home/unixadmin/GitHub/GuidoAmici/my-awi-instance/info/outputs/2026-04-29-sql-audit.md" \
  --model sonnet \
  --slug sql-injection-audit \
  --budget 1.00 \
  --visible
```

### Change 3: Delete or Repurpose Dead Template

**Option A (recommended): Delete `fork_summary_user_prompt.md`**

The template is superseded by the inline Context block format now in SKILL.md. Keeping it creates confusion: future agents might try to fill it and read it back, reintroducing the file-based race condition.

```bash
git rm .claude/skills/delegate/references/fork_summary_user_prompt.md
```

**Option B: Rename to document anti-pattern**

If reference value is wanted, rename to `context_block_example.md` and update content to show a filled-in example of the `## Context` block format. Remove the YAML structure and `<fill_in_*>` placeholders.

---

## What NOT to Change

**`delegate_run.py` — no changes.**

Adding `--context-file`, file prepend logic, or env-var injection is over-engineering. The prompt string IS the communication channel. New code paths add failure modes (file not found, encoding, arg length) with zero benefit. The script is correct.

| Approach | Pro | Con | Verdict |
|---|---|---|---|
| Inline `## Context` block in `--prompt` | Zero infra, works today, auditable in status.json | Long prompts need heredoc discipline | **Use this** |
| `--context-file` in delegate_run.py | Clean separation | File I/O, race conditions, new code path | No |
| Write fork_summary_user_prompt.md then read contents | Familiar to upstream pattern | File-based coupling, race conditions, stale state | No |
| Env var injection | Simple | Not surfaced in status.json, hard to debug | No |

---

## Implementation Plan

| Change | File | Effort | Priority |
|---|---|---|---|
| Add Context Distillation section | SKILL.md | 20 min | P0 |
| Update Step 2 wording + heredoc example | SKILL.md | 10 min | P0 |
| Delete dead template | `fork_summary_user_prompt.md` | 2 min | P1 |

---

## Summary

| Question | Answer |
|---|---|
| Re-integrate fork summary? | **No** to file-based mechanism |
| Is the cold-start problem real? | **Yes** — agents genuinely need context |
| Correct fix? | **SKILL.md** — mandatory Context Distillation section + inline template |
| Changes to delegate_run.py? | **None** — script is correct |
| What to do with dead template? | **Delete it** — inline format in SKILL.md supersedes it |

**Root cause of regression:** SKILL.md Step 2 is too vague. "Include all context" without structure means context gets omitted when Claude takes the path of least resistance. Mandatory Context block format + heredoc example fixes the cold-start problem with zero infrastructure changes.
