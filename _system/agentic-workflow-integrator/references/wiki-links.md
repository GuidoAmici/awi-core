# Wiki Links Convention

Use `[[slug]]` wiki links throughout. Conventions:

| Link type | Format |
|---|---|
| Project → Product | `[[products/newhaze]]` |
| Task → Project | `[[projects/auth-unificado]]` |
| Daily → Task | `[[tasks/research-ai-model-delegation]]` |
| Project → Wiki | `[[wiki/arquitectura-digital/stack]]` |
| App design doc | `[[wiki/app-design/learn/mapa]]` |

## Backlinks

Use Obsidian wiki-style links `[[slug]]` in the markdown body to connect entities. When creating a task linked to a project, update the project file to include `[[task-slug]]`. Check if person/project already exists before creating duplicates.

**Backlinks are mandatory on creation.** When creating any new file that references other files via `[[...]]` links, immediately update each referenced file to link back to the new one. Backlinks are part of the creation step — not a follow-up audit.
