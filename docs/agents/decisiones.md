# Documenting Decisions

A decision that is in force is **documentation**, not agenda: it is true today. It goes to the decision register of the repo it governs ([ADR 0027](../adr/0027-la-agenda-envejece-la-documentacion-se-mantiene.md)):

| La decisión gobierna… | Va a |
|---|---|
| El harness de AWI (skills, hooks, convenciones del vault) | `docs/adr/NNNN-<slug>.md` en awi-core |
| La arquitectura de una organización | `_data/organizations/<org>/documentation/adr/NNNN-<slug>.md` |
| El negocio de una organización (precios, canales, productos) | `_data/organizations/<org>/documentation/bdr/NNNN-<slug>.md` — [plantilla BDR](../../_system/chief-of-staff/references/bdr-template.md) |
| El código de un codebase | `docs/adr/` de ese codebase |

Each record covers what was decided, why, and the trade-offs considered. It is immutable except for its status: a reversed decision gets a new record that supersedes it.

**What is not a decision record:**

- The analysis or research that led to the decision is an **output** (`agenda/outputs/YYYY-MM-DD-<slug>.md`), dated, and links to the record.
- A session-to-session handoff goes to `agenda/handoffs/`, with `estado:` and `supersedes:` — see [file-formats.md § Handoff](../../_system/chief-of-staff/references/examples/file-formats.md#handoff).

When a decision changes a living document, that document gets a line in its `## Cambios` section linking to the record — see [file-formats.md § Documento vigente](../../_system/chief-of-staff/references/examples/file-formats.md#documento-vigente).

# ADR status lifecycle

Every ADR must carry a `status:` field in its YAML frontmatter:

| Status | Meaning |
|--------|---------|
| `Proposed` | Decision under discussion — not yet binding |
| `Accepted` | Adopted and in effect |
| `Superseded` | Replaced by a newer ADR (link to successor in body) |
| `Deprecated` | No longer applies; not replaced by anything specific |

# Output and decision → documentation sync rule

Every output or decision record that changes something permanent **must** include an `affects:` frontmatter field listing the documentation files updated as a result.

```yaml
affects:
  - arquitectura-digital/stack
  - identidad/marca
```

- Paths are relative to the organization's `documentation/` folder, no `.md` extension.
- Purely analytical outputs (audits, research, UX mapping) with no permanent changes use `affects: []`.
- If the documentation *should* be updated but hasn't been yet, list the file anyway — it flags a pending sync.

---
