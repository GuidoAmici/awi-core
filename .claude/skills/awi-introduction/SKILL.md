---
name: awi-introduction
description: Beginner-friendly first-time AWI onboarding. Links GitHub account, sets language, response style, and session learning preferences. Creates user profile. Recommends /awi-initialize next. Usage: /awi-introduction
---

# /awi-introduction — Welcome to AWI

First-time setup. No prior knowledge needed.

## Usage

```
/awi-introduction
```

---

## Steps

### Step 1 — Welcome screen

Display:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Welcome to AWI
  Your personal command center for
  managing clients, tasks, and projects
  through conversation.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [1] Quick setup    — sensible defaults, done in 60 seconds
  [2] Configure      — I'll explain each setting before you choose
  [3] What is AWI?   — plain English overview
```

Wait for reply.

---

### [3] What is AWI?

If user picks 3, display:

```
AWI is a personal operating system you run through Claude.
It keeps your clients, tasks, projects, and notes organized
in plain text files you own and control.
You talk to it like a person — it files, tracks, and reminds.

Ready to get started?

  [1] Quick setup
  [2] Configure
```

Wait for reply, then continue.

---

### Step 2 — GitHub account

Run:
```bash
gh auth status 2>&1
```

**If authenticated:** extract the GitHub username and show:
```
GitHub account detected: <username>
Is this the account you want to use with AWI? (y/n)
```
- Yes → use detected username
- No → ask: "What GitHub username should AWI use?"

**If not authenticated:**
```
AWI uses GitHub to store and sync your data.

To link your account, run this command in your terminal:
  gh auth login

Then run /awi-introduction again.
```
Stop here.

---

### Step 3 — Your name

Ask:
```
What's your name? (first name is fine)
```

Use the reply as `<display_name>`. Derive `<username>` as the GitHub username from Step 2.

---

### [1] Quick setup

Skip Steps 4–6. Use defaults:
- Language: detect from `$LANG` env var; default to English
- Response style: normal
- Session learning: on

Show summary:
```
Here's your setup, <display_name>:

  GitHub:           <github_username>
  Language:         <language>
  Response style:   Normal
  Session learning: On (I'll notice patterns to help you better)

Looks good? (y/n)
```

- Yes → proceed to Step 7
- No → switch to [2] Configure flow

---

### [2] Configure — Step 4: Response style

```
STEP 1 OF 3 — Response style

By default I write full sentences. Caveman mode cuts that
down to compressed fragments — same information, fewer words.

  Normal:   "I've updated the task and linked it to the project."
  Compact:  "Task updated. Linked to project."

Which do you prefer?
  [1] Normal (recommended)
  [2] Compact (caveman mode)
```

Store choice as `response_style`: `normal` or `caveman`.

---

### [2] Configure — Step 5: Session learning

```
STEP 2 OF 3 — Session learning

As we work together, I notice patterns — what you prefer,
how you like to structure things, what helps you focus.

With learning ON, I log these observations so future sessions
feel more tailored to you. You can review or delete them anytime.

  [1] On (recommended)
  [2] Off — don't record anything about me
```

Store choice as `profile_inference`: `on` or `off`.

---

### [2] Configure — Step 6: Language

```
STEP 3 OF 3 — Language

What language should I use for plans, tasks, and notes?

  [1] English
  [2] Spanish
  [3] Other (tell me)
```

Store as `language`.

---

### Step 7 — Save profile

Create `_system/users/<username>.md`:

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

### Step 8 — Handoff

```
Setup complete. Welcome, <display_name>.

Next steps:
  1. /awi-initialize   — build the AWI file structure
  2. /new-client <name>   — add your first client

Type /help anytime.
```

---

## Logging

At the end of this skill — regardless of outcome — log the invocation:

```bash
python3 .claude/skills/shared/scripts/log_command.py awi-introduction <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
