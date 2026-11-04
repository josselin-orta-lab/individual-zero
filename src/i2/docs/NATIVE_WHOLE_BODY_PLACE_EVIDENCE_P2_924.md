# I2 P2: read-only multidimensional personally lived site consequences

**Source lock**: preregistered in [P2 #924](https://github.com/josselin-orta-lab/individual-zero/issues/924#issuecomment-6633849074), before implementation, following separately frozen, exact-head validated and merged [P4 #977](https://github.com/josselin-orta-lab/individual-zero/pull/977). Baseline main `614ca3681343d2ee9dae3eab742edebbbd01989d`. This is a **pure observational evidence contract**, NOT a new learned memory/score, motor policy, reward, autonomous rescue or registered I2 engine.

## Scientific motivation

P4 #977: four genuine continuous 128-tick research lives in two counterbalanced harmful-food worlds reached the technically right-censored horizon. When passage food was harmful, learning OFF ate the safe source at ticks 8, 68 and 128, ending integrity 88; learning ON ate safe source at ticks 8 and 9 but later ate harmful passage again at 128, ending integrity 76 with more UC. When source was harmful, OFF repeated three harmful source meals, final integrity 64; ON had only one harmful source meal but did not subsequently consume the known safe passage food, ending food 53.4 and integrity 88. These are mixed outcomes rather than reliable learned strategy revision. Neither learning ON/OFF first movement divergence nor better single-channel health establishes a general survival advantage.

Existing `lived_place_outcomes` is intentionally an action's **target-only** association: for `manger` it stores only the food reserve change and omits a full-stomach action when food pressure is zero. In reality the native body owner records all four reserves on every committed action. A meal may restore food yet injure integrity, or injure integrity with no food gain. Rather than inferring site quality, first preserve the complete *actually observed* bodily consequences.

## New pure contract, no state mutation

`lived_whole_body_site_consequences(rows, traits, enabled)` in the existing `src/i2/modules/native_place_experience.py` reads only the sole native owner's **already committed** canonical `_rows` stream after an independent owner cold audit. It checks contiguous sequence, native movement adjacency, exact capture and action fields, canonical four-reserve pre/post JSON and bodily continuity. Each admitted `manger`, `boire`, `boire_decouverte`, `dormir` or `attendre` produces an immutable `LivedWholeBodySiteConsequence`, including true before/after values, signed energy/food/water/integrity deltas and four immediately preceding current need pressures.

Attribution uses only previous physically committed adjacent movements. A full-stomach harmful meal remains recorded even when the original P2 target-only evidence omits it. Unknown, unvisited and unconsumed locations produce **no claim**. A pure fixture is never an attested or autonomous life: the caller must cold-verify the original SQLite owner before interpreting any projected record as real evidence. Source names, hidden birth food injury/stocks, unchosen outcomes and future payoffs never enter this observer.

No extra SQLite table, source memory, birth flag, site preference, cognitive score, world/planner, action authority, I1 import, UC mutation or engine activation. The original P2 `ExperiencedPlaceOutcome`, tie-based site preference and G2 chosen-result scorer remain **unchanged**. This work only makes the representational blind spot independently inspectable.

## Negative cases, next hypothesis

Tests in `tests/i2/test_native_whole_body_place_evidence_924.py`: an actually used injurious +food/-integrity opportunity at passage, harmless food at source, zero-gain/-integrity eaten at full stomach, camp drinking, true rest repair, alternating sites without a false source reward, no visits yielding UNKNOWN, invalid/nonadjacent move, noncontiguous rows, malformed or noncanonical body, discontinuous before/after, exact birth flags and a separately cold-audited unscripted native v21 paid life. Synthetic rows validate **only extraction semantics**, never an individual motor choice.

If subsequent research justifies new cognition, the next separately prospectively frozen hypothesis should use a born-locked, non-oracular, name-symmetric, per-channel need-conditioned site association projected into the **existing paid Competition** without motor overrides. Require an equal-learning OFF control, a source-label permutation, repeated harmful contact, low/no food need, inaccessible alternatives and independent held-out lives before claiming survival advantage. This PR does NOT implement that hypothetical valuation.

**Engineering discipline**: one focused module extension, tests and this note; one normal exact-head Python 3.11+3.12 full I2 workflow, six generation boundaries and inert-engine guard. No scientific G3/H3/M11 success from code/test PASS; all four P4 #977 outcomes remain untouched.
