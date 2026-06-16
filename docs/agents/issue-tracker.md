# Issue tracker: GitHub (multi-repo)

Issues live in GitHub Issues, distributed by scope. Use the `gh` CLI for all operations. Always pass `--repo` explicitly.

## Where issues live

Issues live only in org workspace repos, the AWI core repo, or the personal repo. **Never in codebase repos** (e.g. `newhaze-b2b-panel`). Use `repo:` labels to identify which codebase an issue belongs to.

| Scope | Repo | When to use |
|-------|------|-------------|
| One codebase or one org | `GuidoAmici/newhaze-workspace`, `GuidoAmici/afin-workspace`, `GuidoAmici/rabbitek-workspace` | Work scoped to one org, regardless of how many codebases it touches. Label with `repo:<codebase>` when codebase-specific. |
| AWI harness | `GuidoAmici/awi-core` | Changes to the AWI system itself: skills, INSTRUCTIONS.md, hooks, documentation standards, agent behavior. |
| Personal | `GuidoAmici/my-awi-user` | Strictly personal work (agenda, goals, personal projects). Never for harness or cross-org work. |

When an issue touches codebases across multiple orgs, ask the maintainer which org workspace to file it in before creating it.

## Label schema

| Dimension | Examples |
|-----------|---------|
| Org | `org:newhaze`, `org:afin`, `org:rabbitek` — applied to every issue regardless of repo. Enables cross-repo filtering and local (off-GitHub) issue management by org. |
| Codebase | `repo:newhaze-b2b-panel`, `repo:newhaze-api`, `repo:newhaze-ui` |
| Project | `project:ci-cd-pipeline`, `project:sso` (matches `agenda/projects/*.md` slug) |
| Triage | see `docs/agents/triage-labels.md` |

Apply multiple labels when an issue spans repos or projects.

## Milestones

One GitHub Milestone per AWI project (`agenda/projects/*.md`). Create in the relevant org workspace repo. Slug matches the project filename (e.g. `ci-cd-pipeline`).

## Conventions

- **Create**: `gh issue create --repo <owner/repo> --title "..." --body "..."`
- **Read**: `gh issue view <number> --repo <owner/repo> --comments`
- **List**: `gh issue list --repo <owner/repo> --state open --json number,title,body,labels --label "..."`
- **Label**: `gh issue edit <number> --repo <owner/repo> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --repo <owner/repo> --comment "..."`

## When a skill says "publish to the issue tracker"

Always ask the maintainer where to file before creating an issue. Suggest a destination based on scope:

1. One codebase → suggest that codebase's **org workspace repo**, labeled `repo:<codebase>`
2. One org, multiple codebases → suggest that org's workspace repo
3. AWI harness change (skill, hook, INSTRUCTIONS.md, doc standard) → `GuidoAmici/awi-core`
4. Personal → `GuidoAmici/my-awi-user`

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --repo <owner/repo> --comments`. Infer the repo from context — label, project, or codebase being worked on.

## Migration note

`agenda/tasks/` files are retired. Do not create new files there. Actionable work goes to GitHub Issues.
`agenda/projects/` files are kept — they are context/scope documents, not issue lists.
