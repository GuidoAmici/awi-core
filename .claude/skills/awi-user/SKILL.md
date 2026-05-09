---
name: awi-user
description: Unified user management. View current user, switch users, log in/out, create new users. Manages my-awi-user GitHub repo as submodule under _data/users/<github-id>/.
allowed-tools: Read, Write, Bash, Glob, AskUserQuestion
model: sonnet
---

# /awi-user — User Management

One skill for all user operations.

---

## On Invoke

1. Get current date:
   ```bash
   bash .claude/hooks/get-datetime.sh full
   ```
2. Read `_data/users/current-user.json` (may not exist).
3. Display status and menu.

**Status line:**

If logged in:
```
Logged in as: <name> (@<login>) — _data/users/<github-id>/
```

If not:
```
No user logged in.
```

**Menu:**
```
1. User preferences
2. Change user
3. Log out
```

_(Show option 3 only if a user is logged in.)_

---

## Option 1 — User Preferences

Read `_data/users/<github-id>/awi-user-profile.md`. Display Preferences and Long-term patterns sections. Ask if operator wants to edit anything. If yes, use Write to update the file and push the change (see Sync Procedure).

---

## Option 2 — Change User

Show submenu:
```
2a. Switch to a logged user
2b. Log in (authenticate this machine)
2c. Create new user
```

---

### 2a — Switch to Logged User

Find inactive user submodules — entries in `.gitmodules` under `_data/users/` that are NOT the current user:

```bash
grep 'path = _data/users/' .gitmodules | grep -v 'path = _data/users/current-user'
```

Filter out the current `<github-id>`. Present available logins extracted from `.gitmodules` URLs.

If none found: "No other users registered. Use 2b to log in."

**If current user exists:**
1. Run Sync Procedure for current user.
2. Run Deactivate Procedure for current user.

**Activate selected user:**
```bash
git submodule update --init _data/users/<new-id>
```

Update `_data/users/current-user.json` (see format below). Load and display session primer from `_data/users/<new-id>/awi-user-profile.md`.

---

### 2b — Log In

1. Verify GitHub auth:
   ```bash
   gh auth status
   ```
   If not authenticated, prompt: "Run `! gh auth login` in the terminal to authenticate, then re-run /awi-user."

2. Get user info:
   ```bash
   gh api user --jq '{id: .id, login: .login, name: .name}'
   ```

3. If `_data/users/<id>/` already initialized — just update `current-user.json` and load. Skip steps 4–6.

4. Check for `my-awi-user` repo:
   ```bash
   gh repo view <login>/my-awi-user --json name 2>/dev/null && echo "exists" || echo "missing"
   ```

5. **If repo exists:**
   ```bash
   git submodule add -b only https://github.com/<login>/my-awi-user.git _data/users/<id>
   git submodule update --init _data/users/<id>
   ```

   **If repo does not exist:**
   ```bash
   gh repo create <login>/my-awi-user --private --description "AWI user data"
   git submodule add -b only https://github.com/<login>/my-awi-user.git _data/users/<id>
   git submodule update --init _data/users/<id>
   ```
   Then create initial `_data/users/<id>/awi-user-profile.md`:
   ```markdown
   ---
   github-id: <id>
   login: <login>
   name: <name>
   ---

   # <Full Name>

   ## Preferences

   ## Long-term patterns
   ```
   Commit and push this file inside the submodule:
   ```bash
   cd _data/users/<id> && git add -A && git commit -m "init: awi-user-profile" && git push origin only && cd -
   ```

6. Write `_data/users/current-user.json`:
   ```json
   {
     "user": "_data/users/<id>/",
     "github-id": "<id>",
     "login": "<login>",
     "since": "<YYYY-MM-DD>"
   }
   ```

7. Update `_data/submodules.md` to add/reflect the new user submodule entry.

8. Display session primer from `awi-user-profile.md`.

---

### 2c — Create New User

Run steps 1–6 from 2b (auth + repo setup). Then run profile interview — ask **one question at a time**, wait for each answer:

1. "What is your role or main area of responsibility?"
2. "How do you prefer to work? (e.g. async vs sync, detail-oriented vs big-picture, structured vs flexible)"
3. "What topics or domains are you most interested in?"
4. "Any preferences on how Claude should communicate with you? (tone, language, response length)"

Populate `_data/users/<id>/awi-user-profile.md` with answers under `## Preferences`. Commit and push.

---

## Option 3 — Log Out

1. Run Sync Procedure for current user.
2. Run Deactivate Procedure for current user.
3. Delete `_data/users/current-user.json`.
4. Output:
   ```
   Logged out @<login>. Run /awi-user to log in again.
   ```

---

## Sync Procedure

Push current user's uncommitted data to GitHub before any user switch or logout:

```bash
cd _data/users/<github-id>
git add -A
git diff --cached --quiet || git commit -m "awi-user: sync"
git push origin only
cd -
```

If push fails: warn operator and ask whether to proceed anyway. Never proceed silently on push failure.

---

## Deactivate Procedure

Makes the user's local data inaccessible without deleting the GitHub repo:

1. Deinit submodule (removes local checkout, keeps `.gitmodules` entry for later reactivation):
   ```bash
   git submodule deinit _data/users/<github-id>
   rm -rf _data/users/<github-id>
   ```

2. Update `_data/submodules.md` to mark user as inactive.

---

## current-user.json Format

```json
{
  "user": "_data/users/<github-id>/",
  "github-id": "<github-id>",
  "login": "<login>",
  "since": "<YYYY-MM-DD>"
}
```

`user:` field is the `<user-root>` used by all other skills to resolve `<agenda-base>`.

---

## Logging

At the end of this skill — regardless of outcome — log the invocation:

```bash
python3 .claude/skills/shared/scripts/log_command.py awi-user <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
