# I1: active natural artificial individual

This is the **active** engine, independent from frozen `src/i0`.

- `modules/`, `architecture/`, `config/`: cognitive contracts, state and mechanisms.
- `runtime/`: first-person I1 birth, temperament, natural-life runtime,
  learning, sleeping and active publication sources. These are part of I1,
  **not optional overlays**.
- `scripts/build_i1_fork.py`: currently builds an isolated `i1lab`
  package, including an isolated copy of the shared Lab. This is still a
  transition mechanism: source-string transforms remain and need their own
  controlled migration before being removed.
- `scripts/test_i1_ci.py`: real I1 smoke/full, irreversible mortality and
  authenticated M11 checks.

The first native-source migration moves the runtime source files **byte for
byte** into `runtime/`, but preserves the original generated namespace
`i1lab.i1_natural_runtime` and birth contract. The generator skips
`i1/runtime/` in its `i1` copy and installs it exactly once in `i1lab`.

Do not re-enable H1/H2 experiment arms as I1 defaults. Historical trials can
remain importable but do not define the natural actor. I0 is untouched.
