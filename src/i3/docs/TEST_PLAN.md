# I3 tests: current selection guide

**Maintained entrypoint · 16 November 2026.** The complete historical 28,523-byte test catalogue (original Git blob `91679d8db3be1c91c3d983186d3d200ee18de07a`) is preserved, byte-identically, at [TEST_PLAN_HISTORY_2026-11-16.md](TEST_PLAN_HISTORY_2026-11-16.md). Dated paragraphs there document actual past tests and `NOT_RUN` boundaries **at their original times**, not a present Stage6/Stage7 execution or a new permission.

**Tests prove code and contracts only.** A passing run, sealed rehearsal or original-extraction check does not establish persistence improvement, independent custody or scientific GO; Stage2 science stays `NOT_ISSUED/HOLD_NO_VERDICT`. [Current I3 status](STATUS.md), [active surface](ACTIVE_SURFACE.md) and [test placement](../../../tests/TEST_LAYOUT.md) take precedence for current routing.

## Run the minimum software check for the question

| Tier | When to run | Representative command / reference |
| --- | --- | --- |
| T0 · navigation | Docs, archive pins, source metadata or agent routing | `python tools/agent_context.py audit --json`; `python tools/check_repo_navigation.py --scope current`; `python -m unittest discover -s tests -p 'test_agent_historical_sources.py' -v` |
| T1 · focused mechanism | One I3 body/mind/persistence function, its negative contract and paid boundary | `python -m unittest discover -s tests/i3 -p 'test_p13_replay_gate_mind.py' -v`; select the actual changed `test_*.py` |
| T2 · integrated engineering | New or modified generation-owned motor/life/step/receipt/cold-replay contract | The affected `tests/i3/test_*.py`, explicit native integration controls and `python scripts/check_engine_contracts.py --json` |
| T2 · I3 software matrix | Candidate source, `engine.json`, `ACTIVE_SURFACE.json`, or owned tests | Existing [I3 proposal software workflow](../../../.github/workflows/i3-proposal-checks.yml) runs `python -m unittest discover -s tests/i3 -p 'test_*.py' -v` on **Python 3.11 and 3.12** |
| T3 · source-exact engineering | A **new** frozen protocol explicitly demands two rehearsals and separate seals | Use only that protocol's exact source/indices/seed separation; not an ordinary PR or old run replay |
| T4 · prospective science | After a new run-specific freeze and successful exact T3 conditions | Original life/World cohort, negative/random control and preregistered reducer; issue separate scientific verdict |

A full software suite on either Python version never replaces another **required** version, scientific randomization, original artifacts or preregistration. A narrow documentation change should not need an I3 life or cohort.

## Locate domain-specific tests (historical and current)

| Domain | Software tests and original custody |
| --- | --- |
| Active generation ownership, no foreign memory and internal contracts | `tests/i3/test_active_surface.py`, `tests/test_engine_repository.py`, [active surface](ACTIVE_SURFACE.md) |
| Paid fund/energy/vigilance, admission, native motor | `tests/i3/test_funded_cognition.py`, `tests/i3/test_p13_replay_gate_mind.py`, focused native-life tests |
| Stage2 native E3 action discrimination and current HOLD | [Post-E3 agent guard](../../../tests/i3/test_stage2_post_e3_agent_handoff.py), [original E3 negative audit](STAGE2_POST_E3_AUDIT_ADDENDUM_2026-11-11.md) |
| Native M11 and authority anti-rollback boundary | `tests/i3/test_engineering_remote_witness.py`, [off-host independent release gate](engineering/OFFHOST_M11_INDEPENDENCE_RELEASE_GATE_2026-11-13.md). In-process loopback/TLS/HMAC fixtures **do not** establish independently administered custody |
| Stage6 lineage/preflights | `tests/i3/test_stage6_light_*.py`, [original Stage6 protocols and limitations](studies/stage6-light-preparation/). Original 16-population Stage6 campaign closed, not an instruction to rerun |
| Stage7 inherited persistence | `tests/i3/test_stage7_persistence_transport.py`, [frozen Stage7 protocol](studies/stage7-persistence/STAGE7_PERSISTENCE_PROTOCOL_2026-11-16.md), [original run and results](STATUS.md). The Stage7 12/16 primary result is **negative under the fixed 13/16 rule** |
| Older P2/P5 tests and Stage1 studies | [Unaltered original test catalogue](TEST_PLAN_HISTORY_2026-11-16.md) plus original study plans and immutable results |

## Invariants for test maintenance

- Do not add `tests/test_i2_*.py` or `tests/test_i1_*.py` at root; follow [repository placement](../../../tests/TEST_LAYOUT.md). I2 is [archived in place](../../../archive/i2/README.md); its original exhaustive 3.11/3.12 suite is available only on explicit historical manual dispatch, while PRs run fail-closed tree/contract guards.
- Do not delete a negative, repeated-by-design, paid-cost, fatal-state, source-hash or cross-version case merely because it appears expensive. Profile first and preserve full discovery cardinality.
- Never let a test access hidden future World state, give the individual external motor authority, simulate free cognitive work as an admissible funded arm, reopen exhausted indices or restore terminal lives.
- Distinguish **test execution**, **engineering G/R**, **prospective exposure** and **scientific interpretation** in each agent handoff. Record command, SHA, Python version, original receipt URL/hash, observed failures and scientific `NOT_EVALUATED` when appropriate.

Historical experiment counts, CI jobs and `NOT_RUN` evidence are retained at [TEST_PLAN_HISTORY_2026-11-16.md](TEST_PLAN_HISTORY_2026-11-16.md); they are **not** a fresh test checklist.
