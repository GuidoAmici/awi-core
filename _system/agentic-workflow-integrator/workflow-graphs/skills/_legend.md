# Diagram Legend

All skill flowcharts use the same node shapes and Catppuccin Mocha colors.

## Colors

| Color | Class | Meaning |
|-------|-------|---------|
| 🟣 Purple | `ai` | AI — reasoning, decisions, content generation |
| 🟡 Yellow | `det` | Deterministic code — scripts, shell, file I/O, logging |
| 🟠 Orange | `human` | Human — skill invocation and user output |

## Shapes

| Shape | Syntax | Meaning |
|-------|--------|---------|
| Stadium | `([text])` | Entry point — the `/skill` invocation |
| Rectangle | `[text]` | Process step or STOP/BLOCK |
| Diamond | `{text}` | Decision / conditional branch |
| Subroutine | `[[text]]` | Tool call — Read, Grep, Glob, Write, Edit, Bash |
| Parallelogram | `[/text/]` | User interaction — ask / wait / tell |
| Circle | `((text))` | Log invocation (end of every skill) |

## Example

```mermaid
graph LR
    A(["/skill"])
    B["AI reasoning / process step"]
    C{Decision / branch}
    D[["Shell · script · Read · Write"]]
    E[/"User interaction — ask · wait · tell"/]
    F(("log_command.py"))

    classDef ai    fill:#cba6f7,color:#1e1e2e,stroke:#cba6f7
    classDef det   fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef human fill:#fab387,color:#1e1e2e,stroke:#fab387

    class A,E human
    class B,C ai
    class D,F det
```
