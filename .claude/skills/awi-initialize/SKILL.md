---
name: awi-initialize
description: Initialize all org submodules that are toggled on in the user's active-orgs.json. Registers any unregistered orgs in .gitmodules then runs git submodule update --init. Usage: /awi-initialize
---

# /awi-initialize — Initialize Orgs

Reads the current user's `active-orgs.json` and initializes every org
marked `active: true`. If an org is not yet registered in `.gitmodules`,
it is added first using the stored URL.

Run this after a fresh clone, after switching users, or after toggling orgs on.

## Usage

```
/awi-initialize
```

---

## Steps

### Step 1 — Run init script

```bash
python3 .claude/skills/awi-initialize/scripts/init_orgs.py
```

Check the **exit code** and respond accordingly:

---

### Exit 0 — Success

Show the script output directly. No additional narration needed.

---

### Exit 1 — Hard error

Show the script output. Log as `errored`.

---

### Exit 2 — No orgs active, but inactive ones exist

The script prints `INACTIVE: <name>, <name>, ...`

Show the inactive list and ask:

```
No orgs are toggled on. These are currently off:
  - <name>
  - <name>

Which would you like to toggle on? (list names, or n to skip)
```

- **If names given** → for each name:
  ```bash
  python3 .claude/skills/awi-org-toggle/scripts/toggle_org.py on <name>
  ```
  Then re-run `init_orgs.py` from Step 1.

- **If n / skip** → log as `skipped`, done.

---

### Exit 3 — No orgs registered at all

Ask:

```
No orgs registered. Would you like to:
  1. Create a new org
  2. Import an existing one from GitHub
```

- **1 or 2** → hand off to `/awi-client` (handles both modes).
- **Neither** → log as `skipped`, done.

---

## Logging

```bash
python3 .claude/skills/shared/scripts/log_command.py awi-initialize <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
