# .gitmodules is a local ephemeral artifact, not a committed file

`.gitmodules` is generated on demand from `_data/users/<github-id>/user-submodules.json` during `awi-initialize`, user switch, and logout. It is never committed to the AWI instance repo and never mirrored to `awi-core`.

This means each operator's submodule graph is entirely driven by their `user-submodules.json` — cloning the AWI instance on a new machine produces no `.gitmodules` until `awi-initialize` runs. The alternative (committing `.gitmodules`) would mean one user's org registrations leak into the shared `awi-core` template and conflict with other operators' graphs.

## Considered options

- **Commit `.gitmodules`** — simpler tooling, but ties the shared template to one user's org layout and requires merge conflicts to be resolved when users differ.
- **Generate from `user-submodules.json`** (chosen) — each operator gets their own graph; the shared template stays clean; `awi-core` never sees private org URLs.
