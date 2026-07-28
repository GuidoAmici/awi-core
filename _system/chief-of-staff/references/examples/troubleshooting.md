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
3. Confirm file is under `_data/organizations/`, `_data/users/`, or `_system/` (hook ignores other paths)

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

## Repos missing after a folder rename

AWI repos are plain clones, not submodules — see ADR 0009. If a path rename leaves one missing,
fix its `path` in `user-submodules.json` (or its entry in the org's `codebases.json`) and re-run:

```bash
/awi-initialize
```

The old directory is left where it was; move or delete it yourself once you have checked it holds
nothing unpushed.
