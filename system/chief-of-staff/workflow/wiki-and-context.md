---
kind: workflow
---

# Wiki & Context

How living reference knowledge is maintained alongside active work.

---

## Two kinds of knowledge

| Kind | Where | Updated how |
|---|---|---|
| **Active work** | `_documentation/_agenda/` | Constantly — tasks complete, projects evolve |
| **Reference knowledge** | `_documentation/_context/<name>-wiki/` | On decision — only when something permanently changes |

The wiki is a submodule: a separate git repo tracked at a fixed commit inside this one. It is the source of truth for stable facts about the client, product, and codebase.

In the workspace model, each `<name>-workspace` repo owns its own wiki submodule at `_documentation/_context/wiki/`.

---

## When to update the wiki

Update the wiki when:
- A decision changes how something works permanently (architecture, naming, process)
- An output's `affects:` field names a wiki file
- A piece of information in the wiki is found to be wrong or outdated

Do **not** update the wiki for:
- In-progress work (use tasks or projects)
- One-off decisions with no lasting effect (use outputs with `affects: []`)
- Observations or hypotheses (use ideas)

---

## Output → wiki sync loop

Every output that changes something permanent must:

1. List affected wiki files in the `affects:` frontmatter field
2. Actually update those wiki files (or flag them as pending)
3. Commit the wiki submodule pointer update in the parent repo

```yaml
# In the output file:
affects:
  - section/page-slug
  - section/other-page
```

If the wiki update hasn't happened yet, still list the file in `affects:` — it signals a pending sync and prevents the decision from being forgotten.

---

## Context files (non-wiki)

Beyond the wiki, the context layer includes:

| File | Purpose |
|---|---|
| `_documentation/_context/writing-style.md` | Voice, tone, and communication preferences |
| `_documentation/_context/business-profile.md` | Client overview, focus areas, current state |
| `_documentation/_context/codebase/<app>.md` | Per-app technical context (architecture, stack, conventions) |
| `_documentation/_context/users/<username>.md` | Operator profile — preferences, long-term patterns |

The AI reads these before complex tasks. Keep them current. When a preference or pattern becomes stable, update the relevant context file rather than relying on session memory.

---

## Wiki submodule operations

```bash
# Update wiki to latest
cd _documentation/_context/<name>-wiki && git pull

# After editing wiki files, commit the pointer in parent repo
cd <workspace-root>
git add _documentation/_context/<name>-wiki
git commit -m "cos: update wiki pointer"

# Initialize wiki submodule on fresh clone
git submodule update --init _documentation/_context/<name>-wiki
```
