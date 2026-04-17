# awi-user-login

Load person profile for the session. Greets by name, primes context from preferences and patterns.

**Tools:** Read, Bash, Glob

> Node shapes and colors: see [_legend.md](_legend.md)

## Flow

```mermaid
graph TD
    A(["/awi-user-login username"]) --> B{username in args?}
    B -->|no| C[["ls _system/users/ → list users"]]
    C --> Z["STOP — ask who is logging in"]
    B -->|yes| D[["Match against _system/users/"]]
    D -->|no match| Z
    D -->|match| E[[Read user file → extract person field]]
    E -->|no person field| F["STOP — warn: add person field"]
    E -->|has person| G[["Read _agenda/people/FullName.md"]]
    G --> H[[Read latest user-profile-inference entry]]
    H --> I[/Greet + session primer 3–5 bullets/]
    I --> J((log_command.py awi-user-login))

    classDef entry  fill:#89b4fa,color:#1e1e2e,stroke:#89b4fa
    classDef ai     fill:#cba6f7,color:#1e1e2e,stroke:#cba6f7
    classDef read   fill:#94e2d5,color:#1e1e2e,stroke:#94e2d5
    classDef write  fill:#a6e3a1,color:#1e1e2e,stroke:#a6e3a1
    classDef shell  fill:#f9e2af,color:#1e1e2e,stroke:#f9e2af
    classDef user   fill:#fab387,color:#1e1e2e,stroke:#fab387
    classDef stop   fill:#f38ba8,color:#1e1e2e,stroke:#f38ba8
    classDef log    fill:#45475a,color:#cdd6f4,stroke:#45475a

    class A entry
    class B,D ai
    class C,E,G,H read
    class F,Z stop
    class I user
    class J log
```
