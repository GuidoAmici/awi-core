---
group: MAINTENANCE
description: Audit missing context files
order: 4
hidden: true
---

# check-index

Read-only audit of _system/ and _data/organizations/ for missing .abstract.md and .overview.md files.

**Tools:** Bash

> Node shapes and colors: see [_legend.md](_legend.md)

## Flow

```mermaid
graph TD
    A(["/check-index"]) --> B[["find _system -mindepth 1 -type d"]]
    B --> C[["find _clients -mindepth 1 -maxdepth 3 -type d"]]
    C --> D[Apply skip rules: git submodule roots, node_modules,<br/>.git, .claude, single-file folders, uninitialized submodules]
    D --> E{For each folder: .abstract.md exists?}
    E -->|missing| F[ERROR]
    E -->|ok| G{.overview.md exists?<br/>only for folders with 3+ subfolders}
    G -->|missing| H[WARNING]
    G -->|ok| I[OK]
    F --> J[/Print table + counts: Errors / Warnings / OK/]
    H --> J
    I --> J
    J --> K((log_command.py check-index))

    classDef entry  fill:#89b4fa,color:#1e1e2e,stroke:#89b4fa
    classDef ai     fill:#cba6f7,color:#1e1e2e,stroke:#cba6f7
    classDef read   fill:#94e2d5,color:#1e1e2e,stroke:#94e2d5
    classDef write  fill:#a6e3a1,color:#1e1e2e,stroke:#a6e3a1
    classDef shell  fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef user   fill:#fab387,color:#1e1e2e,stroke:#fab387
    classDef stop   fill:#f38ba8,color:#1e1e2e,stroke:#f38ba8
    classDef log    fill:#45475a,color:#cdd6f4,stroke:#45475a

    class A entry
    class B,C shell
    class D,E,G ai
    class F stop
    class H,I ai
    class J user
    class K log
```
