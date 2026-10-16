# A2.34 preregistration: lived outcome → episodic memory → recall → option choice

**Registration date:** 2026-10-16. **No A2.34 heldout executions were performed before this document.**  
**Source:** I1 draft PR #219, baseline SHA `a67bdb11ff8da79b434b07aed444837ecd152202`; I0 `main` `8ce8711b2d5f86b184d66fcee1d95a3e39f30836`.  
**Goal:** distinguish a genuine first-person outcome, admission into autobiographical Memory, an *actual* runtime recall publication, its subsequent Gatekeeper admission, and *causal use* of that information in Stage 8's existing option scoring and Competition. An episode's mere presence, technical journal retrieval, or repeated physical success is **not** evidence of adaptive memory use.

## Motivation and code hypothesis (pre-outcome)

A2.33 independently established a later first-person capture of injury and failed collection but not adaptive behavior. The current Stage 7 `memory.spontaneous_contribution` publishes a `memory_recall` contribution with zero urgency, zero risk and zero value. Stage 8's I1 partial-option evaluation uses a constant experimental `I1_SCORE` when the forecast matches the pending option and does not receive the Memory owner or its recalled episode. This is a **static software hypothesis** about the missing consumer path; we must not silently install a new model, adjust scoring, or invent learned danger to make the test pass. The protocol tests whether runtime memory recalls and competitive witnesses actually occur.

## Frozen new experimental cohort

- **24 matched world pairs = 48 independent mortal I1 lives:** 8 `FAILURE`, 8 `INJURY`, 8 `NOMINAL`. Each pair has exposed/control arm, fresh isolated WorldBody, I1 instance, WAL, memory and journal. In each arm the same existing factorized model is explicitly enabled at birth, with the current 2-UC per forecast policy and unchanged Stage9/Action Control. The arms are executed in alternating order by index. **Nine maximum actual physical commands per life**; stop at first death, safety block or exception, never extend a deceased life.
- All new case IDs `i1:a234:<stratum>:<index>:<arm>`; indexes `00..07`. Body: energy `69 + i%3`, food `11 + i`, water `78 + i%4`, integrity `100`; `berry_b` quantity `6 + i%3`. Standard unchanged WorldBody physical parameters/day-night/safety. No seeds or hidden results from A2.31–A2.33 determine the new outcomes.
- `FAILURE`: B visible at current position, exposed arm receives one external `set_action_failure_schedule` entry for its **first** `collecter`, control is not forced. Only the laboratory may know the schedule; I1 can learn at most from next-step inventory/resource observations.
- `INJURY`: B visible one cell east, exposed arm has one **non-terminal hidden physical danger zone** east, control has none. The physical location is never exposed as a hazard label; only eventual body/position observations are eligible.
- `NOMINAL`: B visible one cell east, no hidden perturbation in either arm; a negative control for run-to-run determinism and independently born memory.
- **Training:** a fresh, external, preregistered physical WorldBody corpus of eight east movements and eight local-B collections. Freeze `EquipmentCorpus.digest`, model version and coefficients **before** constructing any of the 48 heldout lives. The physically executed external examples are research priors, **never** I1's lived memory. Do not use future, Oracle, Bench or hidden world labels in prediction or cognition.

## Source-to-consumer audit contract

Without altering `src/i1`, `src/i0`, `src/lab`, or `src/i1_overlays`, a separate external scorer records existing runtime events (by event ID and t_monde), and at most one authorized opening PerceptualCapture per physical step:
1. `outcome_seen`: first body/inventory observation **strictly after** a physically applied command versus the initial authorized capture; report success, uncertainty and the external-only cause.
2. `episode_custody`: the closed episode's exact event_refs, boundaries, source world-step, and any linked previous episode. Verify refs resolve to authorized autobiographical technical entries with appropriate `auto_segment_commit` (not merely `journal.entries`), no postmortem sourcing. Only first-person source references qualify.
3. `spontaneous_recall`: actual `memory_recall_proposed` receipt in the active step, matching a previously closed episode. An offline call to `Memory.recall()` **does not** count as runtime recall.
4. `gatekeeper_visibility`: subsequent `s_t_published` `competitive_refs` contains that exact Memory contribution ref. If a recall is rejected or expired, report that separately.
5. `decision_use`: a future `stage8_option_evaluation` of a model-origin candidate explicitly cites the Memory source in its signal IDs/producers or verified lineage and **changes its evidence** relative to the paired control, with a matching Competition trace and physically admitted decision. A fixed score without such provenance is **not** learning, even when a memory was recalled.
6. **UC and independence**: count charged/refused forecast operations and memory-related software work where available, distinct identities and WAL/journal digests. No optional operation is called for free from inside cognition to satisfy scientific instrumentation.

Retain raw `lives.jsonl`, chronological `decision_trace.jsonl`, `summary.json`, individual WALs, frozen corpus hash, source commit and event provenance. The external scorer can read hidden physical outcomes but must not pass them into I1.

## Preregistered thresholds and falsifiers

Each stratum uses denominator **eight exposed/control pairs**, including failures, blocked actions and deaths:
- **Observation opportunity:** at least 6/8 failure pairs have an actually applied forced first collection + following first-person unchanged inventory while control's collection succeeds; at least 6/8 injury pairs have actual movement + nonterminal damage visible at the next authorized capture. Otherwise **opportunity not demonstrated**; no claim about learning ability.
- **Episode admission:** at least 6/8 opportunity-positive exposed lives have a closed episode containing the actual appropriate lived transition/observation provenance **before** subsequent decisions, with a valid source ref and no hidden effect keys. Otherwise **episodic admission NOT DEMONSTRATED**.
- **Spontaneous recall:** at least 6/8 opportunity-positive exposed lives publish a correctly linked prior-episode `memory_recall_proposed` after that episode closes. Else **recall route NOT DEMONSTRATED**.
- **Choice influence:** at least 6/8 opportunity-positive exposed lives show a memory-sourced difference in evaluated model-origin evidence, Competition/Action Control, and applied next action relative to the matched control, without operator hidden truth. Else **LEARNING NOT DEMONSTRATED**. This is a *separate gate* from recall.
- **Nominal controls:** paired first authorized preaction perceptions, model statuses and initial choices agree in 8/8 control pairs (ignoring distinct life ID) or the cohort is a determinism alert.
- **Hard NO-GO:** any leaked hidden zone/forced-failure label into first-person cognition, invalid journal, false `safe`/terminal/causal certainty, >1 physical effect per admitted command, resurrected actor, action after death, bypassed Action Control/DC-05, memory source from a future step, or cross-life source sharing. No threshold can be changed after reading results.

**Analysis disposition:** `OBSERVATION_PASS/FAIL`, `EPISODIC_ADMISSION_PASS/NOT_DEMONSTRATED`, `RECALL_PASS/NOT_DEMONSTRATED`, `DECISION_USE_PASS/NOT_DEMONSTRATED`, `NO-GO`. These axes stay separate, and a later failure does not erase an earlier success. A failure at any stage motivates a separately authorized I1-only A2.35 design; it does **not** authorize direct Oracle truth injection, reward forging, or modifications to I0. Two Python versions test software portability on **the same 48 deterministic lives**, not independent scientific replication. **Cognitive deployment remains NO-GO** regardless of software results.
