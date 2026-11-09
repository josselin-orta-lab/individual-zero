# Stage 2.1 v3: sealed original readout adapter (software-only)

**9 November 2026. NO SCIENTIFIC WORLD OR STUDY AUTHORIZATION.** This is a follow-up to the [fixed-G0 mechanism-first design](MECHANISM_FIRST_CANDIDATE_V3.md) and the corrected [selected-pipeline sealed bridge](SEALED_SELECTION_BRIDGE.md). P1.3 remains reference, I3 unregistered, and DEVELOPMENT 80/81 exhausted.

## Scope

The software-only `i3.lab.stage2_mechanism_first_sealed.from_sealed_originals` reads only a fully completed **720-life** archive corresponding to the three v3 arms `FIXED_G0`, `GATE_G0` and `RANDOM_G0` on 240 fixed newborn G0/world blocks. It does **not** select founders or reuse the 3,840-selection plus 1,200-validation selected-pipeline protocol. It never generates a World, dispatches a Mind, issues a ticket, claims an index, or issues a scientific GO.

The adapter requires `i3-stage2-1-mechanism-first-sealed-lock/v1`, intentionally different from the selected-pipeline source-lock schema. It reuses the existing two-phase sealed-original verifier, requiring externally supplied source, manifest, transport and plan SHA pins. Every original is checked for the exact F0 family, population, index, world and life seeds and for the five unselected G0 birth seeds chosen before outcomes. It rejects missing, duplicated, foreign or cross-protocol cells.

Each life is verified against the actual `run_life` schema: complete manifest and source hash consistency, G0 birth-genome digest, matching World snapshot digest across paired arms, actual terminal/death/censoring, source-locked transport admission for GATE/RANDOM but not FIXED, and real cognitive energy/vigilance payment. RANDOM additionally verifies the distinct funded draw count, nominal/eligible/paid replay counts and frozen `5532/867` schedule. The complete checked records are then reduced by the existing v3 **descriptive only** calculator: lived steps, survival at 400, paid cognition per assigned life, inactivity and family/population contrasts.

## Boundaries and unresolved scientific decision

The pins supplied by the caller and the in-archive checksums can agree with themselves without proving a genuine pre-exposure, independently approved source or a World generated from the frozen original ecology. A separately authenticated source and World snapshot witness is still necessary. A successful structural readout cannot certify population independence, improve inferential power, or approve a 5-point mean survival non-inferiority claim. In particular, it must not be misrepresented as a completed scientific experiment or evolutionary selection.

**Verdict: ENGINEERING READER ONLY.** A future v3 experiment still requires independent methodology review, a prospective study record, seed/index collision audit, exact source and World locks, complete full-size G/R rehearsal and a new index-scoped owner lift. This module grants none of those rights and is never a replacement scientific execution entrypoint. All tests use fabricated records or tiny toy archives, not scientific lives.

## Mechanism exposure: physical replay parity is not implied by a nominal schedule

The **read-only** v3 original adapter also extracts, for each assigned life and each fixed family/population, the original funded GATE/RANDOM decision-audit counters, reached sleep actions, funded gate sleep steps, physically executed and paid replays, and RANDOM funded draws/nominal/eligible replay opportunities. Totals and per-assigned-life rates are reported by arm, by population and by F0 family. RANDOM scheduled-minus-paid and eligible-minus-paid gaps remain visible, as does GATE-minus-RANDOM paid replay count.

The frozen RANDOM `5532/867` value was calibrated to **nominal** DEVELOPMENT 80/81 GATE replay count. It is not a guarantee of equal *actual* replay work in v3. A life may die before a sleep, lack physical replay eligibility or not afford a previously scheduled replay. These shortfalls must not be hidden by conditioning only on surviving or successfully funded sleepers.

**Interpretation rule:** no check of these realized counts is a new selection criterion, retrospective matching, gate threshold or permission to resample, rerun or change the frozen RANDOM schedule. Even if actual counts happen to match, a difference in outcomes does not automatically prove the superiority of context-sensitive replay selection: trajectories diverge, and decisions, total cognition and bodily states can also differ. If paid replay counts differ, the mechanism comparison is still descriptively useful but cannot be attributed solely to smarter replay prioritization. The fields `realized_replay_parity_proven=false` and `causal_mechanism_advantage=NOT_ESTABLISHED` are deliberately non-promoting.

**Status unchanged:** software-only test of retrospective measurement, no new World, source owner-lift, registered scientific study, population generalization or survival non-inferiority.
