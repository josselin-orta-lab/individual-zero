# ADR-0007 - Distinguish physiological need, experienced nutrition and aversion

**Status: ACCEPTED by project owner as a scientific interpretation and experimental design direction, 1 November 2026.**

**Study status at original ADR acceptance (historical):** PENDING_PARAMETER_FREEZE; NOT_AUTHORIZED_TO_RUN; NOT_EXECUTED.

**Subsequent separately authorized execution (1 November 2026):**
The owner later accepted the exact v1-r1 numerical lock (Git blob
`a279067fbfd21f02ee4aa7854509c19f12cfbb62`) and authorized
**one bounded non-living G1-LAB study** in
[issue #662](https://github.com/josselin-orta-lab/individual-zero/issues/662#issuecomment-6561384748). PR #814 implemented the single 16-arm
deterministic factorial; PR #815 froze the
[complete outcome report](../research/studies/i2-g1lab-need-aversion-protocol-2026-11-01/execution-report.md).
Observed mechanistic score/action differences do **not** establish natural
autonomous learning; the fixed-prior control also completes collect/eat,
and the high-energy aversive full arm abstains on a tie. **No rerun or
parameter tuning is authorized by that exhausted one-shot permission.**
The rest of this ADR documents the *original* decision and its
pre-approval restrictions. The approved exact parameter-lock source remains
unchanged; G1-LIVE, M11 and G3 are still blocked.
**Scope:** I2 disposable, non-living G1-LAB research only. G1-LIVE/M11/G0/G3 and independent reviews are **unchanged**.

## Context and original evidence

The project owner accepted the scientific analysis following
[PR #808](https://github.com/josselin-orta-lab/individual-zero/pull/808),
which contributed the [prospective candidate protocol](../research/studies/i2-g1lab-need-aversion-protocol-2026-11-01/README.md)
on commit `34bcb1f4c5277a602e625a871b72895813c5a746`.

These claims are already supported by *exploratory software evidence*, not
by an established living individual:

- [PR #805](https://github.com/josselin-orta-lab/individual-zero/pull/805)
  showed that first-person evidence can distinguish model energy 17 versus
  60 without changing the current policy's selected actions or paid UC:
  **energy is represented, not yet used as a motivational variable**.
- [PR #807](https://github.com/josselin-orta-lab/individual-zero/pull/807)
  distinguished physical `metabolic_debit` from
  `food_energy_impulse` in the SAME local SQLite commit. Neither field
  independently represents pain, aversion or physiological hunger.
- [ADR-0006](ADR-0006-evidence-grounded-aversion-reappraisal.md)
  established that a hidden recovery, without a new first-person cue or
  chosen eating result, is not inferable from the individual's available
  experience. The researcher-authored `revisit_after=2` / `+9`
  comparator is **not** a natural low-abstraction mechanism.
- The existing cognitive `ObservedChosenResult.observed_net` remains a
  **single signed net-energy observation**, not a pair of separable
  nutrition and aversive-sensory experiences.

## Options and scientific interpretation

**Rejected:** label a negative food-energy impulse as pain or learned
sensory aversion; use an arbitrary low-energy EAT bonus; force an eating
attempt as training; erase negative memory when the individual chooses
risk; or infer an unexperienced environmental reversal.

**Accepted research framing:** model and measure distinct causal channels:
1. **Previous committed physiological energy**, interpreted only as a
   *toy observable need proxy*, not as proven subjective hunger.
2. **Nutritional benefit from a personally chosen action**, as a separate
   delayed consequence, not as a fabricated counterfactual.
3. **Independent aversive sensory input from the same chosen action**,
   explicitly simulated and fallible, not inferred from energy loss.
4. **Persistent outcome-specific memory and paid action competition**,
   with actual synthetic UC, vetoes, abstentions and simulated terminal
   consequences reported separately.

These channels make two *falsifiable research questions* possible:
`H-N`: does previously observed body energy change the action competition
when nutritional and aversive evidence are fixed? `H-A`: does remembered
aversion change the competition when body need and nutrition evidence are
fixed? Both may have negative or unidentifiable answers.

## Decision: approve the conceptual design, not the experiment yet

The project owner accepts the **factorial, ablation-led design in
principle**. A later separately authorized G1-LAB experiment must
compare four independently initialized, equal-initial-budget arms in
each frozen environment: **full**, **need-off**, **aversion-off** and
**fixed no-learning**. Compare like prior histories where possible and
report failed exposure, different deaths/horizons, chosen actions,
provenance, actual UC, memory retention and all null/adverse outcomes.

The candidate equation in the prospective protocol, including a
researcher-defined deficit and a score term for observed nutrition
minus aversion, remains a **hand-designed hypothesis**. Approval of
the research framing is not approval of the numerical equation as a
natural mechanism, nor scientific evidence for autonomous learning.
Any causal result must survive the need-off and aversion-off controls,
and may still show only how the **engineered** rule operates.

**Before authorizing any behavioral code or run**, the following are
still required and must be reviewed/frozen without outcome-driven
tuning: the actual numeric nutrient and aversive signal magnitudes,
the nonaversive/aversive scenarios, exact integer arithmetic and
clipping/tie handling, finite runs/seeds and step horizon, initial
resources, comparability and censoring criteria, explicit falsifiers,
and a stop condition. The candidate energy states 17 and 60 were
already used by PR #805; results with them cannot be represented as
independent confirmatory generalization.

There is **no authorization from this ADR to start a new experiment,
implement a new valuation policy, alter priors, create an additional
owner, introduce social observation or use the old +9 revisit bonus
as a default**. Further implementation needs a **separate explicit
owner approval of a complete parameter-locked protocol**. A software
test PASS cannot replace causal evidence or independent review.

## Consequences and research gates

- Keep G1-LAB a disposable non-living integrated laboratory, under
  [ADR-0005](ADR-0005-authorize-nonliving-integrated-g1-lab.md).
- Preserve source-bound first-person chronology: a selected consequence
  can only enter cognitive evidence at a later capture; unchosen
  alternatives and hidden regimes never enter the individual's memory.
- Preserve the aversive association even when competing need leads to
  risk-taking. Social demonstration, if considered later, is a
  **separate** hypothesis, not an obligatory biological prerequisite.
- Reject a claimed `H-N` or `H-A` effect if the respective full and
  ablated arms do not provide a discriminating observed contrast.
  Absence of usable chosen experience is `NOT_ESTABLISHED`, never
  manufactured learning.
- This ADR is the **owner's scientific decision**, not an independent
  peer review, G1-LIVE acceptance, M11 attestation, motor authority,
  engine registration, irreversible living death, or a G3 birth.
  Independent architecture/science G1 reviews remain due in
  [issue #662](https://github.com/josselin-orta-lab/individual-zero/issues/662).

**Original decision date/status (2026-11-01):** scientific framing
accepted; parameter freeze and experimental execution were **pending at the
time of adoption**. The later one-shot authorization, execution and
non-living scientific limits are documented at the top of this ADR.
