# Individual Zero Observer (Phase 1 candidate)

Independent, local-only web console for human operators. No `lab`, `i0` or
`adapters` imports from the Observer process. **The Core runs without this
service.** This directory intentionally has its own Python package and static
frontend, with no React/Vite toolchain required for the minimal MVP. A
frontend migration can be considered after operator acceptance.

## Audited integration: upstream `main` at `c74368684f7ea8ceecb60ee0e95e1a5746368942`

- `python -m lab.cli`: bootstrap LabEvents JSONL, `--seed`, `--cycles`,
  `--run-id` and `--output` supported; *not* a cognitive experiment.
- `python -m lab.stage11_autonomous_600_step_probe --steps N`: autonomous,
  mortal, no Oracle/Bench, reports a development diagnostic. It does not
  export the complete journal. Reference world seed is internal, not
  user-adjustable.
- `python -m unittest discover -s tests -p test_causal_journal.py`: small
  fixed journal checks. Never user-supplied shell commands.
- `scripts/verify_i0_journal.py` independently validates a complete canonical
  archive (the operator may use it separately); Observer SHA-256 byte
  comparison alone does **not** replace this verifier.
- `Oracle` has a capability/private token and `EvaluationTrace` is in memory.
  There is no general Oracle network endpoint or guaranteed persisted ground
  truth. Oracle Explorer displays only actual mounted external records.
- Core WAL and explicit immutable export must not be confused with coherent
  post-crash life restoration (M-11 still outstanding).

## Quick start

From the checkout root, with Python 3.11+:

```bash
python -m venv .venv-observer
. .venv-observer/bin/activate
python -m pip install -e './observer[test]'
mkdir -p "$HOME/.local/share/individual-zero-observer/runs"
chmod 700 "$HOME/.local/share/individual-zero-observer/runs"
export I0_OBSERVER_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(36))')"
export I0_CORE_ROOT="$PWD"
individual-zero-observer
# Browser: http://127.0.0.1:8765
```

Keep the printed/exported operator token private. It is *not* checked into
Git. The token must be at least 24 characters. The UI login establishes a
SameSite=Strict, HttpOnly session cookie; the token is not stored by the
browser JavaScript. `GET /api/health` and the blank login shell are public,
all operational APIs require authentication. The service binds only to
127.0.0.1 and does not enable CORS. Do not port-forward or expose it publicly.
TLS termination, operator identity governance and security review are
requirements for any future remote deployment.

Run tests (fixture Core only, no expensive I0 campaigns):

```bash
python -m pytest observer/tests -q
```

The Observer-owned root is a **private directory** (mode 0700). Each run gets
its own newly created ID/directory. A new test is rejected while another is
active. A run root containing an INTERRUPTED or unreadable local receipt is
**locked against further launches**, even if no process remains. After an
interruption, the operator must inspect/terminate any orphan process on the
host and configure a **new isolated run root**. Never delete the old root as a
shortcut: retain its evidence for audit. A restarted service marks any unfinished `PENDING`/`RUNNING` local
receipt `INTERRUPTED`; its logs remain available. No `SUCCESS` status is
inferred from an incomplete run. An explicit cancellation signals the process
group; resource limits and timeouts are enforced on supported POSIX hosts.

**Isolation limit:** subprocesses inherit the filesystem permissions of the
Observer's OS account. Deploy with an unprivileged account, read-only Core
checkout and read-only imported archives, ideally in an OS sandbox without
network. Python resource limits are **not** a complete filesystem sandbox.
Do not run as root or with writable historical scientific archives.

## Real operator usage

1. Sign in with `I0_OBSERVER_TOKEN` and select **Tests**.
2. Run `bootstrap` with seed 0 and 3 cycles. Open **Runs** to inspect the
   process log, `events.jsonl`, the source Git SHA and dirty-worktree flag (when detectable) and
   file digests. Bootstrap cycles are not counted as actual physical world
   steps.
3. Run `mortal_stage11` for e.g. 20 steps. Its report contains the
   upstream `steps_physically_executed`, but no fabricated Oracle timeline.
   Upstream owns the scientific meaning of its report.
4. For Oracle / canonical journal inspection, mount a separately produced
   data directory as described below. Observer **never** calls an internal
   Oracle capability or injects truth into I0.
