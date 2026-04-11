# Hooks

Configured in `.claude/settings.json`. Three hooks are active:

---

## Auto-Commit (PostToolUse)

Triggers after every `Write` or `Edit` operation on vault content.

**Script:** `.claude/hooks/auto-commit.sh` (bash) / `.claude/hooks/auto-commit.ps1` (PowerShell fallback)

**Behavior:**
- Only commits files under `_workspace/` or `_system/`
- For `_workspace/<name>/agenda/<subfolder>/`: derives type from subfolder (`tasks/` → `task`, `people/` → `person`, etc.)
- For `_system/`: type `system`; `_system/users/` → type `user`

**Commit format:**
```
cos: new task - task-name
cos: update person - guido
cos: new chief-of-staff - file-formats
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
3. Confirm file is under `_workspace/` or `_system/`

---

## Stop Sound (Stop)

Plays a notification sound when a delegated task completes.

**Script:** `.claude/hooks/stop-sound.sh`

Only triggers when `CLAUDE_DELEGATED=1` environment variable is set.

---

## Check Delegates (UserPromptSubmit)

Runs on every user message to check for pending delegate outputs.

**Script:** `.claude/hooks/check-delegates.sh`
