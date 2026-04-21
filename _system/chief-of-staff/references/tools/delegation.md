# Delegation

Delegate work to specialized AI employees running in separate terminal sessions.

---

## What Are AI Employees?

AI employees are separate Claude Code repositories with specialized skills. Each lives in its own repo. The Chief of Staff orchestrates them via tasks in the AWI vault.

Current employees: see `.claude/reference/employees.json`

---

## Configure Employee Paths

Edit `.claude/reference/employees.json`:

```json
{
  "gemini-website": "~/projects/<org-name>-website",
  "gemini-learn": "~/projects/<org-name>-learn"
}
```

---

## Delegate Work

```bash
/delegate gemini-website: update the header component colors to match new token file
```

A separate Claude instance spawns in a new terminal, working in the employee's repo. When done:
- Task file updates with output locations
- Notification sound plays
- Full traceability via git log

---

## Gemini Delegation — Frontend Changes

Frontend file changes are **always delegated to Gemini CLI employees**:
- Claude handles: architecture, tokens, API schemas, decisions
- Gemini handles: CSS edits, font changes, component mechanical edits

---

## How It Works

1. Reads `employees.json` for cross-repo delegation targets
2. Builds prompt with full context (absolute paths, source repo reference)
3. Executes via `fork_terminal.py`:
   ```bash
   python3 .claude/skills/delegate/scripts/fork_terminal.py 'claude --model opus "<prompt>"'
   ```
4. New terminal opens with `CLAUDE_DELEGATED=1` set
5. When complete, `stop-sound.sh` plays notification

---

## Model Selection

| Variable | Model | Use Case |
|----------|-------|----------|
| `DEFAULT_MODEL` | opus | Standard delegation |
| `HEAVY_MODEL` | opus | Complex multi-step work |
| `BASE_MODEL` | sonnet | Moderate complexity |
| `FAST_MODEL` | haiku | Quick operations |
