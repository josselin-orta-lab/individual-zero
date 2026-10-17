# I1 native-source migration ledger

Date: 2026-10-17. Working PR: #253, stacked on #252 and #251.

## Migration performed

The 13 former `src/i1_overlays/` files now belong to `src/i1/runtime/` (verbatim original Git blobs). At build time they remain installed exactly once into the historical `i1lab.*` namespace, so canonical `birth_i1` and M11 birth identities are unchanged.

A further six I1 cognitive modules now hold their actual behavior **directly in checked-in `src/i1/modules/`**, rather than receiving source-string patches from `scripts/build_i1_fork.py`:

| Native module | Former build-time transformation |
| --- | --- |
| `memory.py` | cached visible competitive references and active-goal identity |
| `consolidation_batch.py` | priority-bounded `heapq.nsmallest` selection |
| `consolidation_pending_index.py` | detached indexed-episode view and privately owned charged ranks |
| `consolidation_pass_runner.py` | copies removed only at already-owned private boundaries |
| `consolidation_transaction.py` | validated candidate-digest metadata and checkpoint custody |
| `consolidation_semantics.py` | I1 six-pass semantic algorithm previously held in a non-Python text template |

**Source-level parity proof**: prior to each Git write, old `rewrite(original)` plus its exact original transformation was compared with `rewrite(new native source)`; all changed modules matched byte-for-byte. The six-pass native module was copied byte-for-byte from the former I1 template, then the former template was deleted. These assertions concern the produced source text, not a scientific result.

No modification was made to `src/i0/**` or `src/lab/**`. No H1/H2 policy was introduced; no runtime module was disabled. The canonical I1 birth continues to execute complete active cognition.

## Real validation

GitHub Actions [#39032352242](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39032352242) passed I1 SMOKE + FULL, real M11 cold recovery, live archive verification and I0 targeted non-regression under Python 3.11 and 3.12. This confirms this incremental migration passes the current software acceptance gate; it is not a full scientific validation of long-term behavioral emergence.

## Remaining migration

The generator still applies other source transformations, in particular to physical world `i1lab.world`, Stage10 runtime/publication, journal operations, Stage11, M11 and owner custody. They must be migrated **only** with explicit output parity, authenticated M11 cold-recovery checks and mortal fail-stop semantics. The aim is ultimately source-native I1 and an ordinary package build, but deleting the generator or changing persistence schema now would be unsafe.

Migration order: (1) native noncritical optimizations, (2) native typed cognitive owners, (3) native physical and durability implementations, (4) remove mechanical source rewriting only when the new build produces equivalent imports/states and the full CI and fresh independent experiments justify the architectural switch.

This work stays on PR #253, dependent on #252 and #251. Do not merge out of order.