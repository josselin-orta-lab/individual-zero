# I1 issue #314: lived water-place navigation, provisional design

Source control baseline: `main` at `2161b834e4a584c28bcbb663e8d6d04e41c7e70b`.

The I1-only Exploration geographic owner stores finite first-person `WaterPlace` records and uses the existing visited-site ledger and paid `ObservedSurvey` topology. Records are not operator-map facts and carry site coordinates, original observation coordinates, first and latest perceptual sightings, observation provenance, optional physical arrival, confidence and contradictions. A site no longer visible from the current local capture is not classified as absent. Fresh local non-water observations decrease its confidence without deleting it.

When the living Stage4 goal is `drink`, Phase-0 freezes geographic owner data. A charged Stage11 Planning route read walks only recorded visited edges; the first hop also has to be locally perceived passable in the current capture. A destination without a complete observed-edge return path produces no candidate. At most one bounded water-return option is created; normal Stage8/Competition and Stage3 Action Control retain full authority. The memory evaluation bonus is capped at 0.35, scales with water deficit and confidence, and is not a Q reward, a forced action, or a learned hydration claim.

Each code SHA must be experimentally compared with the unmodified `main` control at identical world, seed and temperament. Required outcome states remain separate: recall, proposal, threshold crossing, action admitted, actual physical step, successful drink and attributed later physiological change.

## Caveats / blocking gates

- The dedicated branch enables `observe_routes`, `refresh_surveys` and `geographic_route_enabled` on natural I1 to permit physically observed return routes. This modifies route-observation CPU/UC demand and also activates preexisting frontier-transit behavior. Do not attribute outcomes solely to water-place recall until ablations control these changes.
- This initial implementation has no verified `used_step` attribution after an actual `boire`; it must not claim that a seen place is proven physiologically useful. Eventual cause-specific positive hydration confidence remains unproven.
- The actor-class `individual_id` field is not sufficient to independently certify per-birth identity; verify the authenticated life_id capture/WAL ownership before GO.
- Full integration, UC, M11 restart tests and actual 300/1000 step paired populations have not run in this session. CI is mandatory before converting the draft to ready.
- A memory-influenced proposal is not proof of selection or action. A drink action is not proof of causal learning. Increased survival requires separate physical evidence.

**Scientific status: NO-GO pending CI, physical WALs and paired population evidence.**
