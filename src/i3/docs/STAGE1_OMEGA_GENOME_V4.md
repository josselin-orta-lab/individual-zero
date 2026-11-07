# Stage 1 ω: genome v4 inheritance slice

Issue #1061. Baseline:
`0258b825f9373638699c750792f4d0d9833c44bf`.

**INHERITANCE ONLY. NO BEHAVIORAL WIRING. NO WORLD OR SELECTION.**

## Prerequisite

The owner-approved option-A software falsifier is complete:

- repaired Candidate F shows pre-contact omega capacity (#1125);
- post-contact personal safe/toxic and harmful histories can override the
  inherited disposition (#1126);
- personal post-contact paths do not read omega.

The next step is therefore to make the generic disposition heritable without
changing cognition in the same slice.

## Schema

Current:

`i3-genome-v3`, 30 genes.

Candidate:

`i3-genome-v4`, 31 genes.

The sole addition is:

`omega ∈ [-1,1]`.

It is appended **last** in `GENE_ORDER`, after `belief_rate`.

No action, token, modality, world family or body channel is encoded by omega.
Its meaning remains the generic unsupported-effect expectation tested in the
Stage-1 software falsifier.

## Birth semantics

`generation_zero(seed)` keeps the existing independent uniform draw mechanism.

Because omega is appended last, every v3 common-gene draw consumes exactly the
same RNG stream positions as before. The 30 common values must therefore remain
bit-for-bit identical for a given seed.

Frozen common-gene SHA-256 witnesses:

| seed | compact sorted JSON of 30 v3 genes |
| ---: | --- |
| 0 | `8d3258ef778c55edcc6eca4d3f9b8db591600238e41ae77e1bb0512021cc5d20` |
| 1 | `08c4e9c1ff21696076f19fb0a348be027f080c8330443877e156a754fdb607b7` |
| 39 | `c3dcb0188fb37a50d930ca8b702f6f724581c88cfb5f3528a3e60ea49400f624` |
| 2000000 | `528c8940531cbd8bcd0c4d7bcc9004c4089df63e4a01214f54b5303ca2df6b07` |
| 2000039 | `b82641779ab4180b6e26ffa0ff57b5604afa47f8b89862e7488bfffb032c38be` |

The midpoint genome has `omega = 0`.

The generation-zero distribution is symmetric by construction. There is no
designer-positive default.

## Mutation

The existing mutation algorithm is left unchanged. It mutates every declared
gene with bounded Gaussian noise, so v4 mutation includes omega automatically.

This slice does **not** attempt to make mutation noise for common genes
cross-schema-identical. The existing mutation seed includes the full genome
digest, so schema additions change descendant mutation streams. Any future
lineage experiment that requires matched mutation noise must freeze that
methodological question separately rather than silently changing historical P3
semantics here.

ADR-0015's immediate architecture gate selects among declared generation-zero
candidates, for which common-gene identity is preserved by the final-gene rule.

## No silent migration

A v3 mapping is not accepted as v4 and is not automatically upgraded.

Archived v3 scientific results remain historical evidence under their original
source. No archived genome is rewritten.

## Behavioral boundary

This slice intentionally does **not** read omega in `Mind`.

Two valid v4 genomes that differ only in omega must have identical current
reference cognitive parameters. Candidate F must also produce identical values
unless omega is explicitly supplied later to the experimental first-contact
prior.

Genome identity/digests differ, as they should, because inheritance differs.

## Gate

Pass requires:

1. schema is v4 with exactly 31 genes and omega last;
2. frozen v3 common-gene witnesses are unchanged;
3. midpoint omega is zero and generation-zero produces both signs;
4. v3 mappings fail closed;
5. mutation handles omega inside bounds with no special rule;
6. reference Mind and unwired Candidate F remain omega-blind;
7. full I3 software suite remains green.

A pass authorizes only a separate opt-in cognitive wiring slice.

It does not authorize:

- World/life execution;
- ADR-0015 selection;
- reference adoption;
- I3 registration.
