---
kind: workflow
---

# Public / Private Split

How client-specific content is separated from reusable workflow infrastructure.

---

## The model

This system runs as two repos:

| Repo | Contains | Who sees it |
|---|---|---|
| **Private** (`chief-of-staff`) | Everything — client data, schedule, context, workflow files | Operator only |
| **Public** (`awi-core`) | Workflow files only — generic, no client data | Anyone who forks it |

The public repo is a forkable template. A new operator forks it, runs init, and has the full system scaffolded for a new client.

---

## What is a workflow file vs. a context file

**Workflow** — reusable across any engagement:
- Skills (`.claude/skills/`)
- Hooks (`.claude/hooks/`)
- System documentation (`_documentation/system/chief-of-staff/`)
- Generic ideas and mental models (`_documentation/_schedule/ideas/`)
- Root docs (`CLAUDE.md`, `INSTRUCTIONS.md`, etc.)

**Context** — specific to this client:
- Tasks, projects, people, daily logs, outputs, planning
- Wiki submodule and codebase docs
- User profiles
- Any file that references the client by name or contains client data

**Rule of thumb:** if the file would need editing before sharing with a different client, it's context.

---

## How the sync works

After every auto-commit to the private repo, `sync-public.sh` runs and:

1. Checks if the file's path matches the whitelist (`.claude/config/public-whitelist`)
2. Checks the file's frontmatter for `kind: workflow` (opt-in) or `kind: context` (opt-out)
3. If sync is warranted, copies the file to the public repo clone and commits there

The sync is silent and non-blocking. No manual steps needed.

### Per-file overrides

Add to any `.md` file's frontmatter:

```yaml
kind: workflow   # Sync this file even if its path isn't in the whitelist
kind: context    # Never sync this file even if its path is whitelisted
```

---

## Setup for a new operator

1. Fork `awi-core` on GitHub
2. Clone the fork locally
3. Run `/initialize` — it scaffolds the vault, creates the wiki submodule, and writes the public sync path
4. Set the public repo clone path in `.claude/config/public-repo-path` (gitignored)
5. Start working — the sync runs automatically

---

## Keeping the public repo clean

Never manually push client data to the public repo. The sync script is the only path in. If a file was accidentally synced:

```bash
cd ~/awi-core
git rm <file>
git commit -m "cos: remove accidentally synced context file"
```

Then add `kind: context` to that file's frontmatter in the private repo to prevent future syncs.
