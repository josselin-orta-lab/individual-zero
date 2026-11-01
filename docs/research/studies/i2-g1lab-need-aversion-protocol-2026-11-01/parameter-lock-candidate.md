# G1-LAB need / nutrition / aversion: numerical lock CANDIDATE v1-r1

**Status: PRE-APPROVAL SCIENTIFIC QA REVISION / NOT_OWNER_APPROVED / NOT_EXECUTION_AUTHORIZED / NOT_RUN.**
**Revision of original PR #810 candidate, before parameter approval and BEFORE any new experiment.** The original candidate's capture-3 primary endpoint was invalid because EAT is unavailable with an empty inventory after the first consumption. This revision corrects *only the comparison time and causal interpretation*, not the numerical parameters or policy. Original: main `0199df976421ee96f395091f965eed5e00ae7ed1`, blob `f9aa7910e57d5b262f3ea7862f5458c81a60370a`. Its prior approval request is superseded. **Owner approval of this revised exact SHA remains mandatory.**
**Proposed on 2026-11-01, before any new outcome/behavioral execution.**
**Parent scientific design:** [prospective design](README.md), accepted
*in principle* under [ADR-0007](../../../decisions/ADR-0007-need-nutrition-aversion-scientific-design.md).
**Exact source used to form candidate:** `3b7bc9d4068f9a69ac7cee33e00c80b2c2c92447`.
This file is a **request for a separate owner decision**, not an approval
by the coding agent. No choices, synthetic studies or model simulations
were executed to select these parameters.

## Question, boundary and source provenance

**Primary decision:** after an actual, self-chosen EAT has supplied
separate nutrition and synthetic aversive evidence, can an *engineered*
competition mechanism distinguish energetic need and retained aversion
from their separate ablations **at a matched prior-history choice**?

This is intentionally a deterministic, exploratory **mechanism
identification** exercise. It cannot establish biological hunger,
subjective unpleasantness, natural emergence, statistical generalization,
living autonomy, or a causal welfare benefit over unequal death horizons.

Only the existing G1-LAB disposable single SQLite cognitive/body owner
may be extended *if this complete protocol later receives separate
approval*. Preserve its existing paid UC, Action Control veto, abstention,
terminal, local atomic rollback, post-hoc trace auditing, and no motor
admission. No I1 import, no second mutable owner, no birth, no M11 witness
or G1-LIVE promotion.

## Parameter table (candidate values, not yet authorized)

| Parameter | Proposed fixed value | Prior/provenance and caveat |
| --- | --- | --- |
| Energy state at first capture | **17 or 60** | Taken unchanged from prior negative-control PR #805; NOT new held-out energy states |
| Maximum energy | **100**; floor at **0** | Existing G1-LAB state bound; 0 is modeled terminal, not real death |
| Nutritional gain on a chosen EAT with inventory | **+8** | Reuses G1-LAB's earlier stable positive eating impulse; toy researcher-defined |
| Aversive sensory signal after a chosen EAT | **0 or 4** | Two researcher-defined conditions; 4 is a round positive signed-score penalty, NOT pain |
| Nutritional gain / sensory aversion on non-EAT | **0 / 0** | No unchosen outcome; no invented social evidence |
| Absent action metabolism | **1 energy** | Existing G1-LAB |
| COLLECT / EAT / DRINK metabolic cost | **2 energy** each | Existing G1-LAB |
| Initial inventory | **0** | Existing G1-LAB |
| Initial berry resources | **12** | Existing G1-LAB |
| Toy physics | **collect** consumes one resource and stocks one item; **eat** consumes one stored item; **drink** does not consume berries | Existing G1-LAB availability/physics; EAT offered only when inventory > 0 |
| Synthetic UC per independent instance | **60** initial | Existing G1-LAB paid fixture; actual spent UC must be reported |
| Captures | **up to 8**, stop immediately on terminal or normal refusal | Matches historical G1-LAB horizon; no forced replacement step |
| Initial priors | **C=3, E=4, D=1** | Old researcher-defined priors; stable C→E baseline is NOT proof of learning |
| Old chosen-outcome score offset | **DISABLED** (+5 is not combined) | Prevent mixing a post-hoc synthetic score with the proposed new mechanism |
| Old stale-option revisit | **DISABLED** (+9; revisit_after=2) | ADR-0006, not evidence-grounded endogenous exploration |
| RNG / seeds | **No RNG**; no seed selection | Exact deterministic schedule; one independently initialized instance per cell/arm, not statistical replicates |
| Cell count | **2 energies × 2 aversion conditions = 4** | Nutrition fixed positive at +8, so the study does NOT test an independent nutritional-gain magnitude effect |
| Controls per cell | **Full, need-off, aversion-off, fixed** | Four independent local SQLite owners, equal initial conditions/UC |
| Maximum experiment | **16 model instances × 8 captures = 128 attempted captures** | Bounded nonliving research cost, no reruns with altered parameters |

