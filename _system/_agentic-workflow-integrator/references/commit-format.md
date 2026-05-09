# Commit Format

The auto-commit hook uses this format:

```
cos: <action> - <description>

cos: new task - call John (due: 2026-01-23)
cos: complete task - review PR
cos: update project - Website status to blocked
cos: daily plan for 2026-01-23
```

Filter: `git log --grep="cos:"`
