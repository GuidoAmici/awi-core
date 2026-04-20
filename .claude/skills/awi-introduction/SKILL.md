---
name: awi-introduction
description: First-time AWI onboarding. Explains what AWI is, links GitHub account, sets preferences, scaffolds the repo, and lands the user in /today. Single command — no follow-up required. Usage: /awi-introduction
---

# /awi-introduction — Get Started with AWI

One command. No prior knowledge needed. Covers everything from "what is this?" to a working setup.

## Usage

```
/awi-introduction
```

---

## Steps

### Step 1 — Cold-start check

Check if `_data/` is already populated:

```bash
ls _data/users/ _data/entities/ 2>/dev/null
```

If both exist and are non-empty, stop and say:
```
AWI is already set up. Nothing to do.
Run /today to get started, or /new-client <name> to add a client.
```

---

### Step 2 — What is AWI?

Always show this first — do not skip, do not make it an option:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AWI — Agentic Workflow Integrator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AWI is a personal operating system you run through Claude.
It keeps your clients, tasks, projects, and notes organized
in plain text files you own and control.
You talk to it like a person — it files, tracks, and reminds.

Setup takes about 60 seconds.

  [1] Let's go
  [2] Tell me more first
```

Wait for reply.

**If [2]:** show this, then re-show the menu:
```
AWI works by organizing everything into two folders:

  _data/entities/   — one folder per client or project
  _system/    — your preferences and framework config

Each client has:
  agenda/         tasks, projects, daily plans
  documentation/  notes, wiki, writing style
  codebase/       app repos (as submodules)

You interact through slash commands like /today, /week, /new-client.
Claude handles the filing. You handle the thinking.
```

---

### Step 3 — GitHub account

Run:
```bash
gh auth status 2>&1
```

**If authenticated:** extract username and show:
```
GitHub account detected: <username>
Use this account? (y/n)
```
- Yes → use detected username
- No → ask: "What GitHub username should AWI use?"

**If not authenticated:**
```
AWI uses GitHub to store and sync your data.

Run this in your terminal:
  gh auth login

Then run /awi-introduction again.
```
Stop here.

---

### Step 4 — Your name

```
What's your name? (first name is fine)
```

Use reply as `<display_name>`. Derive `<username>` from Step 3.

---

### Step 5 — Quick or custom setup

```
Hi <display_name>! Two ways to continue:

  [1] Quick setup    — sensible defaults, done in 30 seconds
  [2] Configure      — I'll walk you through each preference
```

**[1] Quick setup defaults:**
- Language: detect from `$LANG`; fallback English
- Response style: normal
- Session learning: on

Show summary:
```
Your setup:

  GitHub:           <github_username>
  Language:         <language>
  Response style:   Normal
  Session learning: On

Good to go? (y/n)
```
- No → switch to [2] Configure

---

### [2] Configure — Response style

```
STEP 1 OF 3 — Response style

  Normal:   "I've updated the task and linked it to the project."
  Compact:  "Task updated. Linked to project."

  [1] Normal (recommended)
  [2] Compact
```

Store as `response_style`: `normal` or `caveman`.

---

### [2] Configure — Session learning

```
STEP 2 OF 3 — Session learning

As we work together, I notice patterns about how you think and work.
With learning ON, I log these so future sessions feel more tailored.
You can review or delete them anytime.

  [1] On (recommended)
  [2] Off
```

Store as `profile_inference`: `on` or `off`.

---

### [2] Configure — Language

```
STEP 3 OF 3 — Language

  [1] English
  [2] Spanish
  [3] Other (tell me)
```

Store as `language`.

---

### Step 6 — Save profile

Create `_data/users/<username>.md`:

```markdown
---
name: <display_name>
github: <github_username>
language: <language>
response-style: <normal|caveman>
profile-inference: <on|off>
---

# <display_name>

## Preferences

- Language: <language>
- Response style: <normal|caveman>
- Session learning: <on|off>

## Long-term patterns

(none yet)
```

---

### Step 7 — Create GitHub repo + scaffold _data/

Create the user's personal AWI instance repo on GitHub from the source template:

```bash
gh repo create <github_username>/my-awi-instance --template GuidoAmici/awi-core --private --clone
cd my-awi-instance
```

Then initialize `_data/` (the user's private layer — clients, users):

```bash
python3 .claude/skills/awi-introduction/scripts/init_awi.py
```

`_system/` and `.claude/` already exist — they ship with the source. Do not recreate them.

Do not narrate this step — it should feel instant and invisible.

---

### Step 8 — Handoff

```
You're all set, <display_name>.

  /today          — start your day
  /new-client <name>   — add your first client
  /help           — see all commands
```

Then immediately run `/today` so the user lands in a working context.

---

## Logging

At the end — regardless of outcome — log the invocation:

```bash
python3 .claude/skills/shared/scripts/log_command.py awi-introduction <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
