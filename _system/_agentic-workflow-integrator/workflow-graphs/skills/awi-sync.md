---
group: MAINTENANCE
description: Sync all submodules
order: 1
---

# awi-sync

Sync all AWI submodules (direct + nested). Pulls main, skips dirty repos, updates _data/submodules.md.

**Tools:** Bash, Write, Edit

> Node shapes and colors: see [_legend.md](_legend.md)

## Flow

```mermaid
graph TD
    A(["/awi-sync"]) --> B[[python3 sync_submodules.py]]
    B --> C[Discover all submodules — AWI-level + nested client]
    C --> D[For each: check clone status]
    D --> E{Uncommitted changes?}
    E -->|yes| F["STOP — skip, report clearly"]
    E -->|no| G[[Checkout main → pull]]
    G --> H[["Update _data/submodules.md — Mermaid + registry"]]
    H --> I[/Show report + updated Mermaid graph/]
    F --> I
    I --> J((log_command.py awi-sync))

    classDef ai    fill:#cba6f7,color:#1e1e2e,stroke:#cba6f7
    classDef det   fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef human fill:#fab387,color:#1e1e2e,stroke:#fab387

    class A,I human
    class B,F,G,J det
    class C,D,E,H ai
```
