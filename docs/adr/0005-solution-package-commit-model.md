# Solution Package commit model

Per-file auto-commit was replaced with a session-scoped **Solution Package** model: one branch per issue, one semver-bumped commit per session, merged and branch-deleted at `/wrap-session`.

We considered per-file commits (current), session-level squash, and date-based versioning. We chose this model because: (1) per-file commits pollute history with noise and make it impossible to read what a session actually delivered; (2) the user works across multiple parallel terminals on different issues — a branch-per-package model is the only one that avoids working-tree collisions; (3) semver with human confirmation gives traceability that a build counter does not.

## Key decisions

- **Branch created** when the user selects Current in `/today`, not on first tool use — explicit over implicit.
- **Branch naming**: `{type}/{issue-number}-{slug}`, auto-generated from GitHub issue title and labels.
- **All repos touched** in the session get a semver bump (including workspace repos), written to a root `VERSION` file initialised at `0.1.0`.
- **Changelogs**: per-repo `CHANGELOG.md` for technical detail + central `CHANGELOG.md` at AWI root for narrative summary (devlog use).
- **Merge**: fully automatic at `/wrap-session` (no PR gate) until a review SOP is written — tracked as a follow-up issue.
- **Branch auto-delete** after merge; only `prod`, `stg`, `dev`, and `only` branches are permanent.
- **Queue state** (`current`, `next`, queue order, deferral counts) lives in `agenda/queue.json` using `org-name#issue-number` refs.
- **Deferral threshold** (default 3, configurable in `user-config.json`) triggers a Deferral Alert issue flagging deviation, friction, or misalignment.
