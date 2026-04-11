# Gemini Delegation — Frontend Changes

When implementing features that span backend + frontend, **always delegate frontend changes to Gemini CLI**. Claude handles architecture, tokens, API, and orchestration. Gemini handles mechanical frontend file edits.

## Why

- Saves Claude tokens for architectural decisions and cross-repo coordination
- Gemini excels at mechanical find/replace, file rewrites, and following step-by-step instructions
- Parallel execution: both repos can be updated simultaneously

## Workflow

### 1. Claude does first (architecture layer)

- Design tokens, schemas, shared contracts (JSON files)
- API changes (models, DTOs, controllers, services)
- Sync scripts between repos
- Create the Gemini task file with exact instructions

### 2. Create delegation file in target repo

File: `<repo>/GEMINI_TASK_<feature-slug>.md`

Structure:
```markdown
# Gemini Task: <Feature Name> — <Repo> Migration

> Execute these changes in order. Each section is a self-contained step.

## Step 1: <Title>
<Exact file path, what to replace, full code blocks>

## Step 2: <Title>
...

## Verification
<How to confirm changes work>
```

Rules for task files:
- **Numbered steps** — sequential, self-contained
- **Exact file paths** — never ambiguous
- **Full code blocks** — not diffs, complete replacement content
- **No decisions** — all choices pre-made by Claude
- **Verification section** — what to check after execution

### 3. Run Gemini headless

```bash
cd <repo-path>
gemini --yolo -p "Read and execute GEMINI_TASK_<slug>.md — follow every step in order. Do not skip any step. Do not ask questions, just execute."
```

- Use `--yolo` for auto-approve (file writes without confirmation)
- Use `-p` for headless (non-interactive) mode
- Run via Bash tool with `run_in_background: true` for parallel execution
- Run both repos simultaneously when possible

### 4. After Gemini finishes

- Read the output to check for errors
- Verify builds/dev servers work
- Clean up: delete `GEMINI_TASK_*.md` files from repos (they're one-shot instructions)

## Which changes go to Gemini

| Gemini (frontend mechanical) | Claude (architecture) |
|---|---|
| CSS variable updates | Design token schema |
| Font import swaps | Font selection decisions |
| Component file rewrites | Component API design |
| Theme provider/context creation | Theme switching architecture |
| Find/replace across components | Semantic key naming |
| Navbar/header markup | Role-gating logic design |
| Style tag updates | API endpoint design |

## Repos and their stacks

| Repo | Path | Frontend stack |
|---|---|---|
| newhaze-website | `D:/GitHub/GuidoAmici/newhaze-website` | Next.js 15 + Tailwind 4 + shadcn |
| newhaze-learn | `D:/GitHub/GuidoAmici/newhaze-learn` | React 18 + Vite 6 + inline styles |