**Important limitation:** the two aversive conditions encode *different
hidden sensory laws*, but NO agent receives that law before its own chosen
EAT effect. A sensory signal exists only in the toy world, and is not the
same thing as negative nutritional energy or physiological harm.

## Exact proposed integer policy (not approved)

At every capture `t`, calculate only from the PREVIOUS committed
physical state `E_t` and explicitly referenced PREVIOUS chosen
experience. No future EAT outcomes, unchosen outcomes, future energy,
negative-world oracle, social signals or researcher-forced exposure.

```text
D_t = 100 - E_t                 # E_t integer in [1,100] for any active life
N_t(a) = last personally observed nutrition_gain for a; else 0
A_t(a) = last personally observed aversive_signal for a; else 0
B_t(a) = (D_t * N_t(a)) // 100 # integer floor, nonnegative

FULL(a)       = prior(a) + B_t(a) - A_t(a)
NEED_OFF(a)   = prior(a) + 0        - A_t(a)
AVERSION_OFF(a)=prior(a) + B_t(a) - 0
FIXED(a)      = prior(a)
```

Only **actually observed** chosen-action events contribute to `N_t`
and `A_t`. Do not infer a missing EAT sensory/nutritional outcome
from another action, a later hidden schedule or the raw signed
`observed_net` scalar. No default positive value for an unexperienced
action. All four arms may retain the same separate personally observed
evidence; ablations affect **valuation only**, not perception, memory
storage or body physics. Prior aversive evidence must remain stored even
when the full or aversion-off arm takes a risky action.

Use the **unchanged** paid Competition semantics: per-candidate UC billed
before valuations; only a **unique positive maximum** is advisory;
a tie, non-positive best value, declined UC or Action Control veto
results in no modeled action. The existing internal G1-LAB callback,
if later authorized, applies at most one reviewed action inside the SAME
SQLite commit. No additional bonus, sigmoid, clipping, hunger threshold,
special EAT command or safety waiver. Reject any integer outside the
existing bounded score contract, rather than silently coerce it.

Physical transition (existing G1-LAB resource law with a nonnegative
nutrition channel in the *new* study):

```text
energy_(t+1) = clamp(E_t - metabolic_cost(action) + nutrition_gain(chosen), 0, 100)
sensory_signal(chosen) = 4 or 0 only after a genuine EAT; else 0
```

The aversive sensory signal does **not** directly reduce body energy.
It is a separately stored simulated outcome, eligible for cognition
only at the NEXT capture and never promoted to biological evidence.
The outcome's provenance must bind one chosen action, energy, nutrition,
sensory signal, capture sequence, and single-owner event head.

## Planned cells and first discriminating checkpoint

| Cell | Initial energy | Sensory signal after chosen EAT | Nutrition after chosen EAT |
| --- | ---: | ---: | ---: |
| L0 | 17 | 0 | +8 |
| L4 | 17 | 4 | +8 |
| H0 | 60 | 0 | +8 |
| H4 | 60 | 4 | +8 |

For each cell, run the four ablations as **independently initialized,
same-law** lab instances. **The primary behavioral endpoint is the
paid action decision at capture 4, conditioned on the same genuinely
observed C,E,C history at captures 1,2,3 and EAT being offered again.**
The post-exposure capture 3 is NOT behaviorally discriminating for
nutrient/aversion-based EAT choice: the preceding EAT consumes the only
berry, inventory becomes zero and the only offered options are COLLECT
and DRINK. These have no new nutrition or aversion observations, so the
candidate rule still gives COLLECT=3 and DRINK=1. Only after this
unforced COLLECT replenishes the inventory can EAT be considered at
capture 4. This is a **pre-execution static affordance proof**, NOT a
newly executed outcome or a guarantee that the protocol will reach
this history.

**If any arm deviates from the required C,E,C prehistory, cannot afford
the charged decision, dies, is vetoed, or lacks EAT at capture 4:**
report `NOT_IDENTIFIABLE_UNMATCHED_PREHISTORY` (or
`NOT_IDENTIFIABLE_NO_EXPOSURE` when no EAT has been personally
experienced). **Do NOT shift the endpoint to a later favorable capture,
restart the arm, or force a missing action.** The same rule applies to
all 16 proposed independently initialized instances.

Before claiming a need effect, verify that the full and need-off arms
had equal personal action/outcome histories, energy, offers and evidence
up to the contrasted capture; likewise full vs aversion-off. If they
diverge early, a direct matched-choice causal interpretation of
subsequent differences is **not identifiable** without a separate,
pre-authorized paired-replay design. Do not cherry-pick a later capture
or silently adjust the comparison window. **Identical chosen actions
despite different computed scores are NOT evidence of changed behavior.**

### Purely algebraic pre-execution check (NOT a simulation)

