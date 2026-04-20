# AWI Taxonomy

- **Entity** — a company or personal context (maps to `_data/organizations/<name>/`)
- **Product** — user-facing offering, may span multiple apps
- **App** — deployable codebase with its own repo (`codebase/`)
- **Project** — time-bound initiative with scope and tasks
- **Module** — component within an app
- **Feature** — specific capability added to an app
- **Task** — single actionable item

**Rule:** every project and task MUST reference the workspace (and product/app if applicable) it belongs to via tags or `[[links]]` in the body.
