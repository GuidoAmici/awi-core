# AWI Skills — Workflow Diagram

<!-- AUTO-GENERATED — edit `_workflow-config.json` and skill frontmatter, not this file -->

```mermaid
flowchart TD
    subgraph SETUP["🔧 One-Time Setup"]
        awi_introduction["awi-introduction<br/>Explain AWI, link GitHub, set prefs"]
        new_client["new-client<br/>Add client submodule"]
        awi_introduction --> new_client
    end

    subgraph IDENTITY["👤 Identity"]
        awi_user_login["awi-user-login<br/>Load session user"]
        awi_user_create["awi-user-create<br/>Create new vault user"]
    end

    subgraph DAY["📅 Daily Rhythm"]
        today_start["today-start<br/>Morning intake"]
        today["today<br/>Hub, view, refresh plan"]
        break["break<br/>Log pause + motive"]
        today_end["today-end<br/>Close day"]
        wrap_session["wrap-session<br/>Observations, save profile"]
        today_start --> today
        today --> break
        break --> today_end
        today_end --> wrap_session
        break --> today
    end

    subgraph PLANNING["🗓️ Planning Cadence"]
        week["week<br/>Current batch"]
        week_review["week-review<br/>Friday re-rank"]
        quarter["quarter<br/>Quarter view"]
        year["year<br/>Year view"]
        week --> week_review
        week_review --> quarter
        quarter --> year
    end

    subgraph WORK["⚙️ Work Execution"]
        new["new<br/>Capture task"]
        delegate["delegate<br/>Background agent"]
        history["history<br/>Audit git activity"]
        new --> delegate
        delegate --> history
    end

    subgraph MAINTENANCE["🔄 Maintenance"]
        awi_sync["awi-sync<br/>Sync all submodules"]
    end

    %% Cross-group flows
    SETUP --> DAY
    IDENTITY -.->|switch user| DAY
    DAY -->|plan work| PLANNING
    PLANNING -->|select tasks| WORK
    WORK -->|end of day| wrap_session
    MAINTENANCE -.->|periodic| DAY
```

## Summary

| Phase | Skills | Cadence |
|---|---|---|
| Setup | awi-introduction → new-client | Once |
| Identity | awi-user-login, awi-user-create | As needed |
| Daily | today-start → today → break → today-end → wrap-session | Every day |
| Planning | week → week-review → quarter → year | Fri / monthly |
| Work | new → delegate → history | Continuous |
| Maintenance | awi-sync | Periodic |
