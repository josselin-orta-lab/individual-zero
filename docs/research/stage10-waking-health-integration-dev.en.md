# Stage 10 waking-health integration, development slice

**Status:** SOFTWARE DEVELOPMENT, NOT SCIENTIFIC ACCEPTANCE / NOT FULL STAGE 10.

**Dependency base:** `i0/vnext-stages-10-12` at commit `646784c197cf4faf24558e37112ef5fa3cb706d1`. This integration is built on a **separate child branch** because parallel work was updating I0-vNext. The protected scientific Stage-9 experimental NO-GO status is unchanged.

**Normative reference:** `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, §§15.1, 15.3, 16 and DC-13. Neither EN nor FR specification has been edited.

## Implemented, narrowly

- `src/i0/modules/sleep_health.py` retains normalized `F_cog` and **once-per-world-step frozen** DC-13 pressure. Only real closed waking cognitive cycles contribute `a_F × UC_cycle / (C_max × B_cycle)`, capped at one. A replay of the same cognitive cycle may not count a second time.
- `src/i0/modules/metacognition.py` attaches this state **optionally** under the pre-existing, sole `metacognition_health` owner. Legacy Stage 4-9 behavior and snapshot field names remain unchanged with this option absent; snapshot restore preflights the optional state before mutating base counters.
- `src/lab/stage10_health_runtime.py` starts from the Stage-9 integrated software runtime, without depending on Exploration Stage 11. The scheduler wraps its existing phase-0 and phase-5 hooks. At the opening of a waking cognitive step it freezes `P_cons` and `p_s` from prior `F_cog`, the **currently closed** EpisodicMemory episode count and the accessible night flag. During phase 5 Metacognition and Health accumulates actual bounded logical compute UC. The frozen assessment is visible in the versioned `S_t.fixed.sleep_readiness`.
- The development-only memory occupancy reference capacity is explicit. Until actual consolidation exists, closed episodes are treated as unconsolidated; there is no pretense that they have been reorganized.
- `src/lab/stage10_health_reference_fixture.py` pins non-scientific P-39/P-40/P-41 values and a memory reference capacity. Tests in `tests/test_stage10_health_runtime.py` check frozen pressure across cycles, UC accumulation, owner uniqueness, snapshot rejection/replay, Stage-9 isolation, and journal determinism.

## Explicitly not implemented

- No option `dormir` is registered in Competition yet; `sleep_readiness.enabled_for_action=false`. The computed `m_a(dormir)` is *observable* but cannot influence the decision or act as a parallel planner.
- No asleep mode, reduced perception, reflex wake, dated-intention wake, maximum-duration enforcement during sleep or fatigue decrease on real sleep steps.
- No consolidated `h`, six transactional passes, cut point, paused/resumed consolidation, or coherent atomic rebase of Q/κ/precision.
- No reward for the fatigue computation, no Energy or other already-counted homeostatic D component in `m_a(dormir)`.
- No Stage 9 held-out execution, no use of sealed seeds or oracle truth, no Stage-10 scientific acceptance, no claim of a two-version 300-step Golden.

## Validation

Run `python -m unittest discover -s tests -p 'test_stage10*.py' -v` on this child branch, then short all-unit validation and smoke only if it is needed. Record the exact commit and CI receipt. **Do not merge to `main`**, or silently rebase/overwrite the actively developing `i0/vnext-stages-10-12` branch. After verification, offer this child branch via a draft PR into I0-vNext for controlled review.
