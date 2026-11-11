# I3 R1: engineering-only durable birth-slot reservation

**Date:** 11 November 2026. **Engineering scope:** preparatory identity/one-shot custody primitive for [R1/R2 release issue #1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331), in the owner-selected [I3 reference transition PR #1330](https://github.com/josselin-orta-lab/individual-zero/pull/1330). **This is not a born I3 session, real M11, a scientific World authorization or engine activation.**

## Question, intervention and falsifier

The previous I3 `run_life` creates a World and Mind within a single function, with observer-only manifest and hash-chain evidence returned at life end. It provides no irreversible, local slot claim before constructing a World. A copied checkout can accidentally try to reuse the same claimed birth index. We need an independent generation-owned reservation contract **before** designing a persistent owner, not another cognitive head.

**Hypothesis (technical):** in one trusted local filesystem, a caller-supplied I3-only `birth_index` can be consumed exactly once via a SQLite `BEGIN IMMEDIATE` transaction with `WAL` and `synchronous=FULL`. On later reads, the strict source/genome/world/seed claim remains available; a second reservation, forged value, foreign SQLite database or altered stored digest fails closed.

**Falsifier:** a duplicate slot succeeds, a foreign database is silently reused, a modified record is treated as valid, an invalid source hash is admitted or the helper constructs a World/Mind. A claim is not equivalent to a life actually executed.

## Boundaries and semantics

- New isolated module `src/i3/runtime/birth_reservation.py` imports only Python stdlib and has **no cognitive or cross-generation dependencies**. `make_reservation` validates 64-character lowercase source/world/genome hashes, a nonnegative bounded life seed and a distinct SQLite-safe integer slot.
- The `Reservation` digest is derived from a canonical JSON envelope with immutable schema and `I3_ENGINEERING_ONLY_NOT_BORN` scope. It is a **consistency checksum**, not a digital signature, durable owner proof, independent external source witness or anti-rollback anchor.
- `reserve(directory, reservation)` requires an existing non-symlink engineering directory and a dedicated database name `i3_birth_reservations.sqlite3`, checks the I3 application ID `I3BR`, rejects foreign schema, and commits one `birth_index` with SQLite's unique primary key under `BEGIN IMMEDIATE`. It will not create a World.
- `inspect(directory, birth_index)` is read-only, does not create a missing database, recalculates the complete record digest and refuses malformed/altered receipts. A successful inspect is **not permission to continue a live person**.
- Every receipt explicitly says `status=RESERVED_NOT_BORN`, `durable_m11=false`, `scientific_world_authorized=false`. No entrypoint in `src/i3/engine.json`, no research life policy, no I1 live session, no registry/stage manifest or World admission is changed.
- Local SQLite durability protects the same existing database only. A deleted/copied/unanchored file can be rolled back by an external actor, so this **does not establish global once-only reservation, authenticated M11 or runtime recovery**. No new scientific indices may be minted from its engineering key.

## Pure example, no organism

```python
from pathlib import Path
from i3.runtime.birth_reservation import make_reservation, reserve, inspect

# The directory is an isolated engineering workspace, not an I1/M11 store.
root = Path("/tmp/isolated-i3-engineering")
root.mkdir(parents=True, exist_ok=True)
slot = make_reservation(
    birth_index=1, life_seed=42, source_sha256="a"*64,
    world_sha256="b"*64, genome_sha256="c"*64)
receipt = reserve(root, slot)        # irreversible in THIS SQLite store
assert inspect(root, 1) == receipt
# No World, Mind, life, M11 or scientific source was created.
```

## Verification

Focused `tests/i3/test_birth_reservation.py` exercises once-only reservation, cold read of the same local database, separate slot distinct identity, invalid index/seed/hash rejection, altered identity, foreign SQLite schema/application-id failure, unknown slot and strict lack of World/cross-generation imports. The four initial checks were executed in an isolated temporary local Python 3 environment and passed. This is **not** the repository's full 3.11/3.12 validation; the exact PR commit requires its own I3 CI.

## Remaining R1/R2 work

1. Introduce an actual generation-owned I3 native birth identity and lifecycle owner, not just a trusted caller-supplied slot.
2. Bind any claim to an independently verified source, unique writer and globally durable external witness where required. Validate input origin rather than trusting a caller hash.
3. Persist/reconstruct *all* mutable World and Mind/RNG plus bodily cost and death, with atomic `POST_PAID_LEARNING` M11 publication. Validate crash-before/after commit and cold continuation parity before allowing the next action. Refuse terminal, ambiguous or old-generation state.
4. Provide exact source Python 3.11/3.12 smoke/fault tests and an explicit production release before considering `active_generation=I3`.

**Scientific state remains:** I3 P1.3 funded-v2, Stage 2.1 `NOT_ISSUED`, E3 exact candidate `CLOSED_NEGATIVE`, all old prospective Worlds closed with no retry.
