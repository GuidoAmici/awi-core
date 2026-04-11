---
type: idea
tags: [cbo, newhaze, afin, agenda, workflow, scheduling]
last-updated: 2026-04-09
---

# Separate NewHaze and AFIN Agendas

Right now both NewHaze work and the AFIN consulting engagement flow into the same daily/weekly planning layer. As AFIN grows, this could create friction — different energy profiles, different stakeholders, different rhythms.

## The angle

Two structurally distinct work contexts:
- **NewHaze** — software product company, sprint-driven, team-facing
- **AFIN** — external consulting, client-facing, milestone-driven

Mixing them in a single flat task list risks misaligned prioritization and blurred context-switching overhead.

## Possible approaches

- Tag-based separation (`newhaze` vs `afin`) with filtered views in daily planning
- Dedicated planning files (e.g. `weekly/newhaze.md` vs `weekly/afin.md`)
- Separate `/today` pass per context — morning for NewHaze, short async check for AFIN
- Separate products in frontmatter already provides machine-readable separation; question is whether the human-facing layer reflects it

## Related

- [[projects/afin-srl-modernization]]
- [[ideas/cbo-traditional-business]]
