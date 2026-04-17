# new

Quick capture — classify and file natural language input into the vault as task, project, person, or idea.

**Tools:** Read, Glob, Write, Edit, AskUserQuestion

> Node shapes and colors: see [_legend.md](_legend.md)

## Flow

```mermaid
graph TD
    A(["/new input"]) --> B[Decompose: extract all entities]
    B --> C["Classify each: task / project / person / idea"]
    C --> D{Confidence < 0.5?}
    D -->|yes| E[/Ask for clarification/]
    D -->|no| F[Extract structured data — due dates, tags, names]
    F --> G[[Read current-user.md → resolve agenda-base]]
    G -->|missing| H["STOP — run /awi-user-login"]
    G -->|ok| I{Task missing due date?}
    I -->|yes| J[/AskUserQuestion: when is this due?/]
    I -->|no| K[[Glob: check if person/project exists]]
    J --> K
    K --> L[["Write files to tasks/ projects/ people/ ideas/"]]
    L --> M[Link entities via frontmatter + wiki links]
    M --> N[/Report what was created/]
    N --> O((log_command.py new))

    classDef entry  fill:#89b4fa,color:#1e1e2e,stroke:#89b4fa
    classDef ai     fill:#cba6f7,color:#1e1e2e,stroke:#cba6f7
    classDef read   fill:#94e2d5,color:#1e1e2e,stroke:#94e2d5
    classDef write  fill:#a6e3a1,color:#1e1e2e,stroke:#a6e3a1
    classDef shell  fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef user   fill:#fab387,color:#1e1e2e,stroke:#fab387
    classDef stop   fill:#f38ba8,color:#1e1e2e,stroke:#f38ba8
    classDef log    fill:#45475a,color:#cdd6f4,stroke:#45475a

    class A entry
    class B,C,D,F,I,M ai
    class E,J,N user
    class G,K read
    class H stop
    class L write
    class O log
```
