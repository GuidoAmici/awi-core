# Three-phase grill panel for ready-for-agent issues

Grilling uses a fixed three-agent panel — `nexus-strategy`, `reality-checker`, and an `assigned-employee` — running sequentially with autonomous interrupts allowed for blockers only. Each agent labels every message.

The alternative was a roundtable (all agents present simultaneously), which was rejected because concurrent voices make it unclear who owns each concern and when a phase is complete. Sequential phases with explicit user sign-off produce cleaner agent briefs: each phase summary maps directly to a section of the brief (strategic rationale, priority + effort, acceptance criteria).

`reality-checker` was chosen over a product manager for phase 2 because its role is to challenge assumptions rather than schedule work — the right lens for effort estimates and quick-win claims that are frequently optimistic. The assigned employee is determined at the end of phase 2, not upfront, because the right employee depends on what the first two phases surface about scope and domain.

The unrelated-issue branch terminates the panel after exactly 3 questions from `nexus-strategy` to keep context capture bounded without derailing the session.
