---
type: idea
tags: [mental-model, reasoning]
created: 2026-03-29
---

# Occam's Razor

Among competing explanations, prefer the one that requires the fewest assumptions.

Not "the simplest explanation is always true" — but "don't multiply complexity beyond necessity."

## When to use
- Debugging: when there are 5 possible causes, start with the most likely one
- Interpreting behavior: before inventing complex motives, check simple ones
- Decision-making: when two strategies both fit the data, choose the leaner one

## Example
Your API is returning 500s. Occam's Razor: check if there's a misconfigured env var before assuming a race condition in the distributed cache.

Someone missed a meeting. Occam's Razor: they forgot — not that they're avoiding you.

## Pitfall
Complex problems sometimes have complex causes. Occam's Razor is a starting heuristic, not a law. Use it to set your prior, not close your mind.

## Related
- [[mental-models/first-principles]] — first principles finds the truth; Occam's Razor picks between equally valid models
- [[mental-models/availability-heuristic]] — vivid explanations feel simpler but may not be
