---
group: MAINTENANCE
description: Sync all submodules
order: 1
---

# awi-sync

Sync all AWI submodules (direct + nested). Commits local changes, pulls, pushes, and updates _data/submodules.md.

**Tools:** Bash

> Node shapes and colors: see [_legend.md](_legend.md)

## Flow

```mermaid
graph TD
    A(["/awi-sync"]) --> B[["python3 sync_submodules.py"]]
    B --> C["Discover submodules — AWI-level + nested"]
    C --> D["For each: check clone status"]
    D --> E{Uncommitted changes?}
    E -->|yes| F[["git add -A → commit"]]
    E -->|no| G[["Checkout branch → pull → push"]]
    F --> G
    G --> H[["Update _data/submodules.md — Mermaid + registry"]]
    H --> I[["Print 1-line summary"]]
    I --> J(("log_command.py awi-sync"))
    J --> K[/"Show output · --full-report for graph · --breakdown for text"/]

    classDef det   fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef human fill:#fab387,color:#1e1e2e,stroke:#fab387

    class A,K human
    class B,C,D,E,F,G,H,I,J det
```
