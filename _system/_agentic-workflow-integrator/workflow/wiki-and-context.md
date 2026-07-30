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

The wiki is a separate repo, cloned into place. It is the source of truth for stable facts about the client, product, and codebase.

It is not tracked at a fixed commit from a parent: there are no gitlinks anywhere, so its contents float at the tip of its branch — which is what a shared context needs, because its value is being up to date. See [ADR 0012](../../../docs/adr/0012-contextos-flotan-dependencias-pinean.md).

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
3. Push the wiki repo — there is no pointer in a parent to update

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

## Operating on the wiki repo

```bash
# Update wiki to latest
cd _documentation/_context/<name>-wiki && git pull

# The wiki is its own repo: commit and push inside it. There is no pointer to
# update in a parent, because there is no gitlink.
cd <workspace-root>/documentation/wiki
git add -A && git commit -m "docs(wiki): ..." && git push

# On a fresh clone, materialise it
git clone <url> <workspace-root>/documentation/wiki
```
