# AWI Skills — Workflow Diagram

```mermaid
flowchart TD
    subgraph SETUP["🔧 One-Time Setup"]
        A["awi-introduction<br/>Explain AWI, link GitHub,<br/>set prefs, scaffold repo"] --> C["new-client<br/>Add client submodule"]
    end

    subgraph IDENTITY["👤 Identity"]
        D["awi-user<br/>switch, login, create"]
    end

    subgraph DAY["📅 Daily Rhythm"]
        E["today-start<br/>Morning intake"] --> F["today<br/>Hub, view, refresh plan"]
        F --> G["break<br/>Log pause + motive"]
        G --> F
        F --> H["today-end<br/>Close day"]
        H --> I["wrap-session<br/>Observations, save profile"]
    end

    subgraph PLANNING["🗓️ Planning Cadence"]
        J["week<br/>Current batch"] --> K["week-review<br/>Friday re-rank"]
        K --> L["quarter<br/>Quarter view"]
        L --> M["year<br/>Year view"]
    end

    subgraph WORK["⚙️ Work Execution"]
        N["new<br/>Capture task"] --> O["delegate<br/>Background agent"]
        O --> P["history<br/>Audit git activity"]
    end

    subgraph MAINTENANCE["🔄 Maintenance"]
        Q["awi-sync<br/>Sync all submodules"]
        R["awi-layer-index<br/>Audit L0/L1 context files"]
    end

    %% Cross-group flows
    SETUP --> DAY
    IDENTITY -.->|switch user| DAY
    DAY -->|plan work| PLANNING
    PLANNING -->|select tasks| WORK
    WORK -->|end of day| I
    MAINTENANCE -.->|periodic| DAY
```

## Summary

| Phase | Skills | Cadence |
|---|---|---|
| Setup | awi-introduction → new-client | Once |
| Identity | awi-user | As needed |
| Daily | today-start → today → break → today-end → wrap-session | Every day |
| Planning | week → week-review → quarter → year | Fri / monthly |
| Work | new → delegate → history | Continuous |
| Maintenance | awi-sync, awi-layer-index | Periodic |
