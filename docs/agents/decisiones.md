# Documenting Decisions

Any architectural decision, infrastructure change, or significant vault improvement **must** be recorded as an output file in `<user-root>agenda/outputs/` using the format `YYYY-MM-DD-<slug>.md`. This includes:

- Changes to vault structure or conventions (new folders, naming rules, taxonomy updates)
- Changes to agent context files (`.abstract.md`, `.overview.md`, `CLAUDE.md`)
- Codebase-wide tooling or workflow decisions (CI changes, new patterns, dependency choices)
- Any decision that a future agent or collaborator would need to understand *why* something is the way it is

The output file should cover: what changed, why, and any trade-offs considered.

A session-to-session handoff is not an output: it goes to `agenda/handoffs/`, with `estado:` and `supersedes:` — see [file-formats.md § Handoff](../../_system/chief-of-staff/references/examples/file-formats.md#handoff).

# ADR status lifecycle

Every ADR must carry a `status:` field in its YAML frontmatter:

| Status | Meaning |
|--------|---------|
| `Proposed` | Decision under discussion — not yet binding |
| `Accepted` | Adopted and in effect |
| `Superseded` | Replaced by a newer ADR (link to successor in body) |
| `Deprecated` | No longer applies; not replaced by anything specific |

# Output → Wiki sync rule

Every output that changes something permanent **must** include an `affects:` frontmatter field listing the wiki files updated as a result.

```yaml
affects:
  - wiki/arquitectura-digital/stack
  - wiki/identidad/identidad-visual
```

- Paths are relative to the workspace's wiki root, no `.md` extension.
- Purely analytical outputs (audits, research, UX mapping) with no permanent changes use `affects: []`.
- If the wiki *should* be updated but hasn't been yet, list the file anyway — it flags a pending sync.

---
