# Pending Tasks Convergence — 2026-04-30

**Scope:** Personal + Rabbitek + New Haze + AFIN  
**Total pending/in-progress items:** ~45 tasks, ~20 active projects

---

## Convergence Map

### Theme 1: New Haze DS v2 / Brand Ship (9 tasks)
All brand-identity and component-system work needed to finalize the shared design system.

| Status | Task |
|--------|------|
| in-progress | learn-visual-refresh — dark blue BG, violet accents, orange CTAs |
| pending | newhaze-brand-token-file — tokens.css with all DS v2 variables (**gate**) |
| pending | newhaze-brand-color-rules — printed vs digital palette rules |
| pending | newhaze-brand-typography-scale — Rubik type scale doc |
| pending | newhaze-brand-export-logo — SVG + PNG all variants |
| pending | newhaze-brand-voice-doc — tone rules + copy examples |
| pending | newhaze-brand-website-audit — audit site against final tokens |
| pending | newhaze-ui-consumer-validation — validate newhaze-ui in CI across consumers |
| active project | newhaze-brand-digital — umbrella for all brand/DS work |

**Gate:** `newhaze-brand-token-file` must ship first — all consumers (website, learn, b2b-panel) depend on tokens.css.

---

### Theme 2: New Haze Full System → Three-Org SaaS (7 items)
Active `saas-vertical-strategy` defines a sequence: New Haze → AFIN → Rabbitek Growshop SaaS. New Haze's full system must be validated before AFIN schema is drafted.

| Status | Item |
|--------|------|
| active (high) | newhaze-full-system — umbrella project, **gates AFIN schema** |
| active | sso — Google OAuth prod publish needed; gates full system |
| active | migracion-sheets-supabase — consolidate Sheets → Supabase |
| active | newhaze-learn — Next.js migration for SEO |
| active | newhaze-website — content + lead capture |
| active | newhaze-b2b-panel — client-facing dashboard |
| active | afin-srl-modernization — AWI at factory; blocked until NH schema done |

**Gate:** `publish-google-oauth-consent-screen` (pending/high) blocks SSO going to prod, which blocks newhaze-full-system sign-off.

---

### Theme 3: New Haze CI/CD / Infra (5 tasks)
Hardening the delivery pipeline before scaling feature work.

| Status | Task |
|--------|------|
| pending (high) | frontend-ci-workflows — GH Actions for website + learn |
| pending (high) | github-branch-protection-rules — enforce CI before merge to dev |
| pending (high) | publish-google-oauth-consent-screen — OAuth prod mode |
| pending | supabase-migration-ci — migration linting in CI |
| active | ci-cd-pipeline — umbrella project |

---

### Theme 4: AWI Tooling (8 tasks)
Internal improvements to the daily workflow system. Two items in-progress right now.

| Status | Task |
|--------|------|
| in-progress (high) | today-skill-multi-org — /today shows org tasks (4 critical gaps documented) |
| in-progress (high) | migrate-dev-env-to-wsl2 — WSL2 + Ubuntu migration |
| in-progress (medium) | audit-start-awi-init — rewrite initialize skill |
| pending (medium) | today-commitments-multiselect — ranked multi-select for commitments |
| pending (medium) | modify-wrap-session-skill — auto-save all files without prompts |
| pending (medium) | ci-pipeline-awi-core — GH Actions: stg → dev-claude |
| pending (low) | fix-check-delegates-hook — missing check-delegates.sh script |
| pending (low) | learn-delegate-skill — hands-on with /delegate |

---

### Theme 5: Content / Strategic Presence (2 items)

| Status | Item |
|--------|------|
| active | awi-core-youtube-devlog — weekly YouTube devlog of awi-core changes |
| active | claude-cowork — Rocío + AFIN on OCB workflow via Claude Cowork |

---

## Critical Path / Blockers

```
publish-google-oauth-consent-screen
    └─► SSO prod deploy
            └─► newhaze-full-system validated
                    └─► AFIN schema drafted
                            └─► Rabbitek Growshop SaaS scoped

newhaze-brand-token-file (tokens.css)
    └─► newhaze-ui-consumer-validation
    └─► newhaze-brand-website-audit
    └─► learn-visual-refresh (can't finalize without tokens)

today-skill-multi-org (in-progress)
    └─► daily /today workflow is correct for all 3 orgs
    └─► today-commitments-multiselect (depends on multi-org working first)
```

