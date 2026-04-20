# Git as Audit Trail

Every action = a commit.

```bash
git log --since="8am" --grep="cos:" --oneline  # Today's activity
git diff HEAD~1                                 # What changed
git log -p <user-root>agenda/tasks/             # Task history
```
