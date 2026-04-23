---
group: SETUP
description: Toggle an org submodule on or off, persisting state to user's active-orgs.json
order: 4
---

# awi-org-toggle

Toggle an org submodule on or off. State persists in `_data/users/<github-id>/active-orgs.json`.

**Tools:** Bash

> Node shapes and colors: see [_legend.md](_legend.md)

## Flow

```mermaid
graph TD
    A(["/awi-org-toggle <org-name>"]) --> B{name in args?}
    B -->|no| C[["toggle_org.py status"]]
    C --> D[/"Which org do you want to toggle?"/]
    B -->|yes| E[["toggle_org.py status"]]
    D --> E
    E -->|not registered| F{URL known?}
    F -->|no| G[/"Ask for GitHub URL"/]
    F -->|yes| H[/"Show current state — confirm toggle"/]
    G --> H
    E -->|registered| H
    H -->|cancel| I["STOP — cancelled"]
    H -->|confirm| J[["toggle_org.py toggle <name> [--url]"]]
    J --> K[/"'<name>' is now ON / OFF"/]
    K --> L(("log_command.py awi-org-toggle"))

    classDef ai    fill:#cba6f7,color:#1e1e2e,stroke:#cba6f7
    classDef det   fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef human fill:#fab387,color:#1e1e2e,stroke:#fab387

    class A,D,G,H,K human
    class B,F ai
    class C,E,I,J,L det
```
