# Hooks

Configured in `.claude/settings.json`. Three hooks are active:

---

## Auto-Commit (PostToolUse)

Triggers after every `Write` or `Edit` operation on vault content.

**Script:** `.claude/hooks/auto-commit.sh` (bash) / `.claude/hooks/auto-commit.ps1` (PowerShell fallback)

**Behavior:**
- Only commits files under `_documents/`
- Derives commit type from subfolder (`tasks/` → `task`, `people/` → `person`, etc.)
- `second-brain-core` subfolder → type `second-brain-core`

**Commit format:**
```
cos: new task - task-name
cos: update person - guido
cos: new second-brain-core - file-formats
```

**Filter all activity:**
```bash
git log --grep="cos:"
```

**Troubleshooting:**
1. Check permissions in `.claude/settings.json`:
   ```json
   "allow": ["Bash(git add:*)", "Bash(git commit:*)"]
   ```
2. Verify hook is executable: `chmod +x .claude/hooks/auto-commit.sh`
3. Confirm file is under `_documents/`

---

## Stop Sound (Stop)

Plays a notification sound when a delegated task completes.

**Script:** `.claude/hooks/stop-sound.sh`

Only triggers when `CLAUDE_DELEGATED=1` environment variable is set.

---

## Check Delegates (UserPromptSubmit)

Runs on every user message to check for pending delegate outputs.

**Script:** `.claude/hooks/check-delegates.sh`
