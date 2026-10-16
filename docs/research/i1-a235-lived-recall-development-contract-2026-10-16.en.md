# A2.35 I1-only development contract: recalled proximal evidence in option valuation

**Development freeze:** 2026-10-16. **Source:** I1 PR #219, SHA `5bc310b8e75aac45796e35ca8193ecee7ac01070`. **Branch:** `experiment/i1-a235-lived-memory-choice-20261016` stacked on I1, not `main`.

## Scientific rationale

A2.34: 48/48 mortal lives closed episodes, had spontaneous recall and placed memory contributions in S_t; 0/670 I1 factorized-option evaluations used a learned value. The current I1 experimental evaluator uses a static score 0.35. This establishes a consumer gap **only for the experimental factorized path**, not all Stage8 cognition.

## Policy `i1-lived-proximal-review-v1`

**Explicit birth opt-in, disabled by default.** Requires I1's already opted-in model and an individual ID from an I1 mortal birth. Positive, versioned **1-UC per candidate review**, charged in the Competition module (in addition to model forecast UC); no added unpriced read. Insufficient UC causes conservative fallback to the historical I1 score 0.35 with an explicit refusal receipt. Model policy, cost and version are pinned into M11's birth fingerprint. Existing I0 and I1 lives retain their histories and behavior.

Only an existing, closed Episode in the **same I1's Memory owner**, an actual `memory_recall_proposed` contribution selected into this cycle's **S_t**, and first-person data retrieved through `JournalViews.autobiographical` with Stage2/7 explicit projection policies can affect the proposed I1 option. A previous `command_experienced` must match `collecter berry_b`; a same-world-step `world_transition_experienced` may then supply a **positive** `effects.collected.kind=berry_b`, integer quantity > 0. The episode must be strictly earlier than the current decision and both event IDs in the episode source refs. The current candidate must be the same primitive and observed local berry resource. A successful proximal collection is evidence that this particular action *was* effective once, **not** a certificate of present success, future resource availability, food safety, or distal goal agency.

Bounded evidence preference: historical baseline `0.35` becomes `0.45` **only** for a matched, uniquely source-backed proximal-success recall. Scores are **instrumental hypotheses**, not learned TD Q-values, probabilities or calibrated protection. Preserve `learned_value_status=unlearned`, `risk_status=unknown`, `safety_uncertainty=1`, and add source IDs to the evaluation. All failures to establish evidence (no recall admitted, no prior source, missing collected effect, forced failure, mismatched command, causal confusion, future timestamp, UC denial) give **NO enhancement**. Never interpret absence of a `collected` effect as proof of failure; a forced physical failure is *not* disclosed to I1. Hidden injury and lethal-zone labels remain inaccessible. No special permission is given to ingest a berry.

The selection still passes through existing Competition → Stage9 → Action Control → WorldBody. There is no alternate decision engine or physical sender.

## Software acceptance prior to prospective A2.35 science

- Pure tests: positive same-episode command/effect/ref linkage, forged external labels denied, missing/zero effect and mismatched resource abstain, future step/cross-episode/cross-life/missing S_t abstain, score doesn't promise Q learning or safety.
- Actual mortal life: before a **real first** collection, no enhancement; after a **real experienced** successful collection and later genuine recall admitted to S_t, I1 can adjust the next eligible option; the same life with policy OFF retains baseline. No synthetic operator truth is passed into either life.
- Negative mortal life: externally forced first collection failure cannot be treated as past successful collection merely because the command was issued. Nonterminal injury doesn't become `known lethal`.
- M11: birth-on/off fingerprint difference, cold recovery cannot silently enable/reprice this policy, copy/restore consistent. Both Python 3.11 and 3.12, plus unchanged I0 regression suite.
- Scientific protocol for novel heldout autonomous pairs must be separately preregistered before executing a new cohort. These development tests **cannot prove** generalization, safe exploration, causal identification or an improved life expectancy.

**Decision:** A2.35 is a new isolated **experimental candidate**, not a normative change to v1.3.3 and not deployment authorization. I0 unchanged; no automatic merge to I1 #219 or `main`.