**Top blockers:**
1. `publish-google-oauth-consent-screen` — single task blocking SSO → newhaze-full-system → AFIN
2. `newhaze-brand-token-file` — blocks all DS v2 consumption across apps
3. `today-skill-multi-org` — blocks correct daily workflow (currently shows only personal tasks)

---

## Recommended Focus Order

| # | Item | Why |
|---|------|-----|
| 1 | `today-skill-multi-org` | In-progress, high — daily workflow is broken without it; low effort to finish |
| 2 | `publish-google-oauth-consent-screen` | High — unblocks SSO → newhaze-full-system → three-org strategy |
| 3 | `newhaze-brand-token-file` | Medium — tokens.css unblocks 5+ downstream brand tasks in one shot |
| 4 | `frontend-ci-workflows` + `github-branch-protection-rules` | High — pair naturally, harden CI before scaling features |
| 5 | `today-commitments-multiselect` + `modify-wrap-session-skill` | Medium — AWI polish, flows naturally after multi-org fix |

---

## Raw Task Inventory

### RABBITEK — Tasks (12)

| Task | Status | Priority |
|------|--------|----------|
| today-skill-multi-org | in-progress | high |
| migrate-dev-env-to-wsl2 | in-progress | high |
| audit-start-awi-init | in-progress | medium |
| today-commitments-multiselect | pending | medium |
| modify-wrap-session-skill | pending | medium |
| ci-pipeline-awi-core | pending | medium |
| fix-check-delegates-hook | pending | low |
| learn-delegate-skill | pending | low |
| import-newhaze-wiki-to-awi | complete | — |
| research-ai-model-delegation | complete | — |
| review-session-2026-04-03 | complete | — |
| document-awi-path-migration | complete | — |

### RABBITEK — Projects (4)

| Project | Status |
|---------|--------|
| mary-whatsapp-bot | active |
| claude-cowork | active |
| chulistic-app | active |
| vault-restructure | complete |

### NEW HAZE — Tasks (27)

| Task | Status | Priority |
|------|--------|----------|
| frontend-ci-workflows | pending | high |
| github-branch-protection-rules | pending | high |
| publish-google-oauth-consent-screen | pending | high |
| learn-visual-refresh | in-progress | medium |
| feature-pipeline-tracker | in-progress | low |
| newhaze-brand-token-file | pending | medium |
| newhaze-brand-color-rules | pending | medium |
| newhaze-brand-export-logo | pending | medium |
| newhaze-ui-consumer-validation | pending | medium |
| integrate-canny-feedback | pending | medium |
| newhaze-brand-typography-scale | pending | low |
| newhaze-brand-voice-doc | pending | low |
| newhaze-brand-website-audit | pending | low |
| migrate-google-credential-factory | pending | low |
| supabase-migration-ci | pending | — |
| separate-panel-tasks | pending | low |
| profile-picture-upload | pending | low |
| learn-offline-content-cache | pending | low |
| design-harmony-brainstorm | complete | — |
| define-environment-strategy | complete | — |
| remove-tailwind-css | complete | — |
| setup-doppler-secrets | complete | — |
| fix-dev-dashboard-bugs | complete | — |
| migrate-learn-content-to-db | complete | — |
| migrate-repos-to-github-org | complete | — |
| fix-newhaze-wiki-contradictions | complete | — |
| research-audit-reclassify-newhaze-wiki | complete | — |

### NEW HAZE — Projects (15)

| Project | Status |
|---------|--------|
| newhaze-full-system | active (high) |
| newhaze-brand-digital | active |
| newhaze-ui | active |
| newhaze-learn | active |
| sso | active |
| ci-cd-pipeline | active |
| newhaze-website | active |
| playwright-e2e-tests | active |
| newhaze-intern-panel | active |
| migracion-sheets-supabase | active |
| newhaze-b2b-panel | active |
| newhaze-pricelist | paused |
| servicio-tecnico-ia | paused |
| sistema-organizaciones | paused |
| tailwind-to-css-modules | complete |

### PERSONAL (3)

| Item | Status | Priority |
|------|--------|----------|
| afin-srl-modernization | active | — |
| awi-core-youtube-devlog | active | — |
| pay-credit-card-remainder | complete | — |

### AFIN — Tasks (0 filed)
No task files yet. Work tracked in personal `afin-srl-modernization` project and daily logs.
