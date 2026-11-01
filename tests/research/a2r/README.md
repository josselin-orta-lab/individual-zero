# A2-R software contract tests

These are **targeted engineering and observational checks**, not a live study, A2-R cohort authorization or scientific GO. No test in this folder may autonomously initiate confirmatory births.

- `test_i1_a2r_launch_gate.py` and `test_i1_a2r_original_slot.py`: static launch conditions and original-slot/custody fail-closed contracts.
- `test_i1_a2r_reward_birth.py`: narrowly scoped reward-birth contract under its dedicated opt-in workflow; do not include it in ordinary documentation-only checks.
- `test_i1_a2r_archive_guard.py`, `test_i1_a2r_archive_assembly.py` and `test_i1_a2r_pair_witness.py`: pure archive and paired-witness software contracts.
- `test_i1_a2r_postflight.py`, `test_i1_a2r_geo_intrinsic_join.py`, `test_i1_a2r_control_cold.py`, `test_i1_a2r_candidate_provenance.py` and `test_i1_a2r_q_coexposure.py`: pure postflight evidence reconciliation, not independent scientific confirmation.

Run only the relevant file in a targeted CI or local checkout, for example:

```bash
PYTHONPATH=tools/research python -m unittest discover -s tests/research/a2r -p test_i1_a2r_archive_guard.py -v
```

The analyzers remain under `tools/research/`. Other original A2-R tests remain temporarily under `tools/research/tests/` pending path/dependency review. Preserve source pins, exact SHA, custody and scientific limitations when continuing this migration.
