# Stage 12 issue #110 — prospective GA-01..07 physical 600-step experiment

**Pre-registration before campaign; status: NOT YET EXECUTED.**
Date: 2026-10-13. Implementation PR #147, normative target PR #148.
Baseline historical main: `f9de6aa6cd11f896db204c0277353989d6445f10`.
Record the exact PR head SHA from the eventual GitHub Actions run; reject artifacts from any different source.

## Question and hypotheses

**H1:** With first-person goal agency and independent joins enabled, genuine autonomous physical steps may yield valid preregistered goal-outcome followups and Action Control judgements. The experiment does not assume either will occur.

**H2:** A low-level subjective self attribution may be supported by a preregistered voluntary ingestion of food and a *separately accessible inventory decrement*, regardless of whether the goal's measured food strict gain succeeds. It is not a claim about hidden food chemistry or proven physical etiology.

**H3:** The current conservative policy does not infer `world` from a failed goal or P-47 discrepancy. Unknown and unavailable judgements are a meaningful result and must be counted.

**H4:** The detector receives a join only when separately lived goal-progress and first-person action evidence agree on one life, goal intent, physical command and observed window, and all UC operations were accepted. If actual admissible successes and failures are below configured thresholds, the output remains `None`.

**H5:** The external auditor rejects forged but fully rehashed independent-source references, duplicate sources, missing/late captures, unsupported agency labels, and unpaid or falsely declared positive bias.

## Locked development fixture

Use `scripts/run_stage12_operator_trial.py --issue110-agency-join --steps 600` in a *new* absolute directory. This reuses the Stage11 geographic and Stage10 awake-only **fixed** autonomous mortal configuration and the Stage12 detector policy from the software operator runner:
`window=12`, `bias_min_outcomes_each=2`, `attribution_bias_threshold=0.75`.
The first-person service cost is 1 UC per attempted judgement and the Metacognition join costs 1 UC when both admissible original sources exist. Both costs are configured before birth and cannot be silently converted to free Lab work. No deliberate decision override, reward injection, P-47 remapping or oracle access is permitted.

Run independent fresh lives for Python 3.11 and 3.12 with their own WAL and cryptographic export. Same fixed seed across interpreters tests implementation determinism, **not** statistical replication.

Stop on death, safety block, transaction failure or operator stop; do not resume or replay a dead identity. Archive all results, including failures. If a trajectory ends before 600, record the exact realized denominator and treat completion as unsuccessful, not as a fabricated 600-step life.

## Mandatory independent metrics

For every run publish: exact SHA, Python version, retained WAL/export, head hash, occurrence count, applied physical steps, last mortal status, source/goal precommits, verified successes/failures/unknowns, Action Control `self/world/unknown/unavailable` counts, pair attempts/admissions/applied/missed/UC refused, unique pair refs, diagnostic outputs, open audits and operator/scientific status.

Check `audit_export_bytes`, `audit_stage12_goal_progress`, `audit_stage12_first_person_agency`, `audit_stage12_attribution_pairs`, `audit_stage12_diagnostics` and the complete operator packet against the same **trusted** tail anchors. No auditor may invoke the I0 runtime, Oracle or Bench.

## Precommitted interpretation

- Software PASS requires all active code and the independent audits to agree under both Python interpreters, including negative test cases. It does **not** require a favorable detector label.
- Exploratory hypothesis SUPPORTED only if actually lived, independently admitted self/world judgements and distinct observed successes/failures are sufficient to exercise the configured detector under physical steps; unknowns remain excluded. Mere presence of 600 steps is not enough.
- INCONCLUSIVE if first-person precommits/judgements or admissible paired outcomes are absent, or only one class occurs; never lower thresholds to salvage.
- NO-GO for physical provenance if the independent auditor rejects a legitimate runtime output or accepts a semantically forged pair.
- Stage 12 remains IN_PROGRESS until separate operator sign-off, and final project-wide scientific validation remains deferred.

Limitations predeclared: this is one awake-only fixed development world, conservative food-ingestion-specific `self` cues, no source-backed `world` policy in this first increment, and no independent physical truth attestation. It therefore cannot by itself prove the whole Stage12 attribution objective, a universal bias, sleep quality, Stage 9 safety validity or M-11 crash recovery.
