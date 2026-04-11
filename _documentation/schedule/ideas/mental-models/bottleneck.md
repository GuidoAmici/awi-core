---
type: idea
tags: [mental-model, systems]
created: 2026-03-29
---

# Bottleneck (Theory of Constraints)

In any system, one constraint limits overall throughput. Improving anything else first is waste.

From Eliyahu Goldratt's *The Goal* (1984). The five steps: Identify → Exploit → Subordinate → Elevate → Repeat.

## When to use
- Product development: what is slowing down shipping more than anything else?
- Personal productivity: what one thing, if removed, would unlock the most?
- System optimization: before scaling anything, find what's actually constrained

## Example
Your deploy pipeline takes 40 minutes. You optimize the test suite from 8 minutes to 4 minutes. But the bottleneck was the staging environment provisioning (30 minutes). Total time: 36 minutes. You saved 4 minutes but got 10% improvement instead of the 50% you were chasing.

Identify the actual bottleneck (staging) → that's where the investment pays.

## Key insight
The bottleneck moves. Once you fix one, another emerges. The work is continuous identification, not a one-time fix.

## Related
- [[mental-models/leverage]] — the bottleneck is the highest-leverage intervention point
- [[mental-models/opportunity-cost]] — fixing non-bottlenecks has high opportunity cost