5. Download individual originals or a generated ZIP. The archive is created
   separately; the originals are opened read-only, never rewritten.

## Read-only imports: `observer-source-v1`

Set `I0_OBSERVER_ARCHIVE_ROOT=/trusted/read-only/archives`. Each immediate
child must be a unique directory named `[a-zA-Z0-9_-]{1,64}` with a manifest
`observer-source-v1.json`, e.g.:

```json
{
  "schema": "observer-source-v1",
  "created_at": "2026-10-12T06:00:00+00:00",
  "metadata": {"description": "Operator-provided example, NOT canonical Oracle data"},
  "files": {"journal": "life-001.jsonl", "oracle": "oracle-export.jsonl"},
  "sha256": {"journal": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"}
}
```

Filenames are direct-child *basenames*, not paths. Symlinks, traversal,
unlisted files, oversized import manifests and unsupported categories are
rejected. Only files actually present will appear. The `sha256` values in the
example are illustrative, **not** evidence; use authentic independently
preserved digests. A missing source is displayed as missing, not guessed.
A successful matching SHA-256 proves only the bytes match the *provided*
reference, not that the reference was independently trusted or physical truth.

The `journal` file must contain original canonical JSONL records:
`{index,event_id,previous_hash,event_hash,causal_event}`. `lab_events`
contains `{run_id,kind,cycle,data}`. `oracle` and `evaluation_trace` are
separately labeled **uninterpreted external JSONL**, since Core has not
published a stable independent export contract for these capabilities.
Do not relabel a cognitive observation as Oracle truth. See
`contracts/observer-source-v1.schema.json` and
`contracts/replay-readiness-v1.md`.

## REST API

`GET /openapi.json` is the machine-readable specification. Session:
`POST /api/session`, `DELETE /api/session`. Reads:
`GET /api/health`, `GET /api/tests`, `GET /api/settings`,
`GET /api/runs?q=&status=&limit=`, `GET /api/runs/{id}`,
`GET /api/runs/{id}/logs?offset=&limit=`,
`GET /api/runs/{id}/events?source=journal&cursor=&limit=&kind=&component=&step=&at=&q=`,
`GET /api/runs/{id}/integrity/{alias}`,
`GET /api/runs/{id}/file/{alias}` and
`GET /api/runs/{id}/archive.zip`. Execution:
`POST /api/runs` with `{ "test_id":"bootstrap", "seed":0, "cycles":3 }`
and `POST /api/runs/{id}/cancel`. The generated ZIP is disk-backed and all
single-file responses stream chunks, without loading complete files in RAM.

Statuses: `PENDING`, `RUNNING`, `SUCCESS`, `FAILED`, `CANCELLED`,
`INTERRUPTED`, plus `IMPORTED` for historical sources whose upstream process
status cannot be established. A status describes the local runner only:
`technical_success`, `assertions_passed` (null for bootstrap and unverified failures), `behavior_conformance`,
`scientific_validation` and `operator_validation` are separate nullable fields.
`SUCCESS` never certifies scientific acceptance or approval of a Stage.

## Security and limits

- No shell expansion; only catalog-fixed argv executed with constrained
  numeric parameters; no arbitrary Python path/test selection from the UI.
- Core source and archive mounts are distinct from the private Observer run
  directory. Runner output paths are unique and not operator-selectable.
- Artifacts are read by alias through `dir_fd` + `O_NOFOLLOW`; raw absolute
  paths are never accepted by HTTP endpoints.
- Pagination scans JSONL sequentially with bounded record size (2 MiB) and
  page limit (200); suitable for large journals **in memory**, but random
  seeks remain O(n). Add a read-only index in a future revision if needed.
- Byte-hash checks and JSONL exploration do **not** constitute the core's
  semantic chain/causal/provenance verifier. Independent audit remains separate.
- No automatic long scientific campaigns are launched by UI tests or CI.
- Current version has no fine-grained role management, remote TLS, public
  network exposure, distributed runner, or streaming ZIP compression. CI now runs a short
  real-Core bootstrap (3 cycles) and Stage 11 (7 physical steps), but not a\n  full scientific campaign. Operator validation required.

## Acceptance gates

