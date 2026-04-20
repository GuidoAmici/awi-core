# Troubleshooting

## Auto-commit not working

1. Check permissions in `.claude/settings.json`:
   ```json
   "allow": ["Bash(git add:*)", "Bash(git commit:*)"]
   ```
2. Verify hook is executable:
   ```bash
   chmod +x .claude/hooks/auto-commit.sh
   ```
3. Confirm file is under `_data/clients/`, `_data/users/`, or `_system/` (hook ignores other paths)

---

## Tasks not appearing in /today

1. Ensure task has `due: YYYY-MM-DD` in frontmatter
2. Check date format matches exactly (no spaces, ISO format)
3. Verify task is in `<user-root>agenda/tasks/` (resolved from `_data/users/current-user.md`)

---

## Classification asking too many questions

Confidence threshold is 0.5. For less confirmation:
- Be more specific: `"task: call John by Friday"`
- Add explicit type hints in your input

---

## Submodule issues after folder rename

If submodules stop resolving after a path rename:
```bash
git submodule sync
git submodule update --init --recursive
```
