# I1 natural agency: default-on birth integration

2026-10-16. Implementation status: source committed, no new physical tests run.

## Default behavior for all new living I1 descendants

The isolated I1 build script now generates an I1 WorldBody with **0.5 integrity per physical step at food=0** and **1.0 integrity per physical step at water=0**, applied after actual ingestion/drinking, before terminal zero-integrity detection. Both can act together. This is external physiology, not innate cognitive knowledge. In I0/shared Lab these properties are unchanged.

The I1-only generated Stage11SleepRuntime (common Stage12 ancestor) now **always** applies the versioned `enable_natural_sleep_birth` policy during constructor preparation. Newborns therefore automatically accumulate UC-based fatigue, memory-backlog and night sleep pressure, genuinely restore physical energy on sleep, and may consolidate lived episodes under paid Stage10 UC. There is no caller flag, helper call, separate optional profile or forced sleep command.

`ExperimentalI1Stage12Runtime` now defaults to `i1_unknown_action_enabled=True`: `manger` can be considered from already perceptually available inventory without inventing food/safety consequences, but Stage6/Competition/Stage9/Action Control remain in control and UC is charged. No automatic collect/eat sequence is installed. The first-person food-affordance mechanism is designed to operate even without the external `MOVE_E/COLLECT_B` predictor.

## Historical science

A2.38 and A2.39 archived source commit hashes and recorded outcomes are immutable. New births on this **new** revision adopt the policy; running archived protocols against their original commit reproduces their historic configuration. Never relabel historical cohorts as new-default cohorts. I0 and the shared normative Lab remain unchanged.

The old opt-in helpers remain as compatibility/source definitions; **no operator call is necessary or expected for new births**. Reapplying the same sleep profile manually to already versioned I1 constructor input is rejected to avoid double-versioning. Older cohorts should run from their frozen historical source, not current experimental HEAD.

Source changes are only in `scripts/build_i1_fork.py` and `src/i1_overlays/i1_active_runtime.py`. No tests, physical births or outcome claims were made. Mainline integration requires review of the stacked PR ancestry and validation.
