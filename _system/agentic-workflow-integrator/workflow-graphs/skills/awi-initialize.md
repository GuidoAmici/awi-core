---
group: SETUP
description: Initialize all org submodules toggled on in the user's active-orgs.json
order: 3
---

# awi-initialize

Initialize all org submodules that are toggled on. Reads the current user's
`active-orgs.json`, registers any unregistered orgs in `.gitmodules`, then
runs `git submodule update --init` for each.

**Tools:** Bash

> Node shapes and colors: see [_legend.md](_legend.md)

## Flow

```mermaid
graph TD
    A(["/awi-initialize"]) --> B[["python3 init_orgs.py"]]
    B -->|exit 0| C[/"Show per-org results"/]
    B -->|exit 1 — git error| D["Show errors"]
    B -->|exit 2 — inactive orgs exist| E[/"List inactive orgs — toggle any on?"/]
    B -->|exit 3 — no orgs at all| F[/"No orgs registered. Create or import?"/]
    E -->|names given| G[["toggle_org.py on <name> · re-run init_orgs.py"]]
    E -->|skip| H["STOP — skipped"]
    F -->|1 or 2| I["/awi-org"]
    F -->|skip| H
    G --> C
    C --> J(("log_command.py awi-initialize"))
    D --> J

    classDef ai    fill:#cba6f7,color:#1e1e2e,stroke:#cba6f7
    classDef det   fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef human fill:#fab387,color:#1e1e2e,stroke:#fab387

    class A,C,E,F human
    class D,H ai
    class B,G,I,J det
```
