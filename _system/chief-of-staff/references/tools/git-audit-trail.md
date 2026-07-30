# Git as Audit Trail

Every action = a commit. Git is the database.

---

## Commit Format

```
type(scope): subject
```

| Pattern | Meaning |
|---------|---------|
| `docs(agenda): nueva tarea — name` | Created task |
| `docs(agenda): actualizar proyecto — name` | Modified project |
| `docs(agenda): completar tarea — name` | Marked complete |
| `docs(agenda): plan diario YYYY-MM-DD` | Created daily note |
| `docs(agenda): revisión diaria YYYY-MM-DD` | End of day review |
| `docs(agenda): update person — guido` | Updated person file |

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
