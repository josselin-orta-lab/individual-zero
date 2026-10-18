# Post-issue-314 natural I1 population restart

**Scientific starting point**: main `9ad819f2ae61df9de3408d68defbff66525513ee`, including merged #315. PR #311 belonged to the **pre-314 architecture** and cannot be pooled with this study. The corrected natural constructor now enables first-person place memory, physical local route surveys, observed-route reuse and tentative entity motion diagnoses. The previous capability audit still expected route survey/search disabled; research branch fixes that laboratory contract, *not the I1 engine*.

## Prespecified first screen

36 fresh mortal individuals, each 400 steps maximum: six frozen at-birth exploratory profiles (native C0, then geographic novelty/intrinsic weights C1=0.20/0.35, C2=0.30/0.35, C3=0.20/0.55, C4=0.30/0.55, C5=0.45/0.55), three unchanged registered world presets (`oasis`, `foraging`, `dry-valley`), independent paired identities/seeds 1041/1042. All candidates retain `observe_routes=True`, `refresh_surveys=True`, `remember_entities=True`, `max_place_candidates=3`, route option enablement and the corrected GoalManager 0.04/0.35, sleep, TD, hunger, physiology, toxic berry -10 and death irreversibility. Candidate C0 forwards exactly the native configuration unchanged.

Born Stage4–12 capability audit must pass before any step and verifies spatial memory active, route surveys/search active and owner consistency. The lab never tells I1 where water is or how to act. Each unique WAL contains the full life, is audited with the native cryptographic journal verifier and is stored with a report of body trajectory, actions, water-zero steps, visits, memory sightings and route surveys. Ranking is operator-only and may be considered after all arms complete, with hard gates for memory interactions, applied drinks/eating, true site arrivals and deaths. A 400-step screen alone cannot justify scientific GO: reserve new seeds and unseen worlds for long replication.

## Software investigation

Audit suspect 1 (confirmed): stale `tools/audit_i1_birth_capabilities.py::EXPECTED` still expected geographic route search and survey disabled despite merged main #315 activating them. Changed only this lab contract to the real corrected natural birth; tests preserve fail-closed activation expectations.

Risk 2 (to verify with WALs): options based on remembered sites may be registered but never cross Competition, or be outcompeted by gratuitous exploration. The existing `tools/audit_i1_spatial_navigation_314.py` distinguishes mere sighting, recall, proposed option, registered, crossed, physically applied and actual destination arrival. No answer may infer successful learning from a mere recall.

Do not alter the engine to make a test pass. In case of genuine owner/module defects, isolate them as an issue and a separate code fix PR with a legitimate test, maintaining an unmodified main control.

**Status:** RUNNING / SCIENTIFIC VERDICT PENDING.
