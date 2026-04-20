# Classification System

## How It Works

When you use `/new`, the system:

1. **Decomposes** input into entities (may be multiple)
2. **Classifies** each as task, project, person, idea, or output
3. **Extracts** due dates, tags, names, structured data
4. **Links** entities via `[[wiki-style]]` links
5. **Writes** files to appropriate folders under `<user-root>agenda/`
6. **Auto-commits** via PostToolUse hook

## Classification Rules

| Type | Trigger | Example |
|------|---------|---------|
| **Task** | Specific actionable item | "Call John by Friday" |
| **Project** | Ongoing work, multiple steps | "Website redesign" |
| **Person** | Named individual with context | "Meeting with Sarah" |
| **Idea** | Speculative, "what if" | "What if we added AI features" |
| **Output** | Decision record or deliverable | Architectural decisions, plans |

## Confidence Scoring

| Score | Action |
|-------|--------|
| **0.9+** | Proceed without confirmation |
| **0.7–0.9** | Probably right, proceed |
| **0.5–0.7** | Uncertain, note in commit |
| **<0.5** | Ask for clarification |

## People vs. User Profile Inference

| File | What goes here |
|------|----------------|
| `people/GuidoAmici.md` | Full name, roles, preferences (self-stated), long-term patterns (graduated) |
| `user-profile-inference/YYYY-MM-DD.md` | Session-level observations Claude noticed — raw material |

**Routing rules:**
- Self-stated preference → `people/GuidoAmici.md § Preferences`
- Claude-observed pattern, first time → `user-profile-inference/YYYY-MM-DD.md`
- Claude-observed pattern, repeated → graduate to `people/GuidoAmici.md § Long-term patterns`
- Never store preferences in local Claude session memory files

## Filing Destinations

| Type | Path |
|------|------|
| Task | `<user-root>agenda/tasks/` |
| Project | `<user-root>agenda/projects/` |
| Product | `<user-root>agenda/products/` |
| Person | `<user-root>agenda/people/` |
| Idea | `<user-root>agenda/ideas/` |
| Output | `<user-root>agenda/outputs/` |
| Daily | `<user-root>agenda/daily/` |
| Weekly | `<user-root>agenda/weekly/` |
| Planning | `<user-root>agenda/planning/` |
| User observations | `<user-root>agenda/user-profile-inference/` |
