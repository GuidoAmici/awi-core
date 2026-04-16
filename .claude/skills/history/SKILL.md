---
name: history
description: Show recent git activity in readable format. Part of chief-of-staff system.
allowed-tools: Bash
model: haiku
subagent_type: general-purpose
---

# /history - Recent Activity

Show chief-of-staff activity from git log.

## Run

```bash
git log --since="7 days ago" --grep="cos:" --format="%ad %s" --date=short
```

Group output by day and summarize actions.

---

## Logging

At the end of this skill — regardless of outcome — log the invocation:

```bash
python3 .claude/skills/shared/scripts/log_command.py history <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
