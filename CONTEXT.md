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

### Submodule management

**user-submodules.json**:
A file in `_data/users/<github-id>/` that lists every git submodule the user wants registered — both org workspaces and system repos. Single source of truth for `.gitmodules` generation.
_Avoid_: active-orgs.json (deprecated), submodule config

**Ephemeral `.gitmodules`**:
The `.gitmodules` file is a local artifact generated from `user-submodules.json` on initialize, user switch, and logout. It is never committed and never mirrored to `awi-core`.
_Avoid_: do not treat as a committed config file

**Org Workspace**:
A submodule mounted under `_data/organizations/<name>/` representing one organization's workspace repo.
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

- `active-orgs.json` was used to mean what is now **user-submodules.json** — resolved: renamed and expanded to cover system repos alongside orgs.
- `workspace_repo` field in the old schema conflicted with `url` expected by `init_orgs.py` — resolved: unified to `url` in the new schema.
- "toggle" was used for both org-specific and system-repo operations — resolved: `/awi-org-toggle` deprecated in favour of `/awi-submodule-toggle`, which handles all entry types uniformly.
