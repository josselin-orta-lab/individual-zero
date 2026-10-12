# Stage 12: independent external operator-control custody audit

**Status:** technical proposal, pending exact-head CI and independent operator review. The normative source remains `docs/architecture/reference/en/mvp-specification-v1.3.1.md`; this is not a specification amendment.

The general canonical journal verifier can establish hashes, full step closure and terminal events but does not by itself establish the *lineage* of an operator's declared policy, monotone step cap and terminal stop. A fully rehashed archive might otherwise carry a plausible stop kind with a forged cap or versioned operator action. This verifier adds a separate, no-I0-import state machine for:

- Exactly one `operator_console_configured` event, valid mode and policy, at a closed physical-step boundary.
- Zero or more `operator_step_cap_set` events with previous-cap continuity, no cap increases or caps in the past, and no physical step opened above the enforced cap.
- A terminal `experiment_stopped` event tied to the *same* policy, mode, current cap and closed step. A `world_step_cap_reached` stop must occur at the precise cap.
- Contiguous deterministic operator event IDs derived independently from the versioned record schema. Missing or reordered operator events are not silently accepted.
- No operator control during an open physical attempt, no unexpected external-operator event kinds and no event following operator termination.
- Rehashed forgery tests where the generic full-life hash audit accepts the modified bytes but the independent control reconstruction refuses the inconsistent operator semantics.

This is a **read-only technical claim**. Neither a valid operator event nor a valid hash proves that the external human truly authorized a decision. For anti-truncation custody, pass a separately retained trusted final head hash and occurrence count. It is not a WAL crash-consistency proof and cannot resolve M-11.

## Focused test

```bash
python -m unittest discover -s tests -p 'test_stage12_operator_control_audit.py' -v
```

Integration with the real `Stage12OperatorConsole`, a retained mortal trial, and the combined operator evidence packet belongs to the separate **TEST ONLY** branch PR #109 until the source PR review concludes. Do not merge without explicit operator permission.
