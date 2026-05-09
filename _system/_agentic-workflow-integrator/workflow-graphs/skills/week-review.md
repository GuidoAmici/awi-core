---
group: PLANNING
description: Friday re-rank
order: 2
---

# week-review

Friday ritual. Review full backlog, re-rank priorities, select next week's work batch.

**Tools:** Read, Write, Bash, Grep

> Node shapes and colors: see [_legend.md](_legend.md)

## Flow

```mermaid
graph TD
    A(["/week-review"]) --> B[[bash get-datetime.sh]]
    B --> C[[grep all pending/in-progress tasks]]
    C --> D[[Read active projects]]
    D --> E[[Scan this week's daily files for patterns]]
    E --> F[Rank backlog: priority → deadline → product group]
    F --> G[Flag tasks pending 2+ weeks without progress]
    G --> H[/Ask operator: which items for next week?/]
    H --> I[/Confirm/adjust: priority, energy, duration, due date/]
    I --> J[Choose mental model relevant to week's theme]
    J --> K[/Show draft weekly plan — ask: realistic?/]
    K --> L[["Write weekly/YYYY-WNN.md after confirmation"]]
    L --> M((log_command.py week-review))

    classDef entry  fill:#89b4fa,color:#1e1e2e,stroke:#89b4fa
    classDef ai     fill:#cba6f7,color:#1e1e2e,stroke:#cba6f7
    classDef read   fill:#94e2d5,color:#1e1e2e,stroke:#94e2d5
    classDef write  fill:#a6e3a1,color:#1e1e2e,stroke:#a6e3a1
    classDef shell  fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef user   fill:#fab387,color:#1e1e2e,stroke:#fab387
    classDef stop   fill:#f38ba8,color:#1e1e2e,stroke:#f38ba8
    classDef log    fill:#45475a,color:#cdd6f4,stroke:#45475a

    class A entry
    class B,C,D,E shell
    class F,G,J ai
    class H,I,K user
    class L write
    class M log
```
