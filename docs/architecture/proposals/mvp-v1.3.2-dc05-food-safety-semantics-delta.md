# Proposed MVP v1.3.2 delta: DC-05 food-safety semantics

Status: **PROPOSAL ONLY — NOT NORMATIVE — OPERATOR REVIEW REQUIRED**

This document does not modify or reinterpret the historical text of MVP
v1.2.1, v1.3.0, or v1.3.1. It records the smallest semantic clarification
identified while resolving issue #89.

## Problem

MVP v1.2.1 deliberately separates the safety status
`etabli_pour_securite` from causal status `etablie`. The implementation,
however, exposes a `toxic_item` safety contingency through the legacy
adapter label `known_toxic`. That wording can be read as an etiological
claim: "the food physically caused the injury."

For a hidden time-varying hazard, that claim is not identifiable from I0's
authorized experience. A benign berry plus a hidden hazard activated at the
meal can produce the same autobiography as a genuinely toxic berry. Oracle,
Bench, and the technical journal are forbidden as cognitive tie-breakers.

## Minimal proposed clarification

For DC-05 only:

1. `etabli_pour_securite` on the existing `toxic_item` veto category means
   **item-associated empirical harm risk sufficient to justify the existing
   ingestion veto**.
2. It MUST NOT be interpreted as proof that the item is the physical
   etiology of the observed harm.
3. A claim of physical causal establishment remains governed separately by
   the causal lifecycle and its `etablie` status.
4. Observation histories that are identical at I0's epistemic boundary MUST
   yield identical cognitive state, even when the external technical journal
   proves that their physical worlds differed.
5. Technical-journal integrity, Oracle labels, Bench labels, missing hidden
   fields, or an external auditor's conclusions MUST NOT increase DC-05
   cognitive credit.
6. Under unchanged v1.3.1 semantics, harmful food associations remain
   withheld when physical etiology is not distinguishable from authorized
   experience.
7. If this v1.3.2 clarification is adopted, DC-05 may promote the **empirical
   ingestion-risk** safety use after `n_sec` independent lived harmful
   consumption episodes with comparable contexts and no *perceptible*
   sufficient competing cause. Hidden causes are not declared absent; they are
   simply irrelevant to the narrower empirical-risk proposition.
8. The promoted safety-use proposition MUST remain barred from simulator
   correction and from causal-status advancement unless the separate causal
   lifecycle independently earns those claims.

## Consequences

Gained:

- safety veto and physical etiology are no longer conflated;
- observational equivalence has an explicit, conservative interpretation;
- the external journal can remain exhaustive without becoming perception.

Trade-off:

- while v1.3.1 remains normative, harmful food safety learning is fail-closed
  and may be absent even for genuinely toxic food;
- if the proposed empirical-risk semantics is adopted, safety learning can
  resume from repeated lived harm without claiming food-specific physical
  etiology;
- no finite first-person protocol can exclude every adversarial hidden cause,
  so the causal `toxic_item` claim remains a separate and stronger burden.

No guarantee is lost that v1.3.1 can information-theoretically provide:
physical etiology remains unidentifiable in observationally equivalent
worlds.

## Compatibility note

The current string `known_toxic` in the ActionControl adapter is a legacy
policy label. If this delta is accepted, a later compatibility change should
rename that outward label to an empirical safety-veto term without changing
the closed veto category or retroactively editing prior specifications.

## Adoption gate

This proposal becomes normative only if the operator explicitly adopts it in
a separately versioned specification. Until then, MVP v1.3.1 remains the
normative reference and this file is decision support for issue #89.
