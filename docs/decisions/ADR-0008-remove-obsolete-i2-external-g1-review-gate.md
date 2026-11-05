# ADR-0008 - Retire obsolete mandatory external G1 review gate for I2 prototyping

**Status: ACCEPTED by the project owner, 1 November 2026.**
**Supersedes only the procedural external-review prerequisites in ADR-0002/0003/0004 and the dated I1->I2 transition instructions.** It does not rewrite those historical decisions, past experiments, or scientific findings.

## Why this change is needed

The owner explicitly withdrew the old requirement to obtain two independent third-party G1 architecture/science verdicts before any further I2 development: **"Retire ces exigences, ce sont des consignes périmées."** The G1 process had become an administrative development blocker despite an expressly requested functional scientific prototype. A mandatory independent *human reviewer* is not the same thing as an independently owned engine, an independent test cohort, or a technically independent anti-rollback witness.

## Normative decision

1. **No mandatory external G1 certification.** Do not require two reviewers, reviewer nominations, an external signature, `ACCEPT_G1_ARCHITECTURE`, or closure of #662 as a condition for implementing, executing, debugging or testing an I2-owned **isolated research prototype**. G1 becomes an **internal falsifiable contract checklist**, not a human approval queue. Independent peer review may be solicited voluntarily and may be valuable, but cannot block engineering.
2. **Prototype development is authorized now.** Proceed autonomously on #664 with a minimal integrated I2-only sandbox loop: fresh local identity; a single canonical state owner; WorldBody, body energy/resources, UC accounting and memory; fresh first-person capture; paid competition and explicit motor admission **inside the isolated research world**; deterministic physical consequence; later personally observable feedback; and a no-learning ablation. Prefer the shortest working vertical path, not another disconnected G2 guard campaign. A prototype can model birth and death and execute internal actions without being registered as the active engine.
3. **Scientific claims still require evidence, not reviewer rituals.** Track exact source/test SHA, real selected and admitted internal actions, delayed causal observation, UC, negative outcomes, terminal behavior, role reversals and controls. Distinguish a software PASS and engineered toy response from proven H1/H2/H3, authenticated M11 or generalized adaptation. Freeze confirmatory N/horizon/seeds/endpoints before G4/G5 comparisons; do not rerun the completed one-shot G1-LAB v1-r1 factorial under its exhausted authorization.
4. **Trust and safety are properties to implement and test.** No I1 runtime or living memory imports; no hidden-world oracle, free UC, researcher-forced action passed off as autonomy, unbounded external motor authority, postmortem recovery, equivocation or rollback described as safe. Local SQLite mock witnesses are not external monotone attestations. If the prototype lacks an independently governed M11 trust anchor, report `M11_NOT_ESTABLISHED` and fail closed on uncertain commits; do **not** claim independent anti-rollback, real-world exactly-once effects or recoverability.
5. **G0 custody is parallel, not a prerequisite to sandbox I2 coding.** Preserve the I1 reference and recorded A1-C `NO_GO`, A2-R `0/96`, source hashes and private archive custody. G0 gaps may still prevent an honest I1/I2 scientific comparison or historical reproducibility claim; they do not stop a new isolated I2 prototype.
6. **No automatic registration or scientific promotion.** Keep `config/engine-registry.json` on I1 until the I2 implementation, engineering safeguards and scientific evidence justify an explicit **owner release decision**. That is project governance, **not external certification**. This ADR authorizes building and bounded internal testing now; it is not an assertion that a living M11 system, its physiological mortality guarantees, or learning efficacy already exists.
7. **Agent routing and drift control.** Prioritize #664 for the next scoped vertical implementation, track #661 separately, retire the procedural request #662 and update the research coordinator, dossiers, tests and agent instructions to stop recommending external G1 signoff as a prerequisite. Escalate only genuine technical/scope conflicts; do not ask the owner to certify an agent's routine work.

## Minimum evidence for the next increment

**Question:** can personally experienced action consequences change a later I2-owned admitted decision (H2) while the full loop pays UC and preserves H1 provenance and H3 arbitration?

**Falsifier:** same-step unseen feedback, forced eating, unchosen-oracle data, motor admission without a fresh veto, learned and ablated trajectories indistinguishable where a difference is claimed, replay/terminal resurrection, or source-dependent I1 state.

**Deliverable:** a runnable isolated research loop and an exact-SHA compact test/trace with all failures and limits, not a manufactured `G3=PASS`. The next engineering issue is [#664](https://github.com/josselin-orta-lab/individual-zero/issues/664).

**Non-retroactivity:** older PRs, G1 review handoffs, parameter-lock documents and scientific reports retain their historical text and exact source pins. This ADR supersedes their outdated instructions when selecting work after 1 November 2026.
