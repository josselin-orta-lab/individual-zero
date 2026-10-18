# I1 #314: generic first-person spatial memory, draft proof protocol

The cognitive mechanism is no longer water-specific. The sole Stage11 Exploration geographic owner records bounded `PlaceMemory` entries keyed by a personally perceived `entity_id`, with type, last observed location, observation origin, birth/life identity, time, confidence, arrival and contradictions. Perception's `visible_entities` is the only entry point. Observation and route history are part of the owner's ordinary causal export and M11 custody; I0 remains unchanged.

An entity's last observed location is **not** a promise of present occupancy or usefulness. If an entity moves while visible, its latest perceived position replaces the old one. If its prior position is currently perceived and the entity is absent, confidence decreases without deleting the historical observation. Remote nonvisibility never proves absence.

For any actual active Stage4 goal, Phase0 freezes prior recorded observations. A priced Stage11 Planning read can build one `SpatialReturnTarget` across edges already surveyed from personally visited sites. The current first hop must also be currently visible and passable. No operator map or full planned motor sequence is ever supplied; each new step requires replanning. Stage3 Action Control and Stage8 Competition retain final authority. The memory's informational score is capped at 0.12, and the preexisting Stage8 TD evaluation supplies any evidence of consequences. No entity type is declared food, safe, dangerous or physiologically effective by this feature.

The new unit scenarios include resources, water, creatures and an unknown type, as well as spatial contradiction, future-memory rejection, no path, duplicate identity and cold owner restore.

## Scientific limitations

- The current path offers a place as a potentially informative destination whenever a natural goal exists; usefulness to **that** goal must still be learned from individual interaction. The generic informational interest is not evidence of a positive physiological consequence.
- Interaction milestones (`used` and attributable effects) are still owned by the canonical causal learning path, not by spatial memory. Do not interpret a place reached as an act learned or a need satisfied.
- Detailed UC and Stage11 concurrent candidate behaviour needs physical evaluation. A route survey is now active in the experimental natural configuration. Its independent impact must be controlled.
- Exact generated-source parity against a pre-change migration reference will reject intentional additions and must be made capable of explicitly documented I1-only development without weakening immutable I0 parity.
- Before scientific GO: pass CI, verify M11 cold recovery, inspect WAL for proposal, crossing, admitted action and physical destination arrival. Run matched 300- and 1000-step lives on untouched main and experimental commit. The independent scientific PR #311 must not be changed.

**Current verdict: implementation experimental, end-to-end learning and survival NO-GO / INCONCLUSIVE.**

## Audit remediation, active branch

- Goal gate is no longer hardcoded to `drink`. Other active first-person goals may retrieve a location, but no innate link to the resource's physiological value is made.
- A bounded retrieval API returns up to 3 spatial alternatives in natural I1. Every alternative must pass independent charged one-hop planning, local safety and normal Competition registration, with a separate cap from geographic novelty proposals.
- Phase-0 options contradicted by later paid Phase-1 perception are withdrawn without crashing the life; each candidate retains its own reference and causal provenance.
- Entity-neutral option invalidation and the configured intrinsic modulation scale are respected. TD learning signatures remain keyed by personally observed entity ID, and only normal applied-action learning can update them.
- Deterministic owner tests now cover multiple offers, cold snapshot restore and local contradiction handling. End-to-end physical selection, resource efficacy attribution, UC/cycle frequencies and 300/1000-step paired survival are pending and do not justify a scientific GO.
- The world presently ranks water/creature/shelter IDs by visible-set enumeration; stable physical identifiers for mutable entities need a separate correction to avoid apparent identity shifts. No claim of lifetime tracking across motion is made.

## 2026-10-18 identity-custody refinement

Perception currently labels water, shelter and creatures by a transient local index. This is **not** a durable individual identity. The spatial owner consequently keys each first-person place by observed entity type and exact *personally seen* coordinates (`sighting:type:x:y`), retaining the raw `perceived_entity_id` as provenance only. Two independent sightings with recycled sensor label cannot be fused, and a moving creature leaves uncertain observations of sites rather than magically tracked personal identity. This deliberately avoids claiming that two encounters concern one creature. It requires future separately evidenced identity tracking for genuinely mobile entities.

New regression coverage: independent same-label water sightings and moving-entity observations, in addition to generic multi-option memory tests. Current physical-action and survival GO remain not demonstrated. The separate PR #311 is untouched.

## Latest correction and read-only evidence audit

A missing OptionProposal plan is rejected before dereferencing its ID in the spatial evaluator. A standalone read-only WAL auditor is available at `tools/audit_i1_spatial_navigation_314.py`; it independently audits the durable hash chain, counts sighting/recall/proposal/registration/crossing events, and **explicitly refuses to infer applied physical action, arrival or learning from these events alone**. It requires a paired, independently verified physical trajectory to promote a scientific claim. The audit never rewrites or resumes an individual and does not touch the original I0 model or scientific PR #311.

## Physical trace attestation v2

`tools/audit_i1_spatial_navigation_314.py` now matches the same WAL attempt and chronological order across a prior perceived site, Planning proposal, Competition registration/crossing, Action Control admission, sent command digest, single physical world transition and committed step closure. A step is marked as a witnessed return only when the physically observed next position matches the proposed hop and the site was seen **before** the action step. An arrival at the remembered site is a separate, stricter conclusion. Unit tests use synthetic event sequences to prove false-positive resistance; those tests are *not* a lived physical demonstration. TD/cause learning and survival gains remain independent scientific questions.

## Code-audit optimizations (2026-10-18)

- Phase-3 Exploration's frozen offers are now reconciled after actual Competition registration, UC payment and registry capacity enforcement: proposals only deemed admissible, or evicted/not charged, cannot remain in the active owner offer set.
- Constructing the one physical SimulationState for several remembered-site candidates is deduplicated per Planning cycle. Each candidate still receives its individual preflight and UC charge.
- The external WAL auditor takes one byte snapshot, verifies the cryptographic chain of a sealed copy, and classifies exactly those bytes. This eliminates a verification-to-re-read race on a live journal; no cognitive/physical state is modified.
- Learned utility remains scientifically NO-GO and long-term survival INCONCLUSIVE pending matched physical WAL cohorts.
