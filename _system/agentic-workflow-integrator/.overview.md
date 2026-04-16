---
kind: workflow
---

# CBO — Codebase Orchestrator

CBO is an **integrator framework**: a repo type that integrates existing frameworks and workflows (BASB, COS, GTD, or any other) and registers the decisions that fall between them.

It does not impose new rules from scratch. It acts as the meta-layer above all other frameworks — the place where custom decisions, conventions, and adaptations get documented so they don't live only in someone's head or in a chat history.

---

## What makes something a CBO decision

A decision belongs in CBO documentation if:
- It is not already covered by a publicly known framework or workflow
- It is specific to this repo's operating context
- It would need to be explained to a new operator who knows BASB or COS but has never used this specific repo

Examples:
- The public/private sync mechanism and the `kind: workflow/context` tag override
- The `_` prefix convention for context folders under `_documentation/`
- The rule that wiki updates require an `affects:` field in the output file

Examples of what does NOT belong here:
- How to capture a task (that's COS)
- How to structure a second brain (that's BASB)
- How to write a daily note (that's COS workflow)

---

## Relationship to other frameworks in `system/`

| Framework | Type | Scope |
|---|---|---|
| BASB | Framework | Knowledge organization principles |
| COS (chief-of-staff) | Workflow | Day-to-day operating process |
| GTD | Methodology | Task capture and processing |
| **CBO** | Integrator | Fills gaps between the above; registers custom decisions |

---

## Creator

CBO is being designed and built by Guido Amici. This repo instance (chief-of-staff) is the first CBO deployment, built in the context of a third-party engineering engagement with New Haze.
