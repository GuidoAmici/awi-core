---
name: awi-user-login
description: Load a person's profile for this session. Usage: /awi-user-login <username>. Greets by name, loads preferences and long-term patterns, primes session context.
allowed-tools: Read, Bash, Glob
model: sonnet
---

# /awi-user-login - Load User Profile

Usage: `/awi-user-login <username>`

## User file format

User files live in `_documentation/_context/users/<username>.md`. The **filename is the username**. The file must contain a `person` field linking to a file in `_documentation/_schedule/people/`:

```markdown
---
type: user
person: GuidoAmici
---
```

- `person` — must match a filename (without `.md`) in `_documentation/_schedule/people/`

---

## What to do

### FIRST: check for an argument

Look at the ARGUMENTS value passed to this skill.

- **If ARGUMENTS is empty or blank** — list available users and STOP:
  ```bash
  ls ./_documentation/_context/users/
  ```
  Output filenames without `.md` as the username list:
  ```
  Who is logging in?
  - <username>
  - ...
  ```
  Then wait for the user to reply. Do nothing else until they do.

- **If ARGUMENTS has a value** — proceed with the steps below.

---

### If an argument was given:

1. List available user files:
   ```bash
   ls ./_documentation/_context/users/
   ```

2. Match the argument case-insensitively against filenames (without `.md`). If no match found, show the list and ask who is logging in.

3. Read the matched user file. Extract the `person` frontmatter field.

4. If `person` is missing or blank — stop and warn:
   ```
   User '<username>' has no linked person. Add a `person: <Name>` field to _documentation/_context/users/<username>.md.
   ```

5. Read the linked person's file at `_documentation/_schedule/people/<person>.md` — name, roles, preferences, long-term patterns.

6. Read the most recent user-profile-inference entry for this person (if any):
   ```bash
   ls ./_documentation/_schedule/user-profile-inference/ | sort -r | head -1
   ```

7. Greet by full name and print a brief **session primer**:
   - Their role / relationship context
   - Active preferences (how they like to work)
   - Long-term patterns to watch for (if any)
   - Keep it to 3–5 bullets, no padding

## Output format

```
[Full Name] — [one-line role description].

**Session primer:**
- [preference or pattern]
- ...

To close the session, run `/wrap-session`.
```

Do not ask for confirmation — just load and greet. If anything in the profile seems outdated, mention it briefly.
