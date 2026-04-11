---
type: idea
tags: [mental-model, systems]
created: 2026-03-29
---

# Feedback Loops

A feedback loop exists when a system's output becomes an input that influences future output.

Two types:
- **Reinforcing (positive)**: output amplifies itself → growth or collapse
- **Balancing (negative)**: output corrects itself → stability

## When to use
- Designing systems: what are the feedback loops? Are they reinforcing the right things?
- Understanding growth: viral loops, compounding interest, learning curves
- Debugging runaway behavior: something keeps getting worse — trace the loop

## Example
Reinforcing (good): Users like the product → refer friends → more users → more data → better product → users like it more.

Reinforcing (bad): Team is under pressure → cuts corners → more bugs → more firefighting → less time to fix root causes → more pressure.

Balancing: Customer churn is rising → team fixes core issues → churn drops → pressure releases → team can invest in quality.

## Design principle
Build reinforcing loops around the behaviors you want (retention, quality, learning). Build balancing loops around the behaviors you want to bound (spend, risk, scope creep).

## Related
- [[mental-models/compounding]] — compounding is a reinforcing feedback loop applied to growth
- [[mental-models/second-order-thinking]] — feedback loops are the mechanism second-order thinking traces
- [[mental-models/leverage]] — high-leverage interventions often target feedback loops
