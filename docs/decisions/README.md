# Architecture Decision Records

An ADR records a **shared architectural decision** after sufficient evidence or explicit constraints exist.

It is a memory of why the reference architecture changed.

## Use an ADR when

Examples include:

- changing a shared cognitive interface;
- changing the global execution cycle;
- changing a structural relationship between several modules;
- adopting a dependency that becomes part of the reference baseline;
- changing a shared benchmark definition in a way that alters result interpretation;
- promoting a candidate I(n+1) to a new reference generation.

## Do not use an ADR for

- a local choice inside one EXP;
- a compatible refactor;
- a minor dependency update;
- an ordinary bug fix;
- a prototype choice that has not become shared reference behavior.

## Evidence first

An ADR should point to the EXPs, benchmarks, measurements, or explicit constraints that motivated the decision.

An ADR never replaces an experiment.

## Lifecycle

A typical architectural change looks like:

**Question -> EXP -> Results -> Shared decision needed? -> ADR -> Reference update**

If the result remains local to the experiment, no ADR is needed.

## Naming

Use sequential files:

```text
ADR-0001-short-title.md
ADR-0002-another-decision.md
```

The number records order, not importance.

## Template

Start from [ADR_TEMPLATE.md](ADR_TEMPLATE.md).

A filled illustrative example is available in [../../examples/adr-example.md](../../examples/adr-example.md).

## Accepted decisions

- [ADR-0001: strict autonomy of architectural generations](ADR-0001-strict-generation-autonomy.md) (31 October 2026). Mandatory for all future engine work; older generations are research references, not runtime dependencies.

- [ADR-0002: scientific prototype first and drift escalation](ADR-0002-scientific-prototype-first.md) (1 November 2026). Prioritize falsifiable end-to-end behavior and flag research-direction drift; does not authorize a living I2.

- [ADR-0003: integrated living I2 demonstration as the next milestone](ADR-0003-integrated-living-i2-milestone.md) (1 November 2026). Reaffirm the scientific goal and narrow the route through independent G1 review; no living authorization.

- [ADR-0004: evidence-driven development and G2 stop rule](ADR-0004-evidence-driven-development-and-g2-stop-rule.md) (1 November 2026). Next I2 task is independent G1 review and then the minimum G3 living loop; no synthetic G2 campaign or permission bypass.

- [ADR-0005: authorized non-living integrated G1-LAB, G1-LIVE unchanged](ADR-0005-authorize-nonliving-integrated-g1-lab.md) (1 November 2026).

- [ADR-0006: evidence-grounded aversion reappraisal](ADR-0006-evidence-grounded-aversion-reappraisal.md) (1 November 2026). A hidden payoff change is not learnable from an unchanged chosen-outcome history; stale +9 remains an artificial comparator.

- [ADR-0007: separate physiological need, nutrition and aversion](ADR-0007-need-nutrition-aversion-scientific-design.md) (1 November 2026). Owner accepts the scientific model and four-arm research design in principle, NOT an executed or parameter-frozen study; G1-LIVE/M11 unchanged.

- [ADR-0008: retire obsolete mandatory external G1 review for I2 prototyping](ADR-0008-remove-obsolete-i2-external-g1-review-gate.md) (1 November 2026). Supersedes earlier two-reviewer and G0-before-coding holds; authorizes autonomous isolated I2 implementation #664, with real technical/scientific safeguards and no automatic active-engine promotion.

- [ADR-0009: I2 physiology and temperament comparability](ADR-0009-i2-physiology-temperament-parity.md) (2 November 2026). Physical and birth-trait parity is required before claiming cross-generation adaptation, without runtime dependence on I1.

- [ADR-0010: stable-world prior and evidence-based associative memory](ADR-0010-stable-world-evidence-based-association.md) (3 November 2026). Unobserved world changes cannot be inferred from time; real targeted experiences accumulate without instant erasure, and innate need is kept distinct from learned resource efficacy.

- [ADR-0011: I2 integrated spatial life, experienced place value and longitudinal priorities](ADR-0011-i2-integrated-spatial-life-priorities.md) (3 November 2026). Owner-approved P0-P5 priority, source-locked same-life return falsifier and no-heuristic-drift requirement, without activation or scientific GO.

- [ADR-0012: I2 scientific development through integrated behavior, generalization and convergence](ADR-0012-i2-scientific-development-methodology.md) (3 November 2026). Owner-approved development method, with a single [I2 operational protocol](../../src/i2/docs/SCIENTIFIC_DEVELOPMENT_METHOD.md); no new experimental or engine authorization.

- [ADR-0013: lived autonomy and experimental restraint](ADR-0013-lived-autonomy-and-experimental-restraint.md) (3 November 2026). Owner-approved research and architecture direction: build the conditions for an individual's own fallible behavior, not a prescribed successful life. The [I2 architecture/science plan](../../src/i2/docs/EMBODIED_AUTONOMY_RESEARCH_PLAN.md) translates it into falsifiable observations; the existing roadmap and method remain canonical.

- [ADR-0014: I3, an individual whose stake is itself, in a persistence-selected lineage](ADR-0014-i3-lignee-enjeu-de-soi.md) (5 November 2026). Owner-accepted I3 research proposal: lifetime persistence as the only selection criterion, generic heritable genes, reformulated birth invariant; I3 unregistered.

- [ADR-0015: I3 gates judge an architecture on its best selected genomes](ADR-0015-i3-portes-sous-selection.md) (5 November 2026). Owner-accepted gate method for I3, applied on the funded v2 substrate; the first application (G2d, v1 physics) is archived and does not certify v2.
