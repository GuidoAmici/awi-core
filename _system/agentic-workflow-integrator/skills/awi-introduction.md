# awi-introduction

First-time AWI onboarding. Links GitHub account, sets language, response style, and session learning. Creates user profile.

**Tools:** Bash, Write

> Node shapes and colors: see [_legend.md](_legend.md)

## Flow

```mermaid
graph TD
    A(["/awi-introduction"]) --> B{Pick mode}
    B -->|1 Quick setup| C
    B -->|2 Configure| D[/Response style?/]
    B -->|3 What is AWI?| E[/Explain AWI/] --> B
    D --> F[/Session learning?/]
    F --> G[/Language?/]
    G --> C
    C[[gh auth status]] -->|not authed| H["STOP — tell user: gh auth login"]
    C -->|authed| I[/Ask display name/]
    I --> J[["Save _system/users/username.md"]]
    J --> K[/"Handoff: run /awi-initialize next"/]
    K --> L((log_command.py awi-introduction))

    classDef entry  fill:#89b4fa,color:#1e1e2e,stroke:#89b4fa
    classDef ai     fill:#cba6f7,color:#1e1e2e,stroke:#cba6f7
    classDef read   fill:#94e2d5,color:#1e1e2e,stroke:#94e2d5
    classDef write  fill:#a6e3a1,color:#1e1e2e,stroke:#a6e3a1
    classDef shell  fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef user   fill:#fab387,color:#1e1e2e,stroke:#fab387
    classDef stop   fill:#f38ba8,color:#1e1e2e,stroke:#f38ba8
    classDef log    fill:#45475a,color:#cdd6f4,stroke:#45475a

    class A entry
    class B ai
    class C shell
    class D,E,F,G,I,K user
    class H stop
    class J write
    class L log
```
