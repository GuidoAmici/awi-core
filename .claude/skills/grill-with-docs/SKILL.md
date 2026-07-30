---
name: grill-with-docs
description: Grilling session that challenges your plan against the existing domain model, sharpens terminology, and updates documentation (CONTEXT.md, ADRs) inline as decisions crystallise. Use when user wants to stress-test a plan against their project's language and documented decisions.
---

<what-to-do>

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing.

If a question can be answered by exploring the codebase, explore the codebase instead.

</what-to-do>

<supporting-info>

## Domain awareness

During codebase exploration, also look for existing documentation:

### File structure

Most repos have a single context:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Create files lazily — only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

Don't couple `CONTEXT.md` to implementation details. Only include terms that are meaningful to domain experts.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).

</supporting-info>

## Triage mode

When invoked from `/triage` for a `ready-for-agent` issue, run the grill as a structured 3-phase panel. Each agent speaks with a `[agent-name]` label on every message. Later-phase agents may interrupt only for blockers (scope explosion, technical impossibility, wildly wrong effort estimate). Each phase ends with maintainer sign-off before the next opens.

### Phase 1 — Strategic alignment (`nexus-strategy`)

Covers: does this solve a real problem? who is it for? is it needed or just interesting?

**If unrelated to any active strategic goal:** ask exactly 3 questions (origin, affected party, future relevance trigger), file a context issue with `needs-context` label, and end the session — do not proceed to phase 2.

**If strategically relevant:** continue until the maintainer signs off on the rationale.

### Phase 2 — Priority & effort (`reality-checker`)

Covers: urgency, effort estimate, quick win vs. big feature, dependencies.

Closes by recommending an agent persona. Shortlist by searching the tree:

```bash
python3 .claude/skills/shared/scripts/agent_personas.py <término>
```

It prints name, category and tagline. Propose one; the maintainer confirms before
phase 3 opens.

### Phase 3 — Quality specs (`assigned-employee`)

Load the confirmed persona's `.md` — `agent_personas.py --resolver <nombre>` gives
the path. Speak as that agent for the rest of the session.

Covers: acceptance criteria, scope boundaries, key interfaces, edge cases.

Closes when the maintainer signs off on the spec. That sign-off is the agent brief body.

### ADR on close

After phase 3 sign-off, write an ADR to `docs/adr/` in the relevant codebase repo documenting the key implementation decision crystallised during the grill — the context, the decision, and the trade-offs an executing agent needs to understand. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).

Include the ADR path in the agent brief so the executing agent can read it before starting work.
