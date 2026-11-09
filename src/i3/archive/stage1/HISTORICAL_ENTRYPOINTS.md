# Historical Stage-1 commands and relocated implementations

Closed Stage-1 records include original CLI commands and source paths that
were frozen before the archive migration. **Do not execute these commands** on
new Worlds or replace the recorded source SHA with a current checkout. Their
presence in a protocol describes historical custody, not a live entrypoint.

| Historical module (removed from active `i3.lab`) | Original retained location | Current importability |
| --- | --- | --- |
| `i3.lab.stage1_candidate_f_cost_vs_policy_diagnostic` | `archive/i3/stage1-2026-11-09/legacy/src/i3/lab/stage1_candidate_f_cost_vs_policy_diagnostic.py` | Archived source only, not an installed Python module |
| `i3.lab.stage1_candidate_g_56_57_posthoc_first_contact` | `archive/i3/stage1-2026-11-09/legacy/src/i3/lab/stage1_candidate_g_56_57_posthoc_first_contact.py` | Archived source only, not an installed Python module |
| `i3.lab.stage1_candidate_i_development_62_63_plan` | `archive/i3/stage1-2026-11-09/legacy/src/i3/lab/stage1_candidate_i_development_62_63_plan.py` | Archived source only, not an installed Python module |
| `i3.lab.stage1_candidate_i_development_64_65_plan` | `archive/i3/stage1-2026-11-09/legacy/src/i3/lab/stage1_candidate_i_development_64_65_plan.py` | Archived source only, not an installed Python module |
| `i3.lab.stage1_candidate_i_development_66_67_plan` | `archive/i3/stage1-2026-11-09/legacy/src/i3/lab/stage1_candidate_i_development_66_67_plan.py` | Archived source only, not an installed Python module |
| `i3.lab.stage1_cost_reduced_diagnostic` | `archive/i3/stage1-2026-11-09/legacy/src/i3/lab/stage1_cost_reduced_diagnostic.py` | Archived source only, not an installed Python module |
| `i3.lab.stage1_diagnostic` | `archive/i3/stage1-2026-11-09/legacy/src/i3/lab/stage1_diagnostic.py` | Archived source only, not an installed Python module |
| `i3.lab.stage1_frontier_water_diagnostic` | `archive/i3/stage1-2026-11-09/legacy/src/i3/lab/stage1_frontier_water_diagnostic.py` | Archived source only, not an installed Python module |
| `i3.lab.stage1_frontier_water_fresh_diagnostic` | `archive/i3/stage1-2026-11-09/legacy/src/i3/lab/stage1_frontier_water_fresh_diagnostic.py` | Archived source only, not an installed Python module |
| `i3.lab.stage1_omega_candidate_f_falsifier` | `src/i3/archive/stage1/lab/stage1_omega_candidate_f_falsifier.py` | Retained for tests as `i3.archive.stage1.lab.stage1_omega_candidate_f_falsifier` |

The archival locations above preserve the original tests, protocols and
negative outcomes. **Do not revive historical command names as active shims:**
that would make closed Stage 1 look runnable and authorize accidental reuse.

Historical links fixed as navigation-only corrections in this audit:
- Stage-1 affordable-projection result links to its archived implementation.
- Candidate-H 58/59 result links to its actual frozen `PROTOCOL.md`.

Code and experimental results are not altered by these link corrections.
