# I0-vNext Stage 11: local threat and recovery modulation, public development protocol

**Classification:** public software development only, not held-out scientific acceptance. **Registered before outcomes of this new probe.** English normative `docs/architecture/reference/en/mvp-specification-v1.2.1.md` §§6.4, 14, 16.4 and S-02.6 prevail. Historical Stage 9 stays NO-GO.

## Design and safety boundary

- Optional Stage-11-only producer, `local_threat_alerts=True` (OFF by default), observes only the four adjacent cells from a single Perception capture. If a creature is physically observed adjacent, Perception emits a risk=1, urgency=1 Contribution to the ordinary Gatekeeper. The security-preempted S_t element is the **sole** input to Global Modulation phase-0 threat entry. Never read WorldBody's private creature/danger layout.
- The `threat_clear` signal is affirmative evidence of the same **local** four-neighbor coverage with no adjacent creature, published into S_t after Perception; it is *not* a claim that the whole world is safe. The indicator is UNKNOWN if a capture is absent/incomplete. A threat alert's absence alone is not a confirmation; transition-out still requires P-24 hysteresis and two distinct confirmed world steps. Action Control reflexes/veto remain in charge, unaffected by profile weighting.
- Body energy/integrity values come from Perception and S_t fixed fields. Recovery enters only after confirmed low energy/integrity across different world steps and can exit after independently recorded body recovery and hysteresis. Stage 10 autonomous sleep is **not** claimed.
- Geographic Exploration can only propose locally perceived, passable frontiers, and is conservative about the currently observed adjacent creature's attack radius. This does not reveal hidden lethal or danger zones and is NOT a replacement for Action Control.

## Prespecified public cases

Use the fixed reference world and Equipment with no code modification to Stage 9.

1. **Local threat:** world starts with one public creature adjacent to the individual at `(3,2)`; full four-neighbor Perception is available. Run 7 world steps and record actual alert emissions, preempted S_t security contribution, profile transitions, physically applied reflexes, local-clear observations and the number of distinct-world-step confirmations. One may additionally run an externally preregistered `remove_creature` at step 3, only via the existing Scenario journal, not through the agent.
2. **Recovery:** initial energy `20` and intact integrity `100`, with no world energy decay/action energy cost. Run 9 steps; at step 5 a versioned public Scenario sets the body's energy to `80`. Verify that this externally induced recovery is published via later Perception, that entry/exit confirmations are delayed in world steps, and that no independent restorative action is falsely claimed.
3. **Geographic obstacle tests:** public variants of the reference layout with north blocked, east corridor or north creature. Keep fixed starting body at Value & Needs setpoints and run at most 8 steps per variant, with Stage-11 geography ON and OFF. Record physical captured sites, applied geographical options, candidate target directions, risk alerts, safety vetoes and verified journal digests. No hidden target injection or navigation plan scripting.

## Required negative checks

- Risk=0 or missing S_t risk cannot activate the threat profile; incomplete adjacent Perception is UNKNOWN, not a local-clear proof.
- Repeating cognitive cycles in one world step cannot satisfy an entry/exit confirmation duration.
- A local risk/clear report cannot bypass Action Control or force an action; the reflex stays higher priority.
- A blocked/creature-occupied neighbor must not become an informational frontier; a known lethal destination must still be vetoed. No map oracle, no hidden-zone classification, no synthetic observation, no predicted numerical effect for unseen Equipment input.
- No scientific GO, Stage-9 Golden change, hidden-world access, parameter calibration or statistical generalization is inferred from these fixtures.

**Output:** exact source SHA, CI run, public diagnostic evidence hashes, individual journal heads and observed limitations after execution. Null results remain valid.
