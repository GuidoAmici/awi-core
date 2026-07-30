# User-org strategic relationship lives in user space, not org space

The AWI User has a personal Mission, Vision, and Values (**Professional Identity**) that is distinct from any organization's MVV. When a user engages with an org, the strategic intersection between the two — alignments, frictions, and how to advance — is personal and private to the user. It must not live in the org workspace, where it would be visible to other users of that org and would conflate the user's private perspective with the org's canonical identity.

We decided to model this as two separate artifacts:

1. `_data/users/<github-id>/documentation/professional-identity.md` — the user's personal MVV, private and portable via `my-awi-user`.
2. `_data/users/<github-id>/org-engagement/<org-name>.md` — the per-org intersection analysis (alignment, friction, path forward, and inter-org dependencies), generated automatically on `/awi-org` and reviewed in `/today`, `/week`, `/quarter`, and `/year`.

The org's own MVV lives as `_data/organizations/<name>/documentation/org-profile.md` and is the source of truth for that org's identity across all users.

## Considered Options

- Storing the intersection analysis in the org workspace — rejected because it exposes the user's private strategic reasoning to other users of the org, and because it couples the org's canonical identity to one user's perspective.
- A single "professional strategy" document mixing global narrative and per-org details — rejected because it makes the global and per-org concerns harder to update independently and harder to surface selectively in rituals.

## Consequences

- Inter-org dependencies (e.g. "newhaze exists to prove results that feed into afin") are recorded inside each Org Engagement, not in Professional Identity — keeping context co-located with the org it describes.
- `/awi-org` must generate an initial Org Engagement stub at incorporation time, prompting the user to articulate alignment and friction against the org's MVV.
- `/today` and `/week` must load the relevant Org Engagement(s) to surface strategic context alongside the daily plan.
