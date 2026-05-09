---
group: SETUP
description: Add or import organization submodule
order: 2
---

# awi-org

Add an organization workspace under `_data/organizations/<name>/` — create from scratch or import from GitHub.

**Tools:** Bash, Write

> Node shapes and colors: see [_legend.md](_legend.md)

## Flow

```mermaid
graph TD
    A(["/awi-org name"]) --> B{name in args?}
    B -->|no| C[/Ask for organization name/]
    B -->|yes| D{Mode?}
    C --> D
    D -->|1 new| E[[python3 init_org.py name]]
    D -->|2 import| F[/Ask for GitHub URL/]
    E --> G[["Creates agenda/ documentation/ codebase/ CLAUDE.md .gitignore"]]
    G --> H[[git init + initial commit]]
    H --> I{Create GitHub repo?}
    I -->|yes| J[[gh repo create → push → git submodule add]]
    I -->|no| K[/Skip — can do later/]
    F --> L[[git submodule add URL → update --init]]
    L --> M[[python3 import_client.py name — scaffold missing structure]]
    J --> N[/Confirm + next steps/]
    K --> N
    M --> N
    N --> O((log_command.py awi-org))

    classDef entry  fill:#89b4fa,color:#1e1e2e,stroke:#89b4fa
    classDef ai     fill:#cba6f7,color:#1e1e2e,stroke:#cba6f7
    classDef read   fill:#94e2d5,color:#1e1e2e,stroke:#94e2d5
    classDef write  fill:#a6e3a1,color:#1e1e2e,stroke:#a6e3a1
    classDef shell  fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef user   fill:#fab387,color:#1e1e2e,stroke:#fab387
    classDef stop   fill:#f38ba8,color:#1e1e2e,stroke:#f38ba8
    classDef log    fill:#45475a,color:#cdd6f4,stroke:#45475a

    class A entry
    class B,D,I ai
    class C,F,K,N user
    class E,H,J,L,M shell
    class G write
    class O log
```
