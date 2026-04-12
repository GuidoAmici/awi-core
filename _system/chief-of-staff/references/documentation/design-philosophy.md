# Design Philosophy

1. **Git is the database** — No separate storage, just markdown and commits
2. **Natural language first** — Say what you mean, let classification handle the rest
3. **Grep before glob** — Never load all files, search efficiently
4. **Progressive disclosure** — Skills load context in layers to manage tokens
5. **Auto-commit everything** — Hooks ensure nothing is lost
6. **Cross-repo awareness** — Delegation maintains context across projects
7. **Two-file person model** — `people/*.md` for profile + preferences; `user-profile-inference/` for raw observations
