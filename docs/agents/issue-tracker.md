# Issue tracker: GitHub (multi-repo)

Issues live in GitHub Issues, distributed by scope. Use the `gh` CLI for all operations. Always pass `--repo` explicitly.

## Where issues live

| Scope | Repo | When to use |
|-------|------|-------------|
| Codebase-specific | e.g. `GuidoAmici/newhaze-b2b-panel` | Work scoped entirely to one codebase |
| Org-level | `GuidoAmici/newhaze-workspace`, `GuidoAmici/afin-workspace`, `GuidoAmici/rabbitek-workspace` | Work spanning multiple codebases within one org |
| Cross-org | `GuidoAmici/my-awi-user` | Work touching multiple orgs, or personal/meta work |

## Label schema

| Dimension | Examples |
|-----------|---------|
| Org | `org:newhaze`, `org:afin`, `org:rabbitek` |
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

Determine scope first:

1. One codebase → issue in that codebase repo, labeled `org:<org>` + `repo:<codebase>`
2. One org, multiple codebases → issue in that org's workspace repo, labeled `org:<org>`
3. Multiple orgs → issue in `GuidoAmici/my-awi-user`

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --repo <owner/repo> --comments`. Infer the repo from context — label, project, or codebase being worked on.

## Migration note

`agenda/tasks/` files are retired. Do not create new files there. Actionable work goes to GitHub Issues.
`agenda/projects/` files are kept — they are context/scope documents, not issue lists.
