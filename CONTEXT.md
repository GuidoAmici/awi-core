# Agentic Workflow Integrator (AWI)

A system that scaffolds and manages per-user, per-org workspaces as git submodules, driven by a user identity resolved from the GitHub CLI auth state.

## Language

### Identity

**AWI User**:
A person operating an AWI instance, identified by their GitHub numeric ID.
_Avoid_: account, operator, login

**Current User**:
The AWI user whose workspace is active in this instance, recorded in `_data/users/current-user.json`.
_Avoid_: logged-in user, active account

**GitHub Auth State**:
The GitHub CLI's currently authenticated account (`gh auth status`). AWI treats this as the source of truth for identity.
_Avoid_: gh session, CLI user

### AWI Core sync

**Mirror** _(instancia → awi-core)_:
Operación de escritura hacia awi-core: copia los archivos fuente de la instancia (todo fuera de `_data/`) al repo awi-core local, commitea y pushea. Solo disponible para colaboradores (`collaborator: true` en `user-config.json`). Herramienta de transición — se elimina cuando haya múltiples devs trabajando directamente en awi-core.
_Avoid_: push, upload, sync-up

**Pull** _(awi-core → instancia)_:
Operación de lectura desde awi-core: copia los archivos fuente del submodulo awi-core local (ya actualizado por `sync_all`) hacia la instancia. Disponible para todos los usuarios. Corre siempre como parte de `/awi-sync`, después de que el submodulo awi-core fue pullado.
_Avoid_: download, sync-down, update

### Submodule management

**user-submodules.json**:
A file in `_data/users/<github-id>/` that lists every git submodule the user wants registered — both org workspaces and system repos. Single source of truth for `.gitmodules` generation.
_Avoid_: active-orgs.json (deprecated), submodule config

**Ephemeral `.gitmodules`**:
The `.gitmodules` file is a local artifact generated from `user-submodules.json` on initialize, user switch, and logout. It is never committed and never mirrored to `awi-core`.
_Avoid_: do not treat as a committed config file

**Org Workspace**:
A submodule mounted under `_data/organizations/<name>/` representing one organization's workspace repo. Identified in `user-submodules.json` by `"type": "org-workspace"`. Its GitHub issue tracker is the source of truth for org-scoped work.
_Avoid_: entity, client repo

**System Repo**:
A submodule mounted under `_system/<name>/` providing shared framework content (e.g. agent libraries). May be marked `upstream: true` to skip pushing.
_Avoid_: workframe, framework submodule

**Upstream**:
A submodule flag (`upstream: true`) indicating the repo is read-only — AWI pulls from it but never pushes.
_Avoid_: read-only submodule, external dep

### Lifecycle

**Initialize**:
The act of reading `user-submodules.json` and running `git submodule update --init` for all active entries, regenerating `.gitmodules` in the process.
_Avoid_: setup, bootstrap

**Deinit**:
Deactivating a submodule: commit+push any local changes, run `git submodule deinit`, remove its entry from the regenerated `.gitmodules`. The folder is emptied but not deleted.
_Avoid_: remove, unlink, delete

**User Switch**:
Changing the Current User — triggered by `gh auth switch`. Requires a PreToolUse commit+push guard; followed by PostToolUse reconfiguration (update `current-user.json`, regenerate `.gitmodules`, init/deinit submodules).
_Avoid_: login swap, account change

### Session & package flow

**Solution Package**:
A discrete unit of work scoped to one GitHub issue, committed as a single semver-bumped commit on a dedicated branch, then merged and branch-deleted. The atomic unit of delivery in AWI.
_Avoid_: feature branch, task commit, session commit

**Current**:
The one active Solution Package being worked on in a session. Has a live branch. Only one Current at a time per AWI instance.
_Avoid_: active task, in-progress issue

**Next**:
The designated next issue to become Current. No branch exists yet — the branch is created only when work starts. Exactly one Next at any time (the queue head).
_Avoid_: upcoming task, queued issue

**Queue**:
The ordered list of issues after Next. New issues created mid-session join the Queue and may bump Next, incrementing Next's deferral count.
_Avoid_: backlog, task list

**Deferral**:
The act of bumping Next in favour of a different issue. Each deferral increments the deferred issue's deferral count.
_Avoid_: postpone, skip, push back

**Deferral Count**:
A per-issue counter tracking how many times that issue has been deferred as Next. Persisted across sessions. Resets to zero when the issue becomes Current.
_Avoid_: skip count, delay count

**Deferral Threshold**:
The configurable maximum deferral count before the harness escalates. When an issue's deferral count reaches the threshold, the harness files a Deferral Alert. Configured in `user-config.json` in the user folder. Default: 3.
_Avoid_: max deferrals, limit

**user-config.json**:
A per-user preferences file at `_data/users/<github-id>/user-config.json`. Travels with the user across AWI instances via the `my-awi-user` submodule. Contains working-style settings (e.g. `deferral_threshold`). Uses `_comment` keys to document each field.
_Avoid_: user settings, user preferences file

**Deferral Alert**:
A GitHub issue filed automatically by the harness when a Deferral Threshold is reached. Contains the deferred issue reference, deferral count, and a prompt to assess one of three root causes: deviation, friction, or misalignment.
_Avoid_: escalation ticket, flag

