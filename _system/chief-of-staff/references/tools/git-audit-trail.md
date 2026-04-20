# Git as Audit Trail

Every action = a commit. Git is the database.

---

## Commit Format

```
cos: <action> - <description>
```

| Pattern | Meaning |
|---------|---------|
| `cos: new task - name` | Created task |
| `cos: update project - name` | Modified project |
| `cos: complete task - name` | Marked complete |
| `cos: daily plan for YYYY-MM-DD` | Created daily note |
| `cos: daily review for YYYY-MM-DD` | End of day review |
| `cos: update person - guido` | Updated person file |

Filter all Chief of Staff activity: `git log --grep="cos:"`

---

## Useful Commands

```bash
# Today's activity
git log --since="8am" --grep="cos:" --oneline

# Last week
git log --since="7 days ago" --grep="cos:" --format="%ad %s" --date=short

# What changed last
git diff HEAD~1

# File history
git log -p <user-root>agenda/tasks/my-task.md

# All Chief of Staff commits
git log --grep="cos:"
```
