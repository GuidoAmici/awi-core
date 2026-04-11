---
type: idea
tags: [second-brain, open-source, tooling]
created: 2026-03-20T00:00:00
---

# second-brain-core: Shareable Vault via Submodules

Extract the reusable parts of the second-brain into a public repo so friends can use the same workflows and get updates automatically.

## Architecture

```
my-vault/
  .claude/
    agents/    ← submodule: msitarzewski/agency-agents
    skills/    ← submodule: second-brain-core
    hooks/     ← personal
    settings.json ← personal
  INSTRUCTIONS.md
  CLAUDE.md
  info/        ← personal data
```

- `.claude/agents/` → submodule of `agency-agents` (Claude Code loads agents from here)
- `.claude/skills/` → submodule of `second-brain-core` (Claude Code loads skills from here)

## second-brain-core contents

- All skills: `/today`, `/week`, `/quarter`, `/year`, `/new`, `/daily-review`, `/history`, `/delegate`
- `.claude/reference/file-formats.md`
- `INSTRUCTIONS.md`, `CLAUDE.md` (vault structure + taxonomy)
- Empty `info/organization/` scaffold

## Update flow

- You update a skill → commit to `second-brain-core`
- Friends run `git submodule update --remote .claude/skills` to pull latest
- Same for `agency-agents` updates

## Related
- [[msitarzewski/agency-agents]] — agent definitions (already public)