**Implemented**: Phase 1 local service/API, closed catalog, subprocess worker,
restart/cancel statuses, read-only import, event browser, original downloads,
ZIP, SHA-256 byte checks, tests and UI.

**Not claimed**: complete Core WAL recovery, independent scientific validity,
Oracle ground-truth attestation, 2D replay or operator approval. Phase 1 stays
**IN_PROGRESS** until reviewed and explicitly accepted. Phase 2 is design only.

## Phase 1 operator acceptance checklist (manual, no scientific verdict)

Use a dedicated unprivileged account, local browser and a **new** mode-0700
run root. Keep the Core checkout read-only and do not grant the Observer OS
account write access to independent Oracle/Bench archives.

1. Confirm the login rejects a wrong token, accepts the configured token,
   and logout removes access to protected API routes.
2. Run bootstrap (seed 0, 3 cycles). Confirm a terminal SUCCESS, exactly
   three lab telemetry events, a downloadable original JSONL and a matching
   integrity digest. This does not prove physical cognitive steps.
3. Run the real Stage 11 diagnostic (7 steps). Confirm the report identifies
   seven physically executed steps, the offline audit completed, and neither
   external Oracle nor Bench was loaded. Scientific validation must remain null.
4. Open the journal and Oracle explorers with separately provided read-only
   canonical sources. Confirm each source is labeled independently, unavailable
   data is not fabricated, and corrupt records are explicitly reported.
5. Download a ZIP and original file; compare their bytes and independently
   retained SHA-256 hashes. Observer does not establish journal chain validity.
6. Cancel a longer test, verify it is not marked SUCCESS, and confirm no
   unexpected child processes remain. Simulate an incomplete receipt in a
   disposable test root, restart, and verify new runs are blocked (HTTP 409).
   Inspect host processes and use a fresh isolated root to resume operations.
7. Confirm Core runs without Observer, no Observer import appears in Core,
   and no Oracle or Bench secrets are passed to an I0 child environment.

Record operator name, date, OS, Python version, Core SHA, Observer SHA,
artifacts/digests, observed failures, and an explicit **ACCEPT / REJECT**
decision. A green CI is not an operator acceptance decision. Phase 2 replay
remains out of scope until this Phase 1 gate is approved.

## Phase 2 (work in progress)

The **Replay historique** tab browses recorded events by journal `t_monde`
or Lab bootstrap cycle. Those timelines are not interchangeable. Imported
`world_frames` files are validated structurally via
`/api/runs/{id}/replay/frames/diagnostic`; the UI displays invalidity
reasons and keeps the 2D map disabled. A structurally valid file is **not**
a verified physical history, even if it carries self-declared attestation
fields. Independent canonical-journal verification and a trusted export
source are required before enabling the map. No Core imports or modifications
are required for this read-only diagnostic.

The replay page also shows a read-only canonical journal hash-chain preflight.
Its computed head and event count come from the imported bytes; without
**separately trusted** head/count they cannot prove an untruncated history.
The preflight is not the Core's complete independent causal audit and does
not establish world-step closure, death sealing or physical truth. Therefore
it never unlocks the map.

### Phase 2 detached signed custody (operator verification)

An imported `observer-source-v1.json` may name `world_frames`, `journal`
and `detached_attestation` as **separate read-only files**. The detached
attestation follows `observer/contracts/observer-detached-attestation-v1.schema.json`.
Its Ed25519 signature covers canonical JSON bytes of the `payload`
(`sort_keys=True`, UTF-8, `ensure_ascii=False`, compact separators).
The private signing key must never enter the Observer, its import directory,
the Core process or the web form. Obtain the public key and expected key ID
through an independent operator-controlled channel, not from the archive.

In **Replay historique**, enter the independently obtained public key (raw
32-byte Ed25519 key, Base64) and key ID and select **Vérifier la signature**.
The API `POST /api/runs/{id}/replay/frames/signed-custody` checks signature,
frame bytes, individual identity, journal chain head and event count, and
recorded step closure. A successful result establishes only a **signed custody
claim**, not physical truth. The key origin is not automatically authenticated
by a mere operator paste, and this endpoint never enables the map.

The final operator acceptance gate must include independently audited
physical world-state provenance and adversarial import tests. Until then the
Phase 2 2D map remains intentionally disabled. The historical event timeline
and all available diagnostics remain usable.
