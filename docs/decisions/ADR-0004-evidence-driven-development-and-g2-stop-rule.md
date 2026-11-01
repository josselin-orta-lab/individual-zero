# ADR-0004 - Evidence-driven development, integrated milestones and G2 stop rule

**Status: ACCEPTED, project-owner development-process decision, 1 November 2026.**
**Scope:** development strategy for Individual Zero, primarily I2. This
supplements [ADR-0002](ADR-0002-scientific-prototype-first.md) and
[ADR-0003](ADR-0003-integrated-living-i2-milestone.md); it does **not**
revise ADR-0001, waive G0/G1/G3/G4-G6, approve an experimental protocol,
authorize a birth, or establish a scientific result.

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
   correctness defect that invalidates interpretation, or direct independent
   G1-review feedback. State the exception explicitly in the PR.
3. **Critical path, in order:** preserve/independently attest G0 I1 baseline
   (#661), obtain two **independent** documented G1 architecture/science
   review verdicts on current source (#662), then implement the **minimum**
   I2-owned living G3 loop (#664), then independently review a frozen G4
   experimental protocol (#663), and only then run G5 comparisons (#665).
   G0 preservation and G1 review may progress in parallel, but unresolved
   gates cannot be silently accepted or bypassed.
4. **First G3 integration target (only AFTER G1 authorization):** one
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
   distinguished from predictions, open reviewer dependencies and the next
   falsifying observation. If unable to progress because an independent
   role, external witness or operator custody is missing, **stop and
   report the missing decision**, not manufacture a green proxy.
8. **No software approval masquerading as science.** No assistant may
   self-designate an independent reviewer, generate a fictitious G1 verdict,
   register or birth I2, authorize real motor effects or declare G3/M11 from
   passing synthetic tests. The owner may formally revise gate scope,
   but a development agent must never relax it silently.

## Immediate intervention authorized by this decision

Prepare a concise **current-SHA reviewer handoff** for G1, with one selected
single-owner internal WorldBody publication candidate, explicit C0-C11
falsifiers, reviewer-specific decisions, minimal G3 vertical-slice scope,
and failure-stop behavior. Do **not** create new G2 implementations to
substitute for independent review. The handoff is a request for independent
judgment, not an acceptance.

See [G1 minimal living-loop review brief](../architecture/proposals/i2-g1-minimal-living-loop-review-brief-2026-11-01.md),
the longer [current-source G1 delta](../architecture/proposals/i2-g1-current-review-delta-2026-11-01.md)
and [publication candidate](../architecture/proposals/i2-g1-single-owner-world-publication-candidate-2026-11-01.md).

## Success condition for the revised development process

The next milestone is **not** PR count, green checks, or stronger isolated
simulation. It is a source-pinned integrated I2 life with objectively
recorded perception -> *admitted action* -> committed bodily consequence ->
later experienced feedback -> changed subsequent action, compared against
a no-learning control, including failure and mortality. Until gate review
and implementation, report **NOT_ESTABLISHED**.
