# Stage 2.1: hardened exact-transport sealed engineering rehearsal

**ENGINEERING PASS. ADR-0017 REMAINS ACTIVE. NO SCIENTIFIC WORLD OPENED.**

The supplied three-commit chain was imported byte-for-byte via
[PR #1220](https://github.com/josselin-orta-lab/individual-zero/pull/1220).
The original sealed rehearsal under transport `e23a28e` passed, but review
found two admission-custody weaknesses:

1. `stage2_admission.admit` and `stage2_panel.execute` accepted a
   caller-selected `STATUS.md` path. A synthetic file containing the exact
   lift line could permit a development World even though the canonical I3
   ledger had not recorded an owner lift.
2. The runtime ticket checked only the World *name*; another complete
   `WorldSpec` could use the same name.

The transport was hardened *before* this rehearsal:

- the only admissible lift source is `src/i3/docs/STATUS.md`;
- tickets carry SHA-256 of the full canonical WorldSpec snapshot and verify
  it against the World about to run;
- reduction checks the ticket digest against the life manifest's World digest;
- tests reject a fabricated status path, and a same-name modified WorldSpec.

Those are engineering custody corrections, not changed cognitive mechanisms,
World definitions, genes, tariffs, arms, horizons, or scientific criteria.

## Corrected full-scale sealed rehearsal

| Measure | Verified value |
| --- | --- |
| Executed source Git SHA | `75a4f325eb5c73c3c14d9f0dcdf313f651061fc0` |
| Exact transport content fingerprint | `dcada9e221f79b9450a4f05fecd20e60ac6595bb306aa871f29e45aefea0b6f1` |
| Frozen plan SHA-256 | `a28606678d13bb9af18f590c328a63eb9eb82f7130c90656e4f520260d294c92` |
| G / R | `GENERATED` 36/36; `COMPLETE` 36/36 |
| Structural invariant failures | 0 on all 10 |
| Mean time per step | 0.816247 ms |
| Sealed manifest SHA-256 | `b280e664190e44dbe402d14441aa8de9bca81a8cc9b75f95220856144f9004ad` |
| Report SHA-256 (original artifact bytes) | `dc36b2632165e1e7287ef1b068dc2f2463769bb8edd75e19971fa894922d4f23` |
| GitHub Actions run | `42628475893` |
| GitHub Actions artifact | `13679561877` (`i3-stage2-1-hardened-rehearsal`) |

The full structural report is preserved inThe **same full-size 36-life sealed engineering rehearsal also PASSED on
Python 3.12** at source `8b1e0527b6ee5f7f27ede7adf1bce24c85c91ee7`
(Actions run `42629796562`, artifact `13680098108`). It yielded the same
exact transport content fingerprint `dcada9e2…f1` and plan SHA-256, with
36/36 generated, 36/36 reduced and zero invariant failures. Its separate
[structural report](HARDENED_REHEARSAL_PY312.json) has SHA-256
`b6a84169ac58cca106bd4c03f25769c579a81d704d7657fd87c9066461ac08c7`,
sealed manifest SHA-256
`22b09edac4b01aba3e9359c950ad9d2a408bbffaa6dbd73633306d199294b461`,
and mean time 1.244456 ms/step.


[`HARDENED_REHEARSAL.json`](HARDENED_REHEARSAL.json), also available as the
immutable workflow artifact. The report contains no survival, death, body,
resource, action, route, or replay outcomes. The engineering Worlds are
non-evidentiary and intentionally repeatable.

**The earlier fingerprint `15136d13…d967f9` is superseded** for transport
approval. It must never be named in an owner lift for this hardened code.

## ADR-0017 readiness

1. Two-phase G/R implemented and tested: **met**.
2. Disjoint non-evidentiary engineering cohort: **met in substance**.
   `engineering_cohort.py` declares it beside the immutable P2 generator
   rather than modifying `P2.COHORTS`. That documented deviation from the
   literal ADR-0017 wording must remain visible to the owner.
3. Full-scale exact-transport rehearsal PASS: **met for source
   `75a4f325` and fingerprint `dcada9e2…f1`**. Before a scientific run,
   verify that the merged source retains the exact content fingerprint.
   Any transport-code or plan change invalidates this PASS.
4. Owner explicitly records the lift in the canonical I3 STATUS ledger:
   **NOT MET**.

**No automatic lift.** The owner may consider the technical gate after
code review and the merged-source fingerprint check. Development indices
80/81 remain unopened; validation and reserve remain sealed.

The canonical software verdict `REPLAY_GATE_CAPACITY_SHOWN` is unchanged.
A sealed engineering PASS says nothing about lived survival or replay
economics.
