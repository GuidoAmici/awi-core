---
group: DAY
description: Morning intake
order: 1
---

# today-start

Morning intake ritual. Captures energy, schedule, and commitments — writes check-in to daily file.

**Tools:** Read, Write, Edit, Bash

> Node shapes and colors: see [_legend.md](_legend.md)

## Flow

```mermaid
graph TD
    A(["/today-start"]) --> B[[Read current-user.md → resolve agenda-base]]
    B -->|missing| C["STOP — run /awi-user-login"]
    B -->|ok| D{Friday? Check week-review done}
    D -->|missing| E["BLOCK — run /week-review first"]
    D -->|ok| F{Monday? Show mental model reminder}
    F --> G[/Q1: AskUserQuestion — energy level<br/>high / medium / low ceiling/]
    G --> H[/Q2: What's scheduled today? blocks + durations/]
    H --> I[/Q3: What 1–3 things committing to finish?/]
    I --> J[Calculate time budget — available = window − scheduled blocks]
    J --> K[["Write daily file — Morning Check-in + Time Budget"]]
    K --> L[/"Tell user: run /today to generate plan"/]
    L --> M((log_command.py today-start))

    classDef entry  fill:#89b4fa,color:#1e1e2e,stroke:#89b4fa
    classDef ai     fill:#cba6f7,color:#1e1e2e,stroke:#cba6f7
    classDef read   fill:#94e2d5,color:#1e1e2e,stroke:#94e2d5
    classDef write  fill:#a6e3a1,color:#1e1e2e,stroke:#a6e3a1
    classDef shell  fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef user   fill:#fab387,color:#1e1e2e,stroke:#fab387
    classDef stop   fill:#f38ba8,color:#1e1e2e,stroke:#f38ba8
    classDef log    fill:#45475a,color:#cdd6f4,stroke:#45475a

    class A entry
    class B read
    class C,E stop
    class D,F ai
    class G,H,I,L user
    class J ai
    class K write
    class M log
```
