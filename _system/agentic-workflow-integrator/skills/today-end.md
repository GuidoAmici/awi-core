---
group: DAY
description: Close day
order: 4
---

# today-end

End-of-day retrospective. Reviews planned vs actual, energy, week pulse, and tomorrow's handoff.

**Tools:** Read, Write, Edit, Bash, Glob

> Node shapes and colors: see [_legend.md](_legend.md)

## Flow

```mermaid
graph TD
    A(["/today-end"]) --> B[[Read current-user.md → resolve agenda-base]]
    B -->|missing| C["STOP — run /awi-user-login"]
    B -->|ok| D[[Read daily file — energy-ceiling, check-in, session logs, breaks]]
    D --> E[[Read weekly file for week progress]]
    E -->|weekly missing| F[["Create minimal weekly file"]]
    F --> G
    E -->|ok| G[/Q1: How did today feel? energy / frustration / momentum/]
    G --> H[/Q2: What worked? What didn't — and why?/]
    H --> I[Synthesize: planned vs actual — deviation analysis, energy read, week pulse]
    I --> J[Identify 1–2 top items to start tomorrow]
    J --> K[["Append Day Review to daily file — set checked-out: true"]]
    K --> L((log_command.py today-end))

    classDef entry  fill:#89b4fa,color:#1e1e2e,stroke:#89b4fa
    classDef ai     fill:#cba6f7,color:#1e1e2e,stroke:#cba6f7
    classDef read   fill:#94e2d5,color:#1e1e2e,stroke:#94e2d5
    classDef write  fill:#a6e3a1,color:#1e1e2e,stroke:#a6e3a1
    classDef shell  fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef user   fill:#fab387,color:#1e1e2e,stroke:#fab387
    classDef stop   fill:#f38ba8,color:#1e1e2e,stroke:#f38ba8
    classDef log    fill:#45475a,color:#cdd6f4,stroke:#45475a

    class A entry
    class B,D,E read
    class C stop
    class F write
    class G,H user
    class I,J ai
    class K write
    class L log
```