**Deviation**:
A Deferral Alert root cause. The user is consistently choosing work outside the agreed plan — the plan may need updating.
_Avoid_: distraction, scope creep

**Friction**:
A Deferral Alert root cause. Something is blocking the issue — technical, personal, or dependency-related. Needs surfacing and resolution.
_Avoid_: blocker, impediment

**Misalignment**:
A Deferral Alert root cause. The issue no longer reflects actual strategic priority — plan and strategy have drifted apart.
_Avoid_: priority drift, stale plan

### Agent delegation

**Employee**:
A named agent persona defined in `.claude/reference/employees.json`, with a `path` to its system prompt file and a `tagline` used for routing.
_Avoid_: agent, worker, bot

**Agent Brief**:
A structured GitHub issue comment posted by `/triage` when an issue moves to `ready-for-agent`. The authoritative specification a background agent works from. Must include `Assigned employee` and `Model`.
_Avoid_: task spec, issue body, briefing

**Grilled Issue**:
An issue that has completed a `/grill-with-docs` session, has an employee assigned in its agent brief, and carries the `ready-for-agent` label. The only issues eligible for background delegation.
_Avoid_: triaged issue, ready issue

**Dispatch**:
The act of selecting grilled issues and firing a background delegate per issue via `/delegate-issue`. Always confirm-before-fire.
_Avoid_: deploy, run, execute

**Grill Panel**:
The three-agent panel that conducts the mandatory grill session: `nexus-strategy` (strategic alignment) → `reality-checker` (priority, effort, employee assignment) → `assigned-employee` (quality specs). Sequential-with-interrupts; each agent labels every message.
_Avoid_: review committee, agents session

**Panel Interrupt**:
An out-of-phase interjection by a later-phase agent, fired autonomously when a blocker is detected (scope explosion, technical impossibility, wildly wrong effort estimate). Always labeled. Not used for commentary.
_Avoid_: cross-talk, sidebar

**Context Issue**:
A GitHub issue filed by `nexus-strategy` when a grilled issue is deemed strategically unrelated. Contains origin, affected party, and future relevance trigger — captured in exactly 3 questions. Labeled `needs-context`. Ends the grill session.
_Avoid_: parking lot issue, backlog ticket

### Professional Strategy

**Professional Identity**:
The AWI User's personal Mission, Vision, and Values as a professional. Private to the user. Lives at `_data/users/<github-id>/documentation/professional-identity.md`. The source of truth for understanding *why* the user engages with any organization.
_Avoid_: personal strategy, user philosophy, user profile

**Org Profile**:
A standardized document in each Org Workspace containing the organization's Mission, Vision, and Values. Lives at `_data/organizations/<name>/documentation/org-profile.md`. Source of truth for the org's strategic identity.
_Avoid_: business profile, org strategy, org context

**Org Engagement**:
A private per-org document in the user's space that captures the strategic intersection between the user's Professional Identity and the org's Org Profile — where they align, where they friction, and how to advance. Lives at `_data/users/<github-id>/org-engagement/<org-name>.md`. Generated automatically when an org is incorporated (`/awi-org`) and reviewed in periodic rituals (`/today`, `/week`, `/quarter`, `/year`).
_Avoid_: user-org relationship, engagement charter, personal charter

## Relationships

- A **Current User** is resolved from **GitHub Auth State** via `current-user.json`
- **user-submodules.json** drives **Ephemeral `.gitmodules`** generation — one-way, always overwritten
- An **Org Workspace** and a **System Repo** are both entries in **user-submodules.json**, differing only in `path` and optionally `upstream`
- A **User Switch** always triggers **Initialize**
- **Deinit** is the inverse of **Initialize** for a single entry

## Example dialogue

> **Dev:** "When Chris switches gh accounts, how does AWI know which orgs to mount?"
> **Domain expert:** "AWI reads the new GitHub Auth State, resolves the AWI User from it, loads their user-submodules.json, and runs Initialize — which regenerates .gitmodules and inits/deinits accordingly."

> **Dev:** "Should I commit .gitmodules after adding a new org?"
> **Domain expert:** "No — .gitmodules is Ephemeral. Add the org to user-submodules.json and re-run Initialize. The file regenerates itself."

## Flagged ambiguities

- `active-orgs.json` was used to mean what is now **user-submodules.json** — resolved: renamed and expanded to cover system repos alongside orgs. `active-orgs.json` is pending deletion; all reads must migrate to `user-submodules.json`.
- `workspace_repo` field in the old schema conflicted with `url` expected by `init_orgs.py` — resolved: unified to `url` in the new schema. `workspace_repo` is derived from `url` at runtime, never stored.
- "toggle" was used for both org-specific and system-repo operations — resolved: `/awi-org-toggle` deprecated in favour of `/awi-submodule-toggle`, which handles all entry types uniformly.
- "cross-org issues" (issues in the user repo carrying `org:` labels) — resolved: concept eliminated. The user repo holds personal issues only; org-scoped issues live exclusively in each Org Workspace's issue tracker. All `org:`-label filtering logic in issue-fetching scripts must be removed.
