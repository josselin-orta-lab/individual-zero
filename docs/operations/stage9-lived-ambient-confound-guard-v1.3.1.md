# Stage 9 development note: first-person ambient injury control

**Status:** software correction proposed; Stage 9 remains **NO-GO** and
requires independent scientific verification and operator approval.

**Base dependency:** [PR #77](https://github.com/josselin-orta-lab/individual-zero/pull/77)
redacts the simulator's hidden damage-source fields from autobiographical
transition effects while retaining the complete append-only technical journal.

## Failure previously possible

The Stage-9 `ingest_closed_autobiographical_episode` code took a decrease
in integrity after eating as direct DC-05 toxic-food safety evidence. It
excluded alternative creature/zone injuries only by consulting
`effects.creature_damage` and `effects.danger_zone_damage`, two physical
attribution fields that belong to WorldBody's **hidden technical record**.
With PR #77 in place those fields are rightly absent from I0's view. Their
absence cannot be interpreted as evidence that no alternative injury occurred.

An ordinary, non-toxic berry eaten inside an unknown damaging zone can
produce exactly the same observed food, body and action history as toxic
food on clean terrain. Without additional observations the cause is not
identifiable from that single experience.

## Conservative software rule

A harmful food exposure is eligible for DC-05 evidence and downstream
numeric causal-correction or hypothesis observations only when the Causal
Model has an **actually applied, non-ingestion `attendre`** control:

- at the same perceived (x, y) position during the immediately preceding
  world step;
- with independently captured integrity **unchanged** during that control;
- with a matching applied command and physical transition, both present in a
  closed, authorized DC-09 autobiographical episode;
- with the next-step Perception integrity matching the body state and the
  pre-food integrity;
- with provenance validated and retained within the Causal Model's
  snapshotted state.

If any component is missing, or waiting was itself harmful, the meal is
still physically executed and its full technical causal journal and
first-person memory remain intact, but it receives **no unwarranted DC-05
harm credit or numeric/correlation evidence**.

Previously admissible no-harm exposure observations remain possible. The
existing safety threshold, single-owner Causal Model publication, previous
life mortality rules, epistemic projection, and Oracle/Bench separation
are unchanged.

Controls are observed passively from genuinely applied decisions. This
does **not** schedule extra waits, force feeding, relabel an unexecuted
command as a physical trial, or use oracle knowledge. Expired controls
are retired unless their immediately following food exposure remains
awaiting a closed Memory episode.

## Limits and review

A clean wait on a previous step is **not definitive causal proof**:
future scenario injections, time-varying hazards, a creature arriving
between steps, hidden compensation by healing and unmeasured physical
changes remain possible. In particular, it must not be called a verified
absence of all confounding.

The current rule is a conservative development safeguard, not a sufficient
final design for toxic-food science. It can withhold valid toxic-food safety
evidence when I0 has no matched control, or when Memory closes different
segments out of order. This is preferable to a false established safety
claim, but warrants a separate operator review and scientific campaign
with contrasts, controls, uncertainty and falsification thresholds.

## Software validation

Run `python -m unittest tests.test_stage9_lived_evidence tests.test_stage9_lived_ambient_confound -v`,
followed by the full Python 3.11/3.12 software matrix and Stage-11
irreversible 600-step diagnostics after the security branch is integrated.

The tests include real `WorldBody` execution with a hidden damaging
zone, benign `berry_a`, authentic Stage-2 autobiographical projections,
and independently verified Causal Model evidence provenance. The full
technical journal still contains the zone damage; I0 must not learn its
physical label.

**Neither the test count nor a green CI reverses the Stage-9 NO-GO.**
