---
type: idea
tags: [mental-model, economics]
created: 2026-03-29
---

# Margin of Safety

Build in a buffer that allows you to be wrong and still be okay. Don't design for the expected case — design for the expected case plus variance.

From Benjamin Graham's value investing framework. Engineers call it a safety factor.

## When to use
- Infrastructure sizing: don't size for average load, size for peak + buffer
- Estimating timelines: pad estimates; complexity always reveals itself late
- Financial decisions: leave room so that if your assumptions are 20% off, you survive
- Irreversible decisions: require more certainty before acting when you can't undo

## Example
You estimate a feature takes 2 weeks. Margin of safety says: tell the stakeholder 3 weeks. If you're right, you deliver early. If unexpected complexity appears, you don't break trust.

You need $50k to operate. Margin of safety says: keep $80k in reserve.

Your load test shows max capacity at 10k RPS. Margin of safety says: plan infrastructure for 6k RPS as your "comfortable operating range."

## Pitfall
Too much margin of safety = paralysis or over-engineering. Calibrate the buffer to the stakes and reversibility of the decision.

## Related
- [[mental-models/dunning-kruger]] — low self-awareness = no margin of safety built in
- [[mental-models/inversion]] — inversion tells you what can go wrong; margin of safety is the buffer you add
