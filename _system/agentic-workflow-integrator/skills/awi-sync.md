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

    classDef entry  fill:#89b4fa,color:#1e1e2e,stroke:#89b4fa
    classDef ai     fill:#cba6f7,color:#1e1e2e,stroke:#cba6f7
    classDef read   fill:#94e2d5,color:#1e1e2e,stroke:#94e2d5
    classDef write  fill:#a6e3a1,color:#1e1e2e,stroke:#a6e3a1
    classDef shell  fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef user   fill:#fab387,color:#1e1e2e,stroke:#fab387
    classDef stop   fill:#f38ba8,color:#1e1e2e,stroke:#f38ba8
    classDef log    fill:#45475a,color:#cdd6f4,stroke:#45475a

    class A entry
    class B,G shell
    class C,D,E ai
    class F stop
    class H write
    class I user
    class J log
```
