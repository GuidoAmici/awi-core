# Memory Routing Rules

## People vs. User Profile Inference

Two separate files track information about the operator — use the right one:

| File | What goes here |
|------|----------------|
| `_data/users/<github-id>/awi-user-profile.md` | Full name, roles, **preferences** (replaces local session memory files), and **long-term patterns** graduated from user-profile-inference |
| `<user-root>agenda/user-profile-inference/YYYY-MM-DD - <FullName>.md` | Session-level observations Claude *noticed* — things the user likely doesn't consciously track. Raw material; may graduate to the user profile over time. |

**Routing rules:**
- Self-stated preference or working style → `_data/users/<github-id>/awi-user-profile.md` § Preferences
- Claude-observed pattern, first time → `<user-root>agenda/user-profile-inference/YYYY-MM-DD - <FullName>.md`
- Claude-observed pattern, confirmed across multiple sessions → graduate to the user profile § Long-term patterns
- Do NOT store preferences in local Claude session memory files — the user profile file is the canonical source

## AI Agent Memory

**Never use the AI agent's local memory system** (e.g. Claude's `~/.claude/` memory files). AWI is the memory system. All context, observations, preferences, and decisions belong in vault files:

- User preferences → `_data/users/<github-id>/awi-user-profile.md`
- Session observations → `<user-root>agenda/user-profile-inference/YYYY-MM-DD - <FullName>.md`
- Project context → project files or workspace wiki pages
- Decisions → `<user-root>agenda/outputs/`
