# today

Generate or refresh daily plan from due tasks and active projects. Re-runnable throughout the day.

**Tools:** Read, Write, Edit, Bash, Grep

> Node shapes and colors: see [_legend.md](_legend.md)

## Flow

```mermaid
graph TD
    A(["/today"]) --> B[[Read current-user.md → resolve agenda-base]]
    B -->|missing| C["STOP — run /awi-user-login"]
    B -->|ok| D[[Read daily file — energy-ceiling,<br/>scheduled blocks, anchored tasks, available time]]
    D -->|no check-in| E["STOP — run /today-start first"]
    D -->|ok| F[[grep tasks by due date — find overdue pending tasks]]
    F --> G[[grep projects for status: active]]
    G --> H[[git log since midnight for completed work]]
    H --> I[Order: anchored → due today → overdue → projects]
    I --> J[Apply energy gating per ceiling]
    J --> K{Total duration > available time?}
    K -->|yes| L[/Show overload warning — ask user what to defer/]
    K -->|no| M[["Write plan sections to daily file"]]
    L --> M
    M --> N((log_command.py today))

    classDef entry  fill:#89b4fa,color:#1e1e2e,stroke:#89b4fa
    classDef ai     fill:#cba6f7,color:#1e1e2e,stroke:#cba6f7
    classDef read   fill:#94e2d5,color:#1e1e2e,stroke:#94e2d5
    classDef write  fill:#a6e3a1,color:#1e1e2e,stroke:#a6e3a1
    classDef shell  fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef user   fill:#fab387,color:#1e1e2e,stroke:#fab387
    classDef stop   fill:#f38ba8,color:#1e1e2e,stroke:#f38ba8
    classDef log    fill:#45475a,color:#cdd6f4,stroke:#45475a

    class A entry
    class B,D read
    class C,E stop
    class F,G,H shell
    class I,J,K ai
    class L user
    class M write
    class N log
```
