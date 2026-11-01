# Tests of active I1's engineering contract

Run `python -m unittest discover -s tests/i1 -p 'test_*.py' -v`.
These tests verify version-owned architecture and tooling; physical, cognitive
and M11 tests remain in the existing I1 CI. Historical I0/A2 cohorts are
not accepted as natural-I1 scientific oracles.

The formerly root-level `test_i1_first_physical_step.py` and `test_i1_m11_cold_recovery.py` are technical regression contracts, not scientific GO criteria. Their paths have been updated, and the historical manual isolation workflow invokes them from this directory.
