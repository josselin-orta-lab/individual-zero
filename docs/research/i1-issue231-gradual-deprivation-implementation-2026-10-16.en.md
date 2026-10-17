# I1 issue #231: gradual deprivation and terminal integrity, implementation note

Status: **software patch authored; no tests or mortal lives executed**. Date 2026-10-16.

Source branch inherits I1 #229 work and A2.39 experimental descendant. Neither the normative I0 world nor the shared Lab WorldBody nor frozen historical A2.38/A2.39 evidence has been edited.

## Diagnosed original behavior

Shared `WorldBody._body_after_continuous_dynamics` decrements food and water on every physical action; `WorldBody.apply` previously deducted integrity for hazards and berries only, and declared death for `zero_integrity` and lethal terrain. Zero food/water alone did not damage integrity.

## Versioned I1-only implementation

The I1 isolated builder (`scripts/build_i1_fork.py`) patches **only the generated `i1lab/world.py`** on build, not `src/lab/world.py` or `src/i0`. Its derived WorldPhysicsConfig gains two explicit frozen fields:
- `starvation_integrity_damage_per_step` (default 0)
- `dehydration_integrity_damage_per_step` (default 0)

The defaults of zero preserve previous I1 reference/historical physical behavior. To **activate at an independent new I1 birth**, use the versioned `scripts/i1_deprivation_profile.py` helper:

```python
from i1_deprivation_profile import enable_gradual_deprivation
physics = enable_gradual_deprivation(physics)  # newly generated i1lab config
# Pass physics as world_config to the ordinary mortal I1 constructor.
```

This pins `+i1-gradual-zero-needs-integrity-v1` in physics.version and uses:
- Food at zero after actual action: **0.5 integrity damage per physical step**.
- Water at zero after actual action: **1.0 integrity damage per physical step**.
- Both at zero: **1.5 combined damage per step** before clamp.
- Replenishment by a legitimately executed `manger`/`boire` is applied first; recovery above zero prevents that deficit's damage that same step.
- Forced physical failures, waiting and sleep still consume a physical step; starvation/dehydration act independently of command intent.
- All body variables remain clamped to [0,100]. Death is not triggered by the isolated zero deficit itself, but by actual **integrity reaching zero** in the existing `zero_integrity` terminal mechanism. Existing terminal freeze and physical custody remain authoritative.
- An ordinary visible body capture can subsequently convey a loss of integrity. Rates are physical-world contract, **not** a learned or injected cognitive prediction; no hidden toxic labels are sent.
- Actual damage components are recorded in `TransitionResult.effects['deprivation_integrity_damage']`; the event is physical receipt, not an automatic reward or evidence of learning.
- The I1 world physics config contains both rates in `as_dict()` and its digest. The M11 structured runtime birth fingerprint already includes `runtime.world.config`.

Rates are preliminary experiment settings, **not** scientifically calibrated truths. Normative proposal PR #239 and issue #231 remain open for future interpretation and review. This is not a validated nutritional learning outcome and does not repair cognition by forcing food/water commands.

## No validation performed

No test code was added or executed and no independent physical cohort was born in this intervention. Physical implementation is committed, but run-time correctness, integration, I1/I0 non-regression, journal parity and long-term behavior remain **unverified**.
