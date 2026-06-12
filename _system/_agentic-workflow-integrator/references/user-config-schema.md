---
affects: awi-user, awi-initialize, awi-sync
---

# user-config.json — Schema Reference

Each AWI user has a `user-config.json` file at `_data/users/<github-id>/user-config.json`.

This file is **written at user setup/config time** by the user management skill (`/awi-user`).
It is **read but never modified** by `/awi-initialize` and `/awi-sync`.

---

## Schema

```json
{
  "awi_upstream_branch": "dev",
  "collaborator": false
}
```

---

## Fields

### `awi_upstream_branch`

**Type:** string  
**Required:** no  
**Default:** `"dev"` (if absent, scripts fall back to this value)

The awi-core branch this instance tracks for upstream pulls.

Valid values depend on which branches awi-core maintains:

| Value | Meaning |
|---|---|
| `prod` | Stable release branch |
| `stg` | Staging / pre-release |
| `dev` | Active development branch |

Set by the user management skill when configuring a new user or changing upstream tracking.

---

### `collaborator`

**Type:** boolean  
**Required:** no  
**Default:** `false` (if absent, treated as non-collaborator)

Whether this user has write access to `awi-core`.

Controls push behavior in `/awi-sync`:

| Value | Behavior |
|---|---|
| absent or `false` | Skip push to awi-core silently |
| `true` (permission confirmed) | Push to `awi_upstream_branch` on awi-core |
| `true` (permission denied) | Warning: collaborator flag set but write access unconfirmed |

Set by the user management skill, never by `/awi-initialize`.

---

## Full Example

```json
{
  "awi_upstream_branch": "dev",
  "collaborator": false
}
```

Collaborator with custom branch:

```json
{
  "awi_upstream_branch": "dev",
  "collaborator": true
}
```
