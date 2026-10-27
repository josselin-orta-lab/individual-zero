# Issue #344: extensible source-pin tests

The source registry remains strictly validated by `scripts/test_i1_artifact_parity.py`. The regression suite now requires all historic reviewed pins **as a subset**, tests every registered file, and verifies that a separately numbered fifth manifest is accepted only when exact Git source bytes match its reviewed SHA. Tampering must fail. No runtime or registry whitelist relaxation.
