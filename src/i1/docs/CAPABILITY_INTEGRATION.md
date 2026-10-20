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
| Goal-independent first-person local option consideration | #327 / PR #332, #342 | DORMANT | Connect distinct producer, preserve goal proposals, dedup + budget + learned Q without invented effect | NOT_ESTABLISHED |
| Experienced-place relevance from personally observed bodily effects | #328 / PR #333, #343 | DORMANT | Handle adverse and contradictory site samples and generic owner-backed outcomes, Stage8 integration | NOT_ESTABLISHED |
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
