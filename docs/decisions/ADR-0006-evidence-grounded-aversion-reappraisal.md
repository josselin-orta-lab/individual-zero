# ADR-0006: Evidence-grounded reappraisal of learned aversion

**Status: ACCEPTED as a project-owner scientific interpretation, 1 November 2026.**
**Scope:** I2 H2/H3 research interpretation; no G1-LIVE, M11, G3, G4 or birth authorization.

## Context and evidence

The non-living G1-LAB changed the hidden eating payoff from harmful to beneficial at capture 5. The chosen-only observational agent did not eat after this hidden change. Its **observed history in the recovery and persistently adverse worlds was identical**: chosen `CECCCCCC`, energy `[22,12,10,8,6,4,2,0]`, and synthetic UC spent `38`, with modeled terminal at capture 8. Because it never tried eating again and received no other discriminating cue, it could not infer that the payoff had changed. Calling the non-retry a failure of learning confuses hidden information with a learning deficiency.

The previously built G2 stale-revisit heuristic (`revisit_after=2`, `revisit_bonus=9`) recovered eating in the recovery scenario of PR #801, but also caused a second harmful eating and early death under persistent adversity, and worsened survival after reversal. It was **researcher-authored**, not an endogenous individual motive. The prior +5 observational offset was historically adjusted post hoc. A stable collect/eat pattern also occurs with learning disabled.

Exact-source evidence: PR #800 merged `175a78f877b2a0085d20c980f03968b2dbd58fec`; PR #801 merged `cb540875dc6949111b951362d948f57b7b5e19aa`. Frozen protocol and results: issue #662, comments 6559888186 and 6559926796.

## Decision

1. **Correct the scientific verdict:** classify non-retry after a hidden unsampled recovery as `LATENT_CHANGE_NOT_IDENTIFIABLE_FROM_CHOSEN_EVIDENCE`, **not** a standalone H2 learning failure. Preserve negative modeled energy, death and UC observations unchanged.
2. A negative experience is not to be automatically reappraised merely because some captures elapsed. **Do not promote the +9 stale-choice bonus as a default natural low-abstraction I2 mechanism.** Keep it only as a clearly identified hand-coded exploratory comparator.
3. Distinguish (a) negative associative memory, (b) newly perceived information suggesting changed outcomes, (c) physiological/motivational competition that can justify risk despite aversion, and (d) newly chosen experience that confirms or refutes the change. A decision under hunger does not erase past harm.
4. A future reappraisal hypothesis requires a traceable source, such as direct subsequent safe experience, changed context/sensory evidence, an observed conspecific with uncertain provenance, or a well-specified physiological need. **Social information is a possible input, not an obligatory biological prerequisite or infallible proof of food safety.**
5. Specify observability and causal controls in any future protocol. Without a new observation or action, the adverse and recovered worlds can be observationally indistinguishable; even an arbitrary exploration policy cannot *know* which world it is in before sampling. Distinguish learning, information gathering, and externally hard-coded exploration.
6. This interpretation does **not** authorize additional G1-LAB policy campaigns. A social/drive hypothesis requires separate owner-approved falsifiable scope, controls and negative predictions. G1-LIVE still requires two independent architecture/science reviewers, external M11 and G0. I2 remains proposal-only and not born.

## Biological qualification

Socially transmitted food preferences and modifications of learned aversions have been demonstrated in particular laboratory rat paradigms (Galef & Wigmore, 1983; Galef, 1986). Individual extinction under later unreinforced/safe exposure is also documented in conditioned taste-aversion literature. These observations **do not establish** that any animal or low-abstraction agent will never reattempt harmful food without social example, nor validate the I2 toy model. Sources and caveats are summarized in the linked [scientific analysis](../research/studies/i2-g1lab-aversion-reappraisal-2026-11-01/README.md).

## Consequence and review

This ADR adopts an interpretive and protocol-design correction, **not a scientific GO**, birth permission or independent review. The integrated lab remains non-living, deterministic, exploratory, one trajectory per arm and regime, with researcher-specified prior scores. No new code or policy tuning is authorized by this ADR. Next critical path: independent G1-LIVE review, issue #662.
