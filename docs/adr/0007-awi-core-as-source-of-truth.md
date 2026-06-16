# awi-core is the source of truth — the instance is downstream

Changes to skills, hooks, and harness configuration are committed to `awi-core` first and flow into AWI instances via submodule pull. The instance never originates changes to shared code.

The alternative — modifying the instance directly and propagating to awi-core — was the original workflow but created bilateral drift: instance-only skills (11 at time of decision), stale hook files in awi-core, and divergent `settings.json`. It also caused confusion for AI agents, which could not distinguish between source code in awi-core and runtime data in the instance.

The cost is one extra step when iterating on a skill (commit to awi-core, pull in instance). The benefit is that a fresh clone of awi-core produces a complete, working AWI harness without any manual reconciliation.

## Considered options

- **Instance-first (rejected):** Fast to iterate but produces drift. Any new clone starts incomplete. AI agents conflate source and data.
- **Separate `my-awi-instance` repo (rejected):** Attempted as a reproducibility fix, but compounded the confusion — two repos claiming to be the harness.
- **awi-core-first (accepted):** Single canonical source. Instance is a runtime deployment of awi-core + user/org submodules.

## Consequences

- `GuidoAmici/my-awi-instance` can be archived once awi-core contains the full skill set
- Skills that were only in the instance (`grill-with-docs`, `triage`, `diagnose`, and 8 others) must be migrated to awi-core as part of this decision (see issue #17)
