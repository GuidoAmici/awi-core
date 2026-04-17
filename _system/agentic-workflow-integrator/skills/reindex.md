# reindex

Create or update .abstract.md (L0) and .overview.md (L1) files across _system/ and _clients/.

**Tools:** Read, Write, Edit, Bash

> Node shapes and colors: see [_legend.md](_legend.md)

## Flow

```mermaid
graph TD
    A(["/reindex"]) --> B[["find _system _clients -mindepth 1 -type d"]]
    B --> C[For each folder: list contents]
    C --> D[[Read existing .abstract.md + .overview.md if present]]
    D --> E{File status?}
    E -->|missing| F[CREATE]
    E -->|stale paths/names| G[UPDATE]
    E -->|accurate| H[SKIP]
    F --> I[["Write .abstract.md — one sentence, noun-first"]]
    G --> I
    I --> J{3+ subfolders or complex structure?}
    J -->|yes| K[["Write .overview.md — folder map table + conventions"]]
    J -->|no| L[SKIP .overview.md]
    K --> M[[git status — show changed files]]
    L --> M
    M --> N[/Report table: Created / Updated / Skipped per tree/]
    N --> O((log_command.py reindex))

    classDef entry  fill:#89b4fa,color:#1e1e2e,stroke:#89b4fa
    classDef ai     fill:#cba6f7,color:#1e1e2e,stroke:#cba6f7
    classDef read   fill:#94e2d5,color:#1e1e2e,stroke:#94e2d5
    classDef write  fill:#a6e3a1,color:#1e1e2e,stroke:#a6e3a1
    classDef shell  fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef user   fill:#fab387,color:#1e1e2e,stroke:#fab387
    classDef stop   fill:#f38ba8,color:#1e1e2e,stroke:#f38ba8
    classDef log    fill:#45475a,color:#cdd6f4,stroke:#45475a

    class A entry
    class B,M shell
    class C,E,J ai
    class D read
    class F,G,H ai
    class I,K write
    class L ai
    class N user
    class O log
```
