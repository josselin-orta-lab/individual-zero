# A2.37-v1 — mixed food and water, unfiltered initial technical failure

**2026-10-16; permanent first attempt record.** Frozen protocol `docs/research/i1-a237-mixed-needs-prereg-2026-10-16.en.md` at `4aea5ee862459934c1165207b242883ed38552cb` (before runner). Exact tested HEAD `e04efb8ed5dbe78bdf9fa16616e2a406eba3ae95`. [GitHub Actions run 38885259351](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38885259351) **FAILED** on both Python 3.11 and 3.12 (study runner exit 1), per-life 90-day archived WAL/canonical/life JSON and unfiltered `lives.jsonl`.

**96 separate mortal I1 births**, 4 strata × 8 case indices × 3 arms `FULL`, `NO_RECALL`, `NO_D2`. **1,312 completed physical steps**, 16 hard violations. An external scorer reads physically executed commands and authoritative first-person journals but never feeds hidden physical facts into I1. All four models were **birth-enabled** in FULL: external Stage6, learned D1 water, source-backed berry memory A2.35 and prudence D2.

## Unfiltered primary results

| Stratum | FULL both drank and collected | NO_RECALL | NO_D2 | Invalid lives |
|---|---:|---:|---:|---|
| BOTH_LOCAL | 8/8 | 8/8 | 8/8 | 0 |
| BERRY_LOCAL_WATER_E | 0/8 | 0/8 | 0/8 | 0 |
| WATER_LOCAL_BERRY_E | 0/8 | 0/8 | 8/8 | **16** (8 FULL, 8 NO_RECALL) |
| BOTH_LOCAL_WATER_E_HIDDEN_LETHAL | 8/8 | 8/8 | 8/8 | 0 |

**Preregistered primary target:** at least six of eight FULL lives must achieve **both** physical effects in BOTH_LOCAL and BERRY_LOCAL_WATER_E. The observed 8/8 and 0/8 mean **MIXED_GOAL_NOT_DEMONSTRATED**. However the 16 invalid lives force overall **TECHNICAL FAIL**, not an interpretable absence-of-effect comparison for WATER_LOCAL_BERRY_E. No deaths were recorded in the four strata; the locally available water/berry resources meant the hidden east danger did not need to be entered. This is not proof I1 knew the east cell was unsafe.

## Independent cause-of-failure reconstruction from A2.37-v1 raw artifacts

All **16 and only 16** invalid lives in WATER_LOCAL_BERRY_E, FULL + NO_RECALL, stopped after two physically executed `boire` steps. Journal/step error pair:

- `AttributeError: 'NoneType' object has no attribute 'export_causal_state'`
- `ValueError: unclosed or invalid physical world step`

When the water learner first proposed an empirical movement, I1 D2's `_register_option_proposal` called `self.exploration.geographic.export_causal_state()`. The preregistered A2.37 fixture intentionally sets geography to `None`; it has **no authentic physical visit ledger**. D2 crashed rather than treating this as no evidence and issuing a charged, logged abstention. The NO_D2 arm in that stratum had 8/8 authentic physically combined success without the exception. This proves a narrow **integration fault**, not the merit of unknown movement or a hazard prediction. No postmortem continuation is counted.

Note also that `BERRY_LOCAL_WATER_E` ran 16 physical steps per individual without physically successful collection or drink (0/8 FULL; zero model proposals or water learning receipts). This is a distinct negative result about the existing goal/option route in that frozen scenario; fixing D2's null geography is not expected to cure it.

## Corrective disposition without rewriting the experiment

The first attempt remains permanently **FAIL**. [Amendment 1](i1-a237-fault-amendment-1-2026-10-16.en.md) was created after seeing this failure but before the code patch. The I1-only D2 overlay must now regard missing optional geography as an **empty visited set**, charge UC, log `prior_physical_visit=False` and refuse unknown movement through normal Competition, with no hidden-safety claim. A new real-body regression `tests/test_i1_a237_d2_no_geography.py` tests this path.

The subsequent **A2.37-R1** uses the same deterministic cases and unchanged primary thresholds; it is a software repair/regression, **not** an independently heldout confirmation. Report it separately. I0 / normative WorldBody stay unchanged, PR #227 remains Draft. General cognitive deployment is NO-GO.
