# Candidate-G projection dependence: results (declared descriptive diagnostic)

Protocol: [STAGE1_CANDIDATE_G_PROJECTION_DEPENDENCE.md](../../STAGE1_CANDIDATE_G_PROJECTION_DEPENDENCE.md),
declared at `4a5600d`, before execution. Executed once. Software only: **no
World, no life, no study index, nothing adopted**; Candidate-G's #1146 verdict
is unchanged. Data: [diagnostic.json](diagnostic.json).

## Resolution after canonical numerical audit (#1155)

The 32-state historical `per_step` count below is **not canonical truth**.
A later frozen audit using the already-authorized end-to-end high-precision
oracle at the same 255-unit cost/forecast selects **24 states, 0 water**, exactly
the same selected-state set as Candidate-F
([result](../stage1-candidate-g-canonical-numeric-audit/RESULTS.md)).

The eight historical extra water selections are caused by repeated-float
numerical semantics at vital boundaries. Do not design a future projector to
recover them. The durable conclusion of this study is therefore: consistent
projection raises Candidate-G from 1 to **24 canonical selected states**; the
remaining 24->32 historical difference is numerical artifact, not lost
canonical decision relevance.

## Result

The reference arm reproduces #1146 exactly, so the diagnostic is valid.

| Arm (frozen #1146 grid, 80 states) | Strictly advantageous epistemic trials | of which water-deficit | Declined | Mean paid simulated steps per state |
| --- | --- | --- | --- | --- |
| `reference` (P1.3 `chunk_end`) | **1** | 0 | 27 | 53 (×1.0) |
| `candidate_f_projection` (`event_local_quadratic4`) | **24** | 0 | 40 | 470 (×8.9) |
| `per_step` (diagnostic truth) | **32** | 8 | 40 | 1288 (×24.3) |

Cycles (18) and memory items (201) are identical across arms. Only projection
work differs.

## Reading

- **The lever is the projection, not personal recurrence.** On the same fixtures,
  an accurate projection makes Candidate-G decision-relevant in 24–32 of 80
  states, against 1 under the P1.3 reference. Its thin #1146 pass is a property
  of the end-of-chunk projection.
- **The obstacle is cost.** The accurate lab-gated projection multiplies paid
  simulation by about 9 here. Per-step costs 24 times more. This is consistent
  with the severe processing-budget failures of the funded Candidate-F
  architecture (868 `NO_PROCESSING_BUDGET` steps, 36.24% inactivity in 54/55).
- **A residual difference.** Candidate-F's projection selects no water-deficit
  state where per-step selects 8, although it passed its own decision-bias gate.
  This is worth an audit (likely death-boundary or water-specific segments).
- **Selected states are mostly non-water deficits.** That is expected and
  correct: the unsupported-effect prior is action-agnostic, so a first `boire`
  trial is valued as learning an unknown effect, not as "drinking relieves
  thirst".

## Next architecture question (proposed, not implemented)

**How can an individual afford a consistent self-projection?** Accuracy alone
is solved in the laboratory; affordability is not. One generic, first-person
candidate:

- Compute the accurate projection once per decision at the current body, plus
  its paid local sensitivity (one extra projection per channel).
- Value every option's end state by that local expansion instead of one
  accurate projection per option.
- Cost becomes six accurate projections per decision, independent of the number
  of options.

It must be frozen first as a software falsifier:

- decision bias versus per-step ≤ 1e-3 on this grid and the #1101/#1146 grids;
- paid work per decision reported against the reference.

No behavior or need is encoded, and the reference stays the default.
