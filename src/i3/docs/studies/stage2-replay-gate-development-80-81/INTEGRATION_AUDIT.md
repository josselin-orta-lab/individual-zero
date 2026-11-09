# Integration audit: Stage-2.1 exact transport bundle

Uploaded package: `i3-stage2-1-exact-transport.zip`, imported with a
thin Git bundle.

- ZIP SHA-256:
  `275e22e03485bf802b95074d410b5023c5cf889e2ca52514de1403ecd73bab7e`
- Git bundle SHA-256:
  `b8df6680f4fa4a8052c545d36289b02657eb81cbd513d769993f4854c8336da7`
- Exact ancestor: `28d33895141a8bbe5a5bbde8f48c7558bb7475d3`
- Prospective frozen plan: `e178a726c20ed682568f26613676422451522862`
- Supplied implementation: `e23a28ef37d232d866543786af838ab2b2382673`
- Supplied rehearsal receipt: `4000293da6641f3401db1eca028c9c38f25de19f`

The exact Git history was imported into PR #1220, preserving the plan-first
freeze, implementation-second, original rehearsal-third sequence. The
initial rehearsal PASS has fingerprint `15136d13…d967f9`.

Review found that a caller-supplied substitute owner ledger and a reused
World name were not adequately rejected. Those defects were corrected with
source changes and regression tests. Accordingly, the original PASS is
historical engineering evidence only and is not the current transport
certification. The hardened full-scale rehearsal is documented in
[HARDENED_REHEARSAL.md](HARDENED_REHEARSAL.md), with fingerprint
`dcada9e221f79b9450a4f05fecd20e60ac6595bb306aa871f29e45aefea0b6f1`.
A second full-scale engineering rehearsal using Python 3.12 also passed on
exactly the same content fingerprint, with a separate immutable
[report](HARDENED_REHEARSAL_PY312.json). Python 3.11 and 3.12 both pass
36/36 G/R and all structural invariants, without opening any scientific World.

The frozen development plan remains indices 80/81, genomes 911/912,
life-seed base 7,540,000. No development, selection, validation or reserve
World was opened by integration. Engineering rehearsal opens only the
declared non-evidentiary cohort under ADR-0019.

**Disposition:** merge the hardened exact transport only after I3 CI succeeds;
keep ADR-0017 active until an explicit owner lift in the canonical ledger.
