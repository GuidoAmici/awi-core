---
name: awi-org-toggle
description: Toggle an AWI org submodule on or off. Updates persistent state in the user's active-orgs.json and syncs the git submodule. Usage: /awi-org-toggle <org-name>
---

# /awi-org-toggle — Toggle Org

Toggle an org submodule on or off. State is persisted per-user in
`_data/users/<github-id>/active-orgs.json`. Orgs toggled on are initialized
by `/awi-initialize`.

## Usage

```
/awi-org-toggle <org-name>
```

---

## Steps

### Step 1 — Get org name

Check ARGUMENTS.

- **If ARGUMENTS has a value** — use it as `<name>`. Proceed to Step 2.
- **If ARGUMENTS is empty** — show current state first:
  ```bash
  python3 .claude/skills/awi-org-toggle/scripts/toggle_org.py status
  ```
  Then ask: `Which org do you want to toggle?`

---

### Step 2 — Show current state

Run:
```bash
python3 .claude/skills/awi-org-toggle/scripts/toggle_org.py status
```

Find `<name>` in the output. If the org is not listed and not in `.gitmodules`, ask:
```
'<name>' is not registered yet. What is its GitHub URL?
(e.g. https://github.com/GuidoAmici/<name>)
```

Store as `<url>` (use empty string if operator skips — submodule add will be deferred to /awi-initialize).

Show what will happen:
```
<name> is currently ON → will be toggled OFF
```
or:
```
<name> is currently OFF → will be toggled ON
```

Ask: `Confirm? (y/n)`

---

### Step 3 — Toggle

On confirm:

```bash
python3 .claude/skills/awi-org-toggle/scripts/toggle_org.py toggle <name> [--url <url>]
```

Output the result:
```
<name> is now ON.   (submodule initialized)
```
or:
```
<name> is now OFF.  (submodule deinitialized, registration kept)
```

---

## Logging

```bash
python3 .claude/skills/shared/scripts/log_command.py awi-org-toggle <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
