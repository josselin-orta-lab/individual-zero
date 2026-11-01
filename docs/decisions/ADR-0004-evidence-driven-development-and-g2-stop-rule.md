# ADR-0004 - Evidence-driven development, integrated milestones and G2 stop rule

**Status: ACCEPTED, project-owner development-process decision, 1 November 2026.**
**Scope:** development strategy for Individual Zero, primarily I2. This
supplements [ADR-0002](ADR-0002-scientific-prototype-first.md) and
[ADR-0003](ADR-0003-integrated-living-i2-milestone.md); it does **not**
revise ADR-0001, assert scientific G1/G3/G4-G6 proof or promote the engine.
**Superseded procedural clauses:** [ADR-0008](ADR-0008-remove-obsolete-i2-external-g1-review-gate.md)
withdraws the old two-external-reviewer G1 prerequisite and authorizes
bounded local I2 prototype engineering now. The original scientific
limitations of ADR-0004 still apply.

## Problem and evidence

I2 has accumulated valuable synthetic cognition, H2, intention, paid
Competition and adversarial tests but has **no born individual or physical
end-to-end WorldBody**. Successive implementation PRs can validate local
contracts without revealing whether a single individual learns a useful
action from its own consequences.

The historical G2 experiments illustrate why the distinction matters:

- PR #779: chosen-only experience did **not** update matched-pair H2;
  without experimenter-supplied counterfactual episodes its feedback stayed
  at zero.
- PR #784: the research food world had made *drink* consume collected berries
  while *eat* was a no-op; this invalidated earlier food-sequence readings.
  The correction also changed a fixed observation-score offset **after**
  failures were inspected, making later regressions exploratory, not
  preregistered.
- PR #786: a collect -> eat sequence appears even in a **fixed-prior,
  no-learning ablation**. Negative/adverse and recovery results differ among
  observational and revisit heuristics. The separate controller follows
  advice; no actual I2 motor authority, independently witnessed body or
  physical learning has been established.

**DRIFT DETECTED:** repeated small G2 improvements, guard additions and
passing CI are being mistaken for progress toward a scientific individual.

## Normative decision

1. **One demonstrable research question per development increment.** Before
   building, state the H1/H2/H3 claim, a falsifier, no-learning/negative
   control, physical and subjective observables, UC costs, and what a null
   outcome would mean. Prefer a **single minimally integrated demonstration**
   over unrelated local completeness.
2. **Stop the open-ended G2 study campaign now.** PR #786 is the bounded
   diagnostic stopping point, not a foundation for more fixed-prior tuning,
   extra synthetic owners, witnesses, score offsets or CI-only progress.
   New G2 work requires a *specific* critical-path blocker, a reproducible
   correctness defect that invalidates interpretation, or direct verified contract feedback. State the exception explicitly in the PR.
3. **Current critical path (ADR-0008):** start the **minimum isolated I2
   vertical prototype #664 now**, with accountable internal WorldBody,
   observation, paid cognition, action admission and later feedback.
   Keep I1 G0 custody #661 in parallel, not as a coding dependency.
   Once real integration evidence exists, freeze the G4 study protocol
   #663 and perform G5 comparative runs #665 only against valid baselines.
   The retired external G1 review request #662 is not a prerequisite.
4. **First isolated G3 engineering target (authorized by ADR-0008):** one
   independently born generation, one canonical state owner including body,
   inventory, RNG, UC, cognition, memory and terminal; first-person
   observation of the last *externally attested* public revision; paid
   Competition plus fresh normal safety/motor admission; one deterministic
   WorldBody transition with no separate executor; causal observation of
   that action at a later capture; persistent learned change to a subsequent
   choice; and irreversible death/nonrollback. A tiny collect/eat/drink
   world is adequate. External side effects are **outside** this minimal
   model until a separately reviewed effect protocol exists.
5. **Science comparators:** independently initialized learning-enabled and
   learning-ablated individuals must face equivalent laws, candidate
   availability and resource accounting, plus stable, neutral, adverse and
   role-reversal conditions. Log actual action admissions, absent offers,
   abstentions, vetoes, UC charges, true body consequences, subjective
   chronology, survival, death, uncertainty and every negative result.
   Equal **initial funding** is not equal **spent UC** if the choices change
   opportunity counts. Do not post-hoc tune to make the regression green.
6. **Engineering/CI budget:** batch related changes into a coherent,
   reviewable increment. Run targeted tests first; reserve broad/heavy
   CI and living cohorts for their proper gate. Avoid new framework
   abstractions, duplicate state owners and legacy fallback unless an
   explicitly demonstrated critical blocker demands them.
7. **Transparent handoff:** every completed intervention reports exact
   baseline/head SHA, changed files, tests with PASS/FAIL/NOT_RUN, evidence
   distinguished from predictions, open technical dependencies and the next
   falsifying observation. Do not block sandbox coding on a missing human
   reviewer or historical custodian. If a genuine external M11 trust
   witness is unavailable, develop the internal path with fail-closed
   behavior and report `M11_NOT_ESTABLISHED` rather than fabricating one.
8. **No software approval masquerading as science.** An agent may build
   and run isolated internal I2 births and physical simulations under
   ADR-0008. A green synthetic test does not certify H1/H2/H3, M11, or
   independent anti-rollback. No agent may activate the engine registry,
   actuate external hardware or publish scientific GO without the
   relevant technical evidence and owner release decision.

## Immediate intervention authorized by this decision

**Superseded by ADR-0008:** the previous reviewer handoff is now historical.
Use its C0-C11 falsifiers as engineering tests while directly building the
smallest bounded #664 single-owner I2 vertical slice; do not organize another
external certification round or synthetic guard campaign in its place.

See [G1 minimal living-loop review brief](../architecture/proposals/i2-g1-minimal-living-loop-review-brief-2026-11-01.md),
the longer [current-source G1 delta](../architecture/proposals/i2-g1-current-review-delta-2026-11-01.md)
and [publication candidate](../architecture/proposals/i2-g1-single-owner-world-publication-candidate-2026-11-01.md).

## Success condition for the revised development process

The next milestone is **not** PR count, green checks, or stronger isolated
simulation. It is a source-pinned integrated I2 life with objectively
recorded perception -> *admitted action* -> committed bodily consequence ->
later experienced feedback -> changed subsequent action, compared against
a no-learning control, including failure and mortality. Until the integrated behavior is actually observed and verified, report
**NOT_ESTABLISHED** regardless of code completeness.
