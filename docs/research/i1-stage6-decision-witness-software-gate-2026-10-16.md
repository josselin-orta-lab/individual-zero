# I1 decision-witness software gate, 2026-10-16

**Scope:** Development-only, deterministic, non-scientific-replication gate on the I1 fork, in PR #219. I0 baseline on main at `8ce8711b2d5f86b184d66fcee1d95a3e39f30836` was not edited.

## Added evidence

- `tests/test_i1_decision_witness.py` builds separate `i1` and `i1lab` namespaces, uses independent mortality-enabled instances, a physically instantiated food-deficit world with a visible berry B, and three real executed step attempts per life.
- It compares an explicit model-ON I1 life with a model-OFF I1 life. This is a **software control**, not an independent scientific cohort. A synthetic model with the placeholder corpus identity `aaaaaaaa…` is used only as test input.
- For the enabled life the test requires actual `i1_partial_preaction_forecast` and `i1_partial_instrumental_option_proposed` events. It now additionally requires that the model-origin option is admitted into the option registry, evaluated by the existing Stage8 evidence seam with a non-null evidence value, and appears in an actual Competition trace.
- For the disabled life it requires **no** `i1_partial_*` events. Both life journals verify their hash chain.
- A partial forecast explicitly leaves `safe`, `terminal` and `causal_responsibility` null, and records that physical safety is not certified.
- These assertions passed on Python 3.11 and Python 3.12 at SHA `8d77bec75f4515c2080c58fe208a6e5894e62090`, GitHub Actions run [38855455103](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38855455103).

## Narrow conclusion

**Démontré logiciel :** an activated experimental I1 partial model can generate a preaction hypothesis, turn it into a grounded option, register that option, evaluate it, and put it before the pre-existing Competition accumulator. The I1-OFF control does not emit any factorized-model events in the same development world.

**Not demonstrated:** that the model-origin option *wins*, that Action Control *admits* that specific action, that this action is physically executed, that it advances a goal, or that it improves survival, calibration, UC efficiency or long-horizon decision quality. A trace showing an option in Competition is not evidence that the option was selected.

**Critical science boundary:** the six-field partial estimate does not know hidden mortality, bodily integrity or distal causal responsibility. A placeholder digest is not an authenticated external laboratory corpus; the study must replace it with a separately audited actual training artifact before prospective claims.

## Next acceptance stages

1. Register **exact model-origin win → Action Control admission → physical transition** with an authenticated command hash and one-to-one journal receipt, plus blocked/adversarial and negative controls.
2. Match I0 and I1 experimental births under the same physical conditions without mixing their cognitive journals. Do not use I0's memory as I1 evidence.
3. Pre-register new independent test worlds (visible nominal, confounded hidden danger, forced failure, lethal transition, truncated/missing observations) and fixed thresholds before observing outcomes.
4. Audit compute charges and excess uncertainty, verify terminal states and hard-crash M11 cold-recovery denial, and execute longer trajectories including consolidation.
5. Perform a review of the full PR, then run exact-head CI before considering merge. **Do not interpret a green PR gate as scientific GO.**

**Disposition:** PR #219 remains Draft; no automatic merge and no Stage validation change.

## Addendum: complete causal option-to-physical chain

A subsequent diagnostic on the same synthetic software fixture (run [38856712486](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38856712486), commit `c9256d830c90542c38583810c7e40407ddec0221`) exposed previously unasserted journal and return-value fields. The enabled I1 life produced a partial-model `collecter berry_b` option, whose Competition trace reports `crossed=true`, whose `command_admitted` carries the exact matching option reference and the cryptographic command hash `62946b34e269d6cfb640c90f7aad185bafa2417ee59a93164d8735d792668c96`, and whose physical step result reports `status=applied` for `collecter`. The disabled I1 control executed `attendre` for three steps and emitted no `i1_partial_*` events. These are physical WorldBody commands executed by *separate mortal runtimes*, not model-only simulations. The existing test gate is now strengthened to REQUIRE the full win/admission/applied chain rather than merely printing it; validation on this new assertion SHA is tracked separately.

The scientific interpretation remains strictly local: one synthetic, nonindependent development scenario with a placeholder model digest, not a new generalization or safety finding, and not an A2.30 independent cohort. There is no inference of food safety or distal causal responsibility. Repeating the same deterministic case under two Python versions tests compatibility rather than replication. No operator approval for deployment is implied.
