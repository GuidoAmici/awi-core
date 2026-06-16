# ready-for-agent requires a completed grill session

The `ready-for-agent` label is the gate for background delegation via `/delegate-issue`. We redefined it to mean: "grilled, employee assigned in agent brief, model specified." An issue cannot reach this state without a `/grill-with-docs` session that resolves design ambiguities and confirms which employee handles it.

The alternative — delegating directly from `ready-for-agent` issues that were manually fast-tracked — created a trust problem: background agents can't ask clarifying questions, so underspecified issues either halt or produce plausible-looking but wrong output with no human checkpoint.

The cost is one mandatory grill per issue before delegation. The benefit is that every dispatched agent has a complete, unambiguous spec and an explicit employee assignment, making `/delegate-issue` confirm-before-fire list auditable and trustworthy.
