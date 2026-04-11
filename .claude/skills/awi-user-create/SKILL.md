---
name: awi-user-create
description: Create a new AWI vault user and their linked person profile. Usage: /awi-user-create <username>. Runs an interactive session to gather name, interests, and preferences.
allowed-tools: Read, Write, Bash, Glob
model: sonnet
subagent_type: general-purpose
---

# /awi-user-create - Create New User

Usage: `/awi-user-create <username>`

Creates:
- `users/<username>.md` — login identity
- `_documentation/_agenda/people/<FullName>.md` — person profile

---

## Steps

### Step 1 — Get username

Check ARGUMENTS.

- **If ARGUMENTS has a value** — use it as the username. Proceed to Step 2.
- **If ARGUMENTS is empty** — ask:
  ```
  What username would you like?
  ```
  Wait for the reply. Use it as the username. Proceed to Step 2.

---

### Step 2 — Check for conflicts

```bash
ls ./users/
```

If a file named `<username>.md` already exists (case-insensitive), stop and warn:
```
User '<username>' already exists. Use /awi-user-login to log in, or choose a different username.
```

---

### Step 3 — Get full name

Ask:
```
What is <username>'s full name?
```

Wait for the reply. Use it as `<FullName>`. Proceed to Step 4.

---

### Step 4 — Pingpong: interests and preferences

Run a short back-and-forth to learn about the person. Ask **one question at a time**, wait for each answer before asking the next. Cover these topics in order — adapt wording naturally based on prior answers:

1. **Role** — "What is <FullName>'s role or main area of responsibility?"
2. **Working style** — "How does <FullName> prefer to work? (e.g. async vs sync, detail-oriented vs high-level, structured vs flexible)"
3. **Interests** — "What topics or domains is <FullName> most interested in or passionate about?"
4. **Communication** — "Any preferences on how Claude should communicate with <FullName>? (e.g. tone, response length, language)"

After the 4th answer, do NOT ask more questions. Proceed to Step 5.

---

### Step 5 — Create files

**Check if the person file already exists:**
```bash
ls ./_documentation/_agenda/people/
```

If `<FullName>.md` (CamelCase, no spaces) already exists, skip creating the person file and note it.

**Create user file** at `users/<username>.md`:

```markdown
---
type: user
person: <FullNameCamelCase>
---
```

**Create person file** at `_documentation/_agenda/people/<FullNameCamelCase>.md`:

Use the gathered answers to populate the profile. Derive `tags` from their role and interests (lowercase, hyphenated). Keep each section concise.

```markdown
---
type: person
tags: [<tag1>, <tag2>]
last-updated: <YYYY-MM-DD>
---

# <Full Name>

<One-line description: role or main area of work.>

## Roles

- <derived from role answer>

## Preferences

- (<YYYY-MM-DD>) <derived from working style and communication answers>

## Long-term patterns

<!-- Behavioral patterns that have repeated across multiple sessions and are considered stable. Graduated from user-profile-inference. -->
```

---

### Step 6 — Confirm

Output:
```
✓ User '<username>' created and linked to <Full Name>.

Files created:
- users/<username>.md
- _documentation/_agenda/people/<FullNameCamelCase>.md

Run /awi-user-login <username> to start a session.
```
