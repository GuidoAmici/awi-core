# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CONTEXT-MAP.md`** at the repo root — points to one `CONTEXT.md` per context. Read each one relevant to the topic.
- **`docs/adr/`** — system-wide architectural decisions.
- Per-org decisions live in the org's `documentation/adr/` (architecture) and `documentation/bdr/` (business); a codebase keeps its own in its `docs/adr/`. See [ADR 0027](../adr/0027-la-agenda-envejece-la-documentacion-se-mantiene.md).

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The producer skill (`/grill-with-docs`) creates them lazily when terms or decisions actually get resolved.

## File structure

This is a multi-context repo. `CONTEXT-MAP.md` at the root points to per-context files:

```
/
├── CONTEXT-MAP.md                        ← index of all contexts
├── docs/adr/                             ← system-wide decisions
├── _data/organizations/newhaze/
│   ├── CONTEXT.md                        ← newhaze domain language
│   └── documentation/
│       ├── adr/                          ← newhaze architecture decisions
│       └── bdr/                          ← newhaze business decisions
├── _data/organizations/afin/
│   ├── CONTEXT.md
│   └── documentation/adr/  documentation/bdr/
└── _data/organizations/rabbitek/
    ├── CONTEXT.md
    └── documentation/adr/  documentation/bdr/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in the relevant `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/grill-with-docs`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 — but worth reopening because…_
