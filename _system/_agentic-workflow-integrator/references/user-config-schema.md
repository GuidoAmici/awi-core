---
affects: awi-user, today
---

# user-config.json — Schema Reference

Each AWI user has a `user-config.json` file at `_data/users/<github-id>/user-config.json`.

This file is **written at user setup/config time** by the user management skill (`/awi-user`).
Everything else reads it and never modifies it.

---

## Schema

```json
{
  "day_start_hour": "00:00:00"
}
```

---

## Fields

### `day_start_hour`

**Type:** string, `HH:MM:SS`
**Required:** no
**Default:** `"00:00:00"`

The time at which a new working day begins. `/today` uses it to resolve the working date: the
calendar date whose `day_start_hour` most recently passed. Someone who habitually works past
midnight sets this to, say, `"06:00:00"`, so a 2am session still files under the previous day.

The working week follows from it too — the week starts Monday at `day_start_hour`.

---

## Removed fields

`awi_upstream_branch` and `collaborator` configured the instance → awi-core mirror. That mirror is
gone: the instance *is* awi-core now, so there is nothing to mirror to. Both fields have no reader
and can be deleted from any config that still carries them. See
[ADR 0007](../../../docs/adr/0007-awi-core-como-source-of-truth.md).