Under the hypothesized unforced `C,E,C` history (whose actual
realization is still untested), energy after captures 1, 2 and 3 is
`E0-2, E0+4, E0+2`. Thus energy **before capture 4** is 19 in
low-energy cells and 62 in high-energy cells; the personally experienced
EAT supplies nutrition 8 and either sensory signal 0 or 4. Prior
COLLECT=3 and DRINK=1 remain unchanged. The proposed formula then
algebraically entails these **EAT valuations**, not observational
outcomes:

| Cell | Full EAT | Need-off EAT | Aversion-off EAT | Fixed EAT | Full decision if EAT offered |
| --- | ---: | ---: | ---: | ---: | --- |
| L0 | 10 | 4 | 10 | 4 | EAT (10 > COLLECT 3) |
| L4 | 6 | 0 | 10 | 4 | EAT (6 > 3); need-off selects COLLECT |
| H0 | 7 | 4 | 7 | 4 | EAT (7 > 3) |
| H4 | 3 | 0 | 7 | 4 | **ABSTAIN** (EAT 3 ties COLLECT 3); need-off selects COLLECT and aversion-off EAT |

These consequences are **predictions derived from a researcher-written
equation**. They are published before any run, not selected from data.
The high-energy/aversive tie means an observed full-arm abstention
would not establish a generalized aversion mechanism. The need
comparison is full versus need-off **within the same energy cell**;
the aversion comparison is full versus aversion-off **within the same
sensory cell**. Scores differing without actions differing do NOT
establish behavioral effects.

**Scientific limitation:** in this deterministic setup, positive
differentiation at capture 4 may be largely guaranteed by the
researcher-assigned formula. A software PASS can demonstrate delayed
information provenance, faithful paid competition and controlled
ablation behavior, **not spontaneous biological hunger or acquired
adaptive competence**. If only the scores differ or the matched
capture never occurs, report the null or unidentifiable case.

**Memory semantics:** `last observed aversive_signal` in the proposed
valuation rule is NOT permission to erase earlier aversive events from
the durable first-person outcome ledger. Keep the complete history
even if a later safe observation changes the value used by the rule.
This is especially important to the already accepted ADR-0006.

Source-pin the exact baseline and all changes before the future run.
Save capture-level first-person evidence, chosen/refused actions, modeled
nutrition and sensory outcomes, raw aversive-memory retention, separate
metabolism, energy/inventory/resources, scores, actual UC charged,
terminal and censoring for **every** cell/arm. The result report must
include both *mechanistic score* contrasts and *behavioral action*
contrasts and must label them differently.

## Precommitted negative and safety falsifiers

1. A sensory or nutritional signal is used before a chosen EAT, or
   appears in the same capture's advice rather than next capture:
   **INVALID**; reject all affected trajectories.
2. The body/UC/memory and internal effect do not roll back in one
   SQLite transaction, or a veto/refusal produces an action: **INVALID**.
3. Prior aversive memory disappears when the individual later eats:
   **INVALID** (a need-driven choice never erases experienced harm).
4. Need-on and need-off have identical matched-history decisions:
   **NO OBSERVED NEED EFFECT**. Same for aversion-on vs aversion-off:
   **NO OBSERVED AVERSION EFFECT**.
5. One or more arms never personally experiences eating:
   **NOT_IDENTIFIABLE_NO_EXPOSURE**, not evidence for or against
   spontaneous nutritional learning.
6. Differently truncated histories or terminal times are interpreted
   as a common-horizon survival advantage: **INVALID SCIENTIFIC CLAIM**.
7. The primary difference is generated by the explicit hand-coded
   formula but described as naturally emergent hunger: **OVERCLAIM**.
8. More than 16 instances, any parameter change after seeing outcomes,
   artificial EAT script, unbilled UC, old +9 exploration, extra seeds,
   or use of a second persistent owner: **STOP**.

**Report ALL failures and nulls**. The smallest successful claim would
be: *within a disposable model, a precisely specified competition rule
responded to source-bound separate experienced nutrition, aversion and
previous body energy in an identifiable matched post-exposure choice*.
Do NOT infer broad natural autonomous learning, feelings, or
independently authenticated life.

## Authorization boundary and required decision

This proposed numeric table is **not yet an approved freeze**.
A project-owner comment/ADR must expressly:

1. **ACCEPT_LOCK_V1_R1**, **REVISE_LOCK_V1_R1**, or **REJECT_LOCK_V1_R1** (the original PR #810 candidate's capture-3 endpoint is withdrawn);
2. pin the exact SHA of this candidate and approve/reject *all* constants,
   arithmetic, scenarios, bounds, ablations and stop conditions;
3. separately **AUTHORIZE_ONE_NONLIVING_G1LAB_RUN** or keep the execution
   blocked, since adopting scientific design is not permission to
   implement behavioral valuation or run the model.

Only after this explicit decision may a narrow implementation PR be
opened for the single bounded study. No social experiment is included.
Independent G1-LIVE review #662, real M11, G0 custody and living G3 #664
remain separate and blocked; `src/i2/engine.json` stays inactive.
