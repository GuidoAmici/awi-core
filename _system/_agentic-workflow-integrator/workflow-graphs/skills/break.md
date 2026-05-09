---
group: DAY
description: Log pause + motive
order: 3
---

# break

Log a break to today's daily file. Tracks start/end and motive for accurate work time calculation.

**Tools:** Read, Write, Edit, Bash

> Node shapes and colors: see [_legend.md](_legend.md)

## Flow

```mermaid
graph TD
    A(["/break motive OR /break back"]) --> B[[Read current-user.md → resolve agenda-base]]
    B -->|missing| C["STOP — run /awi-user-login"]
    B -->|ok| D[[bash get-datetime.sh — get current time]]
    D --> E[[Read daily file]]
    E -->|no daily file| F["STOP — run /today-start first"]
    E -->|ok| G{Command?}
    G -->|break motive| H[["Append to Breaks: HH:MM — motive — started"]]
    G -->|break back| I[Find last open break entry — calculate duration]
    I --> J[["Update line: HH:MM–HH:MM — motive — Xm"]]
    J --> K[/Show: break duration, total breaks, remaining work time/]
    H --> L[/"Tell user: say /break back when done"/]
    K --> M((log_command.py break))
    L --> M

    classDef entry  fill:#89b4fa,color:#1e1e2e,stroke:#89b4fa
    classDef ai     fill:#cba6f7,color:#1e1e2e,stroke:#cba6f7
    classDef read   fill:#94e2d5,color:#1e1e2e,stroke:#94e2d5
    classDef write  fill:#a6e3a1,color:#1e1e2e,stroke:#a6e3a1
    classDef shell  fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef user   fill:#fab387,color:#1e1e2e,stroke:#fab387
    classDef stop   fill:#f38ba8,color:#1e1e2e,stroke:#f38ba8
    classDef log    fill:#45475a,color:#cdd6f4,stroke:#45475a

    class A entry
    class B,E read
    class C,F stop
    class D shell
    class G,I ai
    class H,J write
    class K,L user
    class M log
```
