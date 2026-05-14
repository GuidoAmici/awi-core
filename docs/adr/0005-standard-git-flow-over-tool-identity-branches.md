# Standard git flow over tool-identity branches

AWI contributors previously worked on long-lived personal branches named after their AI tool (`dev-claude`, `dev-gemini`), merging into `stg` and then `prod`. This created a backmerge problem: when one contributor's work landed in `stg`, the other's branch drifted behind and required manual or CI-driven backmerges that added noise to both branches' histories.

We collapsed both tool-named branches into a single `dev` branch following standard git flow: issue branches fork from `dev`, PR back into `dev`, and are deleted after merge. CI auto-promotes `dev` → `stg`; `stg` → `prod` is a manual release. Tool identity (Claude vs Gemini) is irrelevant at the branch level — it's an implementation detail of how a contributor runs their local AWI instance, not a first-class concept in the source repo's topology.

## Considered Options

- **Symmetric backmerge via CI** (`stg` → `dev-claude` and `stg` → `dev-gemini` on every push) — rejected because it creates circular merge noise and doesn't solve the underlying problem; it just automates the churn.
- **Rebase instead of backmerge** — rejected because rebasing rewrites `dev-*` history, breaking `/awi-sync` for any instance tracking those branches by commit pointer.

## Consequences

- `dev-claude` renamed to `dev`; `dev-gemini` treated as a one-time issue branch, PRed into `dev` and deleted
- `guard-dev-gemini.yml` workflow removed
- `/awi-sync` branch targets updated from `dev-claude` to `dev` across all instances
- Branch protection on `stg` and `prod` restricts direct PRs — only `dev` (via CI) promotes to `stg`
