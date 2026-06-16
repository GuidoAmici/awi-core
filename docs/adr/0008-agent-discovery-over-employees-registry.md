# Agent discovery from _system/agency-agents/ replaces employees.json registry

`employees.json` was a manually maintained allowlist of dispatchable agents with explicit `path` and `tagline` fields. It covered roughly 20% of the agents available in `_system/agency-agents/`, making the other 80% invisible to `/triage` and `/delegate-issue` — they could never be suggested or assigned.

We replace it with runtime discovery: skills scan `_system/agency-agents/**/*.md`, derive the agent slug from the frontmatter `name` field (kebab-cased), and read the `description` field as the tagline. No registry file is needed. Adding an agent to the dispatchable pool means adding its `.md` to `_system/agency-agents/` — nothing else.

## Considered options

- **Keep employees.json, expand it manually:** Requires ongoing maintenance, still a partial view of available agents, and duplicates metadata already present in the `.md` files.
- **Replace with a slug-only allowlist:** Eliminates path/tagline duplication but preserves an explicit gate. Rejected because `_system/agency-agents/` is an upstream repo (`upstream: true`) whose files can't be modified — a separate allowlist would recreate the same maintenance burden.
- **Full discovery, no filter (accepted):** All agents in `_system/agency-agents/` are eligible. The triage grill panel's domain-based shortlisting handles routing without a manual gate.

## Consequences

- `/delegate` skill (which also referenced `employees.json` for cross-repo paths) is removed as it has no active users.
- `employees.json` is deleted with no remaining consumers.
- Existing agent briefs that specify a slug (e.g. `senior-developer`) continue to resolve correctly — the slug derivation from `name` is stable and matches the existing vocabulary.
