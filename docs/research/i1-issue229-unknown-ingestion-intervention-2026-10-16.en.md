# Issue #229: I1 unknown ingestion affordance, development intervention

Status: **implemented in code, untested at operator request; scientific NO-GO remains**.

Source: A2.39 experimental descendant `af5006612b45b46d5ee2b2ed9e97b9cf6e104167`, retained on dedicated PR #240. Active baseline main `bf59eceaf97805f04a18b0b28f1396f2e98bfa89`. I0, WorldBody, historical A2.38/A2.39, and MVP v1.3.3 are not modified.

## Mechanistic repair

- An independent opt-in at **new** autonomous mortal I1 birth, `i1_unknown_action_enabled=True` (default OFF), is encoded in the I1 M11 birth digest with `i1_unknown_action_cost_uc` (default 2, strictly positive).
- After exact Stage6 search, when the active goal is food and no complete plan is available, inspect the existing Stage6 primitive enumerator over the **authorized first-person capture**. If inventory contains a berry, the enumerator exposes an executable `manger` command. Neither an oracle, privileged physical model nor a guessed berry effect is consulted.
- When a fully predicted valid goal plan exists, retain it. For incomplete/partial goals, an unknown ingestion candidate can be formed with **zero predicted consequences**, explicit epistemic uncertainty, and the same Plan/Option/Competition/Stage9/Action Control ownership as the original model. No action is dispatched by this capability.
- The new candidate is UC-priced before generation, recorded with accessible inventory, pressure, temperament's exploration and uncertainty coefficients, and the `Q_active` state for the action signature. Its bounded initial evidence is a motivation to *consider* a genuine uncertain affordance, not a predicted food gain or a safety guarantee. Existing Stage8 lived TD updates can subsequently influence this signature after actual action outcomes. Choice and admission remain unforced.
- All existing I1 external-model actions, historical model hashes when this flag is OFF, water learning, H1/H2 historical ablations, Stage9 and the only WorldBody execution path are retained.

This intervention currently limits novel affordance consideration to the existing `eat` need and perceived `manger` primitives. General universal action exploration, safety learning and cross-context competence are **not** claimed.

## Adoption and limits

For a separate future I1 mortal birth, pass:

```python
i1_unknown_action_enabled=True,
i1_unknown_action_cost_uc=2,
```

to the existing I1 runtime constructor. No historic birth is silently changed. No retrospective A2.38/A2.39 re-scoring is authorized.

**Operator specifically requested no additional tests.** No software tests, lives, performance cohorts, new validation data or CI runs are claimed here, and the new #229 diagnostic CI workflow was removed from this branch. Technical compatibility and autonomy are consequently **not certified**. Neither #229 nor PR #240 is scientifically GO/merge-ready. Any future confirmation requires prospective independent evidence, original denominators and review of PR #239.
