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
| Bounded cross-hop intention continuation | #326 / PR #331, #347 | DORMANT | Bind to existing semantic and owner state, re-arbitrate each hop, sleep/need interruption, M11 restart, no motor privilege | NOT_ESTABLISHED |
| Goal-independent first-person local option consideration | #327 / PR #332, #342 | DORMANT | Connect distinct producer, preserve goal proposals, dedup + budget + learned Q without invented effect | NOT_ESTABLISHED |
| Experienced-place relevance from personally observed bodily effects | #328 / PR #333, #343 | DORMANT | Handle adverse and contradictory site samples and generic owner-backed outcomes, Stage8 integration | NOT_ESTABLISHED |
| Alert-on-wake bodily diagnostic | #329 / PR #334 | DORMANT | Decide if ordinary needs/Competition suffice before any sleep option suppression | NOT_ESTABLISHED |
| Broad research source #318 | #317 / PR #318 | RESEARCH, do not merge en bloc | Trace each retained fragment to a targeted issue | INCONCLUSIVE / NO_GO not promoted |

## Merge policy

For **L1**, an exact-SHA CI pass and relevant contract tests suffice without population evidence. An L1-only dormant source stays labeled DORMANT with a linked activation issue. For **L2**, require natural birth wiring, observed input-to-decision data path, no oracle, Action Control admission, bounded UC, M11 fidelity, negative cases and non-interference with GoalManager/Competition. A short authentic step smoke test is a software integration test, not a scientific survival experiment. For **L3**, separate cohorts and prospective hypotheses are optional research, not prerequisites for L1/L2.

Prioritize #317/#326, then #327, #328, #329; maximum two new development PRs at a time, each with its own branch and integration scope. Keep I0 frozen and forbid resurrection/rollback.
