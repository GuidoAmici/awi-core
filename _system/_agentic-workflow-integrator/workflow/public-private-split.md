---
kind: workflow
---

# Public / Private Split

How private instance data is kept out of the public, forkable `awi-core` repo.

---

## The model

There is **one canonical repo**: `awi-core`, and it is public. An AWI instance is a working checkout of it — not a fork that mirrors changes back. See [ADR 0007](../../../docs/adr/0007-awi-core-como-source-of-truth.md).

| Lives in `awi-core` (public) | Lives outside it (private) |
|---|---|
| Skills (`.claude/skills/`) | `_data/` — every user profile and org workspace |
| Hooks (`.claude/hooks/`) | `.gitmodules` — generated per operator |
| System docs (`_system/`) | Anything naming a client or containing their data |
| Root docs (`CLAUDE.md`, `INSTRUCTIONS.md`, ADRs) | |

**Rule of thumb:** if the file would need editing before another operator could use it, it is private.

---

## How the boundary is enforced

By `.gitignore` — not by a sync script, and not by merge strategy:

```gitignore
_data/                      # every instance's private data
.gitmodules                 # generated from user-submodules.json
_system/agency-agents/      # materialised by /awi-initialize
```

Ignoring beats mirroring because there is nothing to keep in step: the private paths never enter the index, so they cannot leak through an accidental `git add -A`.

**No gitlinks are versioned in awi-core.** A gitlink whose URL lives only in an ignored `.gitmodules` is an orphan pointer — a fresh clone fails with `fatal: No url found for submodule path`. Submodules are materialised from `user-submodules.json` instead. See [ADR 0001](../../../docs/adr/0001-gitmodules-is-ephemeral.md).

---

## Where private data actually lives

Each org workspace and each user profile is its **own git repo**, cloned inside `_data/` but invisible to `awi-core`:

| Path | Repo |
|---|---|
| `_data/users/<github-id>/` | the operator's `my-awi-user` |
| `_data/organizations/<name>/` | that org's `<name>-workspace` |

They are declared in `_data/users/<github-id>/user-submodules.json` and operated by `/awi-sync`. Because awi-core versions no gitlink for them, they are ordinary nested repos as far as it is concerned.

---

## Setup for a new operator

1. Fork or clone `awi-core`
2. Run `/awi-introduction` — links the GitHub account and creates the `my-awi-user` repo
3. Run `/awi-initialize` — generates `.gitmodules` from `user-submodules.json` and clones each active submodule

No sync path to configure: there is no second repo to mirror to.

---

## If private data reaches awi-core

Remove it from the tree, add the path to `.gitignore`, and promote through `dev` → `stg` → `prod` so the public default branch stops serving it.

Note that **rewriting history does not reliably erase it**: GitHub keeps unreferenced objects addressable by SHA until it garbage-collects, which requires asking Support. Treat anything already pushed as disclosed, and weigh whether rotating the exposed resource beats rewriting the history.
