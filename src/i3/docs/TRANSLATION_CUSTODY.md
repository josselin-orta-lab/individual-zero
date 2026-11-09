# I3 English translation and original-language custody

**Scope:** This is a language and navigation refactor only, not a scientific
intervention. Candidate source relocation is documented separately in
[the Stage-1 archive](../archive/stage1/README.md).

On 9 November 2026, the editable French prose in current and early historical
I3 documents was translated into English at its original documentation path.
Each translated document's **preceding Git blob** was retained byte-for-byte
under `archive/i3/original-language-records-2026-11-09/`. Original document dates, research questions, negative
findings, outcome counts, criteria, protocol identifiers, World seeds and
candidate/replay verdicts were not intentionally changed.

## Translation inventory

The original Git blob SHA is listed below to establish immutability. A
translated English document must not replace the original evidentiary text
when auditing what was known before a frozen protocol.

| Current English document | Preserved original | Original Git blob |
| --- | --- | --- |
| [`src/i3/README.md`](../README.md) | [Original](../../../archive/i3/original-language-records-2026-11-09/src/i3/README.md) | `3e9c11a7076ef091c8aedeb7b2711e7be23269b6` |
| [`src/i3/docs/ARCHITECTURE.md`](ARCHITECTURE.md) | [Original](../../../archive/i3/original-language-records-2026-11-09/src/i3/docs/ARCHITECTURE.md) | `a88dddc45a8bc1a748376cbae2d46a870db5fba6` |
| [`src/i3/docs/G2B_P11_HELDOUT_PREREG.md`](G2B_P11_HELDOUT_PREREG.md) | [Original](../../../archive/i3/original-language-records-2026-11-09/src/i3/docs/G2B_P11_HELDOUT_PREREG.md) | `c10b0510075192ebfc7863c6dd10c10f05a21f13` |
| [`src/i3/docs/G2C_P12_HELDOUT_PREREG.md`](G2C_P12_HELDOUT_PREREG.md) | [Original](../../../archive/i3/original-language-records-2026-11-09/src/i3/docs/G2C_P12_HELDOUT_PREREG.md) | `31f0aa6efc44e00eb08b0ba3f876c6f4bf1822bc` |
| [`src/i3/docs/G2E_P13_V2_PREREG.md`](G2E_P13_V2_PREREG.md) | [Original](../../../archive/i3/original-language-records-2026-11-09/src/i3/docs/G2E_P13_V2_PREREG.md) | `5fe659b838194f6c0718ab6c41989690190f32da` |
| [`src/i3/docs/G2_FIRST_FALSIFIER_PREREG.md`](G2_FIRST_FALSIFIER_PREREG.md) | [Original](../../../archive/i3/original-language-records-2026-11-09/src/i3/docs/G2_FIRST_FALSIFIER_PREREG.md) | `a7b46d03b96d41972afb49d6c49fcb768b560027` |
| [`src/i3/docs/GENERALIZATION_SCENARIO_SOURCE_2026-11-06.md`](GENERALIZATION_SCENARIO_SOURCE_2026-11-06.md) | [Original](../../../archive/i3/original-language-records-2026-11-09/src/i3/docs/GENERALIZATION_SCENARIO_SOURCE_2026-11-06.md) | `934601a9258a8c5373512764a10709aa1859883a` |
| [`src/i3/docs/SPECIFICATION.md`](SPECIFICATION.md) | [Original](../../../archive/i3/original-language-records-2026-11-09/src/i3/docs/SPECIFICATION.md) | `28fb0b9d96106f7ff08286c116aa728fa330e123` |
| [`src/i3/docs/STATUS_BEFORE_GENERALIZATION_2026-11-06.md`](STATUS_BEFORE_GENERALIZATION_2026-11-06.md) | [Original](../../../archive/i3/original-language-records-2026-11-09/src/i3/docs/STATUS_BEFORE_GENERALIZATION_2026-11-06.md) | `4e1204b80f3759a5035c89f7a44d2304f579e5dc` |
| [`src/i3/docs/TEST_PLAN.md`](TEST_PLAN.md) | [Original](../../../archive/i3/original-language-records-2026-11-09/src/i3/docs/TEST_PLAN.md) | `e7a860c5aa278aca10e41035f74a5a5d1ea2e362` |
| [`src/i3/docs/studies/g2-first-falsifier/RESULTS.md`](studies/g2-first-falsifier/RESULTS.md) | [Original](../../../archive/i3/original-language-records-2026-11-09/src/i3/docs/studies/g2-first-falsifier/RESULTS.md) | `75c122873aff349be7de1e014adfc70313471e61` |
| [`src/i3/docs/studies/g2b-p11-heldout/RESULTS.md`](studies/g2b-p11-heldout/RESULTS.md) | [Original](../../../archive/i3/original-language-records-2026-11-09/src/i3/docs/studies/g2b-p11-heldout/RESULTS.md) | `a552ba35a2f933eb9adeda7aacc03bc83652476f` |
| [`src/i3/docs/studies/g2c-p12-heldout/RESULTS.md`](studies/g2c-p12-heldout/RESULTS.md) | [Original](../../../archive/i3/original-language-records-2026-11-09/src/i3/docs/studies/g2c-p12-heldout/RESULTS.md) | `6194f58de9e3d16a6832497b427e98156cf9f32f` |
| [`src/i3/docs/studies/g2e-p13-v2/RESULTS.md`](studies/g2e-p13-v2/RESULTS.md) | [Original](../../../archive/i3/original-language-records-2026-11-09/src/i3/docs/studies/g2e-p13-v2/RESULTS.md) | `cab2d659c014ce9308aad80a378369ba34c5e947` |

## Repository-level exclusions that preserve scientific meaning

- Python public names, module names, action tokens such as `boire`, `manger`,
  `dormir`, `attendre` and `se_deplacer`, schema/JSON keys and workflow
  input identifiers are **not translated**. They are executable interfaces.
- Raw `.json`, `.json.gz`, trace outputs, numerical fixtures and exact
  experimental receipts are not rewritten for stylistic consistency.
- French source quotations preserved as historical evidence remain quoted in
  their original language; accompanying English explanations are editorial.
- Historical documents may contain out-of-date operational instructions. Use
  [STATUS.md](STATUS.md), [ACTIVE_SURFACE.md](ACTIVE_SURFACE.md) and
  [AGENTS.md](../AGENTS.md) for the current handoff, not a preregistration's
  old “next step”.
- The former French
  `GENERALIZATION_SCENARIO_SOURCE_2026-11-06.md` has original Git blob
  `934601a9258a8c5373512764a10709aa1859883a`, length 22,291
  bytes and SHA-256
  `e3a282e839c597cd610682fecb852340dd30f96ea8038874bebd2367b0a8753c`.
  That hash applies to the archived **French original**, not its translation.

## Verification

Every original path above is archived using its exact pre-translation blob,
not a manually edited reconstruction. The Stage-1 code relocation uses
AST parse, Python import-compatibility tests, retained candidate unit tests,
and the main I3 CI on Python 3.11/3.12. No new World or life is generated by
translation or source relocation.

ADR-0019 is accepted for an engineering-cohort-only exact rehearsal;
ADR-0017's scientific-World moratorium remains active.
