# Migrating from a legacy `my-awi-instance`

For instances that still live in their own repo (`<user>/my-awi-instance`) and mirror changes into `awi-core`. [ADR 0007](adr/0007-awi-core-como-source-of-truth.md) made awi-core the source of truth, so the instance stops being a separate repo and becomes a working checkout of awi-core.

Nothing here is urgent — a legacy instance keeps working. Migrate when you want the harness to stop drifting from awi-core.

---

## What changes

| | Before | After |
|---|---|---|
| `origin` | `<user>/my-awi-instance` | `<user or fork>/awi-core` |
| Where harness changes are made | in the instance, mirrored to core | directly in awi-core |
| `_data/` | versioned in the instance | ignored, never leaves the machine |
| `.gitmodules` | versioned | ignored — generated per operator |
| Submodule gitlinks | versioned | none |

Your history is not lost: `my-awi-instance` stays on GitHub untouched. You stop *using* it, you don't delete it.

---

## Before you start

**1. Confirm every repo is pushed.** The migration replaces the local branch's history; anything unpushed is gone.

```bash
git rev-list --left-right --count origin/only...only     # expect "0	0"
```

Do the same inside each repo under `_data/` — they are separate repos and are **not** covered by the check above:

```bash
for m in _data/organizations/*/ _data/users/*/; do
  echo "== $m"; git -C "$m" status --short
  git -C "$m" rev-list --count HEAD --not --remotes    # expect 0
done
```

**2. Check nested codebases too.** A repo under `codebase/` can sit on a local branch whose HEAD exists nowhere remote:

```bash
for c in _data/organizations/*/codebase/*/; do
  printf "%-40s %s " "$c" "$(git -C "$c" rev-parse --abbrev-ref HEAD)"
  git -C "$c" rev-list --count HEAD --not --remotes
done
```

Any non-zero count is work that exists only on this machine. Push it to a branch before continuing.

---

## Migration

### 1. Keep a way back

```bash
git branch backup/my-awi-instance only
git remote rename origin instance
git remote add origin https://github.com/<user>/awi-core.git
git fetch origin
```

`instance` still points at the old repo, and `backup/my-awi-instance` pins the old history locally. Reverting is `git checkout only`.

### 2. Unstage `_data/` gitlinks before switching

Submodule gitlinks must leave the index first, or the checkout tries to resolve them:

```bash
git rm --cached -r --quiet _data/organizations/* _data/users/*
```

`git rm --cached` on a gitlink leaves the directory on disk. Nothing is deleted.

### 3. Save the regular files under `_data/`

**This is the step that bites.** Gitlinks survive step 2, but *regular tracked files* under `_data/` — `current-user.json`, `.abstract.md`, `.overview.md` — do not exist on the awi-core branch, so checkout **deletes them from disk**. Without `current-user.json`, `.gitmodules` generation fails outright.

List them now:

```bash
git ls-tree -r only --name-only -- _data | grep -v -E '/(organizations|users)/[^/]+$'
```

### 4. Switch to awi-core

```bash
git checkout -B dev origin/dev
```

If it refuses because of untracked files that also exist on the target branch, compare them first — if identical, remove the local copies and retry:

```bash
git diff --no-index <file> <(git show origin/dev:<file>)
```

### 5. Restore what step 3 listed

```bash
for f in $(git ls-tree -r only --name-only -- _data | grep -v -E '/(organizations|users)/[^/]+$'); do
  git show only:"$f" > "$f"
done
cat _data/users/current-user.json    # must show your identity
```

The old history is still local on `only`, which is why this works. Do it before running any skill.

### 6. Verify

```bash
git status --short          # only intended changes; _data/ untracked
git ls-files _data          # empty
ls _data/organizations      # your orgs, still on disk
```

---

## Cleaning up legacy machinery

These exist only in legacy instances. Removing them is what awi-core commits `142ccf5`, `b5af8df` and `ab13552` did.

**The mirror.** Delete `.claude/skills/awi-core-sync-status/`, `.claude/hooks/sync-public.sh`, `.claude/config/public-repo-path` and any `public-whitelist`. Keep `.claude/skills/shared/scripts/sync_status.py` — `/awi-sync` imports from it.

**auto-commit.** Delete `.claude/hooks/auto-commit.{sh,ps1}`. [ADR 0005](adr/0005-solution-package-commit-model.md) replaced per-file auto-commit long ago. Then grep for instructions that still assume it:

```bash
grep -rn "auto-commits after\|do NOT commit manually" .claude/ _system/
```

Those tell an agent **not to commit**, waiting on a hook that never runs — the usual cause of work sitting uncommitted for days. Check `.gemini/settings.json` too: it may register an `AfterTool` hook pointing at a `scripts/auto-commit.py` that does not exist.

**The boundary.** Add to `.gitignore`:

```gitignore
_data/
.gitmodules
_system/agency-agents/
```

Then drop the versioned gitlinks, including the one under `_system/`:

```bash
git rm --cached .gitmodules _system/agency-agents
```

A gitlink whose URL lives only in an ignored `.gitmodules` is an orphan pointer: a fresh clone fails with `fatal: No url found for submodule path`. Either both are versioned or neither is — see [ADR 0001](adr/0001-gitmodules-is-ephemeral.md).

---

## Afterwards

`.gitmodules` is regenerated from `_data/users/<github-id>/user-submodules.json` by `/awi-initialize`, so submodules keep working without being versioned. `/awi-core-sync-status` is gone: there is nothing to compare, the instance no longer originates changes.

Harness changes now go straight to awi-core through its normal branch flow. Your `_data/` repos keep their own remotes and are still operated by `/awi-sync`.
