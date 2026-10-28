# I1 #438: preregistration, paired natural M11 Stage8 Q-read contrast

Date: 2026-10-28. Base `main`: `c0094628d9dd1b17d000da0d140401446991ae20`. Scientific owner: issue #438; related #304 and #305. This is a **bounded research comparison**, never a canonical I1 change.

## Scientific question

Can an **actually learned**, first-person TD/Q value, when read by the normal Stage8 evaluator, change an autonomous motor action during a fresh physically admissible choice, **without confusing that difference with different born physiology, environment, P-40, seeds, or UC?**

Prior evidence from natural paired test #434 (CI #590 / run #40656518108): 13 changed-Q Stage8 reads carried through paid Competition, but 13/13 had distinct pre-action body conditions after reciprocal nutrition; 0 rank/crossing/admission differences. Merely comparing those two different bodies cannot isolate Q.

## Prospective intervention fixed *before birth*

- Engine: current generated I1, canonical `birth_i1_m11` from this PR SHA. I0 remains unmodified.
- Registered world: immutable `dry-valley` preset, with its actual **born v4 metabolic physics** as instantiated by `I1Runtime`. World layout, food effects, other sources and all costs identical. Same `life_id` across two **separate** independently committed M11 SQLite ledgers, to hold birth temperament constant. Up to **12 naturally chosen physical steps per arm**, stop on real death.
- **Control arm:** unmodified natural I1, complete TD/Q write/read behavior.
- **Research arm only:** a test-process, pre-birth-installed wrapper of the existing `Stage8OptionEvaluator.evaluate`. During this one ordinary paid evaluator call, `LinearTDValues.learned_value` is invoked **exactly once** and its genuine answer observed by the operator; Stage8 receives a typed `unlearned` / no-value result instead of the Q readback. The patch is scoped to Stage8 only. Outside Stage8, including Planning's existing personal Q read and all TD updates, the canonical owner method remains untouched.
- No fabricated Q, preset reward, command script, experience injection, privileged map, extra cognitive cycle, threshold change, TD coefficient, sleep priority, Competition shortcut, Action Control override, safe-life guarantee, or mutation of a committed life.
- Variant scope and identity must appear explicitly in the machine-readable report. The ablated arm **must not** be described as canonical natural I1, only as an independently mortal research contrast.

## Hypotheses and primary endpoint

- `H0`: the Stage8 learned-Q read has no attributable effect on a physically applied action during naturally offered opportunities in this 12-step pair.
- `H1`: after authentic TD experience and a real Stage8 learned-Q read, suppression of only that read produces a **different physically committed command** at the **first divergent step** while pre-step world/physiology, previously owned TD state, active goal, Competition state and P-40 are equal. This establishes only a limited **causal effect of Stage8 Q read** on that first action in this matched laboratory comparison, **not** learned usefulness, preference generalization, or survival advantage.
- Required provenance: positive learned Q in unmodified Stage8, same option/cycle in ablated Stage8 where available, both real Competition cycles, Action Control admission, identical pre-divergence physical prefix, command experienced, committed generation, journal head integrity, actual birth physics digest.
- Even a changed Option ID without a changed **command primitive/parameters** is only `OPTION_ID_DIFFERENCE`, not a physically different action.
- A first action difference **before** the first learned Stage8 suppression, or an initial-body/world discrepancy, invalidates the causal claim. A difference with already divergent goal/Q/Competition/P-40 is `INCONCLUSIVE`, not a clean Q-only GO.
- If the natural life never exposes a learned read or matched action opportunity, report `NOT_EXPOSED`. If exposure exists but no changed command, report `L3_NOT_ESTABLISHED`, not a code bug.
- Any subsequent physiology after the first action divergence is **not matched** and cannot be used to claim a clean Q-only survival effect. Both deaths and censored lives are retained.

## Outcomes and checks

Read-only fields from both genuine M11 journals: `command_experienced`, `command_admitted`, `td_update_published`, `stage8_option_evaluation`, `competition_cycle`, `stage10_sleep_pressure_frozen`, `compute_charge`; plus pre/post own-body, location, inventory, owner images (read only) and source ledger audit. Stage8 operator observes the same Q calculation already requested; it does **not** perform a second unpaid owner read.

1. Confirm both arms have identical world physics digest, birth perception, setup and pre-step physical prefix until any first different command; preserve original WAL/M11 custody and handle death terminally.
2. Confirm `Stage8OptionEvaluator` calls through normal charged cognition in both arms; any masked read is only inside that method. Track natural learned reads and real stage8/Competition option identities.
3. Compare the first **physically applied command** difference, *if it exists*, to the actual prior learned Q exposure. Require matched pre-step bodily and owner context and same frozen P-40; never pair later diverged bodies as though identical.
4. Record the ordinary paid option proposal, Competition evaluations/crossings, Action Control admission, command application, and pre/post body. Where a source is absent, explicitly mark `NOT_OBSERVED`.
5. No forced scientific positive assertions: outcome may be negative or censored; code fails only when custody, scope, source, provenance or comparison invariants are violated.
6. Any claim beyond a **single matched motor effect** (learning is useful, repeated, durable or general) requires a separately preregistered independent-life/role-reversal study with real outcomes and appropriate controls.

## Integration gates and limits

A passing CI test only validates the harness and whatever bounded life was recorded. Require exact-head Python 3.11/3.12 structural + natural SMOKE/FULL, source parity, M11 custody and I0 no-regression before **any** merge under issue #348. A scientifically negative run is not a reason to adjust reward, exploration, P-40 or thresholds. Treat this preregistration as fixed before examining the new test's output. No changes to `src/i1/modules/`, `src/i1/runtime/` or I0 are authorized by this PR.
