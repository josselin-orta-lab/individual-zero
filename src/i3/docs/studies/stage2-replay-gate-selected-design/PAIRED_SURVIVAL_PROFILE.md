# Stage 2.1 v3: prospective paired-survival interpretation profile

**9 November 2026 · SOFTWARE-ONLY CANDIDATE · NOT A PREREGISTRATION OR SCIENTIFIC GO.**

This document accompanies the separate [mechanism-first G0 design](MECHANISM_FIRST_CANDIDATE_V3.md) and its [sealed-original reader](MECHANISM_FIRST_SEALED_READOUT.md). It supplements, never rewrites, the historical 80/81 result, the original selected-lineage design, the v2 inference audit, or any frozen policy. No World was run to prepare this contract. P1.3 funded-v2 remains reference and I3 remains unregistered.

## The specific inferential trap

A finite-panel mean difference of zero is **not** evidence of no harm. Imagine two otherwise equal G0/world pairs: GATE dies at step 100 while FIXED lives through 400 in the first; the reverse happens in the second. Both the overall survival difference and average lived-step difference equal zero. Nevertheless, one individual under GATE has suffered a 300-step loss. The loss may be concentrated in one ecological family, and a lower cognition bill may arise only because the GATE life died earlier.

The already proposed v3 `descriptive_readout` reports equal-population mean contrasts. Those are necessary, but alone they hide survival reversals and tail severity. A paired **discordance profile** makes the full finite target explicit without new thresholds.

## Interpretation order for a future authorized v3 panel

1. **Receipt completeness first.** The 720 assigned lives, 240 identical newborn-G0/world blocks and three fixed policy arms must be present. Structural failures are **NO_VERDICT**, never rewritten as deaths, zeros or excluded survivors. The existing read-only `stage2_mechanism_first_sealed` checks original source/manifests only against caller-supplied pins; external pre-exposure authority is not established by successful parsing.
2. **Unconditional, matched outcomes.** For GATE minus FIXED and GATE minus RANDOM, each block reports whether both survived the 400-step horizon, only GATE survived, only the comparator survived, or neither survived. Death **on** step 400 is still death, even if lived steps are 400. Also count blocks where GATE lived longer, shorter or equally long, retaining the worst and best observed lived-step differences.
3. **Harm alongside paid cognition.** Count blocks in which GATE lived less while paying less energy or vigilance, and blocks where it paid less energy but lost horizon survival. These are *co-occurrences*, not proof that energy savings caused mortality. Report actual charged energy/vigilance per **assigned** life, not only per lived step.
4. **Never collapse unfavorable ecology.** Publish the same complete profile for each of the three familiar F0 families (80 paired blocks per arm contrast) and eight population labels (30 paired blocks each), in addition to the overall 240. No family may be omitted or reweighted after outcomes.
5. **Keep mechanisms separable in interpretation.** GATE minus FIXED compares complete replay policies, not context-sensitive choice alone. GATE minus RANDOM is a closer choice/control contrast, but RANDOM's historical nominal 5532/867 schedule does **not** guarantee equal *physically paid* replay work; the original [exposure readout](MECHANISM_FIRST_SEALED_READOUT.md) separately reports funded/eligible/paid amounts. Post-outcome filtering to matched paid work would change the target and is prohibited.

The pure helper `stage2_mechanism_first_design._paired_outcome_profile` computes these **descriptive finite-panel** counts, always returning `statistical_inference=NOT_ESTABLISHED`, `survival_noninferiority_certified=false` and `causal_replay_selection_advantage=NOT_ESTABLISHED`. Because the profile is part of the existing `descriptive_readout`, the sealed-original adapter obtains it without any new execution or admission route.


## Third policy contrast: RANDOM minus FIXED (follow-up, 9 November 2026)

The two existing contrasts alone invite an attribution error. Comparing GATE with FIXED measures the *whole policy difference* (including audit, funding, replay counts and downstream decisions); comparing GATE with RANDOM is closer to replay prioritization, but actual replay quantities may differ. The **third** matched control, RANDOM minus FIXED, must therefore be reported explicitly rather than inferred in prose. It asks whether the full RANDOM funded-replay policy differed from the reference at the same newborn-G0/world slots.

The read-only `random_fixed_control_bridge` from `stage2_mechanism_first_design.descriptive_readout` reports all **240** matched RANDOM/FIXED blocks, the three F0 families (80 each) and eight population labels (30 each). It provides mean differences in lived steps, horizon survival, physical energy/vigilance paid per assigned life and inactivity, plus both survived, RANDOM only survived, FIXED only survived, neither survived and longer/shorter lived-time counts. It never changes the original v3 cohort, adds a policy or reruns a life. The sealed-original reader automatically obtains this addition from the existing reduced readout.

For any additive **matched** outcome (Y), at every block and hence for an equally weighted finite-panel mean:

`Y(GATE)-Y(FIXED) = [Y(GATE)-Y(RANDOM)] + [Y(RANDOM)-Y(FIXED)]`.

The software exposes the largest absolute numerical residual for the five named outcomes, preserving any floating-point rounding as a diagnostic. This equality is an **accounting identity**, not statistical significance, a causal mediation model, proof that RANDOM isolates only the audit cost, or confirmation of equal physically paid replay work. All three policies can change behavior and survival. Never promote a favorable triangle into a superiority or non-inferiority verdict, and never filter to a post hoc matched-payment subset.

**Interpretive stopping point:** these three-policy finite-panel quantities are adequate to *describe* full-policy differences if a separately authorized source-locked F0 study ever takes place. They cannot establish evolutionary advantage, transfer to unseen ecologies or justify new World exposure. Before that, the next meaningful intervention is independent adjudication of the mechanism-only objective and its valid study protocol, not additional automated acceptance thresholds.

## What the result cannot authorize

The proposed eight labeled populations and correlated world/genome blocks are not proven independent random samples from a broader ecological population. No confidence interval for generalizable non-inferiority, biological loss margin, family transfer claim, multiplicity rule, joint power estimate or automatic positive GO follows from this profile. Nor does a count of a severe subgroup establish a population-level frequency outside this finite F0 panel. The current eight-population mean non-inferiority **NO_GO** remains untouched.

**Next owner/reviewer decision:** choose a question and estimand *before any exposure*. A modest descriptive mechanism-only study can report all matched outcomes and their costs without claiming evolutionary selection or mean-survival non-inferiority. A confirmatory survival claim instead requires justified population sampling, meaningful loss margins and power, independent methodological review, externally attested source/World custody, explicit new index-scoped authorization and full engineering G/R rehearsal. Neither decision has been taken here.

**Status: NO SCIENTIFIC WORLD OPENING; RESEARCH DESIGN STILL PROPOSED.**
