# I1 capability integration register (campaign #348)

**Authority:** executable `src/i1/engine.json`, natural `birth_i1` wiring, current `main` source and exact-head CI. This register is an engineering status index; no SCIENTIFIC GO is implied.

## Meaning of status

- `ACTIVE`: integrated through natural birth and executable path; name the integration test.
- `DORMANT`: source is merged but not wired into the natural I1 path.
- `RESEARCH`: implementation remains outside main, or the broad experimental PR is not itself mergeable.
- `BLOCKED`: missing contract or invariant before activation.
- `L1`: technical correction verified; `L2`: natural capability wired and technically verified; `L3`: scientific outcome, which may remain `NOT_ESTABLISHED`.

## Capability ledger at campaign creation, 2026-10-20

| Capability | Issue / merged sources | Main status | Next L2 work | Scientific status |
| --- | --- | --- | --- | --- |
| Competition fallback without false winner residual | #317 / PR #320 | ACTIVE software fix | Preserve existing arbitration tests | NOT_ESTABLISHED |
| Stable personally observed local place-option IDs | #317 / PR #324 | ACTIVE software fix | Distinguish new hop from persistent intention | NOT_ESTABLISHED |
| Stable observed geographical frontier/transit option IDs | #330 / PR #335 | ACTIVE software fix | No change required to existing identities | NOT_ESTABLISHED |
| Bounded cross-hop remembered-place intention | #326, #351 / PR #331, #347, #350, **#352** | **ACTIVE in canonical I1 once #352 merged** | Competition owns an applied-intention descriptor; Stage11 verifies arrival and re-registers a newly paid, subthreshold motor candidate. No motor replay, Action Control still decides. Technical two-step M11 recovery and owner-state tests; a naturally selected multi-hop episode has not been independently observed. | NOT_ESTABLISHED |
| Goal-independent first-person local option consideration | #327 / PR #332, #342, #353 | ACTIVE in natural birth after #353 merge | Separate Phase-1 producer and charged Competition registration; actual canonical M11 1-step candidate publication and cold recovery; existing goal producer preserved, bounded learned Q. | NOT_ESTABLISHED |
| Experienced-place relevance from personally observed bodily effects | #328 / PR #333, #343; canonical integration PR | ACTIVE only after accepted L2 PR merge | Current-life Exploration site effects from genuinely applied local actions and next physical capture, plus positive/negative/contradictory body outcomes; Stage8 uses generic need pressures and confidence. No resource-type utility. | NOT_ESTABLISHED |
| Alert-on-wake bodily diagnostic | #329 / PR #334 | DORMANT | Decide if ordinary needs/Competition suffice before any sleep option suppression | NOT_ESTABLISHED |
| Broad research source #318 | #317 / PR #318 | RESEARCH, do not merge en bloc | Trace each retained fragment to a targeted issue | INCONCLUSIVE / NO_GO not promoted |

## Merge policy

For **L1**, an exact-SHA CI pass and relevant contract tests suffice without population evidence. An L1-only dormant source stays labeled DORMANT with a linked activation issue. For **L2**, require natural birth wiring, observed input-to-decision data path, no oracle, Action Control admission, bounded UC, M11 fidelity, negative cases and non-interference with GoalManager/Competition. A short authentic step smoke test is a software integration test, not a scientific survival experiment. For **L3**, separate cohorts and prospective hypotheses are optional research, not prerequisites for L1/L2.

Prioritize #317/#326, then #327, #328, #329; maximum two new development PRs at a time, each with its own branch and integration scope. Keep I0 frozen and forbid resurrection/rollback.

## Issue #351: canonical L2 integration in PR #352

Source integrations in `src/i1/runtime/stage11_runtime.py` and `src/i1/modules/competition.py` are included in the same generated-I1 engine used by `birth_i1` and `birth_i1_m11`. No feature opt-in or second cognitive owner is created.

