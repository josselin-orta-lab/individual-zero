# Stage 12: S_t module occupancy, development note

Normative v1.3.1 retains v1.2.1 §16.1: monitor entropy of **S_t occupancy by module**. This is distinct from the existing `Stage12LivedDetectors.low_context_entropy`, whose window measures recurrence of perceptual signatures over time.

`stage12_occupancy.module_occupancy_entropy` is a *pure read-only, deterministic* metric. Input is a mapping of module names to the number of currently retained `S_t.competitive` elements attributable to each producer, obtained without inspecting the journal, Oracle or Bench. Normalize by log of an explicitly fixed module universe. No elements means **unavailable**, not a fabricated warning. This PR deliberately does not introduce a new owner, motor veto, reward, or unpriced runtime computation.

## Remaining integration contract

1. Select the fixed module universe from the injection config, and project `S_t.current.competitive` refs to the original emitting module using the existing retained-contribution registry, without reading hidden world truth.
2. Charge the metric to Metacognition/Health using a versioned P-43 operation cost, at an authorized phase. Insufficient UC -> unavailable, never `False`.
3. Journal module occupancy counts, total slots, policy version and result to an external technical operator receipt; do not expose technical journal reads to I0.
4. Verify real integrated samples and adversarial accounting in the independent auditor; compare with existing temporal context-entropy rather than substituting one for the other.
5. Preserve single owner, irreversible death, no postmortem reporting. This is not a scientific claim or stage completion.

A source-only detector and focused unit tests are supplied here, **not** a claim that the full Stage12 runtime obligation is already discharged. M-11 remains FAIL; issue #110 remains open.
## Implementation update: charged runtime and independent reconstruction

The Stage12Runtime now runs the pure metric at phase 5 of each *waking cognitive cycle* using the current published S_t version and Gatekeeper's detached retained-contribution provenance. It uses the fixed and versioned eight-producer `MVP_PHASE1_PRODUCER_ORDER`. It charges `metacognition_health/stage12_occupancy_entropy` with configurable positive `module_occupancy_cost_uc` (default 1), declared before birth in P-43 ceiling/envelope/operation costs. A rejected charge creates `stage12_st_occupancy_deferred` and **does not** generate a metric. The metric is a technical operator diagnostic, not a new motor veto, reward or extra cognitive owner.

The external `lab.stage12_occupancy_audit.audit_stage12_occupancy` first verifies the full chain, then reconstructs the current S_t contents from *earlier* admitted Bus producer witnesses and the `s_t_published` reference list. The verifier enforces one earlier charge per accepted result or deferral, recomputes the module counts and Shannon ratio, and rejects forged counts in a **properly rehashed** journal. The proof concerns trace consistency and UC receipts, not privileged physical truth.

### Exact quick validation (on PR head)

```bash
python -m unittest discover -s tests -p 'test_stage12_module_occupancy.py' -v
python -m unittest discover -s tests -p 'test_stage12_occupancy_runtime.py' -v
python -m unittest discover -s tests -p 'test_stage12_mortal_runtime.py' -v
```

Each invocation must be run against the actual PR head commit; tests are not certified until CI reports success. For operator acceptance, verify real sessions with nonempty and empty S_t, quota exhaustion, absence of postdeath receipts and the independent trusted head/count. A successful diagnostic is not a scientific demonstration of the expected whole-life behavior.

**Still open:** genuine lived agency-attribution outcome pairing (#110), M-11 crash-consistent current-state custody, exhaustive module-by-module DC-07/Stage12 acceptance and an operator signoff. The old phrase “remaining integration contract” above describes the **initial audit plan**, now implemented in this PR where described.


### Operator-facing standalone audit (implemented)

With Python 3.11/3.12 and a *complete immutable canonical export* (not a raw WAL including trailing delimiters), verify the reported module census and its real UC debits using the operator tool. Use an independently retained trusted head and occurrence count to guard against suffix truncation:

```bash
python scripts/report_stage12_occupancy.py /path/to/canonical-export.jsonl \
  --expected-head <trusted-sha256> \
  --expected-count <trusted-entry-count>
```

The command exits 1 when the chain, source references, decoded canonical $f64 values, module census, cost receipts or trusted tail disagree. Its code never imports the i0 package. A positive report describes provenance consistency, not truth about the simulated world's hidden state, motive or cognitive adequacy.