- A personally sighted remembered-place candidate remains ordinary Stage11 Planning input, is admitted under normal competition-register UC and evaluated by Stage8/Competition.
- **Only after** a genuinely applied, nonfallback Competition decision can Stage11 record the selected spatial option and expected next position in the existing Competition causal owner. The observation is not yet claimed confirmed.
- On a later actual Perception capture, the Competition owner checks the anticipated arrival; contradiction and TTL expiry invalidate it. Intervening steps leave it informational/suspended, without borrowed movement evidence. Changed active goals prevent transfer.
- At the **immediately next** physically confirmed step, a separately registered and UC-funded candidate for the same personally known semantic place may receive bounded subthreshold evidence. Competition evaluates it afresh, Action Control admits or refuses it afresh, and only physical execution can apply it. No Q/TD update, innate resource utility or forced wake.
- All new causal state is in the existing Competition export/restore contract for M11, with atomic rejection of invalid intention images. Legacy exports without a lived intention stay unchanged.

**Technical tests:** `tests/i1/test_i1_issue_351_l2_spatial_wiring.py` verifies owner creation/negative cases, physical arrival contradictions, expiry/suspension, one-time transfer, the absence of new motor authority, state export/restore and two real canonical M11 steps with cold recovery. The exact-head CI additionally checks generated source parity and both Python 3.11/3.12.

**Limits:** The owner-level positive test drives contract fixtures; the canonical M11 smoke runs naturally without forcing a remembered-place winner. The test suite does **not** establish that a naturally born individual has completed a two-hop remembered route, nor any gain in survival or learning. Scientific status stays `NOT_ESTABLISHED`. Future scientific work may examine naturally occurring multi-hop episodes without changing L1/L2 technical acceptance.

## Issue #327: independent perceived local options (integration PR)

The natural `I1Runtime` now has a dedicated Planning Phase-1 proposal in addition to the existing GoalManager-connected proposal. It uses only `candidate_commands` from the current personally observed `SimulationState`, a bounded local-action filter, physical command deduplication and the already owned `q_active.learned_value`. There is no inferred physical outcome, innate resource benefit, prescribed drinking/eating or override of an existing active goal.

Each opportunity is separately paid for by Planning, then by the ordinary Competition registration, and its extra Competition evaluation receives a matching cycle/envelope reserve. The existing `I1PartialEvidenceAdapter` supplies its ordinary first-person exploratory/learned-Q evidence for the independently proposed option; Stage8, Competition and Action Control retain all motor authority and UC rules.

`tests/i1/test_i1_issue_327_natural_activation.py` is a generated-I1 technical test covering actual canonical `birth_i1_m11`, perception of available interaction candidates, Planning/Competition publication, no forced motor, M11 two-step cold recovery and negative filter/source checks.

This is **L2 ACTIVE only after PR #353 has passed exact-head CI and merged**. Actual statistical behavioral or survival benefit is separate and **NOT_ESTABLISHED**. No population or behavior campaign is authorized for this stage.

## Issue #328: generic personally witnessed place consequences

The natural I1 birth explicitly enables `experienced_site_effects` in its existing `GeographicExploration` owner. Historical/standalone Stage11 defaults remain disabled. When ordinary Action Control has **actually applied** a local nonmovement interaction, Stage11 records the witnessed before-body and site only. A subsequent distinct physical Perception capture supplies the after-body. The Exploration owner retains a bounded running favorable **and adverse** four-variable association at that personally visited coordinate, including contradictory observations and recency. An action that never applied, a proposed plan, a changed position, absent next capture and source labels themselves supply no evidence.

The existing Stage11/Stage8 evaluator may consider only a previously experienced site's association, weighted by *current real physiological pressures* (energy, food, water and integrity), place confidence, route length, observation age and sample count. Negative associations penalize. This is **not** a prediction of future replenishment or causal attribution, not learned Q/TD, and never a command or motor priority override. Source owner site snapshots, including pending witnesses, are versioned, bounded and validated before restoration under ordinary M11 custody.

Generated engine contracts in `tests/i1/test_i1_issue_328_natural_lived_sites.py` cover favorable/adverse and contradictory site outcomes, nonexistent/malformed/future evidence, snapshot atomicity, no source-type generalization, and canonical natural M11 cold recovery over two real physical steps. These are technical tests, not survival cohorts.

**L2 status:** only once this PR passes exact-head CI and merges. **L3 status:** NOT_ESTABLISHED. No behavioral benefit is claimed.
